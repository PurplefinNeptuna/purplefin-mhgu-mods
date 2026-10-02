#!/usr/bin/env python3
"""Small desktop launcher with streamed startup output."""
from pathlib import Path
import queue
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

ROOT = Path(__file__).resolve().parent.parent
CHOICES = {
    "SaladSoftware — ARC extraction and repacking": "salad",
    "Pax Arc Explorer — ARC browsing and texture preview": "pax",
    "Kuriimu2 — ARC and texture editing": "kuriimu",
    "ImHex — binary editing": "imhex",
    "Blender — models": "blender",
    "GIMP — textures": "gimp",
    "Audacity — audio": "audacity",
    "Titanbreak — monster data": "titanbreak",
    "MHGUQuestEditor — quest data": "quest",
    "STQR editor — audio metadata in browser": "stqr",
    "010 Editor templates — open folder": "templates",
    "MHGU model plugins — open folder": "model-plugins",
}
events = queue.Queue()
window = tk.Tk()
window.title("MHGU Modding Tools")
window.geometry("850x510")
frame = ttk.Frame(window, padding=14)
frame.pack(fill="both", expand=True)
ttk.Label(frame, text="Monster Hunter Generations Ultimate — Modding Tools", font=("sans", 14)).pack(anchor="w")
ttk.Label(frame, text="Edit copies in work/. CLI commands and compatibility notes are in docs/TOOLS.md.").pack(anchor="w", pady=(6, 14))
selection = tk.StringVar(value=next(iter(CHOICES)))
ttk.Combobox(frame, textvariable=selection, values=list(CHOICES), state="readonly", width=76).pack(fill="x")
log = ScrolledText(frame, wrap="word", height=19)


def start():
    name = CHOICES[selection.get()]
    events.put(f"Starting {name}...\n")

    def worker():
        try:
            directory = ROOT / "tools/state/launcher"
            directory.mkdir(parents=True, exist_ok=True)
            logfile = directory / f"{name}-{time.time_ns()}.log"
            # A persistent file keeps child output safe if the toolbox closes.
            with logfile.open("w") as output:
                process = subprocess.Popen(
                    ["/usr/bin/python", str(ROOT / "scripts/tool.py"), name],
                    cwd=ROOT, stdout=output, stderr=subprocess.STDOUT,
                )
                with logfile.open() as reader:
                    while True:
                        for line in reader:
                            events.put(f"[{name}] {line}")
                        if process.poll() is not None:
                            for line in reader:
                                events.put(f"[{name}] {line}")
                            break
                        time.sleep(0.1)
                events.put(f"[{name}] Exited with code {process.wait()}.\n")
        except OSError as error:
            events.put(f"[{name}] {error}\n")
    threading.Thread(target=worker, daemon=True).start()


ttk.Button(frame, text="Launch selected tool", command=start).pack(anchor="w", pady=10)
log.pack(fill="both", expand=True)


def poll():
    while True:
        try:
            line = events.get_nowait()
        except queue.Empty:
            break
        log.insert("end", line)
        if int(log.index("end-1c").split(".")[0]) > 2000:
            log.delete("1.0", "500.0")
        log.see("end")
    window.after(100, poll)


window.after(100, poll)
window.mainloop()
