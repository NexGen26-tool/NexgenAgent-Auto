---
description: Build the CapCut project for downloaded fast-lane videos in the house edit
---
Do step 7 of CLAUDE.md for this week's folder in `work/` (or the folder named here: $ARGUMENTS): write
`capcut.json` from the briefs (project and media named after the week's output name in `week.json`; ask for it if missing) in `week.json` and the files in `videos/`, run the plan check
(`capcut/plan_sheet.py`, look at every frame, fix and repeat until clean), ask the person to quit CapCut, dry-run
`capcut/build_project.py`, then run it with `--save` (`--replace` when the project exists) and tell them which project
to open.
