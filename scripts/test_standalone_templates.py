#!/usr/bin/env python3
"""Exercise real init/build/export/check commands for all four source kinds."""
import argparse,json,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(args,ok=True):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True,cwd='/tmp')
 if (p.returncode==0)!=ok:raise ValueError(str(args)+'\n'+p.stdout+p.stderr)
 return p

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--compiler-storage',type=Path,required=True);a=parser.parse_args()
 with tempfile.TemporaryDirectory(prefix='mhgu-template-validation-') as t:
  root=Path(t);hub=root/'hub';hub.mkdir()
  for name in ('scripts','templates'):shutil.copytree(ROOT/name,hub/name,ignore=shutil.ignore_patterns('__pycache__'))
  (hub/'mods').mkdir()
  for kind in ('plugin','resource','cheat','tool'):
   name='example-'+kind;p=hub/'mods'/name
   args=['python3',hub/'scripts/mod_distribution.py','init',name]
   if kind!='plugin':args+=['--kind',kind] # Also exercise the default plugin kind.
   run(args);run(args,ok=False)
   spec=json.loads((p/'DISTRIBUTION.json').read_text());assert spec['status']=='DEVELOPMENT'
   # Playbook P1 step 10: packaging refuses an unregistered candidate, so register it the documented way.
   spec.update(version='r1',package_name=name,archive=name+'-r1-candidate.zip',candidate='build/'+name+'/candidates/r1/delivery',candidate_builder='scripts/build.py',gamebanana={'ai_code':{'used':False},'ai_assets':[],'credits':[]})
   (p/'DISTRIBUTION.json').write_text(json.dumps(spec,indent=2)+'\n')
   config={'container_storage':str(a.compiler_storage.resolve())};(p/'build.local.json').write_text(json.dumps(config)+'\n')
   if kind!='plugin':
    assert not (p/'src/plugin.cpp').exists() and not (p/'vendor/forge').exists()
    (p/'src/example.txt').write_text('[Example]\n04000000 00000000 00000000\n' if kind=='cheat' else 'Owned synthetic fixture, not a game resource.\n')
    path='cheats/0000000000000000.txt' if kind=='cheat' else 'romfs/nativeNX/example.txt' if kind=='resource' else 'exefs/example.txt'
    (p/'recipe.json').write_text(json.dumps({'kind':kind,'payloads':{path:'src/example.txt'}},indent=2)+'\n')
    run(['python3',p/'scripts/export_source.py','--refresh'])
   for command in (['doctor'],['prepare'],['build'],['test','--host'],['test'],['verify'],['package']):run([p/'build.sh',*command])
   dest=root/('standalone-'+kind);run([p/'build.sh','export','--output',dest]);run([p/'build.sh','export','--output',dest],ok=False)
   (dest/'build.local.json').write_text(json.dumps(config)+'\n')
   for command in (['doctor'],['prepare'],['build'],['test','--host'],['test'],['verify'],['package']):run([dest/'build.sh',*command])
   for folder in (p,dest):
    run(['python3',folder/'scripts/mod_distribution.py','check']);run([folder/'build.sh','package','--release'],ok=False)
    receipt=json.loads((folder/('build/'+name+'/standalone-build.json') if folder==dest else hub/'build'/name/'standalone-build.json').read_text())
    n=next(iter(receipt['payload_files']));payload=(folder if folder==dest else hub)/n;prior=payload.read_bytes();payload.write_bytes(prior+b'changed')
    run([folder/'build.sh','verify'],ok=False);payload.write_bytes(prior)
   (dest/'build.local.json').write_text(json.dumps(dict(config,inputs='missing-inputs'))+'\n')
   run([dest/'build.sh','prepare'],ok=False)
 print('PASS: init/default kind/overwrite refusal; four workspace and standalone builds, host tests, verified candidate ZIPs, export completeness, payload tampering and unapproved-release gates')
if __name__=='__main__':main()
