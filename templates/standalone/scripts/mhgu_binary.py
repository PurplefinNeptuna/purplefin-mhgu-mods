from paths import MOD, SCRIPTS, FORGE, DEPS, PYTHON, CONTAINER_STORAGE, input_path
"""Shared verified ARM32 NSO/ELF/NRO helpers and pinned native build inputs."""
import ctypes
import ctypes.util
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from paths import ROOT, MOD, SCRIPTS, FORGE, DEPS, PYTHON, CONTAINER_STORAGE, input_path
FORGE = FORGE
DEPS = DEPS
REVISION = "b8921fa3bbe35bbbafb11ccc489d5f1c6aa24a2d"
MAIN_SHA = "b3935415499549adaf4c0e89822831daa175cfd456a7990791c79be3997645ef"
BUILD_ID = "fb08f1d20fd1204fe7070672777f869b00000000000000000000000000000000"
IMAGE = "docker.io/devkitpro/devkita64@sha256:1fc388c3a0d34bd2045a6dadcb1020e069d5f876a187fd705de14b4440c00282"
HOOKS = [0x3de064, 0x3af5b4, 0x388ee8, 0x5e8130, 0x3850b0, 0x7a3480]
WINDOWS = {
    "joy_update_BETTER_INPUT_OCCUPIED": 0x3de064,
    "joy_digital_converter_shared": 0x3de4b0,
    "player_quest_input_candidate": 0x2a79cc,
    "player_command_classifier_shared_candidate": 0x27ca28,
    "long_sword_new_instance": 0x2b489c,
}

def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(args, **kwargs):
    return subprocess.run(list(map(str, args)), check=True, **kwargs)


def capture(args, **kwargs):
    return run(args, capture_output=True, text=True, **kwargs).stdout.strip()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def main_image(data):
    if sha(data) != MAIN_SHA or data[:4] != b"NSO0" or data[0x40:0x60].hex() != BUILD_ID:
        raise ValueError("Wrong main NSO: exact source SHA and full build ID are required")
    flags, = struct.unpack_from("<I", data, 0xc)
    sizes = struct.unpack_from("<3I", data, 0x60)
    library = ctypes.CDLL("liblz4.so.1")
    decompress = library.LZ4_decompress_safe
    decompress.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    decompress.restype = ctypes.c_int
    segments = []
    for i, name in enumerate(("text", "rodata", "data")):
        offset, address, size = struct.unpack_from("<3I", data, 0x10 + i * 0x10)
        stored = sizes[i] if flags & (1 << i) else size
        if offset < 0x100 or offset + stored > len(data) or size > 128 * 1024 * 1024:
            raise ValueError("NSO segment bounds invalid")
        raw = data[offset:offset + stored]
        if flags & (1 << i):
            dest = ctypes.create_string_buffer(size)
            if decompress(raw, dest, len(raw), size) != size:
                raise ValueError("NSO segment decompression failed")
            raw = dest.raw
        if flags & (1 << (i + 3)) and hashlib.sha256(raw).digest() != data[0xa0 + 32*i:0xc0 + 32*i]:
            raise ValueError("NSO segment content hash failed")
        if segments and address < segments[-1][0] + len(segments[-1][1]):
            raise ValueError("NSO segment overlap")
        segments.append((address, raw, name))
    image = bytearray(segments[-1][0] + len(segments[-1][1]))
    for address, raw, _ in segments:
        image[address:address+len(raw)] = raw
    return bytes(image), segments


