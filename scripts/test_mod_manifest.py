#!/usr/bin/env python3
"""The mod-manager manifest.json rules, on fixture bytes."""
import json
import unittest

import mod_manifest

SPEC = {'mod': 'sample-mod', 'version': 'r7', 'payloads': {'manifest.json': {'source': 'm'}}}
GOOD = {'manifest_version': 1, 'id': 'PurplefinNeptuna/sample-mod', 'version': '0.7.0', 'name': 'Sample',
        'authors': ['PurplefinNeptuna'], 'description': 'Fixture.', 'gamebananalink': '',
        'requires': {'PurplefinNeptuna/purple-lib': '>=0.20.0'}, 'conflicts': {'someone/other': '*'},
        'load': {'after': ['PurplefinNeptuna/purple-lib'], 'before': []}}


def check(manifest, spec=SPEC):
    blob = manifest if isinstance(manifest, bytes) else json.dumps(manifest).encode()
    return mod_manifest.check(spec, lambda source: blob)


class ManifestTests(unittest.TestCase):
    def test_good_manifest_passes(self):
        self.assertEqual(check(GOOD), [])
        self.assertEqual(check({**GOOD, 'gamebananalink': 'https://gamebanana.com/mods/1'}), [])
        self.assertEqual(mod_manifest.semver('r122'), '0.122.0')

    def test_each_broken_field_is_named(self):
        for change in ({'id': 'PurplefinNeptuna/other'}, {'version': '0.0.1'}, {'version': 'r7'},
                       {'authors': ['Someone']}, {'name': ''}, {'description': ' '}, {'manifest_version': True},
                       {'gamebananalink': 'link.com'}, {'requires': {'purple-lib': '>=0.20.0'}},
                       {'conflicts': {'a/b': ''}}, {'load': {'after': []}}, {'load': {'after': ['x'], 'before': []}}):
            with self.subTest(change=change):
                self.assertEqual(len(check({**GOOD, **change})), 1)

    def test_shape_errors(self):
        self.assertEqual(check(b'{'), ['not JSON'])
        self.assertTrue(check({**GOOD, 'extra': 1}))
        self.assertTrue(check({k: GOOD[k] for k in reversed(GOOD)}))
        self.assertTrue(check(GOOD, {**SPEC, 'payloads': {}}))

    def test_manifest_txt_only_for_the_last_version_built_with_it(self):
        legacy = {'mod': 'wishfinder', 'version': 'r122', 'payloads': {'manifest.txt': {}}}
        self.assertEqual(mod_manifest.check(legacy, None), [])
        self.assertTrue(mod_manifest.check({**legacy, 'version': 'r123'}, None))


if __name__ == '__main__':
    unittest.main()
