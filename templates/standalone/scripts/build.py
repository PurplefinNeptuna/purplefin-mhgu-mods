from paths import NAME
#!/usr/bin/env python3
"""Build one owned mod; never install, activate or publish."""
import argparse, ast, hashlib, importlib, json, os, shutil, subprocess, sys, zipfile
from pathlib import Path
from paths import ROOT, MOD, SCRIPTS, WORKSPACE, CONFIG, PYTHON, FORGE, DEPS, CONTAINER_STORAGE, input_path, check_dependencies

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args, **kwargs): return subprocess.run(list(map(str,args)),check=True,**kwargs)
def record(name,data):
 p=ROOT/'build'/NAME/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n')
def config(): return json.loads((MOD/'mod.json').read_text())
def script(name,*args): run([PYTHON,SCRIPTS/(name+'.py'),*args])
def doctor():
 missing=[]
 for tool in ('python3','c++'):
  if not shutil.which(tool):missing.append(tool)
 cfg=config()
 if cfg['kind']=='plugin' and not shutil.which('podman'):missing.append('podman')
 if (MOD/'dependencies.lock.json').exists():check_dependencies()
 for name in ('main','sdk','forge') if cfg.get('recipe') else ():
  p=input_path(name)
  if not p.is_file():missing.append(name+' input (set build.local.json)')
 if missing:raise ValueError('Missing: '+', '.join(missing))
 if cfg['kind']=='plugin':
  result=subprocess.run(['podman','--root',str(CONTAINER_STORAGE),'--runroot',f'/tmp/mhgu-forge-container-{os.getuid()}','--storage-driver','vfs','image','exists',cfg['compiler_image']])
  if result.returncode:raise ValueError('Pinned compiler image absent; run prepare --fetch explicitly')
 if (MOD/'requirements.txt').exists():
  required={line.split('==')[0]:line.split('==')[1] for line in (MOD/'requirements.txt').read_text().splitlines() if '==' in line}
  run([PYTHON,'-c',"import importlib.metadata as m,json,sys; r=json.loads(sys.argv[1]); actual={n:m.version(n) for n in r}; assert actual==r,(actual,r)",json.dumps(required)])
 if cfg.get('recipe'):
  from mhgu_binary import main_image
  main_image(input_path('main').read_bytes())
  for n,h in check_dependencies()['binary_inputs'].items():
   if digest(input_path(n))!=h:raise ValueError('Incorrect '+n+' fingerprint')
 print('PASS: pinned offline toolchain, dependencies and supplied input fingerprints')

def prepare(fetch=False):
 cfg=config()
 if fetch:
  if cfg['kind']=='plugin':
   run(['podman','--root',CONTAINER_STORAGE,'--runroot',f'/tmp/mhgu-forge-container-{os.getuid()}','--storage-driver','vfs','pull',cfg['compiler_image']])
  if (MOD/'requirements.txt').exists():
   run([sys.executable,'-m','venv',MOD/'.venv']);run([MOD/'.venv/bin/python','-m','pip','install','-r',MOD/'requirements.txt'])
 if (MOD/'dependencies.lock.json').exists():check_dependencies()
 # Copy mod input trees only into the ignored working area. Existing differences fail.
 source=CONFIG.get('inputs')
 if source:
  source=(MOD/source).resolve()
  if not source.is_dir():raise ValueError('Missing supplied input directory: '+str(source))
  dest=ROOT/'work'/NAME/'inputs'
  if source==dest.resolve():raise ValueError('Input source overlaps copied destination')
  for p in sorted(source.rglob('*')):
   if p.is_symlink():raise ValueError('Input symlink: '+str(p))
   if not p.is_file():continue
   q=dest/p.relative_to(source)
   if q.exists() and digest(q)!=digest(p):raise ValueError('Preserving differing input: '+str(q))
   q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 if cfg.get('recipe'):
  from mhgu_binary import main_image
  main_image(input_path('main').read_bytes())
  if digest(input_path('sdk'))!='9a9b7035266637ee693a32da6b0fde54bda00e897bef05b1c8d8cda30f8ac8b0':raise ValueError('SDK fingerprint differs')
  from native_support import nso_exports
  if digest(input_path('forge'))!='9d472d56f81f834f366171426dbd0131af19c7697e132c731c3fd3f335af53d0':raise ValueError('Forge fingerprint differs; explicit dependency update and revalidation required')
  nso_exports(input_path('forge'))
  if NAME=='key-quest-markers':
   if not CONFIG.get('romfs'):raise ValueError('Quest inventory requires romfs in build.local.json')
   pinned=json.loads((MOD/'research/quest-baseline.json').read_text());dest=ROOT/'work'/NAME/'inputs';items=[]
   for n,h in pinned['files'].items():
    src=(MOD/CONFIG['romfs']).resolve()/'nativeNX'/n
    if not src.is_file() or digest(src)!=h:raise ValueError('Quest resource fingerprint differs or missing: '+n)
    q=dest/n
    if q.exists() and digest(q)!=h:raise ValueError('Preserving differing copied quest input: '+n)
    q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,q);items.append({'copy':n,'sha256':h})
   (dest/'provenance.json').write_text(json.dumps(items,indent=2)+'\n')
 print('Prepared pinned dependencies and supplied input validation')
