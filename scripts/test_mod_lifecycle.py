#!/usr/bin/env python3
"""The candidate guard and the lifecycle commands, on temporary fixtures, never game data or build/."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import mod_distribution as distribution
import mod_lifecycle as lifecycle

TEMPLATE_GUARD = Path(__file__).resolve().parents[1] / 'templates/standalone/scripts/candidate_guard.py'
# A builder that writes $PAYLOAD as its runtime, a receipt, and on `package` the delivery too.
BUILDER = '''import os, sys
from pathlib import Path
from paths import BUILD_ROOT
command = sys.argv[1]
if os.environ.get('FAIL') == command:
    (BUILD_ROOT / 'build.json').write_text('half-written')
    sys.exit(1)
(BUILD_ROOT / 'package').mkdir(parents=True, exist_ok=True)
(BUILD_ROOT / 'package' / 'plugin.nro').write_text(os.environ.get('PAYLOAD', 'one'))
(BUILD_ROOT / f'{command}.json').write_text(os.environ.get('PAYLOAD', 'one'))
if command == 'package':
    (BUILD_ROOT / 'delivery' / 'Sample').mkdir(parents=True, exist_ok=True)
    (BUILD_ROOT / 'delivery' / 'Sample' / 'plugin.nro').write_text(os.environ.get('PAYLOAD', 'one'))
'''


class GuardTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='mhgu-guard-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.mod = self.root / 'mods' / 'sample'
        (self.mod / 'scripts').mkdir(parents=True)
        shutil.copy2(TEMPLATE_GUARD, self.mod / 'scripts' / 'candidate_guard.py')
        (self.mod / 'scripts' / 'build.py').write_text(BUILDER)
        # What makes the fixture the workspace rather than an exported source tree.
        (self.root / 'scripts').mkdir()
        (self.root / 'scripts' / 'mod_lifecycle.py').write_text('')
        self.version('r2', 'DEVELOPMENT', 'r2')
        self.folder = self.root / 'build' / 'sample' / 'candidates' / 'r2'

    def version(self, record, status, folder):
        (self.mod / 'DISTRIBUTION.json').write_text(json.dumps(
            {'mod': 'sample', 'version': record, 'status': status, 'package_name': 'Sample'}))
        (self.mod / 'scripts' / 'paths.py').write_text(
            f"from pathlib import Path\nBUILD_ROOT = Path({str(self.root)!r}) / 'build/sample/candidates/{folder}'\n")

    def run_guard(self, command, **env):
        return subprocess.run([sys.executable, self.mod / 'scripts' / 'candidate_guard.py', command],
                              env={'PATH': '/usr/bin:/bin', **env}, capture_output=True, text=True)

    def files(self):
        return lifecycle.inventory(self.folder)

    def test_a_folder_that_is_not_the_recorded_version_is_refused(self):
        self.version('r3', 'DEVELOPMENT', 'r2')
        result = self.run_guard('build')
        self.assertEqual(result.returncode, 2)
        self.assertIn('DISTRIBUTION.json is at r3', result.stderr)
        self.assertFalse(self.folder.exists())

    def test_a_released_version_is_frozen(self):
        self.version('r2', 'READY_TO_DISTRIBUTE', 'r2')
        for command in ('build', 'test', 'verify', 'package'):
            self.assertEqual(self.run_guard(command).returncode, 2, command)
        self.assertFalse(self.folder.exists())
        self.assertEqual(self.run_guard('doctor').returncode, 0, 'read-only commands still run')
        (self.root / 'scripts' / 'mod_lifecycle.py').unlink()
        self.assertEqual(self.run_guard('build').returncode, 0, 'an exported source tree may rebuild a release')

    def test_an_unpackaged_candidate_rebuilds_freely(self):
        self.assertEqual(self.run_guard('build', PAYLOAD='one').returncode, 0)
        self.assertEqual(self.run_guard('build', PAYLOAD='two').returncode, 0)
        self.assertEqual((self.folder / 'package/plugin.nro').read_text(), 'two')

    def test_a_packaged_candidate_keeps_its_runtime(self):
        self.assertEqual(self.run_guard('package', PAYLOAD='one').returncode, 0)
        self.assertEqual(self.run_guard('build', PAYLOAD='one').returncode, 0, 'the same bytes may be rebuilt')
        packaged = self.files()
        for command in ('build', 'package'):
            result = self.run_guard(command, PAYLOAD='two')
            self.assertEqual(result.returncode, 2, command)
            self.assertIn('restored as it was', result.stderr)
            self.assertEqual(self.files(), packaged, f'{command} left the folder changed')

    def test_a_failed_command_on_a_packaged_candidate_leaves_it_as_it_was(self):
        self.run_guard('package', PAYLOAD='one')
        packaged = self.files()
        self.assertEqual(self.run_guard('test', PAYLOAD='one', FAIL='test').returncode, 1)
        self.assertEqual(self.files(), packaged)


class LifecycleTests(unittest.TestCase):
    """A mod released as r1 by the real packager, in its own git repo as the mods are."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='mhgu-lifecycle-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.folder = self.root / 'mods' / 'sample-mod'
        self.write('mods/sample-mod/README.md', 'Install `sample-mod-r1.zip` beside Forge.\n')
        self.write('mods/sample-mod/NOTICE.txt', 'MIT license example.\n')
        self.write('mods/sample-mod/mod.json', json.dumps({'mod': 'sample-mod', 'version': 'r1'}, indent=2) + '\n')
        self.write('mods/sample-mod/scripts/paths.py', "VERSION='r1-small' if SMALL else 'r1'\n")
        self.manifest = json.dumps({'manifest_version': 1, 'id': 'PurplefinNeptuna/sample-mod', 'version': '0.1.0',
                                    'name': 'Sample', 'authors': ['PurplefinNeptuna'], 'description': 'Fixture.',
                                    'gamebananalink': '', 'requires': {}, 'conflicts': {},
                                    'load': {'after': [], 'before': []}}, indent=2) + '\n'
        self.write('mods/sample-mod/manifest.json', self.manifest)
        self.release('r1', b'runtime one')
        git = ['git', '-C', str(self.folder)]
        subprocess.run([*git, 'init', '-q'], check=True)
        self.commit('r1 released')

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text if isinstance(text, bytes) else text.encode())

    def commit(self, message):
        git = ['git', '-C', str(self.folder), '-c', 'user.name=t', '-c', 'user.email=t@example.com']
        subprocess.run([*git, 'add', '-A'], check=True)
        subprocess.run([*git, 'commit', '-qm', message], check=True)

    def release(self, version, runtime):
        """Record `version` as READY with `runtime` as its NRO and package its release."""
        package = f'build/sample-mod/candidates/{version}/package'
        manifest = self.manifest.replace('"0.1.0"', f'"0.{version[1:]}.0"')
        self.write(f'{package}/plugin.nro', runtime)
        self.write(f'{package}/manifest.json', manifest)
        self.write(f'build/sample-mod/candidates/{version}/delivery/sample-mod/plugin.nro', runtime)
        self.write(f'build/sample-mod/candidates/{version}/tests.json', '{"status":"PASSED"}\n')
        spec = {
            'schema_version': 1, 'mod': 'sample-mod', 'status': 'READY_TO_DISTRIBUTE', 'reason': f'{version} fixture',
            'publication': dict(lifecycle.UNPUBLISHED), 'version': version, 'package_name': 'sample-mod',
            'archive': f'sample-mod-{version}.zip', 'approval': {'date': '2026-11-25', 'basis': 'Fixture approval'},
            'target': 'Fixture only', 'limitations': ['No game runtime claim'], 'readme': 'mods/sample-mod/README.md',
            'notices': ['mods/sample-mod/NOTICE.txt'],
            'gamebanana': {'ai_code': {'used': True, 'scope': 'Fixture code.', 'software': [
                {'name': 'Fixture Assistant', 'url': 'https://example.com/assistant'}]}, 'ai_assets': [],
                'credits': [{'name': 'Fixture library', 'author': 'Fixture developers',
                             'url': 'https://example.com/library', 'scope': 'MIT-licensed code.'}]},
            'payloads': {'romfs/nativeNX/plugins/plugin.nro': {
                'source': f'{package}/plugin.nro', 'sha256': distribution.digest(runtime)},
                'manifest.json': {'source': f'{package}/manifest.json',
                                  'sha256': distribution.digest(manifest.encode())}},
            'evidence': {'static': [f'build/sample-mod/candidates/{version}/tests.json'], 'manual_summary': 'None'},
        }
        self.write('mods/sample-mod/DISTRIBUTION.json', distribution.json_bytes(spec))
        distribution.package('sample-mod', self.root)

    def spec(self):
        return json.loads((self.folder / 'DISTRIBUTION.json').read_text())

    def test_start_archives_the_release_by_move_and_moves_every_version_copy(self):
        released = lifecycle.inventory(self.root / 'build/sample-mod/releases/r1')
        lifecycle.start(self.root, 'sample-mod', 'r2: a fixture change')
        archived = self.root / 'backups/accepted/sample-mod/r1-before-r2'
        self.assertEqual(lifecycle.inventory(archived / 'release'), released)
        self.assertEqual(json.loads((archived / 'preservation.json').read_text())['release_sha256'], released)
        self.assertEqual(json.loads((archived / 'DISTRIBUTION.json').read_text())['status'], 'READY_TO_DISTRIBUTE')
        self.assertFalse((self.root / 'build/sample-mod/releases').exists())
        spec = self.spec()
        self.assertEqual((spec['status'], spec['version'], spec['archive']),
                         ('DEVELOPMENT', 'r2', 'sample-mod-r2-candidate.zip'))
        self.assertEqual(spec['candidate'], 'build/sample-mod/candidates/r2/delivery')
        self.assertNotIn('approval', spec)
        self.assertEqual(spec['payloads']['romfs/nativeNX/plugins/plugin.nro']['source'],
                         'build/sample-mod/candidates/r2/package/plugin.nro')
        self.assertIn('"version": "r2"', (self.folder / 'mod.json').read_text())
        self.assertEqual((self.folder / 'scripts/paths.py').read_text(), "VERSION='r2-small' if SMALL else 'r2'\n")
        self.assertIn('"version": "0.2.0"', (self.folder / 'manifest.json').read_text())
        distribution.spec_for('sample-mod', self.root)

    def test_start_refuses_uncommitted_work_and_skips_used_numbers(self):
        self.write('mods/sample-mod/src.rs', 'work in progress')
        with self.assertRaises(ValueError):
            lifecycle.start(self.root, 'sample-mod', 'r2')
        self.assertTrue((self.root / 'build/sample-mod/releases/r1').is_dir(), 'nothing moved')
        self.commit('work')
        (self.root / 'build/sample-mod/candidates/r4').mkdir()
        lifecycle.start(self.root, 'sample-mod', 'after r4')
        self.assertEqual(self.spec()['version'], 'r5')

    def test_withdraw_keeps_the_version_and_needs_its_delivery(self):
        shutil.rmtree(self.root / 'build/sample-mod/candidates/r1/delivery')
        with self.assertRaises(ValueError):
            lifecycle.withdraw(self.root, 'sample-mod', 'r1 is broken')
        self.write('build/sample-mod/candidates/r1/delivery/sample-mod/plugin.nro', b'runtime one')
        lifecycle.withdraw(self.root, 'sample-mod', 'r1 is broken')
        spec = self.spec()
        self.assertEqual((spec['status'], spec['version']), ('DEVELOPMENT', 'r1'))
        self.assertTrue((self.root / 'backups/accepted/sample-mod/r1-withdrawn/release').is_dir())

    def test_rollback_restores_the_archived_release_exactly(self):
        released = lifecycle.inventory(self.root / 'build/sample-mod/releases/r1')
        lifecycle.start(self.root, 'sample-mod', 'r2')
        self.write('mods/sample-mod/README.md', 'Install `sample-mod-r2.zip` beside Forge.\n')
        self.release('r2', b'runtime two')
        self.commit('r2 released')
        lifecycle.rollback(self.root, 'sample-mod', 'r1', 'r2 crashes on load')
        self.assertEqual(lifecycle.inventory(self.root / 'build/sample-mod/releases/r1'), released)
        self.assertTrue((self.root / 'backups/accepted/sample-mod/r2-rolled-back-to-r1/release').is_dir())
        spec = distribution.spec_for('sample-mod', self.root)
        self.assertEqual(spec['version'], 'r1')
        archived = self.root / 'backups/accepted/sample-mod/r2-rolled-back-to-r1'
        kept = json.loads((archived / 'preservation.json').read_text())
        self.assertEqual(kept['reason'], 'r2 crashes on load')
        distribution.verify_release(spec, self.root)

    def test_rollback_refuses_when_the_old_sources_were_overwritten(self):
        lifecycle.start(self.root, 'sample-mod', 'r2')
        self.release('r2', b'runtime two')
        self.commit('r2 released')
        self.write('build/sample-mod/candidates/r1/package/plugin.nro', b'rebuilt later')
        with self.assertRaises(ValueError):
            lifecycle.rollback(self.root, 'sample-mod', 'r1', 'r2 crashes')
        self.assertTrue((self.root / 'build/sample-mod/releases/r2').is_dir(), 'nothing moved')


if __name__ == '__main__':
    unittest.main()
