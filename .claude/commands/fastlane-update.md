---
description: Update the tool to the latest version and check the computer again
---
Run `git pull` in this folder. If it refuses because files here were changed, do not discard or overwrite anything:
say which files and ask the person what to do. If it pulled new commits, summarize them in one or two plain
sentences (from `git log`), not as a list of commit messages. Then run the setup check (Windows
`python setup_check.py`, Mac `./setup.sh`) and report only what needs the person. If anything changed in this folder's
`.claude/` (commands, settings, skills), tell them to start a new session so the new version loads. $ARGUMENTS
