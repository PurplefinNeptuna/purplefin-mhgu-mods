#!/usr/bin/env python3
"""American spelling, never British (AGENTS.md, "American English").

Usage: spelling_rules.py [--staged] [--repo DIR] FILE...
  --staged    check the staged copy of each file (the pre-commit hooks)
  --repo DIR  the git repo FILE paths are relative to: a mod's own submodule (default: the workspace)
Only the lines a commit adds or changes are checked, so older text is fixed when it is next edited.
Markdown lines are checked whole. In source files only string literals are checked, where text a
player or tester reads lives; identifiers such as `kept_colour` are left alone. Whole words only.
A line under a comment holding `spelling: allow` is skipped, for a test that feeds British input.
"""
import re
import subprocess
import sys
from pathlib import Path

import line_rules

ROOT = Path(__file__).resolve().parent.parent
# This checker names the British words it refuses, so it skips itself.
SKIP = re.compile(r'(^|/)(vendor|third_party|licenses)/|^tools/|^references/|/book/html/|^scripts/spelling_rules\.py$')
CODE = re.compile(r'\.(rs|c|cc|cpp|h|hpp|py|lua|js|ts)$')
STRING = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'')
BRITISH = {
    'colour': 'color', 'colours': 'colors', 'coloured': 'colored', 'colouring': 'coloring',
    'grey': 'gray', 'greys': 'grays', 'greyed': 'grayed', 'greyish': 'grayish',
    'behaviour': 'behavior', 'behaviours': 'behaviors', 'favourite': 'favorite', 'favour': 'favor',
    'centre': 'center', 'centred': 'centered', 'honour': 'honor', 'labour': 'labor',
    'neighbour': 'neighbor', 'flavour': 'flavor', 'armour': 'armor', 'licence': 'license',
    'defence': 'defense', 'catalogue': 'catalog', 'programme': 'program', 'metre': 'meter',
    'cancelled': 'canceled', 'cancelling': 'canceling', 'travelled': 'traveled',
    'modelled': 'modeled', 'modelling': 'modeling', 'labelled': 'labeled', 'labelling': 'labeling',
    'analyse': 'analyze', 'analysed': 'analyzed',
}
# -ise verbs and their forms: organise, recognise, initialise, normalise, serialise, optimise ...
ISE = r'(organi|recogni|initiali|normali|seriali|optimi|customi|prioriti|summari|utili|minimi|maximi|reali'
ISE += r'|apologi)'
WORDS = re.compile(r'\b(' + '|'.join(BRITISH) + r'|' + ISE + r's(e|es|ed|ing|ation|ations))\b', re.I)


def checked_text(path, line):
    if path.endswith('.md'):
        return line
    if CODE.search(path):
        return ' '.join(STRING.findall(line))
    return ''


def problems(path, text, changed):
    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        if number not in changed or (number > 1 and 'spelling: allow' in lines[number-2]):
            continue
        for match in WORDS.finditer(checked_text(path, line)):
            word = match.group(0)
            fix = BRITISH.get(word.lower(), 'the -ize form')
            yield f'{path}:{number}: British "{word}"; write {fix}'


def content(repo, name, staged):
    if staged:
        shown = subprocess.run(['git', 'show', f':{name}'], cwd=repo, capture_output=True, check=True)
        return shown.stdout.decode('utf-8', 'replace')
    return (repo / name).read_text(errors='replace')


def self_check():
    assert list(problems('README.md', 'The grey badge', {1}))
    assert not list(problems('README.md', 'The grey badge', set()))
    assert not list(problems('src/a.rs', 'fn kept_colour() {}', {1}))
    assert list(problems('src/a.rs', 'let s = c"Grey badges";', {1}))
    assert list(problems('docs/a.md', 'We organised it', {1}))
    assert not list(problems('docs/a.md', 'GreyBadges and gray', {1}))
    assert not list(problems('src/a.rs', '// spelling: allow\nlet s = "grey";', {2}))


if __name__ == '__main__':
    self_check()
    args = sys.argv[1:]
    staged = '--staged' in args
    repo = ROOT
    if '--repo' in args:
        at = args.index('--repo')
        repo = Path(args[at + 1]).resolve()
        del args[at:at + 2]
    prefix = '' if repo == ROOT else repo.relative_to(ROOT).as_posix() + '/'
    found = []
    for name in (a for a in args if a != '--staged'):
        path = prefix + name
        if SKIP.search(path) or not (path.endswith('.md') or CODE.search(path)):
            continue
        if not (repo / name).exists():
            continue
        text = content(repo, name, staged)
        found += problems(path, text, line_rules.changed_lines(repo, name, staged))
    for problem in found:
        print(problem, file=sys.stderr)
    if found:
        print('Spelling rule: American English on every line you add or change (AGENTS.md).', file=sys.stderr)
    sys.exit(1 if found else 0)
