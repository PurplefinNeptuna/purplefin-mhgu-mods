#!/usr/bin/env python3
"""Create and verify local mod distributions. Never install or publish."""
import argparse
from datetime import datetime, timezone
import hashlib
from html import escape
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile

import mod_manifest as mod_manifest_rules
from purple_lib_clients import purple_lib_clients
from release_html import gamebanana_readme_html, notices_html, readme_html, validate_gamebanana

ROOT = Path(__file__).resolve().parents[1]
STATES = {'DEVELOPMENT', 'LOCAL_ONLY', 'RETIRED', 'READY_TO_DISTRIBUTE', 'PUBLISHED'}
READY = {'READY_TO_DISTRIBUTE', 'PUBLISHED'}
ARCHIVED_SUPPORT = ('README.md',)
DELIVERY_DOCUMENTS = ('README.md', 'README.html', 'GAMEBANANA_README.html', 'NOTICES.txt', 'NOTICES.html')
GAMEBANANA_POLICY = 'https://gamebanana.com/wikis/2175'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def relative(value):
    require(isinstance(value, str) and value and '\\' not in value,
            f'Invalid relative path: {value!r}')
    path = PurePosixPath(value)
    require(not path.is_absolute() and all(p not in ('', '.', '..') for p in value.split('/')),
            f'Unsafe relative path: {value}')
    return path


def local(root, value):
    name = relative(value)
    if (root/'mod.json').is_file() and (root/'DISTRIBUTION.json').is_file():
        mod=json.loads((root/'mod.json').read_text())['mod'];prefix=f'mods/{mod}/'
        if value.startswith(prefix):name=relative(value[len(prefix):])
    path = root/name
    require(not root.is_symlink(), f'Symlink root: {root}')
    for part in [path, *path.parents]:
        require(not part.is_symlink(), f'Symlink path: {part}')
        if part == root:
            break
    require(path.resolve().is_relative_to(root.resolve()), f'Path escapes workspace: {path}')
    return path


def read(root, value):
    path = local(root, value)
    require(path.is_file(), f'Missing file: {path}')
    return path.read_bytes()


