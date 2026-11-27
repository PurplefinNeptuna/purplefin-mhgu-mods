#!/usr/bin/env python3
"""Move a mod between versions and statuses in one checked step. Never installs or publishes.

  start NAME --reason TEXT            the next rN as DEVELOPMENT; a READY release is archived first
  promote NAME --basis TEXT           the packaged DEVELOPMENT candidate's exact bytes become the release
  withdraw NAME --reason TEXT         a READY/PUBLISHED release goes back to DEVELOPMENT, same version
  rollback NAME --to rK --reason TEXT an archived earlier release becomes the current release again:
                                      its runtime and ZIP exactly, support files refreshed to today's docs

Every command refuses before writing when its inputs are wrong. A release leaves build/NAME/releases/
only by move into backups/accepted/NAME/, with a preservation.json whose hashes are checked after the
move. Builds are guarded separately (templates/standalone/scripts/candidate_guard.py).
"""
import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import mod_distribution as distribution

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / 'templates/standalone/scripts/candidate_guard.py'
UNPUBLISHED = {'published': False, 'url': None, 'date': None}
require = distribution.require


def number(version):
    match = re.fullmatch(r'r(\d+)(?:-[a-z0-9-]+)?', version)
    require(match, f'Not an rN version: {version}')
    return int(match[1])


def spec_path(root, mod):
    return root / 'mods' / mod / 'DISTRIBUTION.json'


def load(root, mod):
    distribution.spec_for(mod, root)
    return json.loads(spec_path(root, mod).read_text())


def save(root, mod, spec):
    spec_path(root, mod).write_text(json.dumps(spec, indent=2, ensure_ascii=False) + '\n')


def inventory(folder):
    return {str(p.relative_to(folder)): distribution.digest(p.read_bytes())
            for p in sorted(folder.rglob('*')) if p.is_file()}


def git(root, mod, *args):
    return subprocess.run(['git', '-C', str(root / 'mods' / mod), *args], check=True,
                          capture_output=True, text=True).stdout


def clean(root, mod):
    """The mod's repo has no uncommitted change, so each lifecycle step is its own commit."""
    status = git(root, mod, 'status', '--porcelain')
    require(not status.strip(), f'mods/{mod} has uncommitted changes; commit them first:\n{status}')


def next_version(root, mod, spec):
    """One past every version this mod has used: its record, its build folders and its archives."""
    seen = [number(spec['version'])]
    for folder in [root / 'build' / mod / 'candidates', root / 'build' / mod / 'releases',
                   root / 'backups' / 'accepted' / mod]:
        if folder.is_dir():
            seen += [int(m[1]) for p in folder.iterdir() if (m := re.match(r'r(\d+)\b', p.name))]
    return f'r{max(seen) + 1}'


def archive_name(spec, version, candidate):
    return f'{spec.get("archive_stem", spec["mod"])}-{version}{"-candidate" if candidate else ""}.zip'


def candidate_fields(spec, version):
    spec.update(status='DEVELOPMENT', version=version, archive=archive_name(spec, version, True),
                candidate=f'build/{spec["mod"]}/candidates/{version}/delivery',
                candidate_builder=spec.get('candidate_builder', 'scripts/build.py'), publication=dict(UNPUBLISHED))
    spec.pop('approval', None)


def archive_release(root, mod, spec, label, reason):
    """Move build/NAME/releases/VERSION into backups/accepted/NAME/VERSION-LABEL/release, keeping the
    committed records beside it and a copy of the ZIP in candidates/VERSION/ when no delivery is there."""
    version = spec['version']
    release = root / 'build' / mod / 'releases' / version
    require(release.is_dir(), f'No release folder to archive: {release}')
    target = root / 'backups' / 'accepted' / mod / f'{version}-{label}'
    require(not target.exists(), f'Archive target exists: {target}')
    files = inventory(release)
    candidate = root / 'build' / mod / 'candidates' / version
    if not (candidate / 'delivery').is_dir() and not (candidate / spec['archive']).is_file():
        candidate.mkdir(parents=True, exist_ok=True)
        shutil.copy2(release / spec['archive'], candidate / spec['archive'])
        (candidate / 'SHA256SUMS').write_text(f'{files[spec["archive"]]}  {spec["archive"]}\n')
    target.mkdir(parents=True)
    for name in ('DEVELOPMENT.md', 'DISTRIBUTION.json', 'EVIDENCE.json', 'README.md'):
        if git(root, mod, 'ls-files', name).strip():
            (target / name).write_text(git(root, mod, 'show', f'HEAD:{name}'))
    (target / 'preservation.json').write_bytes(distribution.json_bytes(
        {'version': version, 'release_sha256': files, 'runtime': 'UNCHANGED', 'reason': reason,
         'publication': spec['publication']}))
    shutil.move(str(release), str(target / 'release'))
    require(inventory(target / 'release') == files, f'Archived release reads back differently: {target}')
    if not any(release.parent.iterdir()):
        release.parent.rmdir()
    return target


