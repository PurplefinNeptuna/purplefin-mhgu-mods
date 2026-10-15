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

from paths import ROOT
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
        require(isinstance(spec.get(field), str) and
                re.fullmatch(r'[a-zA-Z0-9]+(?:[.-][a-zA-Z0-9]+)*', spec[field]),
                f'Invalid {field}: {mod}')
    archive = spec.get('archive', '')
    require(isinstance(archive, str) and
            re.fullmatch(re.escape(f'{mod}-{spec["version"]}') + r'(?:-[a-z0-9]+)*\.zip', archive),
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
    payloads = spec.get('payloads')
    require(isinstance(payloads, dict) and payloads, f'No declared payloads: {mod}')
    for path, record in payloads.items():
        require(relative(path).parts[0] in ('romfs', 'exefs', 'cheats') and len(relative(path).parts) > 1,
                f'Runtime files must start at romfs/, exefs/ or cheats/: {path}')
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


def notice_inline(text):
    """Render notice Markdown's code and links without enabling embedded HTML."""
    tokens = re.split(r'(`[^`\n]+`|\[[^\]\n]+\]\([^\s)]+\))', text)
    rendered = []
    for token in tokens:
        link = re.fullmatch(r'\[([^\]\n]+)\]\(([^\s)]+)\)', token)
        if token.startswith('`') and token.endswith('`'):
            # GameBanana can mistake literal INI assignments for HTML attributes.
            rendered.append('<code>' + escape(token[1:-1]).replace('=', '&#61;') + '</code>')
        elif link:
            label, url = link.groups()
            if url.startswith(('https://', 'http://')):
                rendered.append(f'<a href="{escape(url, quote=True)}">{escape(label)}</a>')
            else:
                rendered.append(f'{escape(label)} (<code>{escape(url)}</code>)')
        else:
            rendered.append(escape(token))
    return ''.join(rendered)


def notices_html(sources):
    """GameBanana paste-ready HTML fragment; retain notice text and license terms."""
    labels = {'LICENSE': 'Mod license', 'OFL.txt': 'Font license',
              'OPEN_ART_LICENSE.txt': 'Artwork license', 'DISTRIBUTION_NOTICES.md': 'Credits and component licenses'}
    blocks = ['<h2>Notices and licenses</h2>']
    for name, blob in sources:
        blocks.append(f'<h3>{escape(labels.get(PurePosixPath(name).name, PurePosixPath(name).name))}</h3>')
        # Keep line breaks and all original wording, including legal capitalization.
        for paragraph in re.split(r'\n\s*\n', blob.decode('utf-8').strip()):
            heading = re.fullmatch(r'#{1,6} (.+)', paragraph) if name.endswith('.md') else None
            if heading:
                blocks.append('<h4>' + escape(heading[1]) + '</h4>')
            else:
                body = notice_inline(paragraph) if name.endswith('.md') else escape(paragraph)
                blocks.append('<p>' + body.replace('\n', '<br>\n') + '</p>')
    # Character references keep names readable without a document charset header.
    return ('\n'.join(blocks) + '\n').encode('ascii', 'xmlcharrefreplace')


def readme_inline(text):
    """Render README inline formatting with escaped text and public links only."""
    pattern = r'(`[^`\n]+`|\[[^\]\n]+\]\([^\s)]+\)|\*\*[^*\n]+\*\*|\*[^*\n]+\*)'
    rendered = []
    for token in re.split(pattern, text):
        if token.startswith('**') and token.endswith('**'):
            rendered.append('<strong>' + readme_inline(token[2:-2]) + '</strong>')
        elif token.startswith('*') and token.endswith('*'):
            rendered.append('<em>' + readme_inline(token[1:-1]) + '</em>')
        else:
            rendered.append(notice_inline(token))
    return ''.join(rendered)


def readme_html(blob):
    """Render release-guide Markdown as a paste-ready GameBanana HTML fragment."""
    item_pattern = r'^( *)([-+*]|\d+[.)]) +(.+)$'

    def cells(line):
        return [cell.strip() for cell in re.split(r'(?<!\\)\|', line.strip().strip('|'))]

    def table_start(lines, index):
        return (index + 1 < len(lines) and lines[index].strip().startswith('|') and
                all(re.fullmatch(r':?-{3,}:?', cell) for cell in cells(lines[index + 1])))

    def blocks(lines):
        output = []
        index = 0
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                index += 1
                continue
            heading = re.fullmatch(r'(#{1,6}) +(.+)', line)
            fence = re.fullmatch(r'```[a-zA-Z0-9_-]*\s*', line)
            item = re.match(item_pattern, line)
            if heading:
                level = max(2, len(heading[1]))
                output.append(f'<h{level}>' + readme_inline(heading[2]) + f'</h{level}>')
                index += 1
            elif fence:
                end = index + 1
                while end < len(lines) and lines[end].strip() != '```':
                    end += 1
                require(end < len(lines), 'Unclosed README code block')
                output.append('<pre><code>' + escape('\n'.join(lines[index + 1:end])).replace('=', '&#61;') + '</code></pre>')
                index = end + 1
            elif table_start(lines, index):
                headers = cells(line)
                output.append('<table>\n<thead><tr>' + ''.join('<th>' + readme_inline(cell) + '</th>'
                                                               for cell in headers) + '</tr></thead>\n<tbody>')
                index += 2
                while index < len(lines) and lines[index].strip().startswith('|'):
                    row = cells(lines[index])
                    require(len(row) == len(headers), 'README table row differs from its headers')
                    output.append('<tr>' + ''.join('<td>' + readme_inline(cell) + '</td>' for cell in row) + '</tr>')
                    index += 1
                output.append('</tbody>\n</table>')
            elif item:
                indent = len(item[1])
                ordered = item[2][0].isdigit()
                tag = 'ol' if ordered else 'ul'
                start = int(re.match(r'\d+', item[2])[0]) if ordered else 1
                attribute = f' start="{start}"' if start != 1 else ''
                output.append(f'<{tag}{attribute}>')
                while index < len(lines):
                    current = re.match(item_pattern, lines[index])
                    if (not current or len(current[1]) != indent or
                            current[2][0].isdigit() != ordered):
                        break
                    content_indent = current.start(3)
                    body = [current[3]]
                    index += 1
                    while index < len(lines):
                        continuation = lines[index]
                        if continuation.strip() and len(continuation) - len(continuation.lstrip()) <= indent:
                            break
                        body.append(re.sub(r'^ {0,' + str(content_indent) + '}', '', continuation))
                        index += 1
                    output.append('<li>' + blocks(body) + '</li>')
                output.append(f'</{tag}>')
            else:
                paragraph = [line.strip()]
                index += 1
                while index < len(lines) and lines[index].strip():
                    if (re.match(r'^#{1,6} |^```', lines[index]) or
                            re.match(item_pattern, lines[index]) or table_start(lines, index)):
                        break
                    paragraph.append(lines[index].strip())
                    index += 1
                output.append('<p>' + readme_inline(' '.join(paragraph)) + '</p>')
        return '\n'.join(output)

    return (blocks(blob.decode('utf-8').splitlines()) + '\n').encode('ascii', 'xmlcharrefreplace')


def validate_gamebanana(profile):
    """Require explicit AI-use records; never infer asset or code provenance."""
    require(isinstance(profile, dict), 'Missing GameBanana disclosure/credits record')

    def entries(records, author=False):
        require(isinstance(records, list), 'GameBanana credits/software must be a list')
        for record in records:
            require(isinstance(record, dict), 'Invalid GameBanana credit/software record')
            fields = ('name', 'author') if author else ('name',)
            for field in fields:
                value = record.get(field)
                require(isinstance(value, str) and value.strip() and
                        value.lower().strip() not in ('ai', 'unknown', 'tbd'),
                        f'Missing specific GameBanana {field}')
            require(isinstance(record.get('url'), str) and record['url'].startswith('https://'),
                    'GameBanana software/source requires a public HTTPS link')

    code = profile.get('ai_code', {})
    require(type(code.get('used')) is bool, 'GameBanana AI code use must be explicitly recorded')
    if code['used']:
        require(isinstance(code.get('scope'), str) and code['scope'].strip(),
                'Missing GameBanana AI code assistance scope')
        require(code.get('software'), 'Name/link the AI coding software used')
        entries(code['software'])
    assets = profile.get('ai_assets')
    require(isinstance(assets, list), 'Record GameBanana AI assets explicitly, including an empty list')
    for asset in assets:
        require(isinstance(asset, dict) and isinstance(asset.get('description'), str) and
                asset['description'].strip(), 'Describe the AI-generated asset')
        for group in ('software', 'inputs', 'datasets'):
            require(asset.get(group), f'AI assets require known {group} and their authors/sources')
            entries(asset[group], author=True)
    entries(profile.get('credits'), author=True)
    for credit in profile['credits']:
        require(isinstance(credit.get('scope'), str) and credit['scope'].strip(),
                'Describe the applicable GameBanana credit')


def gamebanana_readme_html(blob, profile):
    """Platform description with policy-specific disclosures and current credits."""
    validate_gamebanana(profile)

    def link(record):
        return f'<a href="{escape(record["url"], quote=True)}">{escape(record["name"])}</a>'

    output = []
    code = profile['ai_code']
    if code['used']:
        output += ['<h2><strong>AI-assisted code</strong></h2>',
                   '<p>AI assistance from ' + ', '.join(link(tool) for tool in code['software']) + ': ' +
                   escape(code['scope']) + '</p>']
    for asset in profile['ai_assets']:
        output += ['<h2><strong>AI-generated assets</strong></h2>', '<p>' + escape(asset['description']) + '</p>']
        for group, heading in (('software', 'AI software'), ('inputs', 'Input credits'),
                               ('datasets', 'Dataset credits')):
            output += ['<h3>' + heading + '</h3>', '<ul>']
            output += ['<li>' + link(record) + ' by ' + escape(record['author']) + '</li>'
                       for record in asset[group]]
            output.append('</ul>')
    output.append(readme_html(blob).decode('ascii').strip())
    if profile['credits']:
        output += ['<h2>Credits</h2>', '<ul>']
        output += ['<li>' + link(credit) + ' by ' + escape(credit['author']) + '</li>'
                   for credit in profile['credits']]
        output.append('</ul>')
    return ('\n'.join(output) + '\n').encode('ascii', 'xmlcharrefreplace')


def make_zip(payloads, package_name, support):
    entries = {f'{package_name}/{name}': blob for name, blob in payloads.items()}
    entries.update(support)
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


def package(mod, root=ROOT, refresh_support=False):
    spec = spec_for(mod, root)
    require(spec['status'] in READY, f'Mod is not approved for distribution: {mod}')
    files = expected_files(spec, root)
    directory = release_dir(spec, root)
    actual = inventory(directory)
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
                {'README.html', 'GAMEBANANA_README.html', 'NOTICES.html'},
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


def check(root=ROOT, source_only=False):
    result = []
    for directory in ([root] if (root/'mod.json').is_file() else sorted((root/'mods').iterdir())):
        if not directory.is_dir():
            continue
        mod = json.loads((directory/'mod.json').read_text())['mod'] if directory==root else directory.name
        spec = spec_for(mod, root)
        require(spec['status'] != 'RETIRED',
                f'Retired mod must be removed from the workspace: {directory.name}')
        archive = None
        if spec['status'] in READY and not source_only:
            archive = verify_release(spec, root)
        if not source_only:
            releases = local(root, f'build/{mod}/releases')
            if releases.exists():
                allowed = {spec['version']} if spec['status'] in READY else set()
                require({p.name for p in releases.iterdir()} == allowed,
                        f'Superseded/unregistered release entries must be archived: {releases}')
        result.append((mod, spec['status'], archive))
    require(result, 'No mod records found')
    if not source_only:
        registered = {mod for mod, _, _ in result}
        for releases in (root / 'build').glob('*/releases'):
            require(releases.parent.name in registered,
                    f'Release directory has no registered mod: {releases}')
        for archive in (root / 'build').rglob('*.zip'):
            parts = archive.relative_to(root / 'build').parts
            require(len(parts) >= 3 and parts[0] in registered and parts[1] in ('releases', 'candidates'),
                    f'ZIP must be under a registered mod\'s releases/ or candidates/: {archive}')
    return result


def check_staged(root=ROOT):
    """Reject records/support that were left out of the actual commit."""
    with tempfile.TemporaryDirectory(prefix='mhgu-distribution-index-') as temporary:
        staged = Path(temporary)
        subprocess.run(['git', 'checkout-index', '--all', f'--prefix={staged}/'],
                       cwd=root, check=True, capture_output=True)
        records = check(staged, source_only=True)
        for mod, status, _ in records:
            spec = spec_for(mod, staged)
            names = [f'mods/{mod}/DISTRIBUTION.json']
            if status in READY:
                names += [spec['readme'], *spec['notices'], *spec.get('support', {}).values()]
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
    packager = commands.add_parser('package', help='Package approved, pinned inputs after mod-specific validation')
    packager.add_argument('mod')
    packager.add_argument('--refresh-support', action='store_true')
    initializer = commands.add_parser('init', help='Register a new mod as DEVELOPMENT')
    initializer.add_argument('mod')
    initializer.add_argument('--kind', choices=('plugin','resource','cheat','tool'), default='plugin')
    args = parser.parse_args()
    if args.command == 'check':
        require(not (args.source_only and args.staged), 'Choose --source-only or --staged')
        records = check_staged() if args.staged else check(source_only=args.source_only)
        for mod, status, archive in records:
            print(f'{mod}: {status}' + (f' | {archive.relative_to(ROOT)}' if archive else ''))
        suffix = ' (staged source records)' if args.staged else (
            ' (source only; packages not checked)' if args.source_only else '')
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
