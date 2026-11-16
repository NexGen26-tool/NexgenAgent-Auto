#!/usr/bin/env python3
"""Contact sheets for the shot check: one frame every 0.5 s of every downloaded video (and its spare), with the
time under each frame, plus the hard cuts (yellow) and Negen's crossfades (orange), which it finds itself. Claude
looks at each sheet and writes the bad stretches and where the video's person is on screen into shots.json; the CapCut
build then keeps every cut out of them and replaces them with clean footage from the spare or the group's other videos.
Each sheet is headed by the week's product photo for that video's SKU (work/<week>/product-photos/, else
work/product-photos/), so drift shows against the real outline; with no photo the sheet starts at the frames.

  python capcut/shot_sheet.py work/<week>          ->  work/<week>/shots/<video>.jpg  and  work/<week>/shots.json

shots.json: {"<video file name>": {"cuts": [2.25, 5.21], "fades": [[3.3, 4.5], ...], "bad": [[start, end, "why"], ...],
             "person": [[start, end], ...], "checked": false}}
"fades" is written by this script; "bad" and "person" by Claude at the shot check (CLAUDE.md step 6b). "person" is
where the video's own person is on screen: another variant of the group may borrow this video's footage only outside
it, so one timeline never shows two different people. Running it again keeps "bad" and "person".
"""
import glob, json, os, re, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_project import find_ffmpeg, mp4_info  # noqa: E402

STEP, THUMB_W, PER_ROW = 0.5, 180, 8
FPS, FW, FH, D = 10, 72, 128, 2  # crossfade search: 10 frames a second, small grey frames, compared 0.2 s apart


