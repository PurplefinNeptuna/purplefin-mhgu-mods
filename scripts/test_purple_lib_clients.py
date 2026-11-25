#!/usr/bin/env python3
"""Purple-lib's client check: every mod's copy of its records, table and export names."""
import unittest

import mod_distribution as distribution
import test_mod_distribution as base

# A one-field record stands in for each of Purple-lib's four.
RECORD = ('#[repr(C)]\n/// Doc.\npub struct Help {\n    pub size: u32,\n'
          '    pub title: Option<extern "C" fn(context: *mut c_void, language: u32) -> *const c_char>,\n}\n')
UNNAMED = RECORD.replace('context: ', '').replace('language: ', '')


class ClientTests(unittest.TestCase):
    # The release tests' fixture: a temporary workspace.
    setUp = base.DistributionTests.setUp
    write = base.DistributionTests.write
    save_spec = base.DistributionTests.save_spec
    rejected = base.DistributionTests.rejected

    def test_purple_lib_client_copy_must_keep_the_record_layout_and_export_names(self):
        records = (RECORD + RECORD.replace('Help', 'Options') + RECORD.replace('Help', 'OptionRow')
                   + RECORD.replace('Help', 'Api'))
        library = 'pub const CLIENT_EXPORT: &[u8] = b"purplelib_on_register";\n' + records
        self.write('mods/purple-lib/core/src/api.rs', library.encode())
        exported = b'{ global: purplelib_api_version; purplelib_add_help; local: *; };'
        self.write('mods/purple-lib/link/exported.txt', exported)
        client = 'const NAME: &[u8] = b"purplelib_api_version";\n' + UNNAMED
        self.write('mods/purple-lib/examples/rust/client.rs', client.encode())
        self.write('mods/other/src/client.rs', client.encode())
        self.assertEqual(len(distribution.purple_lib_clients(self.root)), 2)
        self.write('mods/other/src/client.rs', client.replace('pub size: u32', 'pub size: u16').encode())
        self.rejected(lambda: distribution.purple_lib_clients(self.root))
        self.write('mods/other/src/client.rs', (client + '// purplelib_add_helps\n').encode())
        self.rejected(lambda: distribution.purple_lib_clients(self.root))
        # A version 3 copy names only the function it exports, and carries the table.
        called = 'pub extern "C" fn purplelib_on_register() {}\n' + UNNAMED.replace('Help', 'Api')
        self.write('mods/other/src/client.rs', called.encode())
        self.assertEqual(len(distribution.purple_lib_clients(self.root)), 2)
        self.write('mods/other/src/client.rs', called.replace('pub size: u32', 'pub size: u16').encode())
        self.rejected(lambda: distribution.purple_lib_clients(self.root))
        self.write('mods/other/src/client.rs', client.encode())
        self.write('mods/purple-lib/examples/rust/client.rs', b'// no records\n')
        self.rejected(lambda: distribution.purple_lib_clients(self.root))


if __name__ == '__main__':
    unittest.main()
