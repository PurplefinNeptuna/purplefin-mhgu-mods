#!/usr/bin/env python3
"""Keep source files short ("Source file size" in docs/DEVELOPMENT.md).

Usage: code_rules.py [--staged] [FILE...]
  --staged  check the staged copy of each file (the pre-commit hook)
  no FILE   check every tracked source file
A file over LIMIT lines is refused unless scripts/code_size_limits.json lists it; a listed file may
not grow past its entry, and when it shrinks the entry must come down with it, so the list only falls.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

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
            yield f'{path}: shrank to {count} lines; {fix} in {LIMITS.relative_to(ROOT)}'


def self_check():
    limits = {'a.rs': 700}
    assert not list(problems({'a.rs': 700, 'b.rs': 599}, limits))
    assert len(list(problems({'a.rs': 701, 'b.rs': 600}, limits))) == 2
    assert 'remove its entry' in next(problems({'a.rs': 500}, limits))
    assert SKIP.search('mods/x/vendor/y.rs') and SKIP.search('mods/p/book/html/book.js') and not SKIP.search('mods/x/src/a.rs')


def tracked(paths):
    out = subprocess.run(['git', 'ls-files', '--', *paths], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if SOURCE.search(p) and not SKIP.search(p)]


def count(path, staged):
    if staged:
        data = subprocess.run(['git', 'show', f':{path}'], cwd=ROOT, capture_output=True, check=True).stdout
    else:
        data = (ROOT / path).read_bytes()
    return data.count(b'\n') + (0 if data.endswith(b'\n') or not data else 1)


if __name__ == '__main__':
    self_check()
    args = sys.argv[1:]
    staged = '--staged' in args
    files = tracked([a for a in args if a != '--staged'])
    if staged and not files:
        sys.exit(0)
    limits = json.loads(LIMITS.read_text())
    # A listed file that was deleted or moved leaves its entry behind.
    gone = [p for p in limits if not (ROOT / p).exists()]
    found = [f'{p}: no longer exists; remove its entry' for p in gone]
    found += list(problems({p: count(p, staged) for p in files}, limits))
    for p in found:
        print(p, file=sys.stderr)
    if found:
        print(f'Code rule: source files stay under {LIMIT} lines, one topic per file.', file=sys.stderr)
    sys.exit(1 if found else 0)
