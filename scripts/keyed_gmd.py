#!/usr/bin/env python3
"""Preservation-first text patching for inspected MHGU keyed GMD 0x10302.

All bytes preceding the text block are retained verbatim, except its byte-size
field. No key/hash/bucket/unknown metadata is regenerated or interpreted.
Unsupported/malformed input is rejected rather than guessed.
"""
from dataclasses import dataclass
import struct


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Entry:
    key: str
    index: int
    metadata_offset: int
    metadata_bytes: bytes


class KeyedGmd:
    def __init__(self, data):
        self.data = bytes(data)
        require(len(data) >= 41, 'Truncated GMD header')
        magic, version, language, u1, u2, keys, texts, key_size, text_size, filename = \
            struct.unpack_from('<4s9I', data)
        require(magic == b'GMD\0' and version == 0x10302, 'Unsupported GMD identity')
        require(0 < keys <= texts, 'Expected keyed GMD with bounded text indices')
        self.metadata_start = 41 + filename
        self.key_start = self.metadata_start + keys * 20 + 1024
        self.text_start = self.key_start + key_size
        require(self.text_start + text_size == len(data), 'GMD size accounting differs')
        require(self.metadata_start <= len(data) and data[40+filename] == 0,
                'Invalid filename bounds/terminator')
        require(b'\0' not in data[40:40+filename], 'Unexpected filename terminator')
        raw_text = data[self.text_start:].split(b'\0')
        require(raw_text[-1] == b'' and len(raw_text) == texts+1,
                'Text count or terminator differs')
        self.texts = tuple(t.decode('utf-8') for t in raw_text[:-1])
        self.entries = {}
        indices = set()
        for i in range(keys):
            offset = self.metadata_start+i*20
            index, hash1, hash2, key_offset, unknown = struct.unpack_from('<5I', data, offset)
            require(index < texts and key_offset < key_size, 'Invalid key/index bounds')
            begin = self.key_start+key_offset
            end = data.find(b'\0', begin, self.text_start)
            require(end >= begin, 'Missing key terminator')
            key = data[begin:end].decode('utf-8')
            require(key and key not in self.entries and index not in indices,
                    'Duplicate/empty key or aliased text index is unsupported')
            self.entries[key] = Entry(key, index, offset, data[offset:offset+20])
            indices.add(index)

    def text(self, key):
        return self.texts[self.entries[key].index]

    def patch(self, changes):
        """Map existing key -> (expected original text, replacement text)."""
        values = list(self.texts)
        for key, (old, new) in changes.items():
            require(key in self.entries, f'Unknown GMD key: {key}')
            require(self.text(key) == old, f'Unexpected original text: {key}')
            require(isinstance(new, str) and '\0' not in new, f'Invalid replacement: {key}')
            values[self.entries[key].index] = new
        payload = b''.join(t.encode('utf-8')+b'\0' for t in values)
        require(len(payload) <= 0xffffffff, 'Text block too large')
        prefix = bytearray(self.data[:self.text_start])
        struct.pack_into('<I', prefix, 32, len(payload))
        output = bytes(prefix)+payload
        rebuilt = KeyedGmd(output)
        require(rebuilt.entries == self.entries, 'Key metadata changed')
        require(rebuilt.data[:32] == self.data[:32] and
                rebuilt.data[36:self.text_start] == self.data[36:self.text_start],
                'Opaque metadata changed')
        require(rebuilt.texts == tuple(values), 'Text verification failed')
        return output