def spec_for(mod, root=ROOT):
    require(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', mod), f'Invalid mod name: {mod}')
    spec = json.loads(read(root, f'mods/{mod}/DISTRIBUTION.json'))
    require(spec.get('schema_version') == 1 and spec.get('mod') == mod, f'Invalid identity: {mod}')
    require(spec.get('status') in STATES, f'Invalid distribution status: {mod}')
    platform = spec.get('runtime_platform', 'switch')
    require(platform == 'switch', f'Invalid runtime platform: {mod}')
    require(isinstance(spec.get('reason'), str) and spec['reason'].strip(), f'Missing status reason: {mod}')
    require(isinstance(spec.get('publication'), dict), f'Missing publication record: {mod}')
    publication = spec['publication']
    if spec['status'] == 'PUBLISHED':
        require(publication.get('published') is True and
                isinstance(publication.get('url'), str) and
                publication['url'].startswith('https://') and publication.get('date'),
                f'Published status requires its download URL and date: {mod}')
    else:
        require(publication == {'published': False, 'url': None, 'date': None},
                f'Unpublished status has publication claims: {mod}')
    legacy = local(root, f'mods/{mod}/RELEASE.json')
    if legacy.is_file():
        record = json.loads(read(root, str(legacy.relative_to(root))))
        require(record.get('status') == spec['status'] and
                record.get('published') == publication['published'], f'Stale RELEASE.json: {mod}')
    runtime = local(root, f'mods/{mod}/RUNTIME_RESULTS.json')
    if runtime.is_file():
        record = json.loads(read(root, str(runtime.relative_to(root))))
        if 'release_status' in record:
            require(record['release_status'] == spec['status'], f'Stale runtime release status: {mod}')
    if spec['status'] not in READY:
        return spec
    for field in ('version', 'package_name'):
        # Runtime folders may use the mod's public name ("Please do Better PC").
        # Allow single spaces between name segments, while version identifiers
        # retain their original grammar. Neither permits separators, traversal,
        # leading/trailing spaces or filesystem-special characters.
        pattern = r'[a-zA-Z0-9]+(?:[. -][a-zA-Z0-9]+)*' if field == 'package_name' else r'[a-zA-Z0-9]+(?:[.-][a-zA-Z0-9]+)*'
        require(isinstance(spec.get(field), str) and
                re.fullmatch(pattern, spec[field]),
                f'Invalid {field}: {mod}')
    # A renamed mod's archive follows its public name; its ID, folders and runtime keep the old one.
    archive_stem = spec.get('archive_stem', mod)
    require(isinstance(archive_stem, str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', archive_stem),
            f'Invalid archive stem: {mod}')
    archive = spec.get('archive', '')
    require(isinstance(archive, str) and
            re.fullmatch(re.escape(f'{archive_stem}-{spec["version"]}') + r'(?:-[a-z0-9]+)*\.zip', archive),
            f'Invalid archive name: {mod}')
    require(spec.get('approval', {}).get('date') and spec['approval'].get('basis'),
            f'Distribution approval missing: {mod}')
    require(isinstance(spec.get('target'), str) and spec['target'], f'Missing target: {mod}')
    require(isinstance(spec.get('limitations'), list), f'Missing coverage limits: {mod}')
    require(isinstance(spec.get('dependencies', []), list), f'Invalid dependencies: {mod}')
    for field in ('readme',):
        require(read(root, spec[field]).strip(), f'Empty {field}: {mod}')
    require(isinstance(spec.get('notices'), list) and spec['notices'], f'Missing notices: {mod}')
    for path in spec['notices']:
        require(relative(path).name.lower() not in ('third_party.md', 'development.md', 'readme.md'),
                f'Developer document used as a release notice: {path}; use dedicated DISTRIBUTION_NOTICES.md')
        require(read(root, path).strip(), f'Empty notice: {path}')
    validate_gamebanana(spec.get('gamebanana'))
    for name, source in spec.get('support', {}).items():
        require('/' not in name and name not in (*DELIVERY_DOCUMENTS, 'release-manifest.json', 'SHA256SUMS')
                and not name.endswith('.zip'), f'Invalid support filename: {name}')
        relative(name)
        read(root, source)
    # archives: extra ZIPs beside the mod's archive ({"kit.zip": {"path/in/zip": "source"}}), from tracked
    # files or, like payloads, from build/ (the release check pins those), such as Purple-lib's API kit.
    for name, entries in spec.get('archives', {}).items():
        require('/' not in name and name.endswith('.zip') and name != spec.get('archive')
                and name not in spec.get('support', {}) and entries, f'Invalid extra archive: {name}')
        for inner, source in entries.items():
            relative(inner)
            source.startswith('build/') or read(root, source)
    payloads = spec.get('payloads')
    require(isinstance(payloads, dict) and payloads, f'No declared payloads: {mod}')
    for path, record in payloads.items():
        parts = relative(path).parts
        # manifest.json (manifest.txt before it) beside romfs/ is the mod managers' record.
        require((parts[0] in ('romfs', 'exefs', 'cheats') and len(parts) > 1) or parts in (('manifest.json',), ('manifest.txt',)),
                f'Runtime files must start at romfs/, exefs/ or cheats/, or be manifest.json: {path}')
        require(relative(path).name.lower() not in
                ('readme.md', 'readme.html', 'gamebanana_readme.html', 'notices.txt', 'notices.html',
                 'release-manifest.json', 'sha256sums'),
                f'Support file declared as runtime: {path}')
        relative(record['source'])
        require(re.fullmatch(r'[0-9a-f]{64}', record.get('sha256', '')), f'Missing pinned hash: {path}')
    evidence = spec.get('evidence', {})
    require(evidence.get('static') and evidence.get('manual_summary'), f'Missing validation evidence: {mod}')
    for path in evidence['static'] + evidence.get('manual', []):
        relative(path)
    return spec


def release_dir(spec, root=ROOT):
    return local(root, f'build/{spec["mod"]}/releases/{spec["version"]}')


def make_zip(payloads, package_name, support):
    entries = {f'{package_name}/{name}': blob for name, blob in payloads.items()}
    entries.update(support)
    return zip_bytes(entries)


def zip_bytes(entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as archive:
        for name, blob in sorted(entries.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, blob, compresslevel=9)
    return stream.getvalue()


def expected_files(spec, root=ROOT):
    payloads = {}
    for name, record in spec['payloads'].items():
        blob = read(root, record['source'])
        require(blob and digest(blob) == record['sha256'], f'Pinned runtime payload changed: {name}')
        payloads[name] = blob
    notices = [(p, read(root, p)) for p in spec['notices']]
    support = {'README.md': read(root, spec['readme']),
               'README.html': readme_html(read(root, spec['readme'])),
               'GAMEBANANA_README.html': gamebanana_readme_html(read(root, spec['readme']), spec['gamebanana']),
               'NOTICES.txt': b'\n\n'.join(blob.strip() for _, blob in notices) + b'\n',
               'NOTICES.html': notices_html(notices)}
    zipped = make_zip(payloads, spec['package_name'], {p: support[p] for p in ARCHIVED_SUPPORT})
    support.update({name: read(root, source) for name, source in spec.get('support', {}).items()})
    support.update({name: zip_bytes({inner: read(root, source) for inner, source in entries.items()})
                    for name, entries in spec.get('archives', {}).items()})
    evidence = {p: digest(read(root, p)) for p in
                spec['evidence']['static'] + spec['evidence'].get('manual', [])}
    files = {f'{spec["package_name"]}/{p}': b for p, b in payloads.items()}
    manifest = {
        'schema_version': 1, 'mod': spec['mod'], 'version': spec['version'],
        'status': spec['status'], 'publication': spec['publication'],
        'package_name': spec['package_name'], 'target': spec['target'],
        'dependencies': spec.get('dependencies', []),
        'approval': spec['approval'], 'limitations': spec['limitations'],
        'archive': spec['archive'], 'archive_sha256': digest(zipped), 'archive_bytes': len(zipped),
        'distribution_spec_sha256': digest(read(root, f'mods/{spec["mod"]}/DISTRIBUTION.json')),
        'payloads': {p: {'sha256': digest(b), 'bytes': len(b)} for p, b in sorted(files.items())},
        'support_files': {p: {'sha256': digest(b), 'bytes': len(b)} for p, b in sorted(support.items())},
        'evidence': {**spec['evidence'], 'file_sha256': evidence},
        'installed_by_recipe': False, 'published_by_recipe': False,
    }
    if 'runtime_platform' in spec:
        manifest['runtime_platform'] = spec['runtime_platform']
    files.update(support)
    files[spec['archive']] = zipped
    files['release-manifest.json'] = json_bytes(manifest)
    files['SHA256SUMS'] = ''.join(f'{digest(b)}  {p}\n' for p, b in sorted(files.items())).encode()
    return files


def inventory(directory):
    if not directory.exists():
        return {}
    require(not directory.is_symlink(), f'Symlink release: {directory}')
    result = {}
    for path in directory.rglob('*'):
        require(not path.is_symlink(), f'Symlink release entry: {path}')
        if path.is_dir():
            continue
        require(path.is_file(), f'Unsupported release entry: {path}')
        result[str(path.relative_to(directory))] = path.read_bytes()
    return result


def verify_release(spec, root=ROOT):
    expected = expected_files(spec, root)
    directory = release_dir(spec, root)
    actual = inventory(directory)
    require(actual.keys() == expected.keys(), f'Missing/extra release files: {directory}')
    for path, blob in expected.items():
        require(actual[path] == blob, f'Stale or modified release file: {directory / path}')
    with zipfile.ZipFile(io.BytesIO(actual[spec['archive']])) as archive:
        require(archive.testzip() is None, 'ZIP CRC failed')
        members = {p: b for p, b in expected.items() if p.startswith(spec['package_name'] + '/')}
        members.update({name: expected[name] for name in ARCHIVED_SUPPORT})
        require(archive.namelist() == sorted(members), 'ZIP inventory mismatch')
        for entry in archive.infolist():
            relative(entry.filename)
            require(stat.S_ISREG(entry.external_attr >> 16), 'ZIP entry must be a regular file')
            require(archive.read(entry) == members[entry.filename], 'ZIP member mismatch')
    return directory / spec['archive']


def verify_candidate(spec, root=ROOT):
    """Check an explicitly registered development delivery without granting release status."""
    prefix = f'build/{spec["mod"]}/candidates/{spec["version"]}/'
    candidate = str(relative(spec['candidate'].rstrip('/')))
    require(candidate.startswith(prefix), 'Candidate must stay in its versioned candidate directory')
    directory = local(root, candidate)
    files = inventory(directory)
    require(all(name in files for name in (*DELIVERY_DOCUMENTS, 'manifest.json', 'SHA256SUMS', spec['archive'])),
            'Incomplete development candidate delivery')
    sums = {}
    for line in files['SHA256SUMS'].decode().splitlines():
        expected, name = line.split('  ', 1)
        relative(name)
        require(name not in sums and re.fullmatch('[0-9a-f]{64}', expected), 'Invalid candidate checksum record')
        sums[name] = expected
    require(sums == {name: digest(blob) for name, blob in files.items() if name != 'SHA256SUMS'},
            'Development candidate checksums differ')
    manifest = json.loads(files['manifest.json'])
    require(manifest['mod'] == spec['mod'] and manifest['version'] == spec['version']
            and manifest['status'] == 'DEVELOPMENT' and manifest['package_name'] == spec['package_name'],
            'Candidate manifest identity/status differs')
    payloads = manifest['payloads']
    require(manifest['archive_sha256'] == digest(files[spec['archive']]), 'Candidate ZIP hash differs')
    runtime = {name[len(spec['package_name']) + 1:]: digest(blob) for name, blob in files.items()
               if name.startswith(spec['package_name'] + '/')}
    require(runtime == payloads and payloads, 'Candidate runtime inventory differs')
    with zipfile.ZipFile(io.BytesIO(files[spec['archive']])) as archive:
        names = archive.namelist()
        expected = {'README.md', *(spec['package_name'] + '/' + name for name in payloads)}
        require(len(names) == len(set(names)) and set(names) == expected and archive.testzip() is None,
                'Candidate ZIP inventory/content failed')
        require(archive.read('README.md') == files['README.md'], 'Candidate archived guide differs')
        for name, expected in payloads.items():
            relative(name)
            require(digest(archive.read(spec['package_name'] + '/' + name)) == expected, 'Candidate ZIP payload differs')
    return directory / spec['archive']


def mod_manifest(spec, root=ROOT):
    """Every newly built candidate or release ships manifest.json beside romfs/ (scripts/mod_manifest.py)."""
    errors = mod_manifest_rules.check(spec, lambda source: read(root, source))
    require(not errors, f'manifest.json for {spec["mod"]} {spec["version"]} (docs/DEVELOPMENT.md, Releases): '
            + '; '.join(errors))


def package(mod, root=ROOT, refresh_support=False):
    spec = spec_for(mod, root)
    if spec['status'] == 'DEVELOPMENT' and spec.get('candidate_builder'):
        # The owned builder runs through its candidate guard, which keeps a packaged candidate's
        # runtime as it was. This path never changes distribution approval/status.
        require(spec['candidate_builder'] == 'scripts/build.py', f'candidate_builder must be scripts/build.py: {mod}')
        folder = root if (root / 'mod.json').is_file() else root / 'mods' / mod
        mod_manifest(spec, root)
        subprocess.run([sys.executable, folder / 'scripts/candidate_guard.py', 'package'], cwd=folder, check=True)
        return verify_candidate(spec, root)
    require(spec['status'] in READY, f'Mod is not approved for distribution: {mod}')
    files = expected_files(spec, root)
    directory = release_dir(spec, root)
    actual = inventory(directory)
    if not actual:
        mod_manifest(spec, root)  # existing releases from before the rule keep their bytes
    if actual and actual != files:
        # Runtime stays immutable; the archived README can change with support refresh.
        runtime = [p for p in files if p.startswith(spec['package_name'] + '/')]
        require(all(actual.get(p) == files[p] for p in runtime),
                'Runtime differs from existing release; use a new version')
        prefix = spec['package_name'] + '/'
        payloads = {p[len(prefix):]: files[p] for p in runtime}
        require(actual.get(spec['archive']) in (
                    make_zip(payloads, spec['package_name'],
                             {p: actual[p] for p in ARCHIVED_SUPPORT if p in actual}),
                    make_zip(payloads, spec['package_name'], {})),
                'Existing ZIP differs from its runtime/documentation; preserve/migrate it explicitly')
        require(refresh_support, 'Support files changed; use --refresh-support to back up and refresh them')
        require(actual.keys() <= files.keys() and files.keys() - actual.keys() <=
                {'README.html', 'GAMEBANANA_README.html', 'NOTICES.html', *spec.get('support', {}),
                 *spec.get('archives', {})},
                'Missing/unexpected files in release; preserve/migrate them explicitly')
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        backup = local(root, f'backups/{mod}/distribution-support/{stamp}/{spec["version"]}')
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(directory, backup)
        require(inventory(backup) == actual, 'Support backup readback differs')
        (backup.parent / 'backup-manifest.json').write_bytes(json_bytes(
            {p: digest(b) for p, b in sorted(actual.items())}))
    for name, blob in files.items():
        path = local(root, str((directory / name).relative_to(root)))
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_bytes() != blob:
            path.write_bytes(blob)
    return verify_release(spec, root)


def readme_version(spec, root=ROOT):
    """Reject a README whose code spans (archive name, plugin label) name another version."""
    version = re.match(r'r\d+\b', spec.get('version') or '')
    if not spec.get('readme') or not version:
        return
    for span in re.findall(r'`([^`\n]+)`', read(root, spec['readme']).decode()):
        stale = set(re.findall(r'\br\d+\b', span)) - {version.group()}
        require(not stale, f'README names {span!r} but the version is {spec["version"]}: {spec["mod"]}')


def staged_names(root=ROOT):
    return subprocess.run(['git', 'diff', '--cached', '--name-only', '-z'], cwd=root, check=True,
                          capture_output=True).stdout.decode().split('\0')


def staged_mods(root=ROOT):
    """The mods the commit being made touches: a staged path under mods/NAME/, or its submodule pointer."""
    return {name.split('/')[1] for name in staged_names(root) if name.startswith('mods/') and name.count('/') >= 1}


def packages_to_check(root=ROOT):
    """The mods whose packages `check --touched` verifies: the touched ones, or None (every mod)
    when the commit stages this checker or the scaffold mods are built from, which can change
    whether any mod's package passes."""
    if any(name.startswith(('scripts/mod_distribution.py', 'scripts/mod_manifest.py', 'scripts/standalone_mods.py', 'templates/'))
           for name in staged_names(root)):
        return None
    return staged_mods(root)


def check(root=ROOT, source_only=False, only=None):
    """Every mod's records and, unless `source_only`, its packages. With `only`, a set of mod names,
    packages and build/ entries are checked for those mods alone, so a mod rebuilt by other work in
    progress does not block a commit that leaves it alone. A submodule not checked out (an empty folder
    .gitmodules names) is skipped, and as the index holds none of its files, finding no mod is no error."""
    result, submodules = [], (root/'.gitmodules').read_text() if (root/'.gitmodules').is_file() else ''
    for directory in ([root] if (root/'mod.json').is_file() else sorted((root/'mods').iterdir())):
        if not directory.is_dir() or not any(directory.iterdir()) and f'path = mods/{directory.name}\n' in submodules:
            continue
        mod = json.loads((directory/'mod.json').read_text())['mod'] if directory==root else directory.name
        spec = spec_for(mod, root)
        require(spec['status'] != 'RETIRED',
                f'Retired mod must be removed from the workspace: {directory.name}')
        readme_version(spec, root)
        archive = None
        packages = not source_only and (only is None or mod in only)
        if spec['status'] in READY and packages:
            archive = verify_release(spec, root)
        elif spec['status'] == 'DEVELOPMENT' and spec.get('candidate_builder') and packages:
            archive = verify_candidate(spec, root)
        if packages:
            releases = local(root, f'build/{mod}/releases')
            if releases.exists():
                allowed = {spec['version']} if spec['status'] in READY else set()
                require({p.name for p in releases.iterdir()} == allowed,
                        f'Superseded/unregistered release entries must be archived: {releases}')
        result.append((mod, spec['status'], archive))
    purple_lib_clients(root)
    import mod_lifecycle
    mod_lifecycle.guarded_builders(root)
    if not source_only:
        registered = {mod for mod, _, _ in result}
        for releases in (root / 'build').glob('*/releases'):
            if only is not None and releases.parent.name in registered - only:
                continue
            require(releases.parent.name in registered,
                    f'Release directory has no registered mod: {releases}')
        for archive in (root / 'build').rglob('*.zip'):
            parts = archive.relative_to(root / 'build').parts
            if only is not None and parts[0] in registered - only:
                continue
            require(len(parts) >= 3 and parts[0] in registered and parts[1] in ('releases', 'candidates'),
                    f'ZIP must be under a registered mod\'s releases/ or candidates/: {archive}')
    return result


def check_staged(root=ROOT):
    """Check the commit as staged: every mod's records in the index, and for each mod the commit
    touches, that its records and support are staged as they are on disk. Other mods may have
    unstaged work in progress."""
    touched = staged_mods(root)
    with tempfile.TemporaryDirectory(prefix='mhgu-distribution-index-') as temporary:
        staged = Path(temporary)
        subprocess.run(['git', 'checkout-index', '--all', f'--prefix={staged}/'],
                       cwd=root, check=True, capture_output=True)
        records = check(staged, source_only=True)
        for mod, status, _ in records:
            if mod not in touched:
                continue
            spec = spec_for(mod, staged)
            names = [f'mods/{mod}/DISTRIBUTION.json']
            if status in READY:
                names += [spec['readme'], *spec['notices'], *spec.get('support', {}).values()]
                names += [s for e in spec.get('archives', {}).values() for s in e.values() if not s.startswith('build/')]
                names += [p for p in spec['evidence'].get('manual', []) if p.startswith('mods/')]
            for name in names:
                require(read(staged, name) == read(root, name),
                        f'Distribution source differs from staged commit: {name}')
        return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    checker = commands.add_parser('check', help='Check every current mod, including future directories')
    checker.add_argument('--source-only', action='store_true', help='Validate tracked records without generated artifacts')
    checker.add_argument('--staged', action='store_true', help='Validate the actual Git index and staged support sources')
    checker.add_argument('--touched', action='store_true', help='Check packages only for the mods the staged commit touches')
    packager = commands.add_parser('package', help='Package approved, pinned inputs after mod-specific validation')
    packager.add_argument('mod')
    packager.add_argument('--refresh-support', action='store_true')
    initializer = commands.add_parser('init', help='Register a new mod as DEVELOPMENT')
    initializer.add_argument('mod')
    initializer.add_argument('--kind', choices=('plugin','resource','cheat','tool'), default='plugin')
    args = parser.parse_args()
    if args.command == 'check':
        require(sum((args.source_only, args.staged, args.touched)) <= 1, 'Choose one of --source-only, --staged or --touched')
        records = (check_staged() if args.staged else
                   check(only=packages_to_check()) if args.touched else check(source_only=args.source_only))
        for mod, status, archive in records:
            print(f'{mod}: {status}' + (f' | {archive.relative_to(ROOT)}' if archive else ''))
        suffix = ' (staged source records)' if args.staged else (
            ' (source only; packages not checked)' if args.source_only else
            ' (packages of the mods this commit touches)' if args.touched else '')
        print(f'PASS: {len(records)} mod records{suffix}')
    elif args.command == 'package':
        archive = package(args.mod, refresh_support=args.refresh_support)
        print(f'Verified: {archive}\nSHA-256: {digest(archive.read_bytes())}')
    else:
        require(not (ROOT/'mod.json').exists(), 'This source repo is already registered; initialize new mods from the coordinating workspace')
        from standalone_mods import scaffold
        path = scaffold(ROOT/'mods'/args.mod, args.mod, args.kind)
        print(f'Scaffolded standalone {args.kind}: {path}')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile, subprocess.CalledProcessError) as error:
        print(f'Distribution check failed: {error}', file=sys.stderr)
        sys.exit(1)
