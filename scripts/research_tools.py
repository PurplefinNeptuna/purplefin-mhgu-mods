#!/usr/bin/env python3
"""Import/export the supplied Ghidra database and search research indexes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT =Path(__file__).resolve().parents[1]
WORK = ROOT / "work/research-tooling"
PROJECTS = WORK / "ghidra-projects"
EXPORT = WORK / "ghidra-export"
GHIDRA = ROOT / "tools/ghidra/ghidra_12.1.4_PUBLIC"
SOURCE_SHA = "b4b94c526f2d0b1b91dbcbd4bd5f411479a5db7270de04a50605f61db649f99a"


def ghidra_environment():
    env = os.environ.copy()
    for name, folder in (("XDG_CONFIG_HOME", "config"), ("XDG_CACHE_HOME", "cache"), ("XDG_DATA_HOME", "data")):
        path = ROOT / "tools/state/ghidra" / folder
        path.mkdir(parents=True, exist_ok=True)
        env[name] = str(path)
    return env


def export_analysis(import_database=False, targets=None):
    from mhgu_binary import main_image
    source = WORK / "inputs/MHGU_1.4.0.gzf"
    if hashlib.file_digest(source.open("rb"), "sha256").hexdigest() != SOURCE_SHA:
        raise ValueError("Supplied GZF fingerprint changed")
    main = ROOT / "work/shared/game-exefs/main"
    image, _ = main_image(main.read_bytes())  # Checks exact NSO hash/build/segments.
    image_path = WORK / "inputs/main-memory.bin"
    image_path.write_bytes(image)
    PROJECTS.mkdir(parents=True, exist_ok=True)
    project = PROJECTS / "MHGU_1.4.0.gpr"
    if import_database and project.exists():
        raise ValueError("Project already exists; use export to preserve your annotations")
    if not import_database and not project.exists():
        raise ValueError("Import the database first")
    mode = ["-import", str(source)] if import_database else ["-process", "MHGU_1.4.0", "-readOnly"]
    args = [str(GHIDRA / "support/analyzeHeadless"), str(PROJECTS), "MHGU_1.4.0", *mode,
            "-noanalysis", "-scriptPath", str(ROOT / "scripts/ghidra"), "-postScript", "ExportMhguResearch.java",
            str(EXPORT), str(image_path), *([str(Path(targets).resolve(strict=True))] if targets else []), "-log", str(WORK / "ghidra-export.log"),
            "-scriptlog", str(WORK / "ghidra-script.log")]
    summary_path = EXPORT / "summary.json"
    previous_time = summary_path.stat().st_mtime_ns if summary_path.exists() else None
    subprocess.run(args, env=ghidra_environment(), check=True)
    if not summary_path.exists() or summary_path.stat().st_mtime_ns == previous_time:
        raise ValueError("Ghidra did not produce a fresh export; inspect its script log")
    summary = json.loads(summary_path.read_text())
    if summary["executable_sha256"] != hashlib.sha256(main.read_bytes()).hexdigest():
        raise ValueError("Ghidra program executable metadata does not match the verified main")
    print(f"Exported {summary['function_count']} functions to {EXPORT}")


def find(query, kind, limit):
    categories = [kind] if kind != "all" else ["functions", "types", "symbols", "dti"]
    matches = 0
    for category in categories:
        path = (WORK / "dti/dti.jsonl") if category == "dti" else EXPORT / f"{category}.jsonl"
        if not path.exists():
            continue
        with path.open() as source:
            for line in source:
                if query.casefold() not in line.casefold():
                    continue
                item = json.loads(line)
                item["index"] = category
                if isinstance(item.get("relative_address"), int):
                    item["main_offset"] = f"0x{item['relative_address']:x}"
                print(json.dumps(item, ensure_ascii=False))
                matches += 1
                if matches >= limit:
                    return
    if not matches:
        print("No matching indexed records")


def main_bytes():
    from mhgu_binary import main_image
    return main_image((ROOT / "work/shared/game-exefs/main").read_bytes())[0]


def branch_sites(image, target):
    """ARM `b`/`bl` sites reaching a main-relative target, any condition.

    shortcut: scans the whole image, so a data word that decodes as a branch can appear;
    confirm a surprising site with `dis`. Register and vtable calls are not direct
    branches, so an empty result needs `word_sites` too before it means "unreferenced".
    """
    sites = []
    for at in range(0, len(image) - 3, 4):
        word = int.from_bytes(image[at:at + 4], "little")
        if word >> 28 == 0xF or (word >> 25) & 7 != 0b101:
            continue
        offset = word & 0xFF_FFFF
        offset -= (offset & 0x80_0000) << 1
        if at + 8 + offset * 4 == target:
            sites.append((at, "bl" if word >> 24 & 1 else "b"))
    return sites


def word_sites(image, value):
    """Aligned words equal to value. Vtables and DTI records hold main-relative code offsets."""
    needle = value.to_bytes(4, "little")
    return [at for at in range(0, len(image) - 3, 4) if image[at:at + 4] == needle]


def real_target(instruction, start):
    """objdump prints a branch target relative to the window; give it as main+offset."""
    match = re.fullmatch(r"(bl?x?(?:eq|ne|hs|lo|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)?) 0x([0-9a-f]+)", instruction)
    return f"{match[1]} main+{(start + int(match[2], 16)) & 0xffffffff:#x}" if match else instruction


def disassemble(image, start, size):
    with tempfile.TemporaryDirectory() as folder:
        raw, obj = Path(folder, "win.bin"), Path(folder, "win.o")
        raw.write_bytes(image[start:start + size])
        subprocess.run(["llvm-objcopy", "-I", "binary", "-O", "elf32-littlearm",
                        "--rename-section=.data=.text,code", str(raw), str(obj)], check=True)
        listing = subprocess.run(["llvm-objdump", "-d", "--triple=armv7a", "--no-show-raw-insn", str(obj)],
                                 check=True, capture_output=True, text=True).stdout
    for line in listing.splitlines():
        address, colon, text = line.strip().partition(":")
        if colon and text and all(c in "0123456789abcdef" for c in address):
            print(f"main+0x{start + int(address, 16):x}  {real_target(' '.join(text.split('@')[0].split('<')[0].split()), start)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("import", "export"):
        commands.add_parser(name).add_argument("--targets", help="file of main-relative 0x offsets to decompile, one per line, # comments")
    commands.add_parser("status")
    search = commands.add_parser("find")
    search.add_argument("query")
    search.add_argument("--kind", choices=("all", "functions", "types", "symbols", "dti"), default="all")
    search.add_argument("--limit", type=int, default=30)
    number = lambda text: int(text, 0)
    commands.add_parser("xref", help="ARM b/bl sites reaching a main-relative offset").add_argument("target", type=number)
    commands.add_parser("word", help="aligned words equal to a value (vtable and DTI references)").add_argument("value", type=number)
    window = commands.add_parser("dis", help="disassemble the hash-checked main at a main-relative offset")
    window.add_argument("start", type=number)
    window.add_argument("size", type=number, nargs="?", default=0x40)
    table = commands.add_parser("vtable", help="print a vtable's main-relative code offsets by slot")
    table.add_argument("start", type=number)
    table.add_argument("count", type=number, nargs="?", default=32)
    args = parser.parse_args()
    if args.command in ("import", "export"):
        export_analysis(args.command == "import", args.targets)
    elif args.command == "find":
        if args.limit < 1:
            parser.error("--limit must be positive")
        find(args.query, args.kind, args.limit)
    elif args.command == "xref":
        for at, kind in branch_sites(main_bytes(), args.target):
            print(f"main+0x{at:x}  {kind}")
    elif args.command == "word":
        for at in word_sites(main_bytes(), args.value):
            print(f"main+0x{at:x}")
    elif args.command == "dis":
        disassemble(main_bytes(), args.start, args.size)
    elif args.command == "vtable":
        image = main_bytes()
        for slot in range(args.count):
            print(f"slot 0x{slot * 4:02x}  0x{int.from_bytes(image[args.start + slot * 4:args.start + slot * 4 + 4], 'little'):x}")
    else:
        print((EXPORT / "summary.json").read_text())


if __name__ == "__main__":
    main()
