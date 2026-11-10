#!/usr/bin/env python3
"""Refuse version history in project docs ("Writing project docs" in AGENTS.md).

Usage: doc_rules.py FILE...  (the pre-commit hook passes every tracked project doc).
Each limit is the length the current docs fit with room; history pushes past it.
"""
import re
import sys

CURRENT_WORDS = 150     # the one current-state paragraph: what the build is, not how it got there
CURRENT_VERSIONS = 5    # current, candidate, last accepted, and one or two rollbacks
CELL_WORDS = 80         # a table cell is a status, not a paragraph
VERSION = re.compile(r'(?<![\w+#-])r\d{1,3}\b')
CHAIN = re.compile(r'(?<![\w+#-])r\d{1,3},? (?:is|was) (?:the )?r\d{1,3}\b')
DATED_HEADING = re.compile(r'^#+ .*\b20\d\d-\d\d-\d\d')
PREVIOUS = re.compile(r'\bprevious release\b|\brelease before r\d', re.I)  # "prior release" stays legal in process steps


def problems(path, text):
    for number, line in enumerate(text.splitlines(), 1):
        if DATED_HEADING.match(line):
            yield f'{path}:{number}: dated heading; put the fact in its topic section'
        if PREVIOUS.search(line):
            yield f'{path}:{number}: "previous release" is history; name the rollback build in docs/LOCAL_STATE.md only'
        if line.lstrip().startswith('|'):
            widest = max(len(cell.split()) for cell in line.split('|'))
            if widest > CELL_WORDS:
                yield f'{path}:{number}: table cell of {widest} words (limit {CELL_WORDS}); link to EVIDENCE.json or DEVELOPMENT.md'
    for paragraph in re.split(r'\n\s*\n', text):
        if paragraph.lstrip().startswith('**Current state.**'):
            words = len(paragraph.split())
            versions = sorted(set(VERSION.findall(paragraph)))
            if words > CURRENT_WORDS or len(versions) > CURRENT_VERSIONS:
                yield (f'{path}: current-state paragraph has {words} words and versions {", ".join(versions)} '
                       f'(limit {CURRENT_WORDS} words, {CURRENT_VERSIONS} versions); replace it, and move design facts to sections')
    chains = CHAIN.findall(text)
    if len(chains) > 1:
        yield f'{path}: version chain ({"; ".join(chains[:4])}); state the current build, runs go in EVIDENCE.json'


def self_check():
    bad = '# X\n\n**Current state.** r9 is r8 with a fix. r8 was r7 plus x, the previous release.\n\n## Run 2026-01-02\n'
    assert len(list(problems('t', bad))) == 3, list(problems('t', bad))
    assert not list(problems('t', '**Current state.** r9 DEVELOPMENT; r8 accepted.\n\n| a | push {r4-r7} |\n'))


if __name__ == '__main__':
    self_check()
    found = [p for f in sys.argv[1:] for p in problems(f, open(f, encoding='utf-8').read())]
    for p in found:
        print(p, file=sys.stderr)
    if found:
        print('Doc rule: docs state the current build; history lives in EVIDENCE.json and Git.', file=sys.stderr)
    sys.exit(1 if found else 0)
