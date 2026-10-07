#!/usr/bin/env python3
"""Exercise isolated source scaffolding, allowlists and host-only entry points."""
from pathlib import Path
import tempfile, subprocess, json
import standalone_mods as s

def run(args,expected=0):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True)
 assert p.returncode==expected,(args,p.stdout,p.stderr)
 return p
with tempfile.TemporaryDirectory() as t:
 root=Path(t)
 for kind in ('plugin','resource','cheat','tool'):
  p=s.scaffold(root/kind,'sample-'+kind,kind)
  assert json.loads((p/'DISTRIBUTION.json').read_text())['status']=='DEVELOPMENT'
  run([p/'build.sh','test','--host'])
  run([p/'build.sh','--help'])
  try:s.scaffold(p,'sample-'+kind,kind)
  except ValueError:pass
  else:raise AssertionError('Existing source overwritten')
  if kind!='plugin':
   run([p/'build.sh','build'],1)
   assert not (p/'src/plugin.cpp').exists()
   assert not (p/'scripts/native_support.py').exists()
   assert not (p/'scripts/mhgu_binary.py').exists()
 for bad in ('../escape','/absolute','build/foo','work/foo','src/foo.nro','history/old.md','build.local.json'):
  try:s.safe(bad)
  except ValueError:pass
  else:raise AssertionError(bad)
 for mod in ('damage-numbers','modern-weapon-controls','key-quest-markers','please-do-better'):
  s.refresh(mod);p=s.export(mod,root/mod)
  assert not (p/'.git').exists() and not (p/'build.local.json').exists()
  run([p/'build.sh','--help'])
  # No user inputs: compilation must fail with an actionable input error.
  run([p/'build.sh','prepare'],1)
  records=json.loads((p/'source-export.json').read_text())['files']
  assert all(s.digest(p/n)==v['export_sha256'] for n,v in records.items())
  try:s.export(mod,p)
  except ValueError:pass
  else:raise AssertionError('Existing export overwritten')
print('PASS: four scaffold kinds, host entrypoints, input failures, source export hashes and overwrite/path protection')
