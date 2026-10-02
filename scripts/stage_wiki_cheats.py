#!/usr/bin/env python3
"""Verify and stage the six curated wiki cheats without installing them."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / 'mods/wiki-cheats'
    manifest = json.loads((source / 'manifest.json').read_text())
    payloads = []
    for package in manifest['packages']:
        relative = Path(package['path'])
        data = (source / relative).read_bytes()
        if hashlib.sha256(data).hexdigest() != package['sha256']:
            raise ValueError(f'Cheat differs from the recorded wiki selection: {relative}')
        lines = data.decode('utf-8').splitlines()
        if lines[0] != package['heading'] or len(lines) != package['code_lines'] + 1:
            raise ValueError(f'Unexpected heading or line count: {relative}')
        depth = 0
        for line in lines[1:]:
            if not re.fullmatch(r'[0-9A-F]{8}(?: [0-9A-F]{8}){0,3}', line):
                raise ValueError(f'Invalid code words: {relative}: {line}')
            opcode = int(line[0], 16)
            words = len(line.split())
            expected = {0: 3, 1: 3, 2: 1, 5: 2, 6: 3, 7: 2, 8: 1}[opcode]
            if words != expected:
                raise ValueError(f'Invalid instruction length: {relative}: {line}')
            if opcode in (1, 8):
                depth += 1
            elif opcode == 2:
                depth -= 1
            if depth < 0:
                raise ValueError(f'Unmatched conditional end: {relative}')
        if depth:
            raise ValueError(f'Unclosed conditional block: {relative}')
        destination = ROOT / 'build/wiki-cheats' / relative
        if destination.exists() and destination.read_bytes() != data:
            raise FileExistsError(f'Preserving modified output: {destination}')
        payloads.append((destination, data))
    # Validate every input and existing destination before writing anything.
    for destination, data in payloads:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        if destination.read_bytes() != data:
            raise ValueError(f'Staged copy differs: {destination}')
    print(f'Verified and staged {len(payloads)} separate cheat packages.')


if __name__ == '__main__':
    main()