def build(diagnostics=False):
 if diagnostics and os.environ.get('MHGU_DIAGNOSTICS')!='1':
  env=dict(os.environ,MHGU_DIAGNOSTICS='1');run([PYTHON,__file__,'build'],env=env);return
 cfg=config();name=cfg.get('recipe')
 if not name:return scaffold_build(cfg)
 prepare()
 if name=='modern_weapon_controls':
  m=importlib.import_module(name);m.inspect(input_path('main'));m.build()
 elif name=='key_quest_markers':
  m=importlib.import_module(name);m.build()
 elif name=='build_damage_numbers_capture':
  p=ROOT/'work/damage-numbers/inputs/main';p.parent.mkdir(parents=True,exist_ok=True)
  if p.exists() and digest(p)!=digest(input_path('main')):raise ValueError('Preserving differing main input')
  shutil.copy2(input_path('main'),p)
  script(name)
 else:importlib.import_module(name).build()
 record('standalone-build.json',{'mod':NAME,'diagnostics':os.environ.get('MHGU_DIAGNOSTICS','0')=='1','native_sources':{str(p.relative_to(MOD)):digest(p) for p in sorted((MOD/'src').rglob('*')) if p.is_file()},'source_files':{str(p.relative_to(MOD)):digest(p) for p in source_files()},'payload_files':payload_hashes(),'runtime_test':'NOT RUN'})
def source_files():
 manifest=json.loads((MOD/'EXPORT.json').read_text())
 return [MOD/x for x in manifest['files']]+[MOD/'EXPORT.json']
