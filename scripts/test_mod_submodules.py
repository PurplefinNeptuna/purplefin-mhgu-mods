"""The distribution checker with mods as git submodules: checked out, not checked out, or staged as pointers."""
from pathlib import Path
import subprocess
import tempfile
import unittest

import mod_distribution as distribution


class SubmoduleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='mhgu-submodules-')
        self.root = Path(self.temp.name)
        (self.root / 'mods/private-mod').mkdir(parents=True)

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True)

    def test_a_submodule_not_checked_out_is_skipped(self):
        (self.root / '.gitmodules').write_text('[submodule "mods/private-mod"]\n\tpath = mods/private-mod\n\turl = x\n')
        self.assertEqual(distribution.check(self.root), [])

    def test_an_empty_folder_that_is_no_submodule_is_still_refused(self):
        (self.root / '.gitmodules').write_text('[submodule "mods/other"]\n\tpath = mods/other\n\turl = x\n')
        with self.assertRaises(ValueError):
            distribution.check(self.root, source_only=True)

    def test_a_staged_submodule_pointer_touches_its_mod(self):
        self.git('init', '-q')
        self.git('update-index', '--add', '--cacheinfo', f'160000,{"1" * 40},mods/private-mod')
        self.assertEqual(distribution.staged_mods(self.root), {'private-mod'})


if __name__ == '__main__':
    unittest.main()
