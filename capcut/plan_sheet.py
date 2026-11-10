#!/usr/bin/env python3
"""Plan check: look at what the CapCut timelines will actually show, before saving (CLAUDE.md step 7).

  python capcut/plan_sheet.py work/<week>/capcut.json

For each timeline it prints the sentence lengths of the voice-over (CHECK = a sentence plays too fast or too slow for
its words, usually because the voice ran two sentences together: give "ends" in the edit plan), and it prints the
clean stretches of every video (what shots.json leaves after the bad ones). Then it makes one sheet per group in
work/<week>/plan/: every frame each timeline will use, every 0.6 s, labelled with the video and second. Look at every
frame (hands and feet above all); anything bad goes into shots.json and the shot is replaced, then run this again.
"""
import glob, json, os, re, subprocess, sys

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
    bad = sorted((max(0.0, b[0]), min(dur, b[1])) for b in bp.blocked("", {"": entry}))
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

    # on-screen lines must not repeat the last weeks' wording (owner, Nov 7): the same line or the same 3-word run
    def words(x): return re.findall(r"[a-z0-9']+", (" ".join(x) if isinstance(x, list) else str(x or "")).lower())
    def runs(w): return {" ".join(w[i:i + 3]) for i in range(len(w) - 2)}
    past = {}
    for f in sorted(glob.glob(os.path.join(os.path.dirname(week), "*", "capcut.json")), reverse=True):
        if os.path.abspath(os.path.dirname(f)) == os.path.abspath(week): continue
        try: old = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError): continue
        for o in old.get("timelines", []):
            for k in ("line1", "line2", "line3", "line4", "line5"):
                for r in runs(words(o.get(k))): past.setdefault(r, os.path.basename(os.path.dirname(f)))
        if len({v for v in past.values()}) >= 3: break  # the last three weeks
    seen = set()
    for t in cfg["timelines"]:
        for k in ("line1", "line2", "line3", "line4", "line5"):
            hit = sorted(r for r in runs(words(t.get(k))) if r in past)
            if hit and (k, hit[0]) not in seen:
                seen.add((k, hit[0]))
                print("REPEAT: %s %s \"%s\" was used in %s: write it new" % (t["name"][-24:], k, hit[0], past[hit[0]]))
    # inside the week, no two ads share an argument or a line (owner, Nov 10: Meta groups look-alike ads and shows
    # fewer of them). A group is one ad set: explore = three formats that share nothing but the offer and CTA,
    # iterate = one body with three hooks (only the first sentence and Line 1 differ). Between groups nothing is shared.
    def sents(t): return [x for x in re.split(r"(?<=[.?!])\s+", (t.get("vo") or "").strip()) if x]
    def run4(text):
        w = words(text); return {" ".join(w[i:i + 4]) for i in range(len(w) - 3)}
    def body(t): return run4(" ".join(sents(t)[:-2]))  # before the offer and the CTA
    def hook(t): return run4(" ".join(sents(t)[:1]))
    def lines(t, ks=("line1", "line2", "line3", "line4")): return set().union(*(runs(words(t.get(k))) for k in ks))
    tl = cfg["timelines"]
    for i in range(len(tl)):
        for j in range(i + 1, len(tl)):
            a, b = tl[i], tl[j]; na, nb = a["name"][-24:], b["name"][-24:]
            same_group = a.get("group") and a.get("group") == b.get("group")
            if same_group and a.get("mode") == "iterate":
                vo, ln = sorted(hook(a) & hook(b)), sorted(lines(a, ("line1",)) & lines(b, ("line1",)))
                what = "hook"
            else:
                vo, ln = sorted(body(a) & body(b)), sorted(lines(a) & lines(b))
                what = "voice-over"
                if same_group and a.get("format") and a.get("format") == b.get("format"):
                    print("SAME: %s and %s are both format %s in an explore group: give one another format" % (na, nb, a["format"]))
            if vo: print("SAME: %s and %s share the %s \"%s\": write one of them new" % (na, nb, what, vo[0]))
            if ln: print("SAME: %s and %s share the line words \"%s\": write one of them new" % (na, nb, ln[0]))
    uses = {}  # a format may run twice a week at most; an iterate group counts once
    for t in tl:
        key = (t.get("group"), t.get("format")) if t.get("mode") == "iterate" else (t["name"], t.get("format"))
        if t.get("format"): uses.setdefault(t["format"], set()).add(key)
    for f, k in sorted(uses.items()):
        if len(k) > 2: print("SAME: format %s runs %d times this week (at most 2)" % (f, len(k)))
    for t in tl:
        if t.get("mode") not in ("explore", "iterate"): print("CHECK: %s has no \"mode\" (explore or iterate)" % t["name"][-24:])
        if not t.get("format"): print("CHECK: %s has no \"format\" (ad-brief-compiler, Formats)" % t["name"][-24:])
        elif t["format"] not in bp.FORMATS: print("CHECK: %s format \"%s\" is not in capcut/templates/formats.json" % (t["name"][-24:], t["format"]))
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
        times = ed.get("times") or (bp.vo_times(t["vo"], spans, total, vo, ed.get("ends"), bp.line_map(t)) if t.get("vo") else None)
        print("\n" + t["name"])
        if not times or "starts" not in times:
            print("  CHECK: no sentence starts (give \"ends\" or \"times\" in the edit plan)"); continue
        st = times["starts"] + [total - bp.CTA_HOLD]
        sentences = [s for s in re.split(r"(?<=[.?!])\s+", t["vo"].strip()) if s]
        rates = [len(re.sub(r"[^A-Za-z0-9]", "", s)) / max(st[i + 1] - st[i], 0.01) for i, s in enumerate(sentences)]
        median = sorted(rates[:-1])[len(rates[:-1]) // 2]
        for i, s in enumerate(sentences):
            last = i == len(sentences) - 1  # the last one may run long (it holds the CTA), never short: that is a cut-off voice
            ok = rates[i] / median <= RATE[1] if last else RATE[0] <= rates[i] / median <= RATE[1]
            flag = "   CHECK: cut off at the end of the video? remake the voice-over" if last and not ok else "   CHECK"
            print("  s%d %5.2f s %4.1f letters/s  %s%s" % (i + 1, st[i + 1] - st[i], rates[i], s[:60], "" if ok else flag))
        at = lambda x: x if not isinstance(x, str) else st[int(x[1]) - 1] + (float(x[3:]) if "+" in x else 0.0)
        cuts = [[at(c[0])] + list(c[1:]) for c in ed.get("cuts", [])]
        if not cuts:
            print("  no edit plan cuts: the footage plays as generated"); continue
        pieces, _ = bp.cuts_to_pieces(cuts, total, os.path.dirname(video), shots, own=video, pool=bp.group_pool(cfg, t, shots), tension=(times["starts"][1], times["starts"][2]) if times and len(times.get("starts", [])) > 2 else None)
        frames = []
        for f, a, length, shown in pieces:
            bad = [b for b in bp.blocked(f, shots, video) if a < b[1] and b[0] < a + length]
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