def host():
 name=config().get('recipe')
 if name=='modern_weapon_controls':importlib.import_module(name).test()
 elif name=='please_do_better':importlib.import_module(name).host_tests()
 elif name=='build_damage_numbers_capture':script('test_damage_numbers');script('test_damage_numbers_sprite_codec')
 elif name=='key_quest_markers':
  # Markers' complete inventory suite needs supplied game resources. The other
  # suites simulate the kernel/transaction contracts without any game input.
  w=ROOT/'work'/NAME/'host';w.mkdir(parents=True,exist_ok=True)
  for n in ('memory_reader','transaction','native_platform'):
   sources=[MOD/'tests'/f'{n}.cpp'];flags=['-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-pthread','-fsanitize=address,undefined','-fno-pie','-no-pie']
   if n=='native_platform':sources+=[MOD/'src/native_platform.cpp'];flags+=['-DKQM_HOST_PLATFORM_TEST']
   exe=w/n;run(['c++',*flags,'-I',MOD/'src','-I',MOD/'tests',*sources,'-o',exe]);run([exe],env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0'))
 else:
  for p in (MOD/'scripts').glob('*.py'):ast.parse(p.read_text())
  print('PASS: scaffold source syntax; no implemented mod behavior claimed')
 if (SCRIPTS/'runtime_policy.py').exists():script('runtime_policy')
 record('standalone-host.json',{'status':'PASSED','game_inputs_required':False})
def tests(host_only=False):
 host()
 if host_only:return
 name=config().get('recipe')
 if name=='modern_weapon_controls':
  for n in ('mwc_arm_probe','mwc_bowgun_probe','mwc_command_assets','mwc_bowgun_runtime_probe'):script(n,*(['--prepare'] if n=='mwc_command_assets' else []))
  importlib.import_module(name).validate()
 elif name=='build_damage_numbers_capture':
  for n in ('test_damage_numbers_visual','build_damage_numbers_gateway','damage_numbers_arm_probe','damage_numbers_gateway_probe','damage_numbers_capture_probe','damage_numbers_sdk_fs_probe','damage_numbers_sdk_tls_probe','verify_damage_numbers_ge_compat','verify_damage_numbers_compression','audit_damage_numbers_open_assets'):script(n)
 elif name=='key_quest_markers':importlib.import_module(name).test()
 elif name=='please_do_better':
  for n in ('please_do_better_arm_probe','please_do_better_runtime_probe','please_do_better_native_probe','please_do_better_observation_probe','please_do_better_display_probe','please_do_better_highlight_probe','please_do_better_log_probe'):script(n)
 verify()
 record('standalone-tests.json',{'status':'PASSED','build_record_sha256':digest(ROOT/'build'/NAME/'standalone-build.json'),'runtime_test':'NOT RUN'})
def payload():
 name=config().get('recipe')
 paths={'modern_weapon_controls':'controls-candidate-package/romfs/nativeNX/plugins/modern_weapon_controls.nro','key_quest_markers':'package/romfs/nativeNX/plugins/key_quest_markers.nro','build_damage_numbers_capture':'open-assets/candidate-package/romfs/nativeNX/plugins/damage_numbers_capture.nro','please_do_better':f"candidates/{config()['version']}/Please do Better/romfs/nativeNX/plugins/please_do_better.nro"}
 return ROOT/'build'/NAME/paths[name] if name else ROOT/'build'/NAME/'package'
def payload_hashes():
 p=payload()
 return {str(p.relative_to(ROOT)):digest(p)} if p.is_file() else {str(f.relative_to(ROOT)):digest(f) for f in sorted(p.rglob('*')) if f.is_file()}
def verify():
 check_dependencies() if (MOD/'dependencies.lock.json').exists() else None
 p=ROOT/'build'/NAME/'standalone-build.json'
 if not p.exists():raise ValueError('Build first: missing current build receipt')
 d=json.loads(p.read_text())
 if d.get('payload_files')!=payload_hashes():raise ValueError('Built payload changed; rebuild and validate')
 for n,h in d.get('source_files',{}).items():
  if digest(MOD/n)!=h:raise ValueError('Build sources changed: '+n)
 if config().get('recipe'):
  from mhgu_binary import Nro
  from native_support import nso_exports
  n=Nro(payload().read_bytes());imports={s[0].decode() for s in n.symbols if s[0] and not s[1][5]}
  exports=nso_exports(input_path('forge'))|nso_exports(input_path('sdk'))|nso_exports(input_path('main'))
  if imports-exports:raise ValueError('Unresolved imports: '+str(sorted(imports-exports)))
  native=ROOT/'work'/NAME/('open-assets' if NAME=='damage-numbers' else 'native')
  dis=(native/'disassembly.txt').read_text() if (native/'disassembly.txt').exists() else ''
  import re
  if not dis:raise ValueError('Missing emitted instruction audit; rebuild')
  if re.search(r'\bmsr\b.*(?:APSR_g|APSR_nzcvqg)',dis,re.I):raise ValueError('Unsupported GE restore emitted')
 if not config().get('recipe') and config()['kind']=='plugin':
  from mhgu_binary import Nro
  for n in payload().rglob('*.nro'):
   nro=Nro(n.read_bytes())
   imports={row[0].decode() for row in nro.symbols if row[0] and not row[1][5]}
   if imports:
    from native_support import nso_exports
    if not input_path('forge').is_file():raise ValueError('Supply forge in build.local.json to validate plugin imports')
    available=nso_exports(input_path('forge'))
    for kind in ('sdk','main'):
     if input_path(kind).is_file():available|=nso_exports(input_path(kind))
    if imports-available:raise ValueError('Unresolved plugin imports: '+str(sorted(imports-available)))
 print('PASS: current source/dependency fingerprints, NRO structure, imports and emitted flag restoration')
def package(release=False):
 verify();out=ROOT/'build'/NAME
 build_record=json.loads((out/'standalone-build.json').read_text())
 if build_record.get('diagnostics') and release:raise ValueError('Diagnostic builds cannot become approved releases')
 if release:
  approved=json.loads((MOD/'DISTRIBUTION.json').read_text())
  if approved.get('version')!=config()['version']:raise ValueError('Build version differs from approved distribution version')
  if config().get('recipe') and not any(v['sha256']==digest(payload()) for v in approved.get('payloads',{}).values()):raise ValueError('Current candidate payload is not approved')
  evidence=out/'standalone-tests.json'
  if not evidence.exists() or json.loads(evidence.read_text()).get('status')!='PASSED' or json.loads(evidence.read_text())['build_record_sha256']!=digest(out/'standalone-build.json'):raise ValueError('Complete tests must match this build')
  from mod_distribution import package as standard
  print(standard(NAME));return
 p=payload();pkg=config().get('package_name',{'damage-numbers':'damage-number','modern-weapon-controls':'modern-control'}.get(NAME,NAME))
 files={('romfs/nativeNX/plugins/'+p.name):p} if p.is_file() else {str(x.relative_to(p)):x for x in p.rglob('*') if x.is_file()}
 if not files:raise ValueError('No runtime payloads; implement the recipe first')
 dest=out/'candidates'/('diagnostics' if build_record.get('diagnostics') else 'standalone')
 dest.mkdir(parents=True,exist_ok=True);target=dest/(NAME+'-'+config()['version']+'-candidate.zip')
 import io
 stream=io.BytesIO()
 with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for n,f in sorted(files.items()):
   i=zipfile.ZipInfo(pkg+'/'+n,(1980,1,1,0,0,0));i.external_attr=0o100644<<16;i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,f.read_bytes())
 data=stream.getvalue()
 if target.exists() and target.read_bytes()!=data:raise ValueError('Preserving differing candidate; use a new version or output')
 target.write_bytes(data)
 with zipfile.ZipFile(target) as z:
  if z.testzip():raise ValueError('ZIP CRC failed')
 shutil.copy2(MOD/'README.md',dest/'README.md')
 notices='\n\n'.join(p.read_text() for p in [MOD/'LICENSE',MOD/'THIRD_PARTY.md',*sorted((MOD/'vendor').rglob('LICENSE*')),*sorted((MOD/'fonts').glob('*OFL.txt'))] if p.exists());(dest/'NOTICES.txt').write_text(notices)
 (dest/'manifest.json').write_text(json.dumps({'mod':NAME,'version':config()['version'],'status':'DEVELOPMENT','payloads':{n:digest(p) for n,p in files.items()},'runtime_test':'NOT RUN'},indent=2)+'\n')
 (dest/'SHA256SUMS').write_text(''.join(digest(p)+'  '+p.name+'\n' for p in sorted(dest.iterdir()) if p.is_file() and p.name!='SHA256SUMS'))
 print(target)
