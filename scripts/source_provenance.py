"""Validate original build receipts after a reviewed host-tool/path migration.

Native sources remain exact byte gates. Historical build records are never
rewritten to claim a rebuild; a separate tracked receipt pins changed tooling
and resolves the original source from Git history.
"""
import hashlib
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def verify(name, expected, root=ROOT):
    path = root / name
    if path.is_file() and digest(path.read_bytes()) == expected:
        return
    receipt = json.loads((root / 'docs/WORKSPACE_EVIDENCE.json').read_text())['historical']['WORKSPACE_SOURCE_MIGRATION.json']
    matches = [r for r in receipt['sources'] if r['build_path'] == name and r['build_sha256'] == expected]
    if len(matches) != 1:
        raise ValueError('Unrecorded build source change: ' + name)
    record = matches[0]
    current = root / record['current_path']
    if not current.is_file() or digest(current.read_bytes()) != record['current_sha256']:
        raise ValueError('Migrated source changed after review: ' + name)
    if '/src/' in name or name.startswith(('tools/', 'work/')):
        if record['current_sha256'] != expected:
            raise ValueError('Native source/dependency bytes changed: ' + name)
    else:
        original = subprocess.run(['git', 'show', record['build_commit'] + ':' + name],
                                  cwd=root, check=True, capture_output=True).stdout
        if digest(original) != expected:
            raise ValueError('Git build-source fingerprint mismatch: ' + name)
