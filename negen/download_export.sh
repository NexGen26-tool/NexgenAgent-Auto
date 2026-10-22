#!/bin/bash
# Download a Negen share link (it builds in the background, so this waits for it) and keep the better video.
#   negen/download_export.sh <share link> <output.mp4>
# The better video = highest AI score + product match in the ZIP's manifest; a tie goes to PART A.
set -e
URL="$1"; OUT="$2"
[ -z "$URL" ] || [ -z "$OUT" ] && { echo "usage: $0 <share link> <output.mp4>"; exit 1; }
TMP=$(mktemp -d)
for i in $(seq 1 40); do
  INFO=$(curl -s -L -o "$TMP/export.zip" -w "%{content_type}" "$URL")
  case "$INFO" in *zip*|*octet*) break;; esac
  sleep 15
done
case "$INFO" in *zip*|*octet*) ;; *) echo "The ZIP was not ready after 10 minutes. Try again later."; exit 1;; esac
mkdir -p "$TMP/unz" && unzip -q "$TMP/export.zip" -d "$TMP/unz"
python3 -I - "$TMP/unz" "$OUT" <<'PY'
import csv, os, shutil, sys
unz, out = sys.argv[1:]
rows = list(csv.DictReader(open(os.path.join(unz, "manifest.csv"), encoding="utf-8")))
if not rows: sys.exit("No finished videos in this export.")
def score(r): return (int(r["ai_score"] or 0) + int(r["product_match"] or 0), "part-a" in r["file_path"])
best = max(rows, key=score)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
shutil.copy(os.path.join(unz, best["file_path"]), out)
for r in rows:
    print(("PICKED " if r is best else "       ") + "%s  AI %s  match %s" % (r["shot"].split(" ")[0] + " " + r["shot"].split(" ")[1], r["ai_score"], r["product_match"]))
print("saved:", out)
PY
rm -rf "$TMP"
