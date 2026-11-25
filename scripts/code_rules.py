#!/usr/bin/env python3
"""Keep source files short ("Source file size" in docs/DEVELOPMENT.md).

Usage: code_rules.py [--staged] [--repo DIR] [FILE...]
  --staged    check the staged copy of each file (the pre-commit hook)
  --repo DIR  the git repo FILE paths are relative to: a mod's own submodule (default: the workspace)
  no FILE     check every tracked source file
A file over LIMIT lines is refused unless a scripts/code_size_limits.json lists it: the workspace's,
or for a file under mods/NAME/ that mod's own, keyed from the mod's folder. A listed file may not grow
past its entry, and when it shrinks the entry must come down with it, so the list only falls.
Every line the commit adds or changes must also pass `line_rules`, so a file cannot meet its limit
by packing code onto fewer lines.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import line_rules

LIMIT = 600
SOURCE = re.compile(r'\.(rs|c|cc|cpp|h|hpp|py|S|s|sh|js|ts|lua)$')
# Generated or third-party: mdBook output, rendered test assets, vendored and tool trees.
SKIP = re.compile(r'(^|/)(vendor|third_party)/|^tools/|/book/html/|/tests/oracle/assets/')
ROOT = Path(__file__).resolve().parent.parent
LIMITS = ROOT / 'scripts/code_size_limits.json'


def problems(lines, limits):
    for path, count in sorted(lines.items()):
        ceiling = limits.get(path)
        if ceiling is None:
            if count >= LIMIT:
                yield f'{path}: {count} lines (limit {LIMIT}); split it by topic before adding more'
        elif count > ceiling:
            yield f'{path}: {count} lines, over its ceiling of {ceiling}; split it rather than grow it'
        elif count < ceiling:
            fix = 'remove its entry' if count < LIMIT else f'set its entry to {count}'
            yield f'{path}: shrank to {count} lines; {fix} in its scripts/code_size_limits.json'


def self_check():
    limits = {'a.rs': 700}
    assert not list(problems({'a.rs': 700, 'b.rs': 599}, limits))
    assert len(list(problems({'a.rs': 701, 'b.rs': 600}, limits))) == 2
    assert 'remove its entry' in next(problems({'a.rs': 500}, limits))
    assert SKIP.search('mods/x/vendor/y.rs') and SKIP.search('mods/p/book/html/book.js') and not SKIP.search('mods/x/src/a.rs')


def load_limits():
    """Every ceiling keyed by workspace path: the workspace's own and each checked-out mod's."""
    limits = json.loads(LIMITS.read_text())
    for own in ROOT.glob('mods/*/scripts/code_size_limits.json'):
        prefix = own.parent.parent.relative_to(ROOT).as_posix() + '/'
        limits.update({prefix + p: n for p, n in json.loads(own.read_text()).items()})
    return limits


def tracked(repo, paths):
    """{workspace path: path in repo} for each tracked source file."""
    out = subprocess.run(['git', 'ls-files', '--', *paths], cwd=repo, capture_output=True, text=True, check=True).stdout
    prefix = '' if repo == ROOT else repo.relative_to(ROOT).as_posix() + '/'
    return {prefix + p: p for p in out.splitlines() if SOURCE.search(prefix + p) and not SKIP.search(prefix + p)}


def content(repo, path, staged):
    if staged:
        return subprocess.run(['git', 'show', f':{path}'], cwd=repo, capture_output=True, check=True).stdout
    return (repo / path).read_bytes()


def count(repo, path, staged):
    data = content(repo, path, staged)
    return data.count(b'\n') + (0 if data.endswith(b'\n') or not data else 1)


def dense(repo, files, staged):
    """line_rules problems on the lines each file's commit (or working tree) adds or changes."""
    for path, inside in files.items():
        if not staged and not (repo / inside).exists():
            continue
        text = content(repo, inside, staged).decode('utf-8', 'replace')
        yield from line_rules.problems(path, text, line_rules.changed_lines(repo, inside, staged))


if __name__ == '__main__':
    self_check()
    line_rules.self_check()
    args = sys.argv[1:]
    staged = '--staged' in args
    repo = ROOT
    if '--repo' in args:
        at = args.index('--repo')
        repo = Path(args[at + 1]).resolve()
        del args[at:at + 2]
    files = tracked(repo, [a for a in args if a != '--staged'])
    if staged and not files:
        sys.exit(0)
    limits = load_limits()
    # A listed file that was deleted or moved leaves its entry behind.
    gone = [p for p in limits if not (ROOT / p).exists()]
    found = [f'{p}: no longer exists; remove its entry' for p in gone]
    # A tracked file deleted in the working tree has nothing to count.
    found += list(problems({p: count(repo, r, staged) for p, r in files.items() if staged or (repo / r).exists()}, limits))
    lines = list(dense(repo, files, staged))
    for p in found + lines:
        print(p, file=sys.stderr)
    if found:
        print(f'Code rule: source files stay under {LIMIT} lines, one topic per file.', file=sys.stderr)
    if lines:
        rule = f'one statement per line, at most {line_rules.WIDTH} characters'
        print(f'Line rule: {rule}, on every line you add or change.', file=sys.stderr)
    found += lines
    sys.exit(1 if found else 0)
