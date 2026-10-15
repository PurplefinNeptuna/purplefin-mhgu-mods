"""Exercise migration receipts against real Git history and tampered current files."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from source_provenance import verify


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.name = 'scripts/retired.py'
        self.old = b'original reviewed build helper\n'
        self.current = b'maintained shared helper\n'
        (self.root / 'scripts').mkdir()
        (self.root / self.name).write_bytes(self.old)
        def git(*args):
            return subprocess.check_output(['git', *args], cwd=self.root, stderr=subprocess.DEVNULL).decode().strip()
        git('init', '-q')
        git('add', '.')
        git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'Original build source')
        commit = git('rev-parse', 'HEAD')
        (self.root / self.name).unlink()
        (self.root / 'scripts/shared.py').write_bytes(self.current)
        (self.root / 'docs').mkdir()
        self.record = {'build_path': self.name, 'build_sha256': sha(self.old),
                       'build_commit': commit, 'current_path': 'scripts/shared.py',
                       'current_sha256': sha(self.current)}
        self.save()

    def save(self):
        (self.root / 'docs/WORKSPACE_EVIDENCE.json').write_text(json.dumps({'historical': {'WORKSPACE_SOURCE_MIGRATION.json': {'sources': [self.record]}}}))

    def test_removed_helper_resolves_to_exact_original_git_blob(self):
        verify(self.name, sha(self.old), self.root)

    def test_changed_maintained_helper_is_rejected(self):
        (self.root / 'scripts/shared.py').write_bytes(b'unreviewed change')
        with self.assertRaisesRegex(ValueError, 'after review'):
            verify(self.name, sha(self.old), self.root)

    def test_unrecorded_build_hash_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unrecorded'):
            verify(self.name, sha(b'other build'), self.root)

    def test_false_historical_hash_is_rejected(self):
        self.record['build_sha256'] = sha(b'other build')
        self.save()
        with self.assertRaisesRegex(ValueError, 'Git build-source fingerprint'):
            verify(self.name, self.record['build_sha256'], self.root)

    def test_native_code_cannot_use_tooling_migration_exception(self):
        self.record['build_path'] = 'mods/current/src/plugin.cpp'
        self.save()
        with self.assertRaisesRegex(ValueError, 'Native source/dependency bytes changed'):
            verify(self.record['build_path'], sha(self.old), self.root)


if __name__ == '__main__':
    unittest.main()
