#!/usr/bin/env python3
"""The HTML a release ships beside its README and notices: README.html, GAMEBANANA_README.html and
NOTICES.html, rendered from Markdown with a fixed, small subset, and the GameBanana profile check."""
from html import escape
from pathlib import PurePosixPath
import re


def require(condition, message):
    if not condition:
        raise ValueError(message)


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
    # GameBanana rejects numeric references for Unicode text, so keep UTF-8.
    # Generated attributes are double-quoted, so apostrophes can stay literal.
    return ('\n'.join(blocks) + '\n').replace('&#x27;', "'").encode('utf-8')


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

    return (blocks(blob.decode('utf-8').splitlines()) + '\n').replace('&#x27;', "'").encode('utf-8')


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


def compact_html(html):
    """Space a rendered guide with line breaks: no <p>, two <br> after paragraphs and top-level lists."""
    html = re.sub(r'<li><p>(.*?)</p>\n?(?=<[uo]l|</li>)', r'<li>\1', html)
    html = re.sub(r'<p>(.*?)</p>', r'\1<br><br>', html)
    return re.sub(r'</li>\n(</[uo]l>)(?=\n|$)', r'<br><br></li>\n\1', html)


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
    guide = readme_html(blob).decode('utf-8').strip()
    output.append(compact_html(guide) if profile.get('compact_html') else guide)
    if profile['credits']:
        output += ['<h2>Credits</h2>', '<ul>']
        output += ['<li>' + link(credit) + ' by ' + escape(credit['author']) + '</li>'
                   for credit in profile['credits']]
        output.append('</ul>')
    return ('\n'.join(output) + '\n').replace('&#x27;', "'").encode('utf-8')
