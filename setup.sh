#!/bin/bash
# Checks this Mac has what the fast lane needs and installs the one Python package it uses.
# Safe to run again any time. Run from the repo folder:  ./setup.sh
cd "$(dirname "$0")"
ok=0
say() { printf "%-34s %s\n" "$1" "$2"; }

[ "$(uname)" = "Darwin" ] && say "macOS" "ok" || { say "macOS" "NO - the CapCut step only works on a Mac"; ok=1; }

if command -v python3 >/dev/null; then say "python3" "ok"; else say "python3" "MISSING - install from python.org"; ok=1; fi
if python3 -c "import PIL" 2>/dev/null; then say "Pillow (Python)" "ok"
else
  python3 -m pip install --user --quiet Pillow && say "Pillow (Python)" "installed" || { say "Pillow (Python)" "FAILED - run: python3 -m pip install --user Pillow"; ok=1; }
fi
for t in afconvert afinfo sips curl unzip; do command -v $t >/dev/null && say "$t" "ok" || { say "$t" "MISSING"; ok=1; }; done

if [ -d "/Applications/CapCut.app" ]; then say "CapCut app" "ok"; else say "CapCut app" "MISSING - install CapCut for Mac"; ok=1; fi
DRAFTS="$HOME/Movies/CapCut/User Data/Projects/com.lveditor.draft"
if [ -f "$DRAFTS/root_meta_info.json" ]; then say "CapCut projects folder" "ok"
else say "CapCut projects folder" "NOT FOUND - open CapCut once and make any project"; ok=1; fi

EFF="$HOME/Library/Containers/com.lemon.lvoverseas/Data/Movies/CapCut/User Data/Cache/effect"
missing=""
check() { ls "$EFF/$1"/*/ >/dev/null 2>&1 && say "$2" "ok" || { say "$2" "not downloaded yet"; missing="$missing\n   - $2"; }; }
check 7542214368361057553 "Font: Montserrat"
check 7152810713856086529 "Font: PT Sans"
check 7462286539255500037 "Font: HV-Analogue-Bold-Italic"
check 7229983825080619522 "Animation: Smoke (out)"
check 6740868384637850120 "Animation: Zoom 1 (in)"
if [ -n "$missing" ]; then
  printf "\nCapCut has not downloaded these yet:$missing\nIn CapCut: open any project, add a text, pick each font once; on any clip pick the animation once.\nThen run ./setup.sh again. (Videos still build without them, CapCut just shows a stand-in font.)\n"
fi

mkdir -p work
echo
[ $ok -eq 0 ] && echo "Setup OK. Start Claude Code in this folder and type /fastlane" || echo "Fix the lines marked above, then run ./setup.sh again."
exit $ok
