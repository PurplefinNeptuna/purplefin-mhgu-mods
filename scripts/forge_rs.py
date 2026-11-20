#!/usr/bin/env python3
"""Run cargo-forge with the existing isolated MHGU Rust toolchain."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "tools/mhgu-dti-dumper"
TOOLCHAIN = RUNTIME / "rustup/toolchains/nightly-x86_64-unknown-linux-gnu/bin"
CARGO_FORGE = RUNTIME / "cargo/bin/cargo-forge"
SOURCE = ROOT / "tools/forge-rs"


def status():
    record = json.loads((ROOT / "docs/WORKSPACE_EVIDENCE.json").read_text())["tooling"]["forge_rs"]
    print(f"forge-rs {record['version']}; source: {SOURCE}")
    if SOURCE.exists():
        revision = subprocess.check_output(
            ["git", "-C", str(SOURCE), "rev-parse", "HEAD"], text=True
        ).strip()
        print(f"Source revision: {revision}")
        if revision != record["source_revision"]:
            raise ValueError("Source revision differs from the tooling record")
    else:
        print("Source checkout absent; restore it using docs/TOOLS.md")
    if not CARGO_FORGE.is_file() or not (TOOLCHAIN / "rustc").is_file():
        raise ValueError("Isolated runtime absent; see docs/TOOLS.md")
    digest = hashlib.sha256(CARGO_FORGE.read_bytes()).hexdigest()
    if digest != record["cargo_forge_sha256"]:
        raise ValueError("cargo-forge fingerprint differs from the tooling record")
    print(subprocess.check_output([str(TOOLCHAIN / "rustc"), "--version"], text=True).strip())
    print("Commands: forge-rs new NAME --path work/my-trial; forge-rs build --release")
    print("Build runs in the caller's plugin directory; Cargo defaults to offline mode.")
    print("Supported Switch baseline: upstream Forge 2.0.0; docs/DEVELOPMENT.md")


def run(args):
    if not args or args == ["status"]:
        status()
        return 0
    if not CARGO_FORGE.is_file() or not (TOOLCHAIN / "cargo").is_file():
        raise ValueError("Isolated runtime absent; see docs/TOOLS.md")
    env = os.environ.copy()
    env.update(CARGO_HOME=str(RUNTIME / "cargo"),
               RUSTUP_HOME=str(RUNTIME / "rustup"), RUSTUP_TOOLCHAIN="nightly")
    env.setdefault("CARGO_NET_OFFLINE", "true")
    env["PATH"] = os.pathsep.join((str(TOOLCHAIN), str(CARGO_FORGE.parent), env.get("PATH", "")))
    if args[0] == "build" and not env.get("DEVKITARM") and not env.get("DEVKITPRO"):
        compilers = sorted((ROOT / "tools/forge-container/storage/vfs/dir").glob(
            "*/opt/devkitpro/devkitARM/bin/arm-none-eabi-gcc"))
        if not compilers:
            raise ValueError("devkitARM absent; provide DEVKITARM or DEVKITPRO")
        env["DEVKITARM"] = str(compilers[0].resolve().parent.parent)
    return subprocess.call([str(CARGO_FORGE), "forge", *args], env=env)


if __name__ == "__main__":
    try:
        sys.exit(run(sys.argv[1:]))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Cannot run forge-rs: {error}", file=sys.stderr)
        sys.exit(1)
