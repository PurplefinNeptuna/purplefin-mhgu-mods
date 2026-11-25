"""Keep lines readable, so the file size limit cannot be met by packing code onto fewer lines.

Only the lines a commit adds or changes are checked (against HEAD); older lines stay until they
are touched. Such a line is at most WIDTH characters, unless it is one string literal. It also
holds one statement:
- Python (read with `ast`): no `a; b`, no block body on its header line (`if x: y`,
  `def f(): return y`), no `import a, b`.
- Rust, C, C++, JS, TS: at most one `;` outside strings, comments and brackets, so `for (;;)` and
  `[0u8; 64]` pass and `let a = 1; let b = 2;` does not.
"""
import ast
import re
import subprocess

WIDTH = 120
C_LIKE = re.compile(r'\.(rs|c|cc|cpp|h|hpp|js|ts)$')
# A line that is a single string literal and its punctuation: splitting it would not help a reader.
LONE_STRING = re.compile(r'''^\s*(?:[a-z]{0,2}"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')\s*[,;)\]}]*\s*$''')


def changed_lines(repo, path, staged):
    """1-based numbers of the lines the commit (staged) or the working tree adds or changes."""
    against = ['--cached'] if staged else ['HEAD']
    diff = subprocess.run(['git', 'diff', '-U0', '--no-color', '--no-ext-diff', *against, '--', path],
                          cwd=repo, capture_output=True, text=True, check=True).stdout
    lines = set()
    for match in re.finditer(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', diff, re.M):
        start, count = int(match[1]), int(match[2] or 1)
        lines.update(range(start, start + count))
    return lines


def python_dense(text):
    """{line: why} for each Python line holding more than one statement."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {}
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and len(node.names) > 1:
            found[node.lineno] = 'one module per import line'
        for field in ('body', 'orelse', 'finalbody'):
            block = getattr(node, field, None)
            if not isinstance(block, list) or not block or not isinstance(block[0], ast.stmt):
                continue
            if field == 'body' and isinstance(node, (ast.stmt, ast.excepthandler)) and block[0].lineno == node.lineno:
                found[node.lineno] = 'put the block on its own lines'
            for before, after in zip(block, block[1:]):
                if after.lineno == before.end_lineno:
                    found[after.lineno] = 'one statement per line'
    return found


def semicolons(line):
    """`;` outside strings, char literals, comments and brackets. A line that starts by closing a
    bracket opened above (depth below 0) is still inside it, as is a block comment's `*` line."""
    if line.lstrip().startswith('*'):
        return 0
    count, depth, at = 0, 0, 0
    while at < len(line):
        c = line[at]
        if line.startswith('//', at):
            break
        if line.startswith('/*', at):
            end = line.find('*/', at + 2)
            at = len(line) if end < 0 else end + 2
            continue
        raw = re.match(r'r(#*)"', line[at:])
        if raw and (at == 0 or not line[at - 1].isalnum()):
            end = line.find('"' + raw[1], at + len(raw[0]))
            at = len(line) if end < 0 else end + 1 + len(raw[1])
            continue
        if c == '"':
            literal = re.match(r'"(?:[^"\\]|\\.)*"?', line[at:])
            at += len(literal[0])
            continue
        char = re.match(r"'(?:[^'\\]|\\.[^']*)'", line[at:])
        if char:
            at += len(char[0])
            continue
        if c in '([{':
            depth += 1
        elif c in ')]}':
            depth -= 1
        elif c == ';' and depth == 0:
            count += 1
        at += 1
    return count


def problems(path, text, changed):
    """Messages for the changed lines of `path`, whose full text is `text`."""
    lines = text.split('\n')
    dense = python_dense(text) if path.endswith('.py') else {}
    for number in sorted(changed):
        if number > len(lines):
            continue
        line = lines[number - 1]
        if len(line) > WIDTH and not LONE_STRING.match(line):
            yield f'{path}:{number}: {len(line)} characters (limit {WIDTH}); break it at a natural point'
        if number in dense:
            yield f'{path}:{number}: {dense[number]}'
        if C_LIKE.search(path) and not line.lstrip().startswith('for') and semicolons(line) > 1:
            yield f'{path}:{number}: one statement per line'


def self_check():
    dense = python_dense('import os, re\nif x: y()\na = 1; b = 2\ndef f():\n    return 1\ntry: pass\nexcept E: pass\n')
    assert set(dense) == {1, 2, 3, 6, 7}, dense
    assert not python_dense('if x:\n    y()\nelse:\n    z()\nv = [a for a in b if a]\nfrom m import a, b\n')
    assert semicolons('let a = 1; let b = 2;') == 2
    assert semicolons('let buf = [0u8; 64];') == 1 and semicolons('for (i = 0; i < n; i++) {') == 0
    assert semicolons('log("a; b; c"); // x; y') == 1 and semicolons("let c = ';'; let l: &'a str = r#\"x;y\"#;") == 2
    assert semicolons('}; EXTRA_SETS];') == 0 and semicolons(' * a; b; c') == 0
    assert LONE_STRING.match('        c"' + 'x' * 140 + '",')
    assert not LONE_STRING.match('call(a, b, "' + 'x' * 120 + '")')
    assert list(problems('a.rs', 'fn f() {\n    a(); b();\n}\n', {2}))
    assert not list(problems('a.rs', 'a(); b();\n', set())), 'unchanged lines are not checked'
