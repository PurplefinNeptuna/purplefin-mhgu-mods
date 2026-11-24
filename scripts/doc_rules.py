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
SKILL_SENTENCE_WORDS = 40  # the skill references' median is 11; past 40 a fact wants a list or a table
SKILL_LINE_CHARS = 600     # a paragraph of short sentences still turns into a wall
# a sentence ends at . ! ? (also before ** or a closing quote or bracket), never after e.g. or i.e.
SENTENCE_END = re.compile(r'(?<!\be\.g\.)(?<!\bi\.e\.)(?:(?<=[.!?])|(?<=[.!?]\*\*)|(?<=[.!?]["\)]))\s+')
LIST_ITEM = re.compile(r'^\s*(?:[-*>]|\d+\.)\s')


def paragraphs(text):
    """Prose blocks with wrapped lines joined, so wrapping cannot split a sentence; code, tables, headings skipped."""
    text = re.sub(r'(?s)\A---\n.*?\n---\n', '', text)
    text = re.sub(r'(?s)```.*?```', '', text)
    block = []
    for line in text.split('\n'):
        skip = line.lstrip().startswith(('#', '|'))
        if block and (not line.strip() or skip or LIST_ITEM.match(line)):
            yield ' '.join(block)
            block = []
        if line.strip() and not skip:
            block.append(LIST_ITEM.sub('', line, count=1).strip())
    if block:
        yield ' '.join(block)


def skill_problems(path, text):
    headings = [line.lstrip('#').strip() for line in text.splitlines() if line.startswith('#')]
    if len(headings) > 1 and headings[0] == headings[1]:
        yield f'{path}: the first two headings repeat "{headings[0]}"; keep the title once'
    fence = False
    for number, line in enumerate(text.splitlines(), 1):
        fence ^= line.lstrip().startswith('```')
        if not fence and len(line) > SKILL_LINE_CHARS and not line.lstrip().startswith('|'):
            yield f'{path}:{number}: line of {len(line)} characters (limit {SKILL_LINE_CHARS}); break it at sentence ends'
    for paragraph in paragraphs(text):
        for sentence in SENTENCE_END.split(paragraph):
            words = len(sentence.split())
            if words > SKILL_SENTENCE_WORDS:
                yield (f'{path}: sentence of {words} words (limit {SKILL_SENTENCE_WORDS}): "{sentence[:70]}..."; '
                       'rewrite it as shorter sentences, a list or a table')


def problems(path, text):
    if '.agents/skills/' in path:
        yield from skill_problems(path, text)
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
    skill = '.agents/skills/x.md'
    long_sentence = ' '.join(['word'] * 41) + '.'
    # wrapping a long sentence over lines must not hide it; 41 one-word lines are still one sentence
    assert len(list(problems(skill, long_sentence.replace(' ', '\n')))) == 1
    assert len(list(problems(skill, '# A\n\n## A\n\n' + 'x' * 601 + '\n'))) == 2
    fine = '---\ndescription: ' + long_sentence + '\n---\n# A\n\n' + ('Short one. ' * 30) + '\n\n| ' + long_sentence + ' |\n'
    assert not list(problems(skill, fine)), list(problems(skill, fine))
    # "238. No" inside a line is a sentence end, not a list marker to strip
    assert not list(problems(skill, '- ' + ' '.join(['w'] * 30) + ' 238. ' + ' '.join(['w'] * 30) + '.\n'))
    assert not list(problems('docs/x.md', long_sentence))


if __name__ == '__main__':
    self_check()
    found = [p for f in sys.argv[1:] for p in problems(f, open(f, encoding='utf-8').read())]
    for p in found:
        print(p, file=sys.stderr)
    if found:
        print('Doc rule: docs state the current build; history lives in EVIDENCE.json and Git.', file=sys.stderr)
    sys.exit(1 if found else 0)
