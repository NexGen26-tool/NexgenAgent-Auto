"""The footage catalogue: every shot of every take of one product, so a timeline replaces a bad shot from the takes
already made before anything is generated again (owner, Nov 18: same SKU, a room that does not change much,
close-ups first; remake only what nothing covers).

  python capcut/inventory.py work/<week> <SKU>

Takes: videos/*<SKU>*.mp4, videos/spare/*<SKU>*.mp4 and videos/pool/*<SKU>*.mp4 (first takes and other generations,
copied there with a unique name such as "... - firsttake.mp4"). Each take is split at its cuts (ffmpeg scene change)
and at the crossfades of shots.json; every shot becomes one row of work/<week>/catalog/<SKU>-<n>.jpg (first, middle,
last frame) and one entry in work/<week>/catalog.json:
  {"<file>": {"shots": [{"id": "D12", "a": 3.3, "b": 5.2}, ...]}}
A reviewer then adds to every shot, judged against references/fundamentals.md and the product photo:
  "pass": true|false, "why": "...", "size": "close|medium|wide", "room": "R1" (rooms lettered per product: the same
  letter = a room a viewer would take for the same room), "person": "P1"|null (the same id = the same person),
  "shows": "a few words"
The build then fills and replaces only from passed shots, and from another take only when the shot is a close-up or
in a room of the timeline's own ("rooms" on the timeline) with no person or its own actor ("actor").
"""
import glob, io, json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
FW, FH, PER = 240, 427, 14  # frame size on the sheet, shots per sheet page


def ffmpeg():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from build_project import find_ffmpeg
    return find_ffmpeg()


def duration(ff, f):
    err = subprocess.run([ff, "-i", f], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0.0


def cuts(ff, f, thr=0.18):
    err = subprocess.run([ff, "-i", f, "-vf", "select='gt(scene,%.2f)',showinfo" % thr, "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return [float(x) for x in re.findall(r"pts_time:([\d.]+)", err)]


def frame(ff, f, t):
    out = subprocess.run([ff, "-v", "error", "-ss", "%.2f" % max(0.0, t), "-i", f, "-frames:v", "1", "-vf",
                          "scale=%d:%d" % (FW, FH), "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    return Image.open(io.BytesIO(out)).convert("RGB") if out else Image.new("RGB", (FW, FH), (90, 90, 90))


def font(px):
    for p in ("C:/Windows/Fonts/arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"):
        if os.path.exists(p): return ImageFont.truetype(p, px)
    return ImageFont.load_default()


def main(wk, sku):
    ff = ffmpeg(); V = os.path.join(wk, "videos")
    files = sorted(set(glob.glob(os.path.join(V, "*%s*.mp4" % sku)) + glob.glob(os.path.join(V, "spare", "*%s*.mp4" % sku))
                       + glob.glob(os.path.join(V, "pool", "*%s*.mp4" % sku))))
    shots = json.load(open(os.path.join(wk, "shots.json"), encoding="utf-8")) if os.path.exists(os.path.join(wk, "shots.json")) else {}
    cp = os.path.join(wk, "catalog.json"); cat = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {}
    rows = []; tag = sku[:1].upper() if sku else "S"
    n = max([0] + [int(re.sub(r"\D", "", x["id"]) or 0) for f0, e0 in cat.items() if sku in f0 for x in e0.get("shots", [])])  # ids stay unique
    for f in files:
        b = os.path.basename(f); dur = duration(ff, f)
        if cat.get(b, {}).get("shots"):
            rows += [(f, s) for s in cat[b]["shots"]]; n = max([n] + [int(re.sub(r"\D", "", s["id"]) or 0) for s in cat[b]["shots"]]); continue
        fades = (shots.get(b) or {}).get("fades", [])
        edges = sorted(set([0.0] + [round(c, 2) for c in cuts(ff, f)] + [dur]))
        segs = []
        for a, z in zip(edges, edges[1:]):
            for fa, fb in fades:  # a crossfade is not a shot: the shots end and start around it
                if fa < z and a < fb:
                    if fa - a >= 0.4: segs.append((a, fa))
                    a = max(a, fb)
            if z - a >= 0.4: segs.append((a, z))
        cat[b] = {"shots": []}
        split = []
        for a, z in segs:  # a long stretch with no cut found is judged in pieces of about 2.5 s, so nothing hides in it
            k = max(1, int(round((z - a) / 2.5))) if z - a > 5.0 else 1
            split += [(a + (z - a) * i / k, a + (z - a) * (i + 1) / k) for i in range(k)]
        for a, z in split:
            n += 1; s = {"id": "%s%d" % (tag, n), "a": round(a, 2), "b": round(z, 2)}; cat[b]["shots"].append(s); rows.append((f, s))
    json.dump(cat, open(cp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.makedirs(os.path.join(wk, "catalog"), exist_ok=True)
    for page in range(0, len(rows), PER):
        chunk = rows[page:page + PER]; sheet = Image.new("RGB", (FW * 3, len(chunk) * (FH + 26)), "white"); d = ImageDraw.Draw(sheet)
        for i, (f, s) in enumerate(chunk):
            y = i * (FH + 26); a, z = s["a"], s["b"]
            d.text((4, y + 3), "%s   %s   %.2f-%.2f s" % (s["id"], os.path.basename(f).split(" - ", 2)[-1][-58:], a, z), fill=(0, 0, 0), font=font(15))
            for k, t in enumerate((a + 0.05, (a + z) / 2, max(a + 0.05, z - 0.08))): sheet.paste(frame(ff, f, t), (k * FW, y + 26))
        p = os.path.join(wk, "catalog", "%s-%d.jpg" % (sku, page // PER + 1)); sheet.save(p, quality=82); print("sheet", p, len(chunk), "shots")
    print(len(rows), "shots of", len(files), "takes for", sku)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
