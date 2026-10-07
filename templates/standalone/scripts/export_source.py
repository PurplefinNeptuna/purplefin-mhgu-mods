#!/usr/bin/env python3
"""Scaffold and export independent mod source folders. Never publish."""
import argparse, hashlib, json, re, shutil, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FORBIDDEN={'.git','build','work','tools','.venv','__pycache__','backups','history'}
BINARY={'.arc','.tex','.mod','.lmt','.gmd','.nsp','.xci','.nca','.zip','.7z','.nro','.elf','.o','.exe','.dll','.gzf','.gpr'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(name):
 p=Path(name)
 if p.is_absolute() or '..' in p.parts or any(x in FORBIDDEN for x in p.parts) or p.suffix.lower() in BINARY or p.name in ('build.local.json','source-export.json'):raise ValueError('Non-source export path: '+name)
 return p
def refresh(mod):
 folder=ROOT if (ROOT/'mod.json').is_file() else ROOT/'mods'/mod
 names=[]
 for p in sorted(folder.rglob('*')):
  name=str(p.relative_to(folder))
  try:safe(name)
  except ValueError:continue
  if p.is_symlink():raise ValueError('Source symlink: '+name)
  if p.is_file() and p.name!='EXPORT.json':names.append(name)
 (folder/'EXPORT.json').write_text(json.dumps({'schema_version':1,'mod':mod,'files':names},indent=2)+'\n')
def export(mod,dest):
 folder=ROOT if (ROOT/'mod.json').is_file() else ROOT/'mods'/mod;record=json.loads((folder/'EXPORT.json').read_text())
 if record['mod']!=mod:raise ValueError('Export identity differs')
 if dest.exists():raise ValueError('Preserving existing export destination: '+str(dest))
 files=record['files']+['EXPORT.json']
 if len(files)!=len(set(files)):raise ValueError('Duplicate export entry')
 checked=[]
 for n in files:
  relative=safe(n);p=folder/relative
  if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(folder.resolve()):raise ValueError('Missing/escaping source: '+n)
  if any(q.is_symlink() for q in p.parents if q!=folder.parent and q.is_relative_to(folder)):raise ValueError('Source directory symlink: '+n)
  checked.append((n,p))
 try:
  commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=folder,text=True,stderr=subprocess.DEVNULL).strip()
 except subprocess.CalledProcessError:
  receipt=folder/'source-export.json'
  commit=json.loads(receipt.read_text()).get('parent_commit') if receipt.exists() else None
 dest.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(dir=dest.parent,prefix='.mod-export-') as temporary:
  stage=Path(temporary)/'source';stage.mkdir()
  entries={}
  for n,p in checked:
   q=stage/n;q.parent.mkdir(parents=True,exist_ok=True)
   data=p.read_bytes()
   # Local historical evidence remains in the workspace. Source exports retain
   # its factual claims and hashes without private machine paths.
   if p.suffix in ('.md','.json'):
    s=data.decode('utf-8');s=re.sub(r'/(?:home/purplefin|mnt/storage2)/[^\s\"<>`]*','<local-path>',s)
    s=s.replace('../../docs/','docs/');data=s.encode()
   q.write_bytes(data);shutil.copymode(p,q)
   entries[n]={'source_sha256':digest(p),'export_sha256':digest(q)}
  (stage/'source-export.json').write_text(json.dumps({'schema_version':1,'mod':mod,'parent_commit':commit,'files':entries},indent=2)+'\n')
  stage.rename(dest)
 return dest

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);p.add_argument('--refresh',action='store_true');a=p.parse_args()
 mod=json.loads((ROOT/'mod.json').read_text())['mod']
 if a.refresh:refresh(mod)
 elif a.output:print(export(mod,a.output))
 else:p.error('Provide --output or --refresh')
if __name__=='__main__':main()
