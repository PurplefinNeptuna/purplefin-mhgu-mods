#!/usr/bin/env python3
"""Scaffold and export independent mod source folders. Never publish."""
import argparse, hashlib, json, re, shutil, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FORBIDDEN={'.git','build','work','tools','.venv','__pycache__','backups','history'}
BINARY={'.arc','.tex','.mod','.lmt','.gmd','.nsp','.xci','.nca','.zip','.7z','.nro','.elf','.o','.exe','.dll','.so','.gzf','.gpr'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(name):
 p=Path(name)
 if p.is_absolute() or '..' in p.parts or any(x in FORBIDDEN for x in p.parts) or p.suffix.lower() in BINARY or p.name in ('build.local.json','source-export.json'):raise ValueError('Non-source export path: '+name)
 return p
def refresh(mod):
 folder=ROOT/'mods'/mod
 if (folder/'Cargo.toml').exists():
  subprocess.run(['python3',folder/'scripts/export_source.py','--refresh'],check=True);return
 names=[]
 for p in sorted(folder.rglob('*')):
  name=str(p.relative_to(folder))
  try:safe(name)
  except ValueError:continue
  if p.is_symlink():raise ValueError('Source symlink: '+name)
  if p.is_file() and p.name!='EXPORT.json':names.append(name)
 (folder/'EXPORT.json').write_text(json.dumps({'schema_version':1,'mod':mod,'files':names},indent=2)+'\n')
def export(mod,dest):
 folder=ROOT/'mods'/mod
 if dest.exists():raise ValueError('Preserving existing export destination: '+str(dest))
 if (folder/'Cargo.toml').exists():
  subprocess.run(['python3',folder/'scripts/export_source.py','--output',dest],check=True);return dest
 record=json.loads((folder/'EXPORT.json').read_text())
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
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
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

def scaffold(path,name,kind):
 if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',name):raise ValueError('Invalid mod name')
 if path.exists():raise ValueError('Preserving existing mod folder: '+str(path))
 source=ROOT/'templates/standalone'
 path.mkdir(parents=True)
 try:
  for n in ('build.sh','.gitignore','.gitattributes','build.local.example.json','AGENTS.md','DEVELOPMENT.md'):
   shutil.copy2(source/n,path/n)
   if n=='DEVELOPMENT.md':(path/n).write_text((path/n).read_text().replace('key-quest-markers',name))
  (path/'scripts').mkdir();(path/'src').mkdir();(path/'tests').mkdir();(path/'recipes').mkdir()
  (path/'tests/README.md').write_text('Add focused behavior, failure and persistence tests here. test --host needs no game inputs.\n')
  helpers=['build.py','paths.py','mod_distribution.py','export_source.py']
  if kind=='plugin':helpers+=['mhgu_binary.py','native_support.py']
  for n in helpers:
   shutil.copy2(source/'scripts'/n,path/'scripts'/n)
  (path/'LICENSE').write_text((ROOT/'scripts/standalone-license.txt').read_text().format(name=name))
  (path/'THIRD_PARTY.md').write_text('Owned code uses MIT. Vendored dependencies retain their included license notices. The plugin scaffold uses the project-owned ARM32 startup and linker scaffold; libnx-derived SVC code is not included.\n')
  cfg={'schema_version':1,'mod':name,'kind':kind,'version':'r1','compiler_image':json.loads((source/'mod.json').read_text())['compiler_image']}
  (path/'mod.json').write_text(json.dumps(cfg,indent=2)+'\n')
  (path/'DISTRIBUTION.json').write_text(json.dumps({'schema_version':1,'mod':name,'status':'DEVELOPMENT','reason':'New mod; distribution approval and verified package are not recorded.','publication':{'published':False,'url':None,'date':None}},indent=2)+'\n')
  (path/'README.md').write_text(f'# {name}\n\n{kind.capitalize()} source scaffold; DEVELOPMENT, with no gameplay validation.\n\nRun `./build.sh doctor`, `./build.sh prepare`, `./build.sh build`, `./build.sh test --host`, `./build.sh verify`, and `./build.sh package`. Dependencies are fetched only with `./build.sh prepare --fetch`. Copy `build.local.example.json` to ignored `build.local.json` for supplied inputs. Outputs are ignored `build/` and `work/`; the coordinating workspace retains its root output locations.\n\nFor resources, cheats and tools, map owned source or copied ignored inputs to runtime paths in recipe.json payloads. Plugin callbacks begin without settings or hooks. Implement the mod-specific behavior and focused tests before claiming a working mod. Export with ./build.sh export --output DEST; refresh its explicit allowlist with python3 scripts/export_source.py --refresh. Runtime acceptance and publication require separate evidence.\n')
  if kind=='plugin':
   shutil.copytree(source/'vendor',path/'vendor')
   for n in ('start.S','plugin.ld','exports.txt'):shutil.copy2(source/'src'/n,path/'src'/n)
   # Export only the lifecycle callbacks; the source starts with no hooks/settings.
   (path/'src/exports.txt').write_text('{ global: init; fini; forge_onLoad; forge_onInit; forge_onUpdate; forge_onImGuiInit; forge_onImGuiRender; forge_onImGuiFreeRender; local: *; };\n')
   (path/'src/plugin.cpp').write_text('''#include <stdint.h>
#include <stddef.h>
struct ForgeVersion { uint16_t major,minor,patch; };
struct PluginInitParam { ForgeVersion required_ver; char name[64]; };
static_assert(sizeof(void*)==4 && sizeof(PluginInitParam)==70 && offsetof(PluginInitParam,name)==6,"ARM32 Forge ABI");
extern "C" void init() {}
extern "C" void fini() {}
extern "C" void forge_onLoad(PluginInitParam* p) {
 if (!p) return;
 auto* b=reinterpret_cast<volatile unsigned char*>(p);
 for(unsigned i=0;i<sizeof(*p);++i)b[i]=0;
 b[0]=1;b[2]=5;b[4]=1;
 const char* name="'''+name+'''";
 for(unsigned i=0;name[i] && i<63;++i)b[6+i]=name[i];
}
extern "C" void forge_onInit() {}
extern "C" void forge_onUpdate(float) {}
extern "C" void forge_onImGuiInit(void*,void*,void*) {}
extern "C" void forge_onImGuiRender() {} // Only real settings belong here.
extern "C" void forge_onImGuiFreeRender() {} // Background work remains independent.
''')
  else:
   (path/'recipe.json').write_text(json.dumps({'kind':kind,'payloads':{}},indent=2)+'\n')
  vendor=path/'vendor'
  lock={'schema_version':1,'compiler_image':cfg['compiler_image'],'files':{str(p.relative_to(path)):digest(p) for p in sorted(vendor.rglob('*')) if p.is_file()} if vendor.exists() else {}}
  (path/'dependencies.lock.json').write_text(json.dumps(lock,indent=2)+'\n')
  files=[str(p.relative_to(path)) for p in sorted(path.rglob('*')) if p.is_file()]
  (path/'EXPORT.json').write_text(json.dumps({'schema_version':1,'mod':name,'files':files},indent=2)+'\n')
 except BaseException:
  shutil.rmtree(path);raise
 return path

def main():
 p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command',required=True)
 x=s.add_parser('export');x.add_argument('mod');x.add_argument('--output',type=Path,required=True)
 x=s.add_parser('refresh');x.add_argument('mod')
 a=p.parse_args()
 if a.command=='export':print(export(a.mod,a.output))
 else:refresh(a.mod)
if __name__=='__main__':main()
