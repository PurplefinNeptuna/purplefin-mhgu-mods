#!/usr/bin/env python3
"""Exercise distribution gates with isolated temporary inputs, never game data."""
import copy
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
import zipfile

import mod_distribution as distribution


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='mhgu-distribution-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.mod = 'sample-mod'
        self.write('mods/sample-mod/README.md', b'Install sample-mod alongside Forge.\n')
        self.write('mods/sample-mod/NOTICE.txt', b'MIT license example.\n')
        self.write('build/sample-mod/validated.nro', b'validated-runtime\x00\x01')
        self.write('build/sample-mod/tests.json', b'{"status":"PASSED"}\n')
        self.spec = {
            'schema_version': 1, 'mod': self.mod, 'status': 'READY_TO_DISTRIBUTE',
            'reason': 'Approved fixture', 'publication': {'published': False, 'url': None, 'date': None},
            'version': 'r1', 'package_name': self.mod, 'archive': 'sample-mod-r1.zip',
            'approval': {'date': '2026-10-06', 'basis': 'Fixture approval'},
            'target': 'Fixture only', 'limitations': ['No game runtime claim'],
            'readme': 'mods/sample-mod/README.md', 'notices': ['mods/sample-mod/NOTICE.txt'],
            'payloads': {'romfs/nativeNX/plugins/test.nro': {
                'source': 'build/sample-mod/validated.nro',
                'sha256': distribution.digest(b'validated-runtime\x00\x01')}},
            'evidence': {'static': ['build/sample-mod/tests.json'],
                         'manual_summary': 'No manual gameplay claimed'},
        }
        self.save_spec()

    def write(self, name, blob):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
        return path

    def save_spec(self):
        self.write('mods/sample-mod/DISTRIBUTION.json', distribution.json_bytes(self.spec))

    def package(self, **kwargs):
        return distribution.package(self.mod, self.root, **kwargs)

    def rejected(self, action):
        with self.assertRaises((ValueError, KeyError, TypeError, OSError)):
            action()

    def test_ready_requires_artifacts_and_is_deterministic(self):
        self.rejected(lambda: distribution.check(self.root))
        distribution.check(self.root, source_only=True)
        archive = self.package()
        original = archive.read_bytes()
        first = distribution.inventory(archive.parent)
        self.package()
        self.assertEqual(first, distribution.inventory(archive.parent))
        self.assertEqual(original, archive.read_bytes())
        with zipfile.ZipFile(archive) as zipped:
            self.assertEqual(zipped.namelist(), ['README.md', 'sample-mod/romfs/nativeNX/plugins/test.nro'])
            self.assertEqual(zipped.read('README.md'), first['README.md'])
        distribution.check(self.root)

    def test_future_unregistered_mod_is_rejected(self):
        self.package()
        (self.root / 'mods/new-mod').mkdir()
        self.rejected(lambda: distribution.check(self.root, source_only=True))
        self.rejected(lambda: distribution.check(self.root))

    def test_future_scaffolds_package_readme_beside_runtime_for_every_kind(self):
        from standalone_mods import scaffold
        for kind in ('plugin', 'resource', 'cheat', 'tool'):
            with self.subTest(kind=kind):
                name = 'future-' + kind
                folder = scaffold(self.root / name, name, kind)
                spec = copy.deepcopy(self.spec)
                spec.update(mod=name, package_name=name, archive=name + '-r1.zip',
                            readme='README.md', notices=['LICENSE'])
                runtime = ('cheats/0000000000000000.txt' if kind == 'cheat' else
                           'exefs/example.txt' if kind == 'tool' else
                           'romfs/nativeNX/plugins/test.nro' if kind == 'plugin' else
                           'romfs/nativeNX/example.txt')
                spec['payloads'] = {runtime: {'source': 'build/validated.bin',
                                            'sha256': distribution.digest(b'fixture-runtime')}}
                spec['evidence']['static'] = ['build/tests.json']
                (folder / 'DISTRIBUTION.json').write_bytes(distribution.json_bytes(spec))
                (folder / 'build').mkdir()
                (folder / 'build/validated.bin').write_bytes(b'fixture-runtime')
                (folder / 'build/tests.json').write_bytes(b'{"status":"PASSED"}\n')
                for args in (['package', name], ['check']):
                    subprocess.run([sys.executable, str(folder / 'scripts/mod_distribution.py'), *args],
                                   cwd=folder, check=True, capture_output=True)
                archive = folder / 'build' / name / 'releases/r1' / spec['archive']
                with zipfile.ZipFile(archive) as zipped:
                    self.assertEqual(zipped.namelist(), ['README.md', name + '/' + runtime])
                    self.assertEqual(zipped.read('README.md'), (folder / 'README.md').read_bytes())

    def test_git_gate_rejects_unstaged_registry_and_support(self):
        def git(*args):
            subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True)
        git('init', '-q')
        git('add', 'mods/sample-mod/README.md')
        self.rejected(lambda: distribution.check_staged(self.root))
        git('add', 'mods')
        distribution.check_staged(self.root)
        self.write('mods/sample-mod/README.md', b'Forgotten staged documentation.\n')
        self.rejected(lambda: distribution.check_staged(self.root))
        git('add', 'mods')
        distribution.check_staged(self.root)

    def test_missing_support_and_corrupt_zip_are_rejected(self):
        for name in ('NOTICES.txt', 'README.md', 'release-manifest.json', 'SHA256SUMS', 'sample-mod-r1.zip'):
            with self.subTest(name=name):
                archive = self.package()
                path = archive.parent / name
                data = path.read_bytes()
                path.unlink()
                self.rejected(lambda: distribution.check(self.root))
                path.write_bytes(data + b'changed')
                self.rejected(lambda: distribution.check(self.root))
                path.write_bytes(data)

    def test_changed_input_rejected_before_writes(self):
        self.write('build/sample-mod/validated.nro', b'unapproved-runtime')
        self.rejected(self.package)
        self.assertFalse((self.root / 'build/sample-mod/releases/r1').exists())

    def test_unapproved_status_and_missing_evidence_cannot_package(self):
        old = copy.deepcopy(self.spec)
        for status in ('DEVELOPMENT', 'LOCAL_ONLY', 'RETIRED'):
            self.spec['status'] = status
            self.save_spec()
            self.rejected(self.package)
        self.spec = old
        self.save_spec()
        (self.root / 'build/sample-mod/tests.json').unlink()
        self.rejected(self.package)
        self.assertFalse((self.root / 'build/sample-mod/releases/r1').exists())

    def test_existing_runtime_cannot_be_replaced_by_support_refresh(self):
        archive = self.package()
        original = distribution.inventory(archive.parent)
        blob = b'new-approved-runtime'
        self.write('build/sample-mod/validated.nro', blob)
        self.spec['payloads']['romfs/nativeNX/plugins/test.nro']['sha256'] = distribution.digest(blob)
        self.save_spec()
        self.rejected(lambda: self.package(refresh_support=True))
        self.assertEqual(original, distribution.inventory(archive.parent))

    def test_support_refresh_requires_flag_and_verified_backup(self):
        archive = self.package()
        old = distribution.inventory(archive.parent)
        self.write('mods/sample-mod/README.md', b'Updated install instructions.\n')
        self.rejected(self.package)
        self.package(refresh_support=True)
        self.assertNotEqual(old['sample-mod-r1.zip'], archive.read_bytes())
        with zipfile.ZipFile(archive) as zipped:
            self.assertEqual(zipped.read('README.md'), b'Updated install instructions.\n')
            self.assertEqual(zipped.read('sample-mod/romfs/nativeNX/plugins/test.nro'),
                             old['sample-mod/romfs/nativeNX/plugins/test.nro'])
        receipts = list((self.root / 'backups/sample-mod/distribution-support').glob('*/backup-manifest.json'))
        self.assertEqual(len(receipts), 1)
        self.assertEqual(distribution.inventory(receipts[0].parent / 'r1'), old)
        self.assertEqual(json.loads(receipts[0].read_text()),
                         {p: distribution.digest(b) for p, b in old.items()})
        distribution.check(self.root)

    def test_legacy_zip_refresh_adds_readme_and_preserves_backup(self):
        archive = self.package()
        runtime = {'romfs/nativeNX/plugins/test.nro': b'validated-runtime\x00\x01'}
        archive.write_bytes(distribution.make_zip(runtime, self.mod, None))
        old = distribution.inventory(archive.parent)
        self.rejected(lambda: distribution.check(self.root))
        self.rejected(self.package)
        self.package(refresh_support=True)
        receipt = next((self.root / 'backups/sample-mod/distribution-support').glob('*/backup-manifest.json'))
        self.assertEqual(distribution.inventory(receipt.parent / 'r1'), old)
        with zipfile.ZipFile(archive) as zipped:
            self.assertEqual(zipped.namelist(), ['README.md', self.mod + '/romfs/nativeNX/plugins/test.nro'])
        distribution.check(self.root)

    def test_support_metadata_refresh_preserves_zip(self):
        archive = self.package()
        old = archive.read_bytes()
        self.spec['limitations'].append('Another coverage limit')
        self.save_spec()
        self.package(refresh_support=True)
        self.assertEqual(old, archive.read_bytes())
        distribution.check(self.root)

    def test_refresh_rejects_modified_zip_members_without_writes(self):
        archive = self.package()
        original = archive.read_bytes()
        for name, blob in [('sample-mod/README.md', b'Wrong location'),
                           ('README.md', b'Stale instructions'),
                           ('sample-mod/romfs/nativeNX/plugins/test.nro', b'changed-runtime')]:
            with self.subTest(name=name):
                with zipfile.ZipFile(archive, 'w') as zipped:
                    members = {'README.md': b'Install sample-mod alongside Forge.\n',
                               'sample-mod/romfs/nativeNX/plugins/test.nro': b'validated-runtime\x00\x01'}
                    members[name] = blob
                    for member, data in members.items():
                        zipped.writestr(member, data)
                old = distribution.inventory(archive.parent)
                self.rejected(lambda: self.package(refresh_support=True))
                self.assertEqual(old, distribution.inventory(archive.parent))
        archive.write_bytes(original)

    def test_extra_files_symlinks_and_old_versions_are_rejected(self):
        archive = self.package()
        extra = self.write(str((archive.parent / 'extra.txt').relative_to(self.root)), b'extra')
        self.rejected(lambda: distribution.check(self.root))
        extra.unlink()
        extra.symlink_to(self.root / 'mods/sample-mod/README.md')
        self.rejected(lambda: distribution.check(self.root))
        extra.unlink()
        (archive.parent.parent / 'r0').mkdir()
        self.rejected(lambda: distribution.check(self.root))

    def test_retired_mod_cannot_remain_in_current_workspace(self):
        self.spec['status'] = 'RETIRED'
        self.save_spec()
        self.rejected(lambda: distribution.check(self.root, source_only=True))
        self.rejected(lambda: distribution.check(self.root))

    def test_unregistered_release_directory_is_rejected(self):
        self.package()
        (self.root / 'build/unknown-mod/releases/r1').mkdir(parents=True)
        self.rejected(lambda: distribution.check(self.root))

    def test_candidate_archives_cannot_masquerade_as_flat_releases(self):
        self.package()
        flat = self.write('build/sample-mod/sample-mod-candidate.zip', b'development archive')
        self.rejected(lambda: distribution.check(self.root))
        candidate = self.root / 'build/sample-mod/candidates/sample-mod-candidate.zip'
        candidate.parent.mkdir()
        flat.rename(candidate)
        distribution.check(self.root)

    def test_paths_and_archive_names_are_validated(self):
        for invalid in ('../escape', '/tmp/escape', 'a/../escape', 'a\\escape', 'a//b'):
            with self.subTest(path=invalid):
                self.rejected(lambda: distribution.relative(invalid))
        for field, invalid in [('version', '../r1'), ('package_name', 'romfs/extra'),
                               ('archive', 'sample-mod-r10.zip')]:
            with self.subTest(field=field):
                old = copy.deepcopy(self.spec)
                self.spec[field] = invalid
                self.save_spec()
                self.rejected(self.package)
                self.spec = old
                self.save_spec()

    def test_source_symlink_and_document_in_runtime_root_rejected(self):
        path = self.root / 'build/sample-mod/validated.nro'
        path.unlink()
        path.symlink_to(self.root / 'mods/sample-mod/README.md')
        self.rejected(self.package)
        path.unlink()
        path.write_bytes(b'validated-runtime\x00\x01')
        payload = self.spec['payloads'].pop('romfs/nativeNX/plugins/test.nro')
        self.spec['payloads']['README.md'] = payload
        self.save_spec()
        self.rejected(self.package)

    def test_publication_needs_url_and_date_and_legacy_records_agree(self):
        self.spec['status'] = 'PUBLISHED'
        self.save_spec()
        self.rejected(self.package)
        self.spec['publication'] = {'published': True, 'url': 'https://example.com/sample-mod-r1.zip',
                                    'date': '2026-10-06'}
        self.save_spec()
        self.package()
        self.write('mods/sample-mod/RELEASE.json', b'{"status":"READY_TO_DISTRIBUTE","published":false}\n')
        self.rejected(lambda: distribution.check(self.root, source_only=True))


if __name__ == '__main__':
    unittest.main()
