#!/usr/bin/env python3
"""Download a Negen share link and keep the better of the batch's two videos (Mac and Windows).

  python negen/download_export.py "<share link>" "work/<week>/videos/01_ETW_WallArt_FocalWall_V1.mp4"

The ZIP builds in the background, so this waits up to 10 minutes for it. The better video = highest AI score +
product match in the ZIP's manifest.csv; a tie goes to PART A. The other video is kept as spare footage in
videos/spare/<name> - spare.mp4 (capcut/shots.py and the CapCut build use it to replace bad shots).
"""
import csv, http.client, io, os, shutil, sys, tempfile, time, urllib.request, zipfile


def fetch(url):
    """Stream the ZIP to a temp file; wait while it is still building, retry when a download breaks off."""
    tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False); tmp.close()
    for _ in range(40):
        try:
            with urllib.request.urlopen(url, timeout=120) as r, open(tmp.name, "wb") as out:
                shutil.copyfileobj(r, out, 1 << 20)
            if zipfile.is_zipfile(tmp.name):
                return tmp.name
        except (OSError, http.client.HTTPException):
            pass
        time.sleep(15)
    sys.exit("The ZIP was not ready (or kept breaking off) for 10 minutes. Try again later.")


def main():
    if len(sys.argv) != 3: sys.exit(__doc__)
    url, out = sys.argv[1:]
    path = fetch(url); z = zipfile.ZipFile(path)
    rows = list(csv.DictReader(io.TextIOWrapper(z.open("manifest.csv"), encoding="utf-8")))
    if not rows: sys.exit("No finished videos in this export.")
    score = lambda r: (float(r["ai_score"] or 0) + float(r["product_match"] or 0), "part-a" in r["file_path"])
    best = max(rows, key=score)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with z.open(best["file_path"]) as src, open(out, "wb") as dst:
        dst.write(src.read())
    # the other video of the batch is kept as spare footage: the CapCut build swaps bad shots for good ones from it
    spare_dir = os.path.join(os.path.dirname(os.path.abspath(out)), "spare")
    stem = os.path.splitext(os.path.basename(out))[0]
    for r in rows:
        part = " ".join(r["shot"].split(" ")[:2])
        print(("PICKED " if r is best else "       ") + "%s  AI %s  match %s" % (part, r["ai_score"], r["product_match"]))
        if r is not best:
            os.makedirs(spare_dir, exist_ok=True)
            with z.open(r["file_path"]) as src, open(os.path.join(spare_dir, stem + " - spare.mp4"), "wb") as dst:
                dst.write(src.read())
    z.close(); os.remove(path)
    print("saved:", out)


if __name__ == "__main__":
    main()
