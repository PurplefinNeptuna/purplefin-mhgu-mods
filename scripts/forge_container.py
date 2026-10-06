"""Pinned container command shared by maintained native Forge builds."""
import os
from pathlib import Path
from mhgu_binary import IMAGE as BASE_IMAGE
ROOT = Path(__file__).resolve().parents[1]
def podman():
    return ["podman", "--root", str(ROOT / "tools/forge-container/storage"),
            "--runroot", f"/tmp/mhgu-forge-container-{os.getuid()}", "--storage-driver", "vfs"]
