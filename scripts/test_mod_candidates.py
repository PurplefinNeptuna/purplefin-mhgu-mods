#!/usr/bin/env python3
"""DEVELOPMENT candidates: the builder path of `package` and the candidate checks, on temporary inputs."""
import json
import unittest
import zipfile

import mod_distribution as distribution
import test_mod_distribution as base


class CandidateTests(unittest.TestCase):
    # The release tests' fixture: a READY sample mod in a temporary workspace.
    setUp, write, save_spec = base.DistributionTests.setUp, base.DistributionTests.write, base.DistributionTests.save_spec
    package, rejected = base.DistributionTests.package, base.DistributionTests.rejected

    def development_candidate(self):
        """Convert only this temporary fixture into an explicit candidate delivery."""
        import shutil
        archive = self.package()
        directory = self.root / 'build/sample-mod/candidates/r1/delivery'
        shutil.copytree(archive.parent, directory)
        shutil.rmtree(archive.parent.parent)
        manifest = json.loads((directory / 'release-manifest.json').read_text())
        (directory / 'release-manifest.json').unlink()
        manifest['status'] = 'DEVELOPMENT'
        manifest['payloads'] = {name[len(self.mod) + 1:]: value['sha256']
                                for name, value in manifest['payloads'].items()}
        (directory / 'manifest.json').write_bytes(distribution.json_bytes(manifest))
        self.spec.update(status='DEVELOPMENT', candidate='build/sample-mod/candidates/r1/delivery/',
                         candidate_builder='scripts/candidate.py')
        self.write('mods/sample-mod/scripts/candidate.py', b'import sys; assert sys.argv[1:] == ["package"]\n')
        self.save_spec()
        self.candidate_checksums(directory)
        return directory

    def candidate_checksums(self, directory):
        files = distribution.inventory(directory)
        (directory / 'SHA256SUMS').write_text(''.join(distribution.digest(blob) + '  ' + name + '\n'
                    for name, blob in sorted(files.items()) if name != 'SHA256SUMS'))

    def test_development_builder_validates_without_promoting(self):
        directory = self.development_candidate()
        result = self.package()
        self.assertEqual(result.parent, directory)
        self.assertEqual(distribution.check(self.root)[0][1], 'DEVELOPMENT')
        self.assertEqual(json.loads((self.root / 'mods/sample-mod/DISTRIBUTION.json').read_text())['status'], 'DEVELOPMENT')
        (directory / 'sample-mod/romfs/nativeNX/plugins/test.nro').write_bytes(b'changed')
        self.rejected(lambda: distribution.check(self.root))

    def test_candidate_rejects_forged_inventory_and_escape(self):
        directory = self.development_candidate()
        with zipfile.ZipFile(directory / self.spec['archive'], 'a') as archive:
            archive.writestr('../extra.txt', b'extra')
        manifest = json.loads((directory / 'manifest.json').read_text())
        manifest['archive_sha256'] = distribution.digest((directory / self.spec['archive']).read_bytes())
        (directory / 'manifest.json').write_bytes(distribution.json_bytes(manifest))
        self.candidate_checksums(directory)
        self.rejected(lambda: distribution.check(self.root))
        self.spec['candidate'] = '../outside'
        self.save_spec()
        self.rejected(lambda: distribution.check(self.root))


if __name__ == '__main__':
    unittest.main()
