#!/usr/bin/env python3
"""Prepare/build the research dumper or index a copied runtime dump. Never installs it."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "mods/dti-dumper-support"
TOOLS = ROOT / "tools/mhgu-dti-dumper"
SOURCE = TOOLS / "source"
OUTPUT = ROOT / "build/dti-dumper"
WORK = ROOT / "work/research-tooling"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def prepare():
    recipe = json.loads((RECIPE / "recipe.json").read_text())
    archive = ROOT / recipe["archive"]
    if sha(archive) != recipe["archive_sha256"]:
        raise ValueError("Dumper source archive fingerprint changed")
    WORK.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=WORK, prefix="dti-prepare-") as temporary:
        with tarfile.open(archive) as archive_file:
            archive_file.extractall(temporary, filter="data")
        candidate = next(Path(temporary).iterdir())
        if sha(candidate / "src/lib.rs") != recipe["upstream_lib_sha256"]:
            raise ValueError("Unexpected upstream implementation")
        # Exact source hashing above makes zero-context hunks safe to replay.
        subprocess.run(["git", "apply", "--unidiff-zero", "--check", str(RECIPE / "upstream.patch")], cwd=candidate, check=True)
        subprocess.run(["git", "apply", "--unidiff-zero", str(RECIPE / "upstream.patch")], cwd=candidate, check=True)
        shutil.copy2(RECIPE / "json.rs", candidate / "src/json.rs")
        compiler = next((ROOT / "tools/forge-container/storage/vfs/dir").glob(
            "*/opt/devkitpro/devkitARM/bin/arm-none-eabi-gcc"))
        target = candidate / "armv7a-none-eabi.json"
        config = json.loads(target.read_text())
        config["linker"] = str(compiler.resolve())
        target.write_text(json.dumps(config, indent=4) + "\n")
        if SOURCE.exists():
            for relative in ("src/lib.rs", "src/json.rs", "Cargo.lock", "armv7a-none-eabi.json"):
                existing = SOURCE / relative
                if existing.exists() and existing.read_bytes() != (candidate / relative).read_bytes():
                    raise ValueError(f"Local source differs: {existing}; preserve edits before preparing")
        shutil.copytree(candidate, SOURCE, dirs_exist_ok=True)
    print(f"Prepared pinned source at {SOURCE}")


def nso_exports(path):
    """Read defined dynamic symbols from a copied NSO, checking its segment hashes."""
    data = path.read_bytes()
    if data[:4] != b"NSO0":
        raise ValueError("Not an NSO")
    flags = struct.unpack_from("<I", data, 12)[0]
    library = ctypes.CDLL("liblz4.so.1")
    decompress = library.LZ4_decompress_safe
    decompress.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    decompress.restype = ctypes.c_int
    segments = []
    for index in range(3):
        offset, address, size = struct.unpack_from("<3I", data, 16 + index * 16)
        stored = struct.unpack_from("<I", data, 96 + index * 4)[0] if flags & (1 << index) else size
        if offset + stored > len(data) or size > 128 * 1024 * 1024:
            raise ValueError("NSO bounds invalid")
        raw = data[offset:offset+stored]
        if flags & (1 << index):
            destination = ctypes.create_string_buffer(size)
            if decompress(raw, destination, len(raw), size) != size:
                raise ValueError("NSO decompression failed")
            raw = destination.raw
        if flags & (1 << (index+3)) and hashlib.sha256(raw).digest() != data[160+index*32:192+index*32]:
            raise ValueError("NSO segment hash mismatch")
        segments.append((address, raw))
    image = bytearray(max(address + len(raw) for address, raw in segments))
    for address, raw in segments:
        image[address:address+len(raw)] = raw
    mod = struct.unpack_from("<I", image, 4)[0]
    if image[mod:mod+4] != b"MOD0":
        raise ValueError("NSO MOD0 missing")
    dynamic = mod + struct.unpack_from("<i", image, mod+4)[0]
    tags = {}
    for offset in range(dynamic, len(image), 8):
        tag, value = struct.unpack_from("<II", image, offset)
        if not tag:
            break
        tags[tag] = value
    count = struct.unpack_from("<I", image, tags[4]+4)[0]
    exports = set()
    for index in range(count):
        name_offset, _, _, info, _, section = struct.unpack_from("<IIIBBH", image, tags[6]+index*16)
        if section and info >> 4 in (1, 2):
            start = tags[5] + name_offset
            end = image.find(0, start, tags[5]+tags[10])
            if end < 0:
                raise ValueError("NSO symbol name unterminated")
            exports.add(bytes(image[start:end]).decode("ascii"))
    return exports


def build():
    from mhgu_binary import main_image
    from mhgu_binary import Nro
    recipe = json.loads((RECIPE / "recipe.json").read_text())
    for relative, expected in (("src/lib.rs", recipe["patched_lib_sha256"]), ("Cargo.lock", recipe["cargo_lock_sha256"])):
        if sha(SOURCE / relative) != expected:
            raise ValueError(f"Pinned source changed: {relative}")
    if (SOURCE / "src/json.rs").read_bytes() != (RECIPE / "json.rs").read_bytes():
        raise ValueError("JSON helper differs from recipe")
    main = ROOT / "work/shared/game-exefs/main"
    if sha(main) != recipe["main_sha256"]:
        raise ValueError("Copied main executable fingerprint changed")
    image, _ = main_image(main.read_bytes())
    for signature in recipe["target_signatures"]:
        offset = int(signature["offset"], 16)
        expected = bytes.fromhex(signature["bytes"])
        if image[offset:offset+len(expected)] != expected:
            raise ValueError("Dumper target signature differs from the original executable")
    baseline = json.loads((ROOT / "docs/FORGE_LOCAL_BRANCH.json").read_text())
    forge = ROOT / "tools/forge-local"
    if subprocess.check_output(["git", "-C", str(forge), "rev-parse", "HEAD"], text=True).strip() != baseline["commit"]:
        raise ValueError("Maintained Forge baseline changed")
    if subprocess.check_output(["git", "-C", str(forge), "status", "--porcelain"], text=True).strip():
        raise ValueError("Maintained Forge baseline has local edits")
    env = os.environ.copy()
    env.update(RUSTUP_HOME=str(TOOLS / "rustup"), CARGO_HOME=str(TOOLS / "cargo"),
               RUSTUP_TOOLCHAIN=recipe["toolchain"], CARGO_NET_OFFLINE="true")
    env["PATH"] = str(TOOLS / "cargo/bin") + os.pathsep + env.get("PATH", "")
    compiler_version = subprocess.check_output(["rustc", "--version"], env=env, text=True).strip()
    if compiler_version != "rustc " + recipe["rust_version"]:
        raise ValueError("Isolated Rust compiler version changed")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with (OUTPUT / "build.log").open("w") as log:
        process = subprocess.Popen(["cargo", "forge", "build", "--release"], cwd=SOURCE, env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end="", flush=True); log.write(line); log.flush()
        if process.wait():
            raise RuntimeError("Dumper build failed; see build/dti-dumper/build.log")
    if sha(SOURCE / "Cargo.lock") != recipe["cargo_lock_sha256"]:
        raise ValueError("Cargo changed the dependency lock")
    binary = SOURCE / "mhgu_dti_dumper.nro"
    nro = Nro(binary.read_bytes())
    imports = [(entry[0].decode("ascii"), entry[1][3] >> 4) for entry in nro.symbols if entry[0] and entry[1][5] == 0]
    if any(name.startswith(("forge_hook", "jit", "svc")) for name, _ in imports):
        raise ValueError("Dumper unexpectedly imports a hook/JIT/CodeMemory API")
    live_forge = Path(baseline["installed_packages"]["forge-patched"]) / "exefs/subsdk9"
    if sha(live_forge) != baseline["installed_forge_sha256"]:
        raise ValueError("Installed Forge fingerprint changed")
    sdk = ROOT / "work/shared/game-exefs/sdk"
    if sha(sdk) != recipe["sdk_sha256"]:
        raise ValueError("Copied SDK fingerprint changed")
    available = nso_exports(live_forge) | nso_exports(main) | nso_exports(sdk)
    missing = [name for name, binding in imports if binding != 2 and name not in available]
    if missing:
        raise ValueError(f"Unresolved strong NRO imports: {missing}")
    staged = OUTPUT / "package/romfs/nativeNX/plugins/mhgu_dti_dumper.nro"
    staged.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(binary, staged)
    manifest = {"source_revision": recipe["revision"], "rustc": compiler_version,
                "sha256": sha(staged), "size": staged.stat().st_size, "package": str(staged.relative_to(ROOT)),
                "strong_imports_resolved": True, "imports": [name for name, _ in imports],
                "unresolved_weak_imports": [name for name, binding in imports if binding == 2 and name not in available],
                "additional_code_memory_objects": 0, "opt_in_flag_in_package": False,
                "installed": False, "runtime_validation": "not performed",
                "inputs": {str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path): sha(path)
                           for path in (main, sdk, live_forge, RECIPE / "upstream.patch", RECIPE / "json.rs")}}
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Verified and staged {staged}; no runtime activation")


def ingest(source):
    rows = json.loads(source.read_text())
    if not isinstance(rows, list):
        raise ValueError("Expected the dumper's JSON class array")
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("dti"), str) or not isinstance(row.get("properties"), list):
            raise ValueError("Invalid class record")
        if row.get("vft_kind") not in ("object", "dti"):
            raise ValueError("Ambiguous vtable kind; use the prepared dumper")
    destination = WORK / "dti"
    destination.mkdir(parents=True, exist_ok=True)
    copied = destination / "dti_dump.json"
    if copied.exists() and sha(copied) != sha(source):
        raise ValueError("A different runtime dump is already indexed; preserve it before replacing")
    if source.resolve() != copied.resolve():
        shutil.copy2(source, copied)
    with (destination / "dti.jsonl").open("w") as out:
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
    (destination / "provenance.json").write_text(json.dumps({"source": str(source.resolve()),
        "sha256": sha(copied), "classes": len(rows), "runtime_build_verified": False}, indent=2)+"\n")
    print(f"Indexed {len(rows)} runtime classes; verify the run's build separately")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "build", "status"):
        commands.add_parser(name)
    load = commands.add_parser("import")
    load.add_argument("dump", type=Path)
    args = parser.parse_args()
    if args.command == "prepare": prepare()
    elif args.command == "build": build()
    elif args.command == "import": ingest(args.dump)
    else:
        path = OUTPUT / "manifest.json"
        print(path.read_text() if path.exists() else "Source imported; no staged build yet")


if __name__ == "__main__":
    main()
