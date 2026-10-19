#!/usr/bin/env python3
"""Import/export the supplied Ghidra database and search research indexes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
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
    args = parser.parse_args()
    if args.command in ("import", "export"):
        export_analysis(args.command == "import", args.targets)
    elif args.command == "find":
        if args.limit < 1:
            parser.error("--limit must be positive")
        find(args.query, args.kind, args.limit)
    else:
        print((EXPORT / "summary.json").read_text())


if __name__ == "__main__":
    main()