def help_assets():
 if NAME!='modern-weapon-controls':raise ValueError('help is only available for Modern Weapon Controls')
 from stage_hd_project import stage
 required=('hd','library','romfs')
 if any(not CONFIG.get(n) for n in required):raise ValueError('help needs hd, library and romfs in build.local.json')
 out=ROOT/'build'/NAME/'help'/config()['version'];work=ROOT/'work'/NAME/'help'/config()['version']
 stage(out,work,hd=(MOD/CONFIG['hd']).resolve(),library=(MOD/CONFIG['library']).resolve(),vanilla=(MOD/CONFIG['romfs']).resolve()/'nativeNX',controls=payload())
 from package_modern_weapon_controls import main as bundle
 bundle(validate=False,visual_root=out)
 print(out)
def scaffold_build(cfg):
 if cfg['kind']=='plugin':
  from mhgu_binary import elf_to_nro
  native=ROOT/'work'/NAME/'native';native.mkdir(parents=True,exist_ok=True)
  args=['podman','--root',CONTAINER_STORAGE,'--runroot',f'/tmp/mhgu-forge-container-{os.getuid()}','--storage-driver','vfs','run','--pull=never','--rm','--network=none','-v',f'{MOD}:/mod:ro','-v',f'{native}:/output:rw',cfg['compiler_image'],'bash','-lc',"set -eu; export PATH=/opt/devkitpro/devkitARM/bin:$PATH; arm-none-eabi-g++ -std=c++17 -O2 -fPIC -marm -fno-exceptions -fno-rtti -I/mod/vendor/forge/include -isystem /mod/vendor/sdk/libs/libnx/nx/include -isystem /mod/vendor/sdk/libs/cimgui -include /mod/vendor/forge/include/compat.h -c /mod/src/plugin.cpp -o /output/plugin.o; arm-none-eabi-gcc -fPIC -marm -c /mod/src/start.S -o /output/start.o; arm-none-eabi-g++ -shared -nostdlib -Wl,--hash-style=sysv,-z,max-page-size=4096,-init=init,-fini=fini -Wl,-T,/mod/src/plugin.ld -Wl,--version-script=/mod/src/exports.txt /output/start.o /output/plugin.o -o /output/plugin.elf"]
  args[-1]=args[-1].replace('-std=c++17','-std=c++17 -DMHGU_DIAGNOSTICS='+('1' if os.environ.get('MHGU_DIAGNOSTICS')=='1' else '0'))
  run(args);p=ROOT/'build'/NAME/'package/romfs/nativeNX/plugins'/('plugin.nro');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(elf_to_nro((native/'plugin.elf').read_bytes()))
 else:
  recipe=json.loads((MOD/'recipe.json').read_text());dest=ROOT/'build'/NAME/'package'
  expected=set(recipe.get('payloads',{}))
  existing={str(p.relative_to(dest)) for p in dest.rglob('*') if p.is_file()}
  if existing-expected:raise ValueError('Stale candidate payload; preserve/archive it before updating the recipe')
  for name,src in recipe.get('payloads',{}).items():
   rel=Path(name)
   if not rel.parts or rel.is_absolute() or '..' in rel.parts or rel.parts[0] not in ('romfs','exefs','cheats'):raise ValueError('Unsafe runtime path')
   p=(MOD/src).resolve()
   if not p.is_relative_to(MOD.resolve()):raise ValueError('Payload outside repo; copy it into ignored inputs first')
   q=dest/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
  if not recipe.get('payloads'):raise ValueError('Scaffold has no payload recipe yet')
 record('standalone-build.json',{'mod':NAME,'diagnostics':os.environ.get('MHGU_DIAGNOSTICS','0')=='1','source_files':{str(p.relative_to(MOD)):digest(p) for p in source_files()},'payload_files':payload_hashes(),'runtime_test':'NOT RUN'})
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',nargs='?',default='build',choices=('doctor','prepare','build','test','verify','package','help','export'));p.add_argument('--host',action='store_true');p.add_argument('--fetch',action='store_true');p.add_argument('--release',action='store_true');p.add_argument('--diagnostics',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args()
 if a.host and a.command!='test' or a.fetch and a.command!='prepare' or a.release and a.command!='package' or a.diagnostics and a.command!='build':p.error('Option does not apply to this command')
 if a.command=='doctor':doctor()
 elif a.command=='prepare':prepare(a.fetch)
 elif a.command=='build':build(a.diagnostics)
 elif a.command=='test':tests(a.host)
 elif a.command=='verify':verify()
 elif a.command=='package':package(a.release)
 elif a.command=='export':
  if not a.output:p.error('export requires --output')
  from export_source import export
  print(export(NAME,a.output))
 else:help_assets()
if __name__=='__main__':
 try:main()
 except (ValueError,OSError,RuntimeError,ImportError,subprocess.CalledProcessError) as e:print('Build failed: '+str(e),file=sys.stderr);sys.exit(1)
