#!/usr/bin/env python3
"""Launch the locally installed MHGU toolkit with isolated dependencies."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
PYTHON = str(TOOLS / "python-env/bin/python")


def launch(name, args):
    env = os.environ.copy()
    state = TOOLS / "state" / name
    for variable, directory in (
        ("XDG_CONFIG_HOME", "config"),
        ("XDG_CACHE_HOME", "cache"),
        ("XDG_DATA_HOME", "data"),
    ):
        path = state / directory
        path.mkdir(parents=True, exist_ok=True)
        env[variable] = str(path)
    cwd = ROOT
    temporary_alias = None
    commands = {
        "salad": [PYTHON, str(TOOLS / "saladsoftware/SaladSoftware.py")],
        "pax": [str(TOOLS / "pax/arc_explorer")],
        "imhex": [str(TOOLS / "imhex/squashfs-root/AppRun")],
        "blender": [str(TOOLS / "blender/blender-4.5.14-linux-x64/blender")],
        "audacity": [str(TOOLS / "audacity/squashfs-root/AppRun")],
        "gimp": ["gimp", "--new-instance"],
        "titanbreak": [PYTHON, str(TOOLS / "titanbreak/launcher.py")],
        "quest": [str(TOOLS / "quest-build/MHGUQuestEditor/MHGUQuestEditor")],
        "gmd": ["node", str(TOOLS / "gmd-source/dist/cli/index.js")],
        "revil": [str(TOOLS / "revil/revil_toolset")],
        "ffmpeg": ["ffmpeg"],
        "adpcm": [PYTHON, str(TOOLS / "ifrit-source/wav2adpcm_single.py")],
        "stqr": ["xdg-open", str(TOOLS / "ifrit-source/STQREditor.html")],
        "templates": ["xdg-open", str(ROOT / "references/MHGU-Modding/templates")],
        "model-plugins": ["xdg-open", str(TOOLS / "model-plugins")],
        "ghidra": [str(TOOLS / "ghidra/ghidra_12.1.4_PUBLIC/ghidraRun")],
        "ghidra-headless": [str(TOOLS / "ghidra/ghidra_12.1.4_PUBLIC/support/analyzeHeadless")],
        "research": [sys.executable, str(ROOT / "scripts/research_tools.py")],
        "dti-dumper": [sys.executable, str(ROOT / "scripts/dti_dumper.py")],
        "dti-resources": ["xdg-open", str(ROOT / "mods/dti-dumper-support/README.md")],
        "forge-rs": [sys.executable, str(ROOT / "scripts/forge_rs.py")],
        "forge-rs-resources": ["xdg-open", str(ROOT / "docs/TOOLS.md")],
    }
    if name == "ghidra" and not args:
        args = [str(ROOT / "work/research-tooling/ghidra-projects/MHGU_1.4.0.gpr")]
    if name == "pax":
        env["LD_LIBRARY_PATH"] = str(TOOLS / "pax/runtime/usr/lib/x86_64-linux-gnu")
    elif name == "imhex":
        # ImHex requires mode 0700; the host runtime directory has mode 0710.
        runtime = state / "runtime"
        runtime.mkdir(mode=0o700, exist_ok=True)
        runtime.chmod(0o700)
        previous_runtime = env.get("XDG_RUNTIME_DIR")
        display = env.get("WAYLAND_DISPLAY")
        if previous_runtime and display and not os.path.isabs(display):
            env["WAYLAND_DISPLAY"] = str(Path(previous_runtime) / display)
        env["XDG_RUNTIME_DIR"] = str(runtime)
    elif name == "blender":
        env["BLENDER_USER_CONFIG"] = str(state / "config")
        env["BLENDER_USER_SCRIPTS"] = str(state / "scripts")
        env["BLENDER_USER_DATAFILES"] = str(state / "data")
        for variable in ("BLENDER_USER_CONFIG", "BLENDER_USER_SCRIPTS", "BLENDER_USER_DATAFILES"):
            Path(env[variable]).mkdir(parents=True, exist_ok=True)
    elif name in ("kuriimu", "kuriimu-cli"):
        package = TOOLS / ("kuriimu2-gui" if name == "kuriimu" else "kuriimu2-cli")
        env["DOTNET_ROOT"] = str(TOOLS / "dotnet31")
        env["DOTNET_SYSTEM_GLOBALIZATION_INVARIANT"] = "1"
        env["LD_LIBRARY_PATH"] = str(TOOLS / "dotnet31/compat/usr/lib/x86_64-linux-gnu")
        env.pop("DOTNET_ROLL_FORWARD", None)
        cwd = package  # The release discovers plugins relative to its cwd.
        # Kuriimu2 1.2.1 mistakes /mnt/<letter> paths for virtual Windows drives.
        temporary_alias = Path(tempfile.mkdtemp(prefix="mhgu-kuriimu-"))
        (temporary_alias / "workspace").symlink_to(ROOT, target_is_directory=True)
        print(f"Kuriimu workspace: {temporary_alias / 'workspace'}", flush=True)
        print("Open and save workspace files through this alias to avoid its /mnt path bug.", flush=True)
        rewritten = []
        for argument in args:
            if not argument.startswith("-") and Path(argument).exists():
                path = Path(argument).resolve()
                if path.is_relative_to(ROOT):
                    argument = str(temporary_alias / "workspace" / path.relative_to(ROOT))
            rewritten.append(argument)
        args = rewritten
        commands[name] = [str(package / "Kuriimu2")]
    elif name in ("nxaenc", "adpcm-encoder", "adpcm"):
        env["WINEPREFIX"] = str(TOOLS / "wine-ifrit")
        env["WINEDEBUG"] = "-all"
        env["WINEDLLOVERRIDES"] = "mscoree,mshtml="
        env["PATH"] = str(TOOLS / "bin") + os.pathsep + env.get("PATH", "")
        if name != "adpcm":
            executable = "NXAenc.exe" if name == "nxaenc" else "AdpcmEncoder.exe"
            commands[name] = ["wine", str(TOOLS / "ifrit-source" / executable)]
            rewritten = []
            for argument in args:
                if not argument.startswith("-") and (
                    Path(argument).exists() or "/" in argument or
                    Path(argument).suffix.lower() in (".wav", ".raw", ".opus", ".adpcm", ".aiff")
                ):
                    argument = "Z:" + str(Path(argument).absolute()).replace("/", "\\")
                rewritten.append(argument)
            args = rewritten
    if name not in commands:
        raise ValueError(f"Unknown tool: {name}")
    # Preserve relative paths given from the caller's directory.
    if cwd == ROOT:
        cwd = Path.cwd()
    try:
        return subprocess.call([*commands[name], *args], cwd=cwd, env=env)
    finally:
        if temporary_alias:
            shutil.rmtree(temporary_alias)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: scripts/tool.sh TOOL [arguments]")
        print("GUI: salad, pax, kuriimu, imhex, blender, audacity, gimp, titanbreak, quest, ghidra")
        print("CLI: salad, kuriimu-cli, gmd, revil, nxaenc, adpcm-encoder, adpcm, ffmpeg, ghidra-headless, research, dti-dumper, forge-rs")
        print("Resources: stqr, templates, model-plugins, dti-resources, forge-rs-resources")
        sys.exit(0)
    try:
        sys.exit(launch(sys.argv[1], sys.argv[2:]))
    except (OSError, ValueError) as error:
        print(f"Cannot launch tool: {error}", file=sys.stderr)
        sys.exit(1)
