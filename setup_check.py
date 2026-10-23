#!/usr/bin/env python3
"""Checks this computer (Mac or Windows) has what the workflow needs and installs the one Python package it uses.
Safe to run any time, from the repo folder:   Mac: python3 setup_check.py    Windows: python setup_check.py
"""
import glob, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
WINDOWS = os.name == "nt"
problems, notes = [], []


def say(what, status): print("%-34s %s" % (what, status))


say("System", "Windows" if WINDOWS else "Mac")
say("Python", sys.version.split()[0] + (" ok" if sys.version_info >= (3, 9) else " TOO OLD, need 3.9+"))
if sys.version_info < (3, 9): problems.append("python")

try:
    import PIL  # noqa: F401
    say("Pillow (Python)", "ok")
except ImportError:
    r = subprocess.run([sys.executable, "-m", "pip", "install", "--user", "--quiet", "Pillow"])
    say("Pillow (Python)", "installed" if r.returncode == 0 else "FAILED: run  " + sys.executable + " -m pip install --user Pillow")
    if r.returncode: problems.append("Pillow")

for tool, need, how in (("git", True, "Windows: winget install Git.Git   Mac: xcode-select --install"),
                        ("ffmpeg", WINDOWS, "Windows: winget install Gyan.FFmpeg  (then open a new terminal)   Mac: brew install ffmpeg")):
    found = shutil.which(tool)
    if found or not WINDOWS and tool == "ffmpeg" and shutil.which("afconvert"):
        say(tool, "ok" if found else "not needed on Mac (afconvert is used)")
    else:
        say(tool, "MISSING: " + how)
        if need: problems.append(tool)

sys.path.insert(0, os.path.join(ROOT, "capcut"))
sys.argv = [sys.argv[0]]
try:
    import build_project as bp
except SystemExit:
    raise
except Exception as e:  # Pillow just installed in this run, or a broken install
    say("CapCut builder", "could not load (%s); run this check again" % e)
    sys.exit(1)

if WINDOWS:
    app = glob.glob(os.environ.get("LOCALAPPDATA", "") + "/CapCut/Apps/*/CapCut.exe") or glob.glob(
        os.environ.get("LOCALAPPDATA", "") + "/CapCut/Apps/CapCut.exe")
else:
    app = glob.glob("/Applications/CapCut.app")
say("CapCut app", "ok" if app else "not found (install CapCut, or ignore if it lives elsewhere)")
if not os.path.isdir(bp.DRAFTS):
    say("CapCut projects folder", "NOT FOUND: open CapCut once and make any project")
    problems.append("CapCut projects")
else:
    say("CapCut projects folder", "ok")
    name, msg = bp.draft_format()
    say("CapCut can take built projects", "yes (" + name + ")" if name else "NO")
    if not name: notes.append(msg)

missing = [label for key, label in bp.NEEDED.items() if not glob.glob(bp.EFFECTS + "/" + key + "/*")]
for key, label in bp.NEEDED.items():
    say(label, "not downloaded yet" if label in missing else "ok")
if missing:
    notes.append("In CapCut: open any project, add a text and pick each missing font once; on any clip pick the "
                 "missing animations once. Then run this check again. (Projects still build without them; CapCut "
                 "just shows a stand-in font.)")

os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
print()
for n in notes: print("NOTE:", n, "\n")
print("Setup OK. Open Claude Code in this folder and type /fastlane" if not problems
      else "Fix these, then run the check again: " + ", ".join(problems))
sys.exit(1 if problems else 0)