def set_version_copies(root, mod, old, new):
    """mod.json, scripts/paths.py and manifest.json name the version; returns the files changed."""
    folder, changed = root / 'mods' / mod, []
    edits = [('mod.json', lambda s: s.replace(f'"version": "{old}"', f'"version": "{new}"')),
             ('scripts/paths.py', lambda s: re.sub(rf"(['/]){old}((?:-[a-z0-9]+)?')", rf'\g<1>{new}\2', s)),
             ('manifest.json', lambda s: s.replace(f'"version": "0.{number(old)}.0"',
                                                   f'"version": "0.{number(new)}.0"'))]
    for name, edit in edits:
        path = folder / name
        if path.is_file() and (text := path.read_text()) != (after := edit(text)):
            path.write_text(after)
            changed.append(name)
    return changed


def leftovers(root, mod, old):
    """Lines in the mod that still name the old version, for the agent to read one by one."""
    found = subprocess.run(['git', '-C', str(root / 'mods' / mod), 'grep', '-nw', old, '--', '.',
                            ':!EVIDENCE.json', ':!book/html', ':!vendor'], capture_output=True, text=True).stdout
    return found.strip()


def start(root, mod, reason):
    clean(root, mod)
    spec = load(root, mod)
    old, new = spec['version'], next_version(root, mod, spec)
    archived = None
    if spec['status'] in distribution.READY:
        archived = archive_release(root, mod, spec, f'before-{new}', reason)
    else:
        require(spec['status'] == 'DEVELOPMENT',
                f'{mod} is {spec["status"]}; only DEVELOPMENT and released mods move on')
    candidate_fields(spec, new)
    spec['reason'] = reason
    spec['runtime_test'] = f'{new} has not run. See EVIDENCE.json.'
    spec.setdefault('evidence', {})['static_summary'] = f'{new}: not built yet.'
    for record in spec.get('payloads', {}).values():
        record['source'] = re.sub(rf'/(candidates|releases)/{old}/', f'/candidates/{new}/', record['source'])
        record['sha256'] = ''
    # Extra ZIPs built from build/ move to the new version like the payloads.
    moved = lambda source: re.sub(rf'/(candidates|releases)/{old}/', f'/candidates/{new}/', source)
    spec['archives'] = {name.replace(old, new): {inner: moved(source) for inner, source in entries.items()}
                        for name, entries in spec.get('archives', {}).items()}
    save(root, mod, spec)
    changed = set_version_copies(root, mod, old, new)
    print(f'{mod}: {old} -> {new} (DEVELOPMENT). Changed DISTRIBUTION.json, {", ".join(changed) or "no other file"}.')
    if archived:
        print(f'{old} release archived by move to {archived.relative_to(root)}; '
              f'its candidate stays in build/{mod}/candidates/{old}/.')
    print('Still yours to write: limitations, the evidence summaries, the README/TESTING mentions below,\n'
          'the DEVELOPMENT.md current-state paragraph and the docs/LOCAL_STATE.md row.')
    rest = leftovers(root, mod, old)
    if rest:
        print(f'Lines still naming {old} (keep the ones about {old} itself):\n{rest}')


def promote(root, mod, basis):
    spec = load(root, mod)
    require(spec['status'] == 'DEVELOPMENT', f'{mod} is {spec["status"]}; promote takes a DEVELOPMENT candidate')
    distribution.verify_candidate(spec, root)
    version, before = spec['version'], spec_path(root, mod).read_bytes()
    delivered = root / spec['candidate'] / spec['package_name']
    for path, record in spec['payloads'].items():
        blob = (delivered / path).read_bytes()
        require((root / record['source']).read_bytes() == blob,
                f'{record["source"]} is not the packaged {path}; the release must be the bytes that were handed out')
        record['sha256'] = distribution.digest(blob)
        if path.endswith('.nro'):
            require(record['sha256'][:8] in basis,
                    f'The basis must name the installed {path} hash ({record["sha256"][:8]}...)')
    spec.update(status='READY_TO_DISTRIBUTE', archive=archive_name(spec, version, False),
                approval={'date': datetime.date.today().isoformat(), 'basis': basis})
    spec.pop('candidate')
    spec.pop('candidate_builder', None)
    release = root / 'build' / mod / 'releases' / version
    require(not release.exists(), f'A release folder already exists: {release}')
    save(root, mod, spec)
    try:
        distribution.package(mod, root)
        packaged = {p: distribution.digest((release / spec['package_name'] / p).read_bytes()) for p in spec['payloads']}
        pinned = {p: r['sha256'] for p, r in spec['payloads'].items()}
        require(packaged == pinned, 'Release runtime differs from the candidate')
    except BaseException:
        spec_path(root, mod).write_bytes(before)
        shutil.rmtree(release, ignore_errors=True)
        raise
    print(f'{mod} {version} is READY_TO_DISTRIBUTE at {release.relative_to(root)}. Update DEVELOPMENT.md, '
          'docs/LOCAL_STATE.md (both tables) and the root README table.')


