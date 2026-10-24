#!/usr/bin/env python3
"""Contact sheets for the shot check: one frame every 0.5 s of every downloaded video (and its spare), with the
time under each frame, plus the hard cuts. Claude looks at each sheet and writes the bad stretches into shots.json;
the CapCut build then replaces them with clean footage from the spare or from the other videos of the same group.

  python capcut/shot_sheet.py work/<week>          ->  work/<week>/shots/<video>.jpg  and  work/<week>/shots.json

shots.json: {"<video file name>": {"cuts": [2.25, 5.21], "bad": [[start, end, "why"], ...], "checked": false}}
Running it again keeps the "bad" lists already written.
"""
import glob, json, os, re, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_project import find_ffmpeg, mp4_info  # noqa: E402

STEP, THUMB_W, PER_ROW = 0.5, 180, 8


def cuts(ffmpeg, path):
    out = subprocess.run([ffmpeg, "-hide_banner", "-i", path, "-vf", "scdet=threshold=8:sc_pass=1", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return [round(float(t), 2) for t in re.findall(r"lavfi\.scd\.time: ([\d.]+)", out)]


def sheet(ffmpeg, path, dst, cut_times):
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
    img = Image.new("RGB", (PER_ROW * THUMB_W, rows * (th + lab)), "white"); dr = ImageDraw.Draw(img)
    for i, (t, im) in enumerate(zip(times, thumbs)):
        x, y = (i % PER_ROW) * THUMB_W, (i // PER_ROW) * (th + lab)
        img.paste(im, (x, y))
        cut = any(t - STEP / 2 <= c < t + STEP / 2 for c in cut_times)
        dr.rectangle([x, y + th, x + THUMB_W - 1, y + th + lab - 1], fill="#ffd400" if cut else "white")
        dr.text((x + 6, y + th + 4), "%.1f s%s" % (t, "  CUT" if cut else ""), fill="black")
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
        dst = os.path.join(out_dir, os.path.splitext(name)[0] + ".jpg")
        sheet(ffmpeg, v, dst, c)
        print("%-60s cuts %s  ->  %s" % (name[:60], c, dst))
    json.dump(data, open(jpath, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("saved:", jpath)


if __name__ == "__main__":
    main()
