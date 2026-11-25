#!/usr/bin/env python3
"""Exercise distribution gates with isolated temporary inputs, never game data."""
import copy
from html import unescape
from html.parser import HTMLParser
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
        manifest = json.dumps({'manifest_version': 1, 'id': 'PurplefinNeptuna/sample-mod', 'version': '0.1.0',
                               'name': 'Sample', 'authors': ['PurplefinNeptuna'], 'description': 'Fixture.',
                               'gamebananalink': '', 'requires': {'PurplefinNeptuna/purple-lib': '>=0.20.0'},
                               'conflicts': {}, 'load': {'after': ['PurplefinNeptuna/purple-lib'], 'before': []}}).encode()
        self.write('build/sample-mod/manifest.json', manifest)
        self.spec = {
            'schema_version': 1, 'mod': self.mod, 'status': 'READY_TO_DISTRIBUTE',
            'reason': 'Approved fixture', 'publication': {'published': False, 'url': None, 'date': None},
            'version': 'r1', 'package_name': self.mod, 'archive': 'sample-mod-r1.zip',
            'approval': {'date': '2026-10-06', 'basis': 'Fixture approval'},
            'target': 'Fixture only', 'limitations': ['No game runtime claim'],
            'readme': 'mods/sample-mod/README.md', 'notices': ['mods/sample-mod/NOTICE.txt'],
            'gamebanana': {
                'ai_code': {'used': True, 'scope': 'Assisted with fixture code.',
                            'software': [{'name': 'Fixture Coding Assistant', 'url': 'https://example.com/assistant'}]},
                'ai_assets': [],
                'credits': [{'name': 'Fixture library', 'author': 'Fixture developers',
                             'url': 'https://example.com/library', 'scope': 'MIT-licensed code.'}],
            },
            'payloads': {'romfs/nativeNX/plugins/test.nro': {
                'source': 'build/sample-mod/validated.nro',
                'sha256': distribution.digest(b'validated-runtime\x00\x01')},
                'manifest.json': {'source': 'build/sample-mod/manifest.json', 'sha256': distribution.digest(manifest)}},
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

    def test_archive_follows_a_declared_stem_only(self):
        self.spec.update(archive='public-name-r1.zip')
        self.save_spec()
        self.rejected(self.package)
        self.spec['archive_stem'] = 'public-name'
        self.save_spec()
        self.assertEqual(self.package().name, 'public-name-r1.zip')

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
            self.assertEqual(zipped.namelist(), ['README.md', 'sample-mod/manifest.json', 'sample-mod/romfs/nativeNX/plugins/test.nro'])
            self.assertEqual(zipped.read('README.md'), first['README.md'])
            self.assertNotIn('NOTICES.txt', zipped.namelist())
            self.assertNotIn('NOTICES.html', zipped.namelist())
            self.assertNotIn('README.html', zipped.namelist())
            self.assertNotIn('GAMEBANANA_README.html', zipped.namelist())
        self.assertEqual(first['README.html'], b'<p>Install sample-mod alongside Forge.</p>\n')
        distribution.check(self.root)

    def test_readme_naming_another_version_is_rejected(self):
        self.write('mods/sample-mod/README.md', b'Extract `sample-mod-r1.zip`; r0 is history.\n')
        distribution.check(self.root, source_only=True)
        self.write('mods/sample-mod/README.md', b'Check **Loaded Plugins**: `Sample Mod r0`.\n')
        self.rejected(lambda: distribution.check(self.root, source_only=True))

    def test_future_unregistered_mod_is_rejected(self):
        self.package()
        (self.root / 'mods/new-mod').mkdir()
        self.rejected(lambda: distribution.check(self.root, source_only=True))
        self.rejected(lambda: distribution.check(self.root))

    def test_new_builds_need_a_valid_manifest_json(self):
        # The rules themselves are tested in test_mod_manifest.py.
        manifest = self.root / 'build/sample-mod/manifest.json'
        blob = manifest.read_bytes().replace(b'0.1.0', b'0.2.0')
        manifest.write_bytes(blob)
        self.spec['payloads']['manifest.json']['sha256'] = distribution.digest(blob)
        self.save_spec()
        self.rejected(self.package)
        # A release written before the rule, without one, still verifies and re-packages.
        del self.spec['payloads']['manifest.json']
        self.save_spec()
        directory = distribution.release_dir(self.spec, self.root)
        for name, blob in distribution.expected_files(self.spec, self.root).items():
            self.write(str((directory / name).relative_to(self.root)), blob)
        self.package()
        distribution.check(self.root)

    def test_public_folder_name_with_spaces_is_preserved_in_zip(self):
        self.spec['package_name'] = 'Please do Better PC'
        self.save_spec()
        archive = self.package()
        with zipfile.ZipFile(archive) as zipped:
            self.assertEqual(zipped.namelist(), [
                'Please do Better PC/manifest.json', 'Please do Better PC/romfs/nativeNX/plugins/test.nro', 'README.md'])
        distribution.check(self.root)

    def test_public_folder_names_cannot_escape_or_loosen_version_rules(self):
        for name in ('../Please do Better PC', 'Please/Better', 'Please\\Better',
                     ' Please do Better PC', 'Please do Better PC ',
                     'Please  do Better PC', 'Please:Better', '.'):
            with self.subTest(name=name):
                self.spec['package_name'] = name
                self.save_spec()
                self.rejected(self.package)
        self.spec['package_name'] = 'Please do Better PC'
        self.spec['version'] = 'r1 with spaces'
        self.save_spec()
        self.rejected(self.package)

    def test_developer_documents_cannot_be_release_notices(self):
        for name in ('THIRD_PARTY.md', 'DEVELOPMENT.md', 'README.md'):
            with self.subTest(name=name):
                source = 'mods/sample-mod/' + name
                self.write(source, b'Developer provenance and history.\n')
                self.spec['notices'] = [source]
                self.save_spec()
                self.rejected(self.package)
        self.assertFalse((self.root / 'build/sample-mod/releases/r1').exists())

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
                self.assertEqual((archive.parent / 'README.html').read_bytes(),
                                 distribution.readme_html((folder / 'README.md').read_bytes()))
                self.assertEqual((archive.parent / 'GAMEBANANA_README.html').read_bytes(),
                                 distribution.gamebanana_readme_html((folder / 'README.md').read_bytes(),
                                                                      spec['gamebanana']))

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

    def test_git_gate_checks_only_the_mods_a_commit_touches(self):
        def git(*args):
            subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True)
        other = copy.deepcopy(self.spec)
        other.update(mod='other-mod', package_name='other-mod', archive='other-mod-r1.zip',
                     readme='mods/other-mod/README.md', notices=['mods/other-mod/NOTICE.txt'])
        self.write('mods/other-mod/README.md', b'Install other-mod alongside Forge.\n')
        self.write('mods/other-mod/NOTICE.txt', b'MIT license example.\n')
        self.write('mods/other-mod/DISTRIBUTION.json', distribution.json_bytes(other))
        git('init', '-q')
        git('add', 'mods')
        git('-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '-m', 'base')
        # Work in progress on other-mod, left unstaged, and a broken package of it on disk.
        other['reason'] = 'Being changed by other work'
        self.write('mods/other-mod/DISTRIBUTION.json', distribution.json_bytes(other))
        self.write('build/other-mod/releases/stale/x.txt', b'unregistered release entry\n')
        self.write('mods/sample-mod/README.md', b'Install sample-mod alongside Forge, updated.\n')
        git('add', 'mods/sample-mod')
        self.assertEqual(distribution.staged_mods(self.root), {'sample-mod'})
        distribution.check_staged(self.root)
        self.rejected(lambda: distribution.check(self.root, only={'other-mod'}))
        # A commit that touches other-mod is checked as before.
        self.write('mods/other-mod/README.md', b'Install other-mod alongside Forge, updated.\n')
        git('add', 'mods/other-mod/README.md')
        self.rejected(lambda: distribution.check_staged(self.root))
        # Staging the checker itself checks every mod's package, but not other mods' unstaged records.
        git('reset', '-q', 'mods/other-mod/README.md')
        self.write('scripts/mod_distribution.py', b'# fixture\n')
        git('add', 'scripts')
        self.assertIsNone(distribution.packages_to_check(self.root))
        self.assertEqual(distribution.staged_mods(self.root), {'sample-mod'})
        distribution.check_staged(self.root)

    def test_missing_support_and_corrupt_zip_are_rejected(self):
        for name in ('NOTICES.html', 'NOTICES.txt', 'README.md', 'release-manifest.json', 'SHA256SUMS', 'sample-mod-r1.zip'):
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

    def test_extra_archive_is_built_from_sources_and_added_by_refresh(self):
        archive = self.package()
        old = distribution.inventory(archive.parent)
        self.write('mods/sample-mod/API.md', b'API for other mods.\n')
        self.spec['archives'] = {'sample-mod-api-r1.zip': {'docs/API.md': 'mods/sample-mod/API.md'}}
        self.save_spec()
        self.rejected(self.package)
        self.package(refresh_support=True)
        self.assertEqual(archive.read_bytes(), old['sample-mod-r1.zip'])
        with zipfile.ZipFile(archive.parent / 'sample-mod-api-r1.zip') as zipped:
            self.assertEqual(zipped.namelist(), ['docs/API.md'])
            self.assertEqual(zipped.read('docs/API.md'), b'API for other mods.\n')
        distribution.check(self.root)
        for bad in ('sample-mod-r1.zip', 'kit.txt'):
            self.spec['archives'] = {bad: {'docs/API.md': 'mods/sample-mod/API.md'}}
            self.save_spec()
            self.rejected(lambda: distribution.check(self.root, source_only=True))

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
        runtime = {'romfs/nativeNX/plugins/test.nro': b'validated-runtime\x00\x01',
                   'manifest.json': (self.root / 'build/sample-mod/manifest.json').read_bytes()}
        archive.write_bytes(distribution.make_zip(runtime, self.mod, {}))
        old = distribution.inventory(archive.parent)
        self.rejected(lambda: distribution.check(self.root))
        self.rejected(self.package)
        self.package(refresh_support=True)
        receipt = next((self.root / 'backups/sample-mod/distribution-support').glob('*/backup-manifest.json'))
        self.assertEqual(distribution.inventory(receipt.parent / 'r1'), old)
        with zipfile.ZipFile(archive) as zipped:
            self.assertEqual(zipped.namelist(), ['README.md', self.mod + '/manifest.json', self.mod + '/romfs/nativeNX/plugins/test.nro'])
        distribution.check(self.root)

    def test_support_metadata_refresh_preserves_zip(self):
        archive = self.package()
        old = archive.read_bytes()
        self.spec['limitations'].append('Another coverage limit')
        self.save_spec()
        self.package(refresh_support=True)
        self.assertEqual(old, archive.read_bytes())
        distribution.check(self.root)

    def test_notice_refresh_updates_adjacent_formats_and_preserves_zip(self):
        archive = self.package()
        old = distribution.inventory(archive.parent)
        notice = b'Copyright (c) Fixture contributors\n\nPermission & conditions remain intact.\n'
        self.write('mods/sample-mod/NOTICE.txt', notice)
        self.rejected(self.package)
        self.package(refresh_support=True)
        with zipfile.ZipFile(archive) as zipped:
            self.assertEqual(old['sample-mod-r1.zip'], archive.read_bytes())
            self.assertEqual((archive.parent / 'NOTICES.txt').read_bytes(), notice)
            self.assertIn(b'Permission &amp; conditions remain intact.', (archive.parent / 'NOTICES.html').read_bytes())
            self.assertNotIn('NOTICES.txt', zipped.namelist())
            self.assertNotIn('NOTICES.html', zipped.namelist())
            self.assertEqual(zipped.read('sample-mod/romfs/nativeNX/plugins/test.nro'),
                             old['sample-mod/romfs/nativeNX/plugins/test.nro'])
        receipt = next((self.root / 'backups/sample-mod/distribution-support').glob('*/backup-manifest.json'))
        self.assertEqual(distribution.inventory(receipt.parent / 'r1'), old)
        distribution.check(self.root)

    def test_older_delivery_adds_adjacent_html_without_changing_zip(self):
        archive = self.package()
        runtime = {'romfs/nativeNX/plugins/test.nro': b'validated-runtime\x00\x01',
                   'manifest.json': (self.root / 'build/sample-mod/manifest.json').read_bytes()}
        archive.write_bytes(distribution.make_zip(runtime, self.mod,
                                                {'README.md': (archive.parent / 'README.md').read_bytes()}))
        (archive.parent / 'NOTICES.html').unlink()
        (archive.parent / 'README.html').unlink()
        (archive.parent / 'GAMEBANANA_README.html').unlink()
        old = distribution.inventory(archive.parent)
        self.rejected(self.package)
        self.package(refresh_support=True)
        receipt = next((self.root / 'backups/sample-mod/distribution-support').glob('*/backup-manifest.json'))
        self.assertEqual(distribution.inventory(receipt.parent / 'r1'), old)
        self.assertEqual(archive.read_bytes(), old['sample-mod-r1.zip'])
        distribution.check(self.root)

    def test_readme_html_preserves_guide_structure_and_escapes_markup(self):
        markdown = b'''# Fixture Mod

Shows **gold digits** and *markers* with `A > B`.

## Installation

1. Get [Forge](https://example.com/releases?a=1&b=2).
2. Copy `fixture-mod` into:
   - Eden: `~/.local/share/eden/load/`
   - Ryujinx: `mods/contents/`
3. Enable the mod.

## Settings

```ini
[Fixture]
enabled=1
literal=<script>&
```

| Setting | Value |
| --- | --- |
| `enabled` | `1` or `0` |

<script>alert('literal')</script>
[Unsafe](javascript:alert) [Local](README.md)
'''
        html = distribution.readme_html(markdown)
        self.assertIn(b'<h2>Installation</h2>', html)
        self.assertIn(b'<strong>gold digits</strong>', html)
        self.assertIn(b'<em>markers</em>', html)
        self.assertIn(b'<code>A &gt; B</code>', html)
        self.assertIn(b'href="https://example.com/releases?a=1&amp;b=2"', html)
        self.assertIn(b'<li><p>Copy <code>fixture-mod</code> into:</p>\n<ul>', html)
        self.assertIn(b'<li><p>Enable the mod.</p></li>\n</ol>', html)
        self.assertIn(b'<pre><code>[Fixture]\nenabled&#61;1\nliteral&#61;&lt;script&gt;&amp;</code></pre>', html)
        self.assertIn(b'<th>Setting</th><th>Value</th>', html)
        self.assertIn(b'<td><code>enabled</code></td><td><code>1</code> or <code>0</code></td>', html)
        self.assertNotIn(b'<script>', html)
        self.assertNotIn(b'href="javascript:', html)
        self.assertNotIn(b'href="README.md"', html)

    def test_html_code_assignments_keep_copyable_text_without_raw_style_assignment(self):
        markdown = b'Use `style=rise`.\n\n```ini\n[DamageNumbers]\nstyle = wilds\n```\n'
        for html in (distribution.readme_html(markdown),
                     distribution.gamebanana_readme_html(markdown, self.spec['gamebanana']),
                     distribution.notices_html([('NOTICE.md', b'Use `style=rise`.\n')])):
            with self.subTest(html=html):
                self.assertNotRegex(html, rb'(?i)\bstyle\s*=')
                self.assertIn(b'<code>style&#61;rise</code>', html)
                self.assertIn('<code>style=rise</code>', unescape(html.decode('ascii')))
                if b'<pre>' in html:
                    self.assertIn('[DamageNumbers]\nstyle = wilds', unescape(html.decode('ascii')))

    def test_html_keeps_unicode_literal_in_guides_credits_and_licenses(self):
        text = 'Copyright © Unicode, Inc. 花花花花花椰菜 <script> & "terms"'
        markdown = text.encode('utf-8')
        profile = copy.deepcopy(self.spec['gamebanana'])
        profile['credits'][0]['author'] = '花花花花花椰菜'
        for html in (distribution.readme_html(markdown),
                     distribution.gamebanana_readme_html(markdown, profile),
                     distribution.notices_html([('LICENSE', markdown)])):
            with self.subTest(html=html):
                rendered = html.decode('utf-8')
                self.assertIn('©', rendered)
                self.assertIn('花花花花花椰菜', rendered)
                self.assertNotRegex(html, rb'&#(?:[0-9]+|[xX][0-9a-fA-F]+);')
                self.assertNotIn(b'<script>', html)
                self.assertIn(b'&lt;script&gt; &amp; &quot;terms&quot;', html)
                self.assertIn(text, unescape(rendered))

    def test_html_apostrophes_stay_literal_without_unescaping_markup_or_attributes(self):
        markdown = b'''Fexty's guide: <script>alert('literal')</script>

[Author's page](https://example.com/author's?x="quoted"&y=1)

`don't <script>`
'''
        profile = copy.deepcopy(self.spec['gamebanana'])
        profile['ai_code']['scope'] = "Author's code."
        profile['credits'][0]['author'] = "Author's team"
        for html in (distribution.readme_html(markdown),
                     distribution.gamebanana_readme_html(markdown, profile),
                     distribution.notices_html([('NOTICE.md', markdown),
                                               ('LICENSE', b"Author's terms: <script>literal</script>")])):
            with self.subTest(html=html):
                self.assertNotIn(b'&#x27', html)
                self.assertNotIn(b'&amp;#x27', html)
                self.assertIn(b"Fexty's guide", html)
                self.assertIn(b"<code>don't &lt;script&gt;</code>", html)
                self.assertNotIn(b'<script>', html)
                self.assertIn(b'''href="https://example.com/author's?x=&quot;quoted&quot;&amp;y=1"''', html)

    def test_readme_html_tampering_is_rejected_and_refresh_preserves_zip(self):
        archive = self.package()
        old = archive.read_bytes()
        (archive.parent / 'README.html').write_bytes(b'<p>Incorrect instructions</p>')
        self.rejected(lambda: distribution.check(self.root))
        self.package(refresh_support=True)
        self.assertEqual(archive.read_bytes(), old)
        self.assertEqual((archive.parent / 'README.html').read_bytes(),
                         distribution.readme_html((archive.parent / 'README.md').read_bytes()))
        distribution.check(self.root)

    def test_gamebanana_description_discloses_software_and_keeps_guides_separate(self):
        archive = self.package()
        guide = (archive.parent / 'README.html').read_bytes()
        platform = (archive.parent / 'GAMEBANANA_README.html').read_bytes()
        self.assertTrue(platform.startswith(b'<h2><strong>AI-assisted code</strong></h2>'))
        self.assertIn(b'Fixture Coding Assistant</a>', platform)
        self.assertIn(b'href="https://example.com/assistant"', platform)
        self.assertIn(b'Assisted with fixture code.', platform)
        self.assertIn(b'Fixture library</a> by Fixture developers</li>', platform)
        self.assertNotIn(b'MIT-licensed code.', platform)
        self.assertIn(guide.strip(), platform)
        self.assertNotIn(b'AI-assisted', guide)
        (archive.parent / 'GAMEBANANA_README.html').write_bytes(b'<p>AI was used</p>')
        self.rejected(lambda: distribution.check(self.root))
        self.package(refresh_support=True)
        self.assertEqual((archive.parent / 'GAMEBANANA_README.html').read_bytes(), platform)

    def test_gamebanana_missing_or_vague_disclosures_are_rejected_before_packaging(self):
        good = copy.deepcopy(self.spec['gamebanana'])
        broken = [None, {'ai_code': {'used': True}, 'ai_assets': [], 'credits': []}]
        vague = copy.deepcopy(good)
        vague['ai_code']['software'][0]['name'] = 'AI'
        broken.append(vague)
        unknown_assets = copy.deepcopy(good)
        unknown_assets['ai_assets'] = [{'description': 'Texture', 'software': [], 'inputs': [], 'datasets': []}]
        broken.append(unknown_assets)
        for profile in broken:
            with self.subTest(profile=profile):
                self.spec['gamebanana'] = profile
                self.save_spec()
                self.rejected(self.package)
                self.assertFalse((self.root / 'build/sample-mod/releases/r1').exists())

    def test_gamebanana_compact_html_spaces_the_guide_with_line_breaks(self):
        profile = copy.deepcopy(self.spec['gamebanana'])
        markdown = b'# Fixture\n\nOne.\n\n1. First\n2. Copy:\n   - Nested\n3. Last\n\nTwo.\n'
        plain = distribution.gamebanana_readme_html(markdown, profile)
        self.assertIn(b'<p>One.</p>', plain)
        profile['compact_html'] = True
        html = distribution.gamebanana_readme_html(markdown, profile).decode()
        self.assertIn('</h2>\nOne.<br><br>\n<ol>\n<li>First</li>\n<li>Copy:<ul>\n'
                      '<li>Nested</li>\n</ul></li>\n<li>Last<br><br></li>\n</ol>\nTwo.<br><br>\n', html)
        if profile['ai_code']['used']:
            self.assertIn('<p>AI assistance from', html)

    def test_gamebanana_asset_credits_and_code_only_exceptions(self):
        profile = copy.deepcopy(self.spec['gamebanana'])
        profile['ai_code'] = {'used': False}
        html = distribution.gamebanana_readme_html(b'# Fixture\n', profile)
        self.assertNotIn(b'AI-assisted', html)
        self.assertNotIn(b'AI-generated', html)
        profile['ai_assets'] = [{'description': 'Generated fixture texture',
            'software': [{'name': 'Fixture generator', 'author': 'Tool maker', 'url': 'https://example.com/tool'}],
            'inputs': [{'name': 'Input art', 'author': 'Input artist', 'url': 'https://example.com/input'}],
            'datasets': [{'name': 'Training art', 'author': 'Dataset artist', 'url': 'https://example.com/data'}]}]
        html = distribution.gamebanana_readme_html(b'# Fixture\n', profile)
        self.assertTrue(html.startswith(b'<h2><strong>AI-generated assets</strong></h2>'))
        for text in (b'Input artist', b'Dataset artist', b'Tool maker'):
            self.assertIn(text, html)

    def test_html_fragment_preserves_license_text_and_escapes_markup(self):
        class Parser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.tags = []
                self.text = []
                self.attrs = []

            def handle_starttag(self, tag, attrs):
                self.tags.append(tag)
                self.attrs.extend(attrs)

            def handle_data(self, data):
                self.text.append(data)

        terms = 'Copyright © Fixture\n\nPermission & "AS IS" terms. <script>literal</script>\n'
        html = distribution.notices_html([('LICENSE', terms.encode('utf-8'))])
        parser = Parser()
        parser.feed(html.decode('utf-8'))
        self.assertTrue(set(parser.tags) <= {'h2', 'h3', 'p', 'br'})
        self.assertFalse(parser.attrs)
        self.assertIn(' '.join(terms.split()), ' '.join(''.join(parser.text).split()))
        markdown = distribution.notices_html([('NOTICE.md',
            b'# Credits\n\n`src/test.S` [Upstream](https://example.com/license?a=1&b=2)\n\n[Local notice](fonts/OFL.txt)\n')])
        self.assertIn(b'<h4>Credits</h4>', markdown)
        self.assertIn(b'<code>src/test.S</code>', markdown)
        self.assertIn(b'href="https://example.com/license?a=1&amp;b=2"', markdown)
        self.assertIn(b'Local notice (<code>fonts/OFL.txt</code>)', markdown)
        self.assertNotIn(b'href="fonts/OFL.txt"', markdown)

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