def fades(ffmpeg, path):
    """Negen's scene changes are crossfades of 0.8-1.0 s. In a crossfade a frame is the mix of the frames before and
    after it; ordinary motion is not. Returns [[start, end], ...] of every crossfade, rounded to 0.1 s."""
    from PIL import Image, ImageChops, ImageStat
    raw = subprocess.run([ffmpeg, "-v", "error", "-i", path, "-vf", "fps=%d,scale=%d:%d,format=gray" % (FPS, FW, FH),
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    n = FW * FH; fr = [Image.frombytes("L", (FW, FH), raw[i:i + n]) for i in range(0, len(raw) - n + 1, n)]
    mean = lambda im: ImageStat.Stat(im).mean[0]; hits = []
    for t in range(D, len(fr) - D):
        a, b, c = fr[t - D], fr[t], fr[t + D]
        den = mean(ImageChops.difference(a, c))
        if den > 6 and mean(ImageChops.difference(b, Image.blend(a, c, 0.5))) / den < 0.22: hits.append(t / FPS)
    out = []
    for t in hits:
        if out and t - out[-1][1] <= 0.15: out[-1][1] = t
        else: out.append([t, t])
    return [[round(max(0.0, a - D / FPS), 1), round(b + D / FPS, 1)] for a, b in out if b - a >= 0.1]


def cuts(ffmpeg, path):
    out = subprocess.run([ffmpeg, "-hide_banner", "-i", path, "-vf", "scdet=threshold=8:sc_pass=1", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return [round(float(t), 2) for t in re.findall(r"lavfi\.scd\.time: ([\d.]+)", out)]


def product_photo(week, video):
    """The week's product photo for this video's product: the SKU from the codified name (" - <SKU> - "), matched in
    work/<week>/product-photos/ first, then work/product-photos/ (as cut_sheet.py does). None when there is none."""
    m = re.search(r" - ([A-Z][A-Z0-9]{5,}) - ", os.path.basename(video))
    if not m: return None
    sku = re.compile(r"(?<![A-Z0-9])%s(?![A-Z0-9])" % m.group(1))
    for d in (os.path.join(week, "product-photos"), os.path.join(os.path.dirname(os.path.abspath(week)), "product-photos")):
        for p in sorted(glob.glob(os.path.join(d, "*"))):
            if p.lower().endswith((".jpg", ".jpeg", ".png", ".webp")) and sku.search(os.path.basename(p)): return p
    return None


def sheet(ffmpeg, path, dst, cut_times, fade_times=(), photo=None):
    from PIL import Image, ImageDraw
    dur = mp4_info(path)[0]
    times = [round(i * STEP + STEP / 2, 2) for i in range(int(dur / STEP))]
    tmp = tempfile.mkdtemp()
    thumbs = []
    for i, t in enumerate(times):
        f = os.path.join(tmp, "%03d.jpg" % i)
        subprocess.run([ffmpeg, "-v", "error", "-y", "-ss", str(t), "-i", path, "-frames:v", "1",
                        "-vf", "scale=%d:-2" % THUMB_W, f], check=True)
        thumbs.append(Image.open(f).convert("RGB"))
    th = thumbs[0].height; lab = 22; rows = (len(thumbs) + PER_ROW - 1) // PER_ROW
    ph = None
    if photo:  # the product photo heads the sheet: every frame below is judged against its outline
        ph = Image.open(photo).convert("RGB"); ph.thumbnail((THUMB_W * 3, th))
    top = ph.height + lab if ph else 0
    img = Image.new("RGB", (PER_ROW * THUMB_W, top + rows * (th + lab)), "white"); dr = ImageDraw.Draw(img)
    if ph:
        img.paste(ph, (0, 0)); px = ph.width + 12; ph.close()
        dr.text((px, 10), "PRODUCT PHOTO: every frame below must match this outline", fill="#c00000")
        dr.text((px, 28), os.path.basename(photo), fill="black")
    for i, (t, im) in enumerate(zip(times, thumbs)):
        x, y = (i % PER_ROW) * THUMB_W, top + (i // PER_ROW) * (th + lab)
        img.paste(im, (x, y))
        cut = any(t - STEP / 2 <= c < t + STEP / 2 for c in cut_times)
        fade = any(a <= t <= b for a, b in fade_times)
        dr.rectangle([x, y + th, x + THUMB_W - 1, y + th + lab - 1], fill="#ffd400" if cut else "#ff9a3c" if fade else "white")
        dr.text((x + 6, y + th + 4), "%.1f s%s" % (t, "  CUT" if cut else "  FADE" if fade else ""), fill="black")
        dr.line([x + THUMB_W - 1, y, x + THUMB_W - 1, y + th + lab], fill="white", width=2)
    img.save(dst, quality=88)
    for im in thumbs: im.close()


def main():
    if len(sys.argv) != 2: sys.exit(__doc__)
    week = sys.argv[1].rstrip("/\\")
    ffmpeg = find_ffmpeg()
    if not ffmpeg: sys.exit("ffmpeg is missing: run setup_check.py and install it.")
    videos = sorted(glob.glob(os.path.join(week, "videos", "*.mp4")) + glob.glob(os.path.join(week, "videos", "spare", "*.mp4")))
    out_dir = os.path.join(week, "shots"); os.makedirs(out_dir, exist_ok=True)
    jpath = os.path.join(week, "shots.json")
    data = json.load(open(jpath, encoding="utf-8")) if os.path.exists(jpath) else {}
    for v in videos:
        name = os.path.basename(v)
        c = cuts(ffmpeg, v)
        entry = data.setdefault(name, {"bad": [], "checked": False}); entry["cuts"] = c
        entry["fades"] = fades(ffmpeg, v)
        dst = os.path.join(out_dir, os.path.splitext(name)[0] + ".jpg")
        photo = product_photo(week, v)
        sheet(ffmpeg, v, dst, c, entry["fades"], photo)
        print("%-60s cuts %s fades %d%s  ->  %s" % (name[:60], c, len(entry["fades"]), "" if photo else "  (no product photo)", dst))
    json.dump(data, open(jpath, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("saved:", jpath)


if __name__ == "__main__":
    main()