def withdraw(root, mod, reason):
    clean(root, mod)
    spec = load(root, mod)
    require(spec['status'] in distribution.READY, f'{mod} is {spec["status"]}; only a release can be withdrawn')
    version = spec['version']
    require((root / 'build' / mod / 'candidates' / version / 'delivery').is_dir(),
            f'build/{mod}/candidates/{version}/delivery is missing; '
            f'without it {version} would be rebuilt from newer source')
    published = spec['publication']['published']
    archived = archive_release(root, mod, spec, 'withdrawn', reason)
    candidate_fields(spec, version)
    spec['reason'] = reason
    save(root, mod, spec)
    print(f'{mod} {version} withdrawn to DEVELOPMENT; release archived to {archived.relative_to(root)}.')
    if published:
        print('Its public page is unchanged: taking it down is the user\'s step.')


def rollback(root, mod, to, reason):
    clean(root, mod)
    spec = load(root, mod)
    require(spec['status'] in distribution.READY, f'{mod} is {spec["status"]}; rollback replaces a release')
    archives = root / 'backups' / 'accepted' / mod
    sources = sorted(p for p in archives.glob(f'{to}-*')
                     if (p / 'release').is_dir() and (p / 'DISTRIBUTION.json').is_file())
    require(len(sources) == 1, f'Need exactly one archived {to} release with its DISTRIBUTION.json in {archives}; '
                               f'found {[p.name for p in sources]}')
    source = sources[0]
    kept = json.loads((source / 'preservation.json').read_text())['release_sha256']
    require(inventory(source / 'release') == kept, f'The archived {to} release differs from its preservation.json')
    old = json.loads((source / 'DISTRIBUTION.json').read_text())
    require(old['version'] == to and old['status'] in distribution.READY, f'{source} does not record a {to} release')
    # Before anything moves: the release check rebuilds its runtime from these sources.
    for path, record in old['payloads'].items():
        blob = (source / 'release' / old['package_name'] / path).read_bytes()
        require(distribution.digest(blob) == record['sha256'] and (root / record['source']).read_bytes() == blob,
                f'{record["source"]} no longer holds the released {to} {path}; '
                f'restore it from the archived release first')
    archived = archive_release(root, mod, spec, f'rolled-back-to-{to}', reason)
    shutil.copytree(source / 'release', root / 'build' / mod / 'releases' / to)
    # The release record hashes DISTRIBUTION.json, so both go back byte for byte; why is in the archive.
    shutil.copy2(source / 'DISTRIBUTION.json', spec_path(root, mod))
    shutil.copy2(source / 'README.md', root / 'mods' / mod / 'README.md')
    distribution.package(mod, root, refresh_support=True)
    print(f'{mod}: release is {to} again (from {source.relative_to(root)}); {spec["version"]} archived to '
          f'{archived.relative_to(root)}. README.md is {to}\'s. Source and mod.json still hold the newer code; '
          f'the next `start` continues after the highest version used.')


def guarded_builders(root=ROOT):
    """Every mod with a builder runs it through the identical candidate_guard.py, from build.sh."""
    for builder in sorted((root / 'mods').glob('*/scripts/build.py')):
        folder = builder.parent.parent
        guard = folder / 'scripts' / 'candidate_guard.py'
        require(guard.is_file() and guard.read_bytes() == GUARD.read_bytes(),
                f'{guard.relative_to(root)} must be a copy of templates/standalone/scripts/candidate_guard.py')
        script = (folder / 'build.sh').read_text()
        require('scripts/candidate_guard.py' in script and 'scripts/build.py' not in script,
                f'mods/{folder.name}/build.sh must run scripts/candidate_guard.py, not build.py directly')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)
    flags = [('start', '--reason'), ('promote', '--basis'), ('withdraw', '--reason'), ('rollback', '--reason')]
    for name, text in flags:
        command = commands.add_parser(name)
        command.add_argument('mod')
        command.add_argument(text, required=True)
        if name == 'rollback':
            command.add_argument('--to', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'start':
            start(ROOT, args.mod, args.reason)
        elif args.command == 'promote':
            promote(ROOT, args.mod, args.basis)
        elif args.command == 'withdraw':
            withdraw(ROOT, args.mod, args.reason)
        else:
            rollback(ROOT, args.mod, args.to, args.reason)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'{args.command} refused: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
