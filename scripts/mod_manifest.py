"""The mod-manager manifest.json that every new candidate or release ships beside romfs/."""
import json
import re

AUTHOR = 'PurplefinNeptuna'
# The last version of each mod built with the old three-line manifest.txt; its next version ships manifest.json.
MANIFEST_TXT = {'damage-numbers': 'r48', 'imgui-meter': 'r4', 'online-roaming': 'r16', 'please-do-better': 'r37',
                'purple-lib': 'r22', 'purple-lib-tester': 'r14', 'wishfinder': 'r122', 'wishfinder-mwt-bridge': 'r11'}
KEYS = ['manifest_version', 'id', 'version', 'name', 'authors', 'description', 'gamebananalink',
        'requires', 'conflicts', 'load']


def semver(version):
    """Version rN is written 0.N.0 for mod managers, which compare semver ranges."""
    match = re.fullmatch(r'r(\d+)', version)
    return match and f'0.{int(match[1])}.0'


def ranges(value):
    """requires/conflicts map another mod's "author/mod" id to a version range such as ">=0.20.0" or "*"."""
    return isinstance(value, dict) and all(
        re.fullmatch(r'[^/\s]+/[^/\s]+', k) and isinstance(v, str) and v.strip() for k, v in value.items())


def problems(spec, data):
    """What is wrong with this manifest.json for this DISTRIBUTION.json spec; empty when it is right."""
    try:
        m = json.loads(data)
    except ValueError:
        return ['not JSON']
    if not isinstance(m, dict) or list(m) != KEYS:
        return [f'keys must be exactly, in order: {", ".join(KEYS)}']
    load = m['load']
    checks = {
        'manifest_version is 1': m['manifest_version'] == 1 and type(m['manifest_version']) is int,
        f'id is "{AUTHOR}/{spec["mod"]}"': m['id'] == f'{AUTHOR}/{spec["mod"]}',
        f'version is "{semver(spec["version"])}" (from {spec["version"]})': semver(spec['version']) == m['version'],
        'name is the README title': isinstance(m['name'], str) and m['name'].strip(),
        f'authors is ["{AUTHOR}"]': m['authors'] == [AUTHOR],
        'description is set': isinstance(m['description'], str) and m['description'].strip(),
        'gamebananalink is "" or a GameBanana URL': isinstance(m['gamebananalink'], str) and (
            m['gamebananalink'] == '' or m['gamebananalink'].startswith('https://gamebanana.com/')),
        'requires maps ids to ranges': ranges(m['requires']),
        'conflicts maps ids to ranges': ranges(m['conflicts']),
        'load is {"after": [ids], "before": [ids]}': isinstance(load, dict) and sorted(load) == ['after', 'before']
            and all(isinstance(ids, list) and ranges(dict.fromkeys(ids, '*')) for ids in load.values()),
    }
    return [name for name, ok in checks.items() if not ok]


def check(spec, read):
    """Return the problems with the spec's mod-manager manifest; read(path) gives a payload source's bytes."""
    payloads = spec['payloads']
    if 'manifest.txt' in payloads and MANIFEST_TXT.get(spec['mod']) == spec['version']:
        return []
    if 'manifest.json' not in payloads:
        return ['no manifest.json payload beside romfs/']
    return problems(spec, read(payloads['manifest.json']['source']))
