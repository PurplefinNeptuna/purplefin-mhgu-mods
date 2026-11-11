#!/usr/bin/env python3
"""Download pinned third-party sources into vendor/. The only build step that uses the network.

Each archive is a GitHub tree at a pinned commit; only the files pinned under its `dest` in
dependencies.lock.json are written. Its optional `patches` (tracked files, applied with GNU patch -p1
inside `dest`) run next, and every pinned file must then match its SHA-256. Rust mods add forge-rs
(`forge_rs_revision`) and crates.io sources, which cargo checks against Cargo.lock.
"""
import hashlib, io, json, os, subprocess, tarfile, urllib.request
from pathlib import Path
from paths import MOD, CONFIG

ARCHIVE='https://codeload.github.com/{repo}/tar.gz/{rev}'

def archives(lock):
    entries=list(lock.get('archives',[]))
    if 'forge_rs_revision' in lock and not any(e['dest']=='vendor/forge-rs/' for e in entries):
        entries.append({'dest':'vendor/forge-rs/','repo':'Fexty12573/forge-rs','rev':lock['forge_rs_revision']})
    return entries

def owner(name,entries):
    """A pinned file belongs to the archive with the longest matching dest, if any."""
    matches=[e for e in entries if name.startswith(e['dest'])]
    return max(matches,key=lambda e:len(e['dest'])) if matches else None

def fetch(entry,pins):
    with urllib.request.urlopen(ARCHIVE.format(**entry),timeout=120) as response: data=response.read()
    wanted={entry.get('source','')+name[len(entry['dest']):]:name for name in pins}
    found={}
    with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as archive:
        for item in archive.getmembers():
            path='/'.join(Path(item.name).parts[1:])  # drop the <repo>-<rev>/ prefix
            if item.isfile() and path in wanted: found[wanted[path]]=archive.extractfile(item).read()
    missing=set(pins)-set(found)
    if missing: raise ValueError(entry['repo']+' '+entry['rev']+' lacks pinned files: '+', '.join(sorted(missing)))
    for name,blob in found.items():
        path=MOD/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(blob)
    for patch in entry.get('patches',[]):
        subprocess.run(['patch','-p1','--batch','--silent','-d',MOD/entry['dest'],'-i',MOD/patch],check=True)
    for name,expected in pins.items():
        if hashlib.sha256((MOD/name).read_bytes()).hexdigest()!=expected:
            raise ValueError(entry['repo']+' '+entry['rev']+' differs from the pin: '+name)

def main():
    lock=json.loads((MOD/'dependencies.lock.json').read_text())
    entries=archives(lock)
    rust=(MOD/'Cargo.toml').is_file()
    targets=[MOD/e['dest'].rstrip('/') for e in entries]+([MOD/'vendor/crates'] if rust else [])
    for p in targets:
        if p.exists(): raise ValueError('Preserving existing '+str(p.relative_to(MOD))+'; remove it to fetch again')
    pins={id(e):{} for e in entries}
    for name,expected in lock['files'].items():
        entry=owner(name,entries)
        if entry: pins[id(entry)][name]=expected
    for entry in entries: fetch(entry,pins[id(entry)])
    if rust:
        cargo=Path(CONFIG['rust_bin'])
        library=(cargo.parent/'lib/rustlib/src/rust/library').resolve()  # cargo rejects a workspace path with '..'
        # build-std resolves the toolchain's library workspace, and test harnesses keep their own locks.
        extra=[library/'Cargo.toml',*(p.parent/'Cargo.toml' for p in sorted(MOD.glob('tests/*/Cargo.lock')))]
        env=dict(os.environ,CARGO_HOME=str(CONFIG['cargo_home']),CARGO_NET_OFFLINE='false')
        args=[cargo/'cargo','vendor','--quiet','--locked','--versioned-dirs']
        for manifest in extra: args+=['--sync',manifest]
        subprocess.run([*map(str,args),'vendor/crates'],cwd=MOD,env=env,check=True,stdout=subprocess.DEVNULL)
    print('Fetched',', '.join(e['repo']+'@'+e['rev'][:7] for e in entries)+(' and crates' if rust else ''),'into vendor/')

if __name__=='__main__': main()
