"""Purple-lib's client check: every mod's copy of its API records, table and export names."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def api_records(text):
    """The fields of the Purple-lib API records a Rust file declares: {struct: [(name, type)]}, with
    argument names dropped from callback types so only the layout is compared."""
    records = {}
    for name in ('OptionRow', 'Options', 'Help', 'Api'):
        body = re.search(r'#\[repr\(C\)\](?:\s*(?:///[^\n]*|#\[[^\n]*))*\s*pub struct ' + name + r' \{(.*?)\n\}', text, re.S)
        if body:
            records[name] = [(field, re.sub(r'\b\w+: ', '', kind).replace(' ', ''))
                             for field, kind in re.findall(r'^\s*pub (\w+): (.+),$', body[1], re.M)]
    return records


def purple_lib_clients(root=ROOT):
    """Every mod carries its own copy of Purple-lib's records, function table and names, because no
    mod may build from a sibling. Refuse a copy whose layout or names differ from Purple-lib's own,
    and return the files compared. A client's `Api` may be the start of Purple-lib's: an older API
    version's table. A copy is a file that names `purplelib_api_version` or the
    function a mod exports for Purple-lib to call (`CLIENT_EXPORT` in core/src/api.rs)."""
    library = root/'mods/purple-lib'
    if not (library/'core/src/api.rs').is_file():
        return []
    api = (library/'core/src/api.rs').read_text()
    expected = api_records(api)
    require(set(expected) == {'OptionRow', 'Options', 'Help', 'Api'}, 'Purple-lib API records not found in core/src/api.rs')
    client_export = re.search(r'CLIENT_EXPORT: &\[u8\] = b"(purplelib_\w+)"', api)
    require(client_export, 'Purple-lib CLIENT_EXPORT not found in core/src/api.rs')
    markers = {'purplelib_api_version', client_export[1]}
    exports = set(re.findall(r'purplelib_\w+', (library/'link/exported.txt').read_text())) | markers
    compared = []
    for source in sorted((root/'mods').glob('*/**/*.rs')):
        parts = source.relative_to(root/'mods').parts
        if {'vendor', 'target'} & set(parts) or parts[:2] in (('purple-lib', 'core'), ('purple-lib', 'src')):
            continue
        text = source.read_text()
        found = set(re.findall(r'purplelib_\w+', text))
        require(found <= exports, f'Not a Purple-lib export: {sorted(found - exports)} in {source.relative_to(root)}')
        if not found & markers:
            continue
        for name, fields in api_records(text).items():
            # The table only grows at its end, so a client built for an older API version keeps a
            # shorter copy of `Api`; every other record matches exactly.
            same = fields == expected[name] or (name == 'Api' and fields and fields == expected[name][:len(fields)])
            require(same, f'{name} differs from mods/purple-lib/core/src/api.rs: {source.relative_to(root)}')
            compared.append((str(source.relative_to(root)), name))
    require(any(path.startswith('mods/purple-lib/examples/') for path, _ in compared),
            'Purple-lib client check found no records in its own Rust example')
    return compared
