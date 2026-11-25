#!/usr/bin/env python3
"""Run one scripts/build.py command without changing a version that was already handed out.

The build folder (`paths.BUILD_ROOT`, build/NAME/candidates/VERSION) takes writes only while
DISTRIBUTION.json names that same version as DEVELOPMENT. Once the folder holds a packaged
delivery, a command may rewrite it only if the runtime it leaves there is byte-identical to that
delivery. Otherwise the folder is put back exactly as it was and the command fails. A changed
runtime is a new version: `python3 scripts/mod_lifecycle.py start NAME` from the workspace.
build.sh and `mod_distribution.py package` run every command through this file.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
MOD = SCRIPTS.parent
# Commands that never write under the build folder.
READ_ONLY = {'doctor', 'fetch', 'export', 'help', '-h', '--help'}
# In the workspace, released versions have their folders under build/ and stay frozen. An exported
# source tree builds into its own folder, so a released version can be rebuilt there.
WORKSPACE = MOD.parent.name == 'mods' and (MOD.parent.parent / 'scripts/mod_lifecycle.py').is_file()


def inventory(folder):
    """Every file under `folder` with its SHA-256, or None when the folder is missing."""
    if not folder.is_dir():
        return None
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob('*')) if p.is_file()}


def refuse(message):
    print(f'candidate_guard: refused: {message}', file=sys.stderr)
    sys.exit(2)


def build_root():
    sys.path.insert(0, str(SCRIPTS))
    import paths
    return Path(paths.BUILD_ROOT)


def main(argv):
    run = [sys.executable, str(SCRIPTS / 'build.py'), *argv]
    if not argv or argv[0] in READ_ONLY:
        return subprocess.call(run)
    spec = json.loads((MOD / 'DISTRIBUTION.json').read_text())
    mod, version, status = spec['mod'], spec.get('version'), spec['status']
    folder = build_root()
    if folder.parent.name != 'candidates' or folder.parent.parent.name != mod:
        refuse(f'scripts/paths.py builds into {folder}, which is not build/{mod}/candidates/VERSION')
    if folder.name != version and not folder.name.startswith(f'{version}-'):
        refuse(f'scripts/paths.py builds {folder.name}, but DISTRIBUTION.json is at {version}. '
               f'Start versions with `python3 scripts/mod_lifecycle.py start {mod}`, which moves both')
    if WORKSPACE and status != 'DEVELOPMENT':
        refuse(f'{version} is {status}, so build/{mod}/candidates/{folder.name} is frozen. '
               f'Start a new version first: `python3 scripts/mod_lifecycle.py start {mod}`')
    # Packaging needs a package_name, so a mod without one has no delivery to keep.
    delivered = folder / 'delivery' / spec.get('package_name', '')
    packaged = inventory(delivered) if spec.get('package_name') else None
    if packaged is None:
        return subprocess.call(run)
    with tempfile.TemporaryDirectory(prefix=f'{mod}-{folder.name}-') as temp:
        snapshot = Path(temp) / 'snapshot'
        shutil.copytree(folder, snapshot, symlinks=True)
        if inventory(snapshot) != inventory(folder):
            refuse(f'the snapshot of {folder} reads back differently; nothing was run')
        code = subprocess.call(run)
        staged = inventory(folder / 'package')
        changed = inventory(delivered) != packaged or (staged is not None and staged != packaged)
        if code != 0 or changed:
            shutil.rmtree(folder)
            shutil.copytree(snapshot, folder, symlinks=True)
            if changed:
                refuse(f'{folder.name} is packaged (delivery/), and this run left a different runtime. '
                       f'The folder is restored as it was. A runtime change is a new version: '
                       f'`python3 scripts/mod_lifecycle.py start {mod}`')
            print(f'candidate_guard: the command failed; {folder} is restored as it was', file=sys.stderr)
    return code


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
