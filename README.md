# NexgenAgent Auto - Negen fast lane

Make about 12 test video ads a week with Negen, finished in CapCut in the house edit, with Claude Code doing the
clicking, the briefs, the downloads and the CapCut setup. You choose the products, sign in, check names, and do the
final look in CapCut.

What you get for each video: a clean Negen video with voice-over, and a CapCut timeline that already has the
on-screen text in the house style, the brand logo, the end animation and the voice-over on its own track.

## What you need

- Windows or Mac.
- Claude Code: the Claude desktop app (Code tab) is easiest, because it has a built-in browser. The terminal
  version works too with the Claude in Chrome extension (`claude --chrome`).
- A Negen account (https://marketing-tool.nexgenbros.com).
- CapCut desktop (version 9.x), opened at least once, with any project made in it.
- Windows only: Git, Python and ffmpeg. If you don't have them, paste this into PowerShell, then close and reopen it:

```powershell
winget install Git.Git; winget install Python.Python.3.12; winget install Gyan.FFmpeg
```

## Install (once)

Windows, in PowerShell:

```powershell
git clone https://github.com/NexGen26-tool/NexgenAgent-Auto.git $HOME\NexgenAgent-Auto; cd $HOME\NexgenAgent-Auto; python setup_check.py
```

Mac, in Terminal:

```bash
git clone https://github.com/NexGen26-tool/NexgenAgent-Auto.git ~/NexgenAgent-Auto && cd ~/NexgenAgent-Auto && ./setup.sh
```

The setup check installs the one Python package it needs (Pillow) and checks Git, ffmpeg and CapCut. If it says a
font or animation is "not downloaded yet": open CapCut, open any project, add a text and pick each listed font once
(Montserrat, PT Sans, HV-Analogue-Bold-Italic); on any clip pick the in-animation "Zoom 1" and the out-animation
"Smoke" once. Run the check again until it says Setup OK.

It also tests whether your CapCut can take projects built by the tool. Some CapCut versions lock their project
files. If yours does, everything still works except the CapCut step: you get the clean videos plus a text sheet
with every line and its timing to type in by hand.

Or let Claude Code do it: open Claude Code anywhere and say
"Install https://github.com/NexGen26-tool/NexgenAgent-Auto into ~/NexgenAgent-Auto and run its setup".

## Use it every week

1. Open Claude Code in the `NexgenAgent-Auto` folder (desktop app: Code tab, pick the folder; terminal:
   `cd ~/NexgenAgent-Auto && claude --chrome`).
2. Sign in to Negen in the browser Claude uses (the built-in browser pane, or Chrome).
3. Type `/fastlane`. Claude asks what to name this week's outputs (the CapCut project and folders) and which
   products to test, then runs storyboards, writes the briefs, shows you the
   hooks for each group, launches the batches, downloads the better video of each, and builds the CapCut project.
4. When Claude asks, quit CapCut so the project can be written, then open CapCut and finish each timeline
   (check text fits, logo, voice-over).

Other commands: `/fastlane-status` (where the batches stand), `/fastlane-capcut` (rebuild the CapCut project).

## The rules Claude follows

- 12 videos a week = 2 Spry groups + 2 ETW groups. A group is one product, one angle, three videos that differ only
  in hook and delivery, so ad sets can be built per group.
- Batch names "<Mon DD> - <Product> <Angle> V1|V2|V3", never a person's or tool's name. Negen cannot rename or
  delete, so names are checked before Start.
- You sign in yourself. Nothing that costs money happens without asking. Grok credits and ChatGPT sign-ins are fixed
  by the admin.
- Only product facts from the Negen product page.

## If something stops

- Batches "Paused: Grok ... out of credits" or ChatGPT signed out: ask the admin; the batches continue by themselves.
- "CapCut is open": quit CapCut (Mac: Cmd+Q; Windows: close it and quit it from the tray) and ask Claude to run
  the build again.
- A text in CapCut looks like a different font: run the setup check, download the missing font in CapCut, rebuild.
- The CapCut build on Windows is new. Check the first timeline it makes carefully and report anything odd.

## What is in here

| Path | What |
|---|---|
| `CLAUDE.md` | The full procedure Claude follows |
| `.claude/commands/` | `/fastlane`, `/fastlane-status`, `/fastlane-capcut` |
| `.claude/skills/ad-brief-compiler/` | Writes the three Ad briefs per group from a storyboard |
| `chatgpt/ad-brief-compiler-v2.zip` | The same brief skill for ChatGPT, for people who write briefs there |
| `setup_check.py`, `setup.sh` | The setup check (Windows: `python setup_check.py`; Mac: `./setup.sh`) |
| `negen/` | Browser routines (fill a batch, status, export) and the download script |
| `capcut/` | The CapCut builder, the text-sheet fallback, the house-edit template and an empty project skeleton |
| `brand/` | ETW and Spry logos and per-store settings |
| `references/` | How Negen works, lessons, time per video, the camera rule |
| `work/` | Your weeks, one folder per week and output name (not uploaded to GitHub) |
