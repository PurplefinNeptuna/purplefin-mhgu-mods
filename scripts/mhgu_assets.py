"""Shared MHGU ARC preservation and independent ARC/GMD readback helpers."""
import hashlib
import json
import struct
import subprocess
import zlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_arc(path):
    blob = path.read_bytes()
    require(len(blob) >= 12, f'Truncated header: {path}')
    magic, version, count = struct.unpack_from('<4sHH', blob)
    require(magic == b'ARC\0' and version == 17 and count > 0,
            f'Unsupported header: {path}')
    end = 12 + count * 80
    require(end <= len(blob), f'Truncated table: {path}')
    entries = {}
    for index in range(count):
        raw = blob[12 + index * 80:12 + (index + 1) * 80]
        name, kind, size, flags, offset = struct.unpack('<64sIIII', raw)
        key = (name.split(b'\0', 1)[0].decode('ascii'), kind)
        require(key not in entries, f'Duplicate resource: {key}')
        require(offset >= end and offset + size <= len(blob), f'Invalid bounds: {key}')
        packed = blob[offset:offset + size]
        decoder = zlib.decompressobj()
        data = decoder.decompress(packed) + decoder.flush()
        require(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail,
                f'Invalid compressed block: {key}')
        require(len(data) == flags & 0xffffff, f'Invalid resource size: {key}')
        entries[key] = dict(index=index, raw=raw, offset=offset, size=size,
                            flags=flags, packed=packed, data=data)
    ranges = sorted((e['offset'], e['offset'] + e['size']) for e in entries.values())
    require(all(a[1] <= b[0] for a, b in zip(ranges, ranges[1:])), 'Overlapping blocks')
    return blob, entries


def repack(blob, baseline, selected):
    # Preserve original header/table, gaps, trailer, flags and unchanged blocks.
    first = min(e['offset'] for e in baseline.values())
    out = bytearray(blob[:first])
    cursor = first
    for key, entry in sorted(baseline.items(), key=lambda item: item[1]['offset']):
        out.extend(blob[cursor:entry['offset']])
        donor = selected[key][1]
        offset = len(out)
        out.extend(donor['packed'])
        table = 12 + entry['index'] * 80
        struct.pack_into('<III', out, table + 68, len(donor['packed']),
                         (entry['flags'] & 0xff000000) | len(donor['data']), offset)
        cursor = entry['offset'] + entry['size']
    out.extend(blob[cursor:])
    return bytes(out)


def independent_arc(path):
    code = '''import importlib.util,sys,hashlib,json
s=importlib.util.spec_from_file_location('salad',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
a=m.MTArc();a.load(sys.argv[2])
print(json.dumps([[f['filename_base'].split(b'\\0',1)[0].decode('ascii'),f['ext_hash'],hashlib.sha256(a.extract_file(f,sys.argv[2])).hexdigest()] for f in a.files]))
'''
    result = subprocess.run([str(ROOT/'tools/python-env/bin/python'), '-c', code,
                             str(ROOT/'tools/saladsoftware/SaladSoftware.py'), str(path)],
                            check=True, capture_output=True, text=True)
    return {(name, kind): digest for name, kind, digest in json.loads(result.stdout.splitlines()[-1])}


def independent_gmd(path, expected):
    # Published decoder is used ONLY to read. Its known lossy encoder is never
    # called. Prefix preservation is checked independently by byte comparison.
    module = ROOT/'tools/gmd/node_modules/@beequeue/gmd/dist/index.js'
    code = '''const fs=require('node:fs');const {decodeGmd}=require(process.argv[1]);
const g=decodeGmd(fs.readFileSync(process.argv[2]));
console.log(JSON.stringify(g.entries.map(e=>({key:e.key??null,text:e.text}))));'''
    result = subprocess.run(['node', '-e', code, str(module), str(path)],
                            check=True, capture_output=True, text=True)
    actual = json.loads(result.stdout)
    require([e['text'] for e in actual] == list(expected.texts), 'Independent GMD texts differ')
    require({e['key']: e['text'] for e in actual if e['key'] is not None} ==
            {key: expected.text(key) for key in expected.entries}, 'Independent GMD keys differ')