def elf_to_nro(data):
    if data[:7] != b"\x7fELF\x01\x01\x01" or struct.unpack_from("<H", data, 18)[0] != 40:
        raise ValueError("Expected ELF32 little-endian ARM")
    phoff = struct.unpack_from("<I", data, 28)[0]
    phsize, count = struct.unpack_from("<HH", data, 42)
    if phsize != 32 or phoff + count*phsize > len(data):
        raise ValueError("Invalid ELF program headers")
    segments = [struct.unpack_from("<8I", data, phoff+i*32) for i in range(count)]
    segments = [s for s in segments if s[0] == 1]
    if len(segments) != 3 or [s[6] for s in segments] != [5,4,6]:
        raise ValueError("Expected RX/R/RW load segments")
    align = lambda x: (x+4095)&~4095
    cursor = 0
    for s in segments:
        if s[2] != cursor or s[1]+s[4] > len(data) or s[4] > s[5]:
            raise ValueError("Unexpected ELF segment layout or bounds")
        cursor += align(s[4])
    image = bytearray(cursor)
    for s in segments:
        image[s[2]:s[2]+s[4]] = data[s[1]:s[1]+s[4]]
    image[16:128] = bytes(112)
    image[16:20] = b"NRO0"
    struct.pack_into("<I", image, 24, len(image))
    for i,s in enumerate(segments):
        struct.pack_into("<II", image, 32+i*8, s[2], align(s[4]))
    struct.pack_into("<I", image, 56, align(max(0,segments[2][5]-align(segments[2][4]))))
    # Deterministic content fingerprint in the NRO build-id field.
    image[64:96] = hashlib.sha256(data).digest()
    return bytes(image)


def elf_hash(name):
    value = 0
    for byte in name:
        value = (value << 4) + byte
        high = value & 0xF0000000
        if high:
            value ^= high >> 24
        value &= ~high
    return value & 0xFFFFFFFF


class Nro:
    def __init__(self, data):
        self.data = data
        self.region(0, 0x80)
        if data[0x10:0x14] != b"NRO0" or self.u32(0x18) != len(data):
            raise ValueError("Unsupported NRO header/image length")
        self.segments = [struct.unpack_from("<II", data, 0x20 + i * 8) for i in range(3)]
        end = 0
        for offset, size in self.segments:
            self.region(offset, size)
            if offset < end or offset % 4096 or size % 4096:
                raise ValueError("Invalid NRO segment bounds/alignment")
            end = offset + size
        if end != len(data):
            raise ValueError("Unexpected trailing image data")
        mod = self.u32(4)
        self.region(mod, 28)
        if data[mod:mod + 4] != b"MOD0":
            raise ValueError("Missing MOD0")
        dynamic = mod + struct.unpack_from("<i", data, mod + 4)[0]
        tags = {}
        self.dynamic_end = None
        for offset in range(dynamic, len(data), 8):
            self.region(offset, 8)
            tag, value = struct.unpack_from("<II", data, offset)
            if tag == 0:
                self.dynamic_end = offset + 8
                break
            if tag in tags:
                raise ValueError("Duplicate dynamic tag")
            tags[tag] = value
        if self.dynamic_end is None or any(tag not in tags for tag in (4, 5, 6, 10, 11)):
            raise ValueError("Incomplete dynamic table")
        if tags[11] != 16 or 0x6FFFFEF5 in tags:
            raise ValueError("Unsupported symbol/hash format")
        self.tags = tags
        self.hash_offset, self.string_offset, self.symbol_offset = tags[4], tags[5], tags[6]
        self.region(self.hash_offset, 8)
        self.buckets, self.count = struct.unpack_from("<II", data, self.hash_offset)
        if not self.buckets or not self.count:
            raise ValueError("Empty symbol hash")
        self.hash_size = 8 + 4 * (self.buckets + self.count)
        self.region(self.hash_offset, self.hash_size)
        self.region(self.string_offset, tags[10])
        self.region(self.symbol_offset, self.count * 16)
        spans = [(self.hash_offset, self.hash_size), (self.string_offset, tags[10]),
                 (self.symbol_offset, self.count * 16)]
        for index, (start, size) in enumerate(spans):
            for other, other_size in spans[index + 1:]:
                if start < other + other_size and other < start + size:
                    raise ValueError("Overlapping dynamic metadata")
        self.symbols = []
        for i in range(self.count):
            entry = struct.unpack_from("<IIIBBH", data, self.symbol_offset + 16 * i)
            name_offset = entry[0]
            if name_offset >= tags[10]:
                raise ValueError("Symbol name outside string table")
            start = self.string_offset + name_offset
            stop = data.find(b"\0", start, self.string_offset + tags[10])
            if stop < 0:
                raise ValueError("Unterminated symbol name")
            self.symbols.append((data[start:stop], entry, start, stop))
        raw = struct.unpack_from(f"<{self.buckets + self.count}I", data, self.hash_offset + 8)
        if any(index >= self.count for index in raw):
            raise ValueError("Hash references invalid symbol")
        for bucket in raw[:self.buckets]:
            seen = set()
            while bucket:
                if bucket in seen:
                    raise ValueError("Cyclic symbol hash")
                seen.add(bucket)
                bucket = raw[self.buckets + bucket]

    def region(self, offset, size):
        if offset < 0 or size < 0 or offset + size > len(self.data):
            raise ValueError("NRO range out of bounds")

    def u32(self, offset):
        self.region(offset, 4)
        return struct.unpack_from("<I", self.data, offset)[0]

    def rebuild_hash(self):
        buckets = [0] * self.buckets
        chains = [0] * self.count
        for index, (name, *_rest) in enumerate(self.symbols[1:], 1):
            bucket = elf_hash(name) % self.buckets
            current = buckets[bucket]
            if not current:
                buckets[bucket] = index
            else:
                while chains[current]:
                    current = chains[current]
                chains[current] = index
        return struct.pack(f"<{2 + self.buckets + self.count}I",
                           self.buckets, self.count, *buckets, *chains)


