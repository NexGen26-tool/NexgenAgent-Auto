#!/usr/bin/env python3
"""Plan check: look at what the CapCut timelines will actually show, before saving (CLAUDE.md step 7).

  python capcut/plan_sheet.py work/<week>/capcut.json

For each timeline it prints the sentence lengths of the voice-over (CHECK = a sentence plays too fast or too slow for
its words, usually because the voice ran two sentences together: give "ends" in the edit plan), and it prints the
clean stretches of every video (what shots.json leaves after the bad ones). Then it makes one sheet per group in
work/<week>/plan/: every frame each timeline will use, every 0.6 s, labelled with the video and second. Look at every
frame (hands and feet above all); anything bad goes into shots.json and the shot is replaced, then run this again.
"""
import json, os, re, subprocess, sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_project as bp  # noqa: E402

STEP = 0.6          # seconds between frames on the sheet
COLS = 14           # frames per line
WIDTH = 150         # frame width on the sheet
RATE = (0.6, 1.5)   # a sentence's pace (letters a second) against the voice's median; outside = CHECK (Oct 28 errors: ~3x)


def clean_stretches(entry, dur):
    """[start, end] stretches of a video that no bad stretch touches."""
    bad = sorted((max(0.0, b[0]), min(dur, b[1])) for b in entry.get("bad", []))
    out, at = [], 0.0
    for a, b in bad:
        if a > at + 0.3: out.append((round(at, 1), round(a, 1)))
        at = max(at, b)
    if dur > at + 0.3: out.append((round(at, 1), round(dur, 1)))
    return out


def frame(path, t, out):
    subprocess.run([bp.find_ffmpeg() or "ffmpeg", "-v", "error", "-y", "-ss", "%.2f" % t, "-i", path, "-frames:v", "1",
                    "-vf", "scale=%d:-1" % WIDTH, out])
    return Image.open(out).copy()


def main():
    if len(sys.argv) < 2: raise SystemExit(__doc__)
    cfg_path = os.path.abspath(sys.argv[1]); week = os.path.dirname(cfg_path)
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    shots_path = os.path.join(week, "shots.json")
    shots = json.load(open(shots_path, encoding="utf-8")) if os.path.exists(shots_path) else {}
    out_dir = os.path.join(week, "plan"); os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_frame.jpg")

    print("Clean stretches (what shots.json leaves):")
    for name, entry in sorted(shots.items()):
        folder = os.path.join(week, "videos", "spare" if " - spare" in name else "")
        f = os.path.join(folder, name)
        if os.path.exists(f):
            print("  %-60s %s%s" % (name[-60:], clean_stretches(entry, bp.mp4_info(f)[0]),
                                    "" if entry.get("checked") else "   (NOT CHECKED)"))

    groups = {}
    for t in cfg["timelines"]:
        video = os.path.expanduser(t["video"]); ed = t.get("edit") or {}
        vo = bp.extract_vo(video, out_dir)
        spans = bp.speech_spans(vo, bp.mp4_info(vo)[0])
        total = sum(b - a for a, b in spans) / bp.VO_SPEED + bp.CTA_HOLD
        times = ed.get("times") or (bp.vo_times(t["vo"], spans, total, vo, ed.get("ends")) if t.get("vo") else None)
        print("\n" + t["name"])
        if not times or "starts" not in times:
            print("  CHECK: no sentence starts (give \"ends\" or \"times\" in the edit plan)"); continue
        st = times["starts"] + [total - bp.CTA_HOLD]
        sentences = [s for s in re.split(r"(?<=[.?!])\s+", t["vo"].strip()) if s]
        rates = [len(re.sub(r"[^A-Za-z0-9]", "", s)) / max(st[i + 1] - st[i], 0.01) for i, s in enumerate(sentences)]
        median = sorted(rates[:-1])[len(rates[:-1]) // 2]
        for i, s in enumerate(sentences):
            ok = RATE[0] <= rates[i] / median <= RATE[1] or i == len(sentences) - 1  # the last one holds the CTA
            print("  s%d %5.2f s %4.1f letters/s  %s%s" % (i + 1, st[i + 1] - st[i], rates[i], s[:60], "" if ok else "   CHECK"))
        at = lambda x: x if not isinstance(x, str) else st[int(x[1]) - 1] + (float(x[3:]) if "+" in x else 0.0)
        cuts = [[at(c[0])] + list(c[1:]) for c in ed.get("cuts", [])]
        if not cuts:
            print("  no edit plan cuts: the footage plays as generated"); continue
        pieces, _ = bp.cuts_to_pieces(cuts, total, os.path.dirname(video), shots)
        frames = []
        for f, a, length, shown in pieces:
            bad = [b for b in shots.get(os.path.basename(f), {}).get("bad", []) if a < b[1] and b[0] < a + length]
            if bad: print("  BAD STRETCH USED: %s %.1f-%.1f s (%s)" % (os.path.basename(f), a, a + length, bad[0][2]))
            k = 0.0
            while k < length - 0.05:
                label = "%s %.1f" % (os.path.basename(f).rsplit(" - ", 2)[-2][-11:] + (" sp" if " - spare" in f else ""), a + k)
                frames.append((label, frame(f, a + k, tmp)))
                k += STEP
        groups.setdefault(t.get("group", "timelines"), []).append((t["name"].split(" - ")[-1], frames))

    for gname, rows in groups.items():
        w, h = rows[0][1][0][1].size
        lines = [(name if i == 0 else "", frames[i:i + COLS]) for name, frames in rows for i in range(0, len(frames), COLS)]
        sheet = Image.new("RGB", (COLS * w, len(lines) * (h + 26)), "white"); d = ImageDraw.Draw(sheet)
        for ri, (name, frames) in enumerate(lines):
            y = ri * (h + 26); d.text((2, y), name, fill="red")
            for ci, (label, im) in enumerate(frames):
                sheet.paste(im, (ci * w, y + 12)); d.text((ci * w + 2, y + 12 + h), label, fill="black")
        out = os.path.join(out_dir, re.sub(r"[^\w-]+", "_", gname) + ".jpg"); sheet.save(out)
        print("\nsheet:", out)
    if os.path.exists(tmp): os.remove(tmp)


if __name__ == "__main__":
    main()
