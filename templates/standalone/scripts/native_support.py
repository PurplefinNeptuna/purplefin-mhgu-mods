from paths import MOD, SCRIPTS, FORGE, DEPS, PYTHON, CONTAINER_STORAGE, input_path
import ctypes, ctypes.util, struct, hashlib
from mhgu_binary import nso_segments
from paths import input_path
def nso_exports(source):
    data = source.read_bytes() if hasattr(source, "read_bytes") else source
    """Read the actual ARM32 MOD0 dynamic table after segment hash validation."""
    segments = nso_segments(data)
    image = bytearray(max(s['address'] + s['size'] for s in segments))
    lib = ctypes.CDLL(ctypes.util.find_library('lz4'))
    lib.LZ4_decompress_safe.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    flags = struct.unpack_from('<I', data, 12)[0]
    for i, segment in enumerate(segments):
        offset = struct.unpack_from('<I', data, 16 + 16 * i)[0]
        packed_size = struct.unpack_from('<I', data, 96 + 4 * i)[0]
        packed = data[offset:offset + packed_size]
        if flags & (1 << i):
            buf = ctypes.create_string_buffer(segment['size'])
            if lib.LZ4_decompress_safe(packed, buf, len(packed), segment['size']) != segment['size']:
                raise ValueError('NSO decompression changed')
            packed = buf.raw
        image[segment['address']:segment['address'] + segment['size']] = packed
    def span(offset, count):
        if offset < 0 or count < 0 or offset + count > len(image):
            raise ValueError('NSO dynamic metadata out of bounds')
        return image[offset:offset + count]
    def u32(offset):
        return struct.unpack('<I', span(offset, 4))[0]
    mod = u32(4)
    if span(mod, 4) != b'MOD0':
        raise ValueError('Unsupported Forge MOD0')
    dynamic = mod + struct.unpack('<i', span(mod + 4, 4))[0]
    tags = {}
    for i in range(128):
        tag, value = struct.unpack('<II', span(dynamic + i * 8, 8))
        if not tag:
            break
        if tag in tags and tag in (4,5,6,10,11):
            raise ValueError('Repeated symbol-table tag')
        tags[tag] = value
    else:
        raise ValueError('Unterminated dynamic table')
    if not {4, 5, 6, 10, 11} <= tags.keys() or tags[11] != 16:
        raise ValueError('Unsupported Forge dynamic symbol format')
    buckets, count = struct.unpack('<II', span(tags[4], 8))
    span(tags[4], 8 + (buckets + count) * 4)
    symbols = span(tags[6], count * 16)
    names = bytes(span(tags[5], tags[10]))
    exports = set()
    for offset in range(0, len(symbols), 16):
        name, _, _, info, _, section = struct.unpack_from('<IIIBBH', symbols, offset)
        if name >= len(names) or names.find(b'\0', name) < 0:
            raise ValueError('Invalid Forge symbol name')
        if section and info >> 4 in (1, 2):
            exports.add(names[name:names.index(b'\0', name)].decode('ascii'))
    return exports
def snapshot():
    path=input_path('forge')
    data=path.read_bytes()
    return [{'emulator':'configured','path':str(path),'sha256':hashlib.sha256(data).hexdigest(),'exports':sorted(nso_exports(data)),'activation':'not inferred'}]