def dynamic_exports(elf):
    if elf[:7] != b"\x7fELF\x01\x01\x01" or struct.unpack_from("<H", elf, 18)[0] != 40:
        raise ValueError("Expected ELF32 little-endian ARM")
    offset = struct.unpack_from("<I", elf, 32)[0]
    size, count = struct.unpack_from("<HH", elf, 46)
    sections = [struct.unpack_from("<10I", elf, offset + i * size) for i in range(count)]
    tables = [s for s in sections if s[1] == 11]
    if len(tables) != 1:
        raise ValueError("Expected one ELF dynamic symbol table")
    table = tables[0]; strings = sections[table[6]]
    names = elf[strings[4]:strings[4] + strings[5]]
    exports = {}
    for index in range(table[5] // 16):
        name, value, length, info, visibility, defined = struct.unpack_from("<IIIBBH", elf, table[4] + index * 16)
        if defined and info >> 4 in (1, 2) and visibility & 3 == 0:
            exports[names[name:].split(b"\0", 1)[0]] = (value, length)
    return exports


def nso_segments(nso):
    if nso[:4] != b"NSO0" or len(nso) < 256:
        raise ValueError("Invalid rebuilt NSO")
    lib = ctypes.CDLL(ctypes.util.find_library("lz4"))
    lib.LZ4_decompress_safe.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    flags = struct.unpack_from("<I", nso, 12)[0]
    results = []
    for i, name in enumerate(("text", "rodata", "data")):
        file_offset, address, expected = struct.unpack_from("<III", nso, 16 + i * 16)
        packed_size = struct.unpack_from("<I", nso, 96 + i * 4)[0]
        if file_offset < 256 or file_offset + packed_size > len(nso) or expected > 64 * 1024 * 1024:
            raise ValueError("NSO segment out of bounds")
        packed = nso[file_offset:file_offset + packed_size]
        if flags & (1 << i):
            dest = ctypes.create_string_buffer(expected)
            if lib.LZ4_decompress_safe(packed, dest, len(packed), expected) != expected:
                raise ValueError("NSO decompression failed")
            decoded = dest.raw
        else:
            decoded = packed
        if len(decoded) != expected or sha(decoded) != nso[160 + i * 32:192 + i * 32].hex():
            raise ValueError("NSO segment length/hash mismatch")
        results.append({"name": name, "address": address, "size": expected, "sha256": sha(decoded)})
    return results
