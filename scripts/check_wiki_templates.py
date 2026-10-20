#!/usr/bin/env python3
"""Check wiki 010 Editor templates against a RomFS dump: header + count * record == file size.

Usage: python3 scripts/check_wiki_templates.py [ROMFS]
Results recorded in .agents/skills/mhgu-understanding/references/resources-and-tooling.md.
"""
import collections
import struct
import sys
from pathlib import Path

from mhgu_assets import read_arc

ROMFS = Path(sys.argv[1] if len(sys.argv) > 1 else
             Path.home() / '.local/share/eden/dump/0100770008DD8000/romfs')

W_BASE = {w: h for w, h in zip((0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14), (
    0x4199032B, 0x56E21768, 0x6F6F2BAD, 0x78143FEE, 0x1C755227, 0x32837AA1, 0x25F86EE2,
    0x7A41A133, 0x6D3AB570, 0x2E5B6815, 0x39207C56, 0x00AD4093, 0x17D654D0, 0x73B73919))}
W_LEVEL = {w: h for w, h in zip(W_BASE, (
    0x437D7704, 0x2CBF1C3A, 0x4788A739, 0x284ACC07, 0x4A96D77E, 0x4E630743, 0x21A16C7D,
    0x50AA37F0, 0x3F685CCE, 0x02F3A8C4, 0x6D31C3FA, 0x060678F9, 0x69C413C7, 0x0B1808BE))}
W_MOTION = [0x29482CCB, 0x65E22C55, 0x6B6D2BB6, 0x27C72B28, 0x2D022231, 0x6F27254C, 0x238D25D2,
            0x7AAD377E, 0x360737E0, 0x3E333888, 0x72993816, 0x7C163FF5, 0x30BC3F6B, 0x3A793672]
# template: (type hashes, packed record format). Every file is a 4-byte version/magic + int32 count + records.
TEMPLATES = {
    'w00d_mhgu': (list(W_BASE.values()), '<IHHBBBBIBBBHBB10B'),
    'w04d_mhgu': (list(W_BASE.values()), '<IHHBBBBIBBHBB10B'),
    'w00d_lvl_mhgu': (list(W_LEVEL.values()), '<IBBBBhBbhB'),
    'w04d_lvl_mhgu': (list(W_LEVEL.values()), '<IBBhBbBBBB5B15B66B'),
    'wpd_mhgu': ([0x15FCE6C6], '<HH' + 'HB' * 4 + 'HH' + 'HH' * 3),
    'wcd_mhgu': ([0x42354DC6], '<HHH' + 'HBB' * 4 + 'HH' + 'HH' * 3),
    'apd_mhgu': ([0x7522DD13], '<4HH' + 'HB' * 4 + 'HH' + 'HH' * 3),
    'wXXm_mhgu': (W_MOTION, '<i'),
    'itemData_mhgu': ([0x7C4883A8], '<iBBBhBBBBBBBBBBiiB8h'),
    'itemPreData_mhgu': ([0x5B8E6BF3], '<hiiiBB3sB3sB'),
    'itemPreTypeData_mhgu': ([0x63D62424], '<8B'),
    'alchemyData_mhgu': ([0x43057C7C], '<hBhBhBhBhB'),
    'ot_lvl_mhgu': ([0x4B51E836], '<hhhiBBBBB'),
    'amlt_mhgu': ([0x3E2A4D8E], '<IIB'),
    'amskl_mhgu': ([0x000692F5], '<Hbb'),
    'amslt_mhgu': ([0x21F33E01], '<4B'),
    'sem_mhgu': ([0x2553701D], '<IIffff'),
    'slt_mhgu': ([0x619D23DF], '<Iiii'),
    'ssjje_mhgu': ([0x25A60BC4], '<HHB'),
    'sup_mhgu': ([0x54539AEE], '<' + 'HBB' * 40),
    'tril_mhgu': ([0x29751294], '<' + 'HH' * 4),
    'rem_mhgu': ([0x5B3C302D, 0x160329F8], '<' + 'BB' * 8 + 'HBB' * 40),
    'skd_mhgu': ([0x39C8DC68], '<h16B'),
    'emsizetbl_mhgu': ([0x5ADC692C], '<Iffffff'),  # no count: 8-byte header, records to EOF
}


def payloads():
    """Map type hash -> [(location, decompressed bytes)], opening only archives that hold a wanted type."""
    wanted = {h for hashes, _ in TEMPLATES.values() for h in hashes}
    found = collections.defaultdict(list)
    for path in sorted(ROMFS.rglob('*.arc')):
        with path.open('rb') as f:
            head = f.read(8)
            if head[:4] != b'ARC\0':
                continue
            table = f.read(4 + struct.unpack_from('<H', head, 6)[0] * 80)
        kinds = {struct.unpack_from('<I', table, 4 + i * 80 + 64)[0] for i in range(len(table) // 80)}
        if kinds & wanted:
            for (name, kind), entry in read_arc(path)[1].items():
                if kind in wanted:
                    found[kind].append((f'{path.relative_to(ROMFS)}:{name}', entry['data']))
    return found


def main():
    found = payloads()
    for template, (hashes, fmt) in TEMPLATES.items():
        record = struct.calcsize(fmt)
        fits, misses = [], []
        for kind in hashes:
            for where, data in found[kind]:
                count = struct.unpack_from('<i', data, 4)[0]
                if template == 'emsizetbl_mhgu':
                    ok = (len(data) - 8) % record == 0
                else:
                    ok = 8 + count * record == len(data)
                (fits if ok else misses).append(
                    f'{where.rsplit(":", 1)[1]} ({(len(data) - 8) / count if count else 0:g})')
        print(f'{template:22} record={record:<4} fit={len(fits):<5} miss={len(misses)}')
        for miss in misses[:6]:
            print(f'    miss {miss}')

    headers = collections.Counter(p.read_bytes()[:8].hex() for p in ROMFS.rglob('*.gui'))
    print('gui headers:', dict(headers))
    gmd = collections.Counter()
    for path in ROMFS.rglob('*.gmd'):
        data = path.read_bytes()
        keys, count = struct.unpack_from('<ii', data, 20)
        end = 40
        try:
            for _ in range(count + 1):  # the template's entry 0 is the file name
                end = data.index(b'\0', end) + 1
        except ValueError:
            end = -1
        gmd['keyed' if keys else 'unkeyed', 'fit' if end == len(data) else 'miss'] += 1
    print('gmd:', dict(gmd))


if __name__ == '__main__':
    main()
