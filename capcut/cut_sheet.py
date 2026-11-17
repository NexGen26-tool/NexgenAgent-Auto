#!/usr/bin/env python3
"""Cut check: the first and last frames of every cut of every timeline, 0.1 s apart (CLAUDE.md step 7, plan check).

  python capcut/cut_sheet.py work/<week>/capcut.json     ->  work/<week>/plan/cuts/<timeline>.jpg

The plan sheet shows a frame every 0.6 s, which can miss a crossfade still on screen when a cut lands, or another
variant's person in a borrowed shot. This sheet shows each cut's first five frames (in, +0.1 ... +0.4 s) and last
three (out -0.3 ... -0.1 s), exactly as the build will place them (cuts moved out of fades and bad stretches, shots
stopped before the next one). A row from another variant of the group is labelled OTHER VARIANT: its frames must
show the product only. Look at every row before saving.

Each row also names the scene row the cut comes from (A01-B04) and its shot size from the brief's camera direction
("CLOSE / slow slide: ..."; older rows: the size word in the direction), and the script prints SAME SIZE where two cuts
in a row show the same size, when the timeline's "structure" is one that changes size at every cut (argued, follow,
tableau, montage; capcut/templates/structures.json).
"""
import glob, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_project as bp  # noqa: E402

W, H = 135, 240
ROWS = ["A01", "A02", "A03", "A04", "B01", "B02", "B03", "B04"]
ROW_START = [0.0, 2.0, 5.0, 8.0, 10.0, 13.0, 15.0, 18.0]  # where each scene row plays in Negen's merged 20 s video
SIZES = ["TOP-DOWN", "LOW", "CLOSE", "MEDIUM", "WIDE"]
SIZE_WORDS = [("TOP-DOWN", r"top[- ]?down|overhead"), ("LOW", r"low[- ]angle"), ("CLOSE", r"close|macro"),
              ("MEDIUM", r"medium"), ("WIDE", r"wide")]


def shot_size(direction):
    """The shot size a scene row names: "CLOSE / slow slide: ..." (the shot map), else the size word in its camera
    part (before the first colon), else anywhere in it; "?" when it names none."""
    d = re.sub(r"^IMPORTANT:.*?LEDs\.\s*", "", direction or "")
    m = re.match(r"\s*([A-Z-]+)\s*/", d)
    if m and m.group(1) in SIZES: return m.group(1)
    for part in (d.split(":")[0], d):
        for size, pat in SIZE_WORDS:
            if re.search(pat, part, re.I): return size
    return "?"


def brief_rows(week):
    """{video file name: [8 camera directions]} from week.json; a spare shares its video's rows."""
    p = os.path.join(week, "week.json")
    if not os.path.exists(p): return {}
    w = json.load(open(p, encoding="utf-8"))
    return {v["file"]: (v.get("brief") or {}).get("shots") or [] for g in w.get("groups", []) for v in g["videos"] if v.get("file")}


def row_of(rows, path, t):
    """(scene row, size) of the footage at time t of a video file."""
    i = max(k for k, s in enumerate(ROW_START) if s <= t + 0.05)
    shots = rows.get(os.path.basename(path).replace(" - spare.mp4", ".mp4")) or []
    return ROWS[i], (shot_size(shots[i]) if i < len(shots) else "?")


def main():
    if len(sys.argv) != 2: raise SystemExit(__doc__)
    from PIL import Image, ImageDraw
    cfg_path = os.path.abspath(sys.argv[1]); week = os.path.dirname(cfg_path)
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    jpath = os.path.join(week, "shots.json")
    shots = json.load(open(jpath, encoding="utf-8")) if os.path.exists(jpath) else {}
    out_dir = os.path.join(week, "plan", "cuts"); os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(tempfile.mkdtemp(), "f.jpg"); ffmpeg = bp.find_ffmpeg() or "ffmpeg"
    rows = brief_rows(week)

    def frame(path, t):
        t = min(max(0.0, t), bp.mp4_info(path)[0] - 0.1)
        subprocess.run([ffmpeg, "-v", "error", "-y", "-ss", "%.2f" % t, "-i", path, "-frames:v", "1",
                        "-vf", "scale=%d:%d" % (W, H), tmp], check=True)
        return Image.open(tmp).copy()

    for t in cfg["timelines"]:
        video = os.path.join(os.path.dirname(cfg_path), os.path.relpath(t["video"], os.path.relpath(week, os.getcwd()))) \
            if not os.path.isabs(t["video"]) and not os.path.exists(t["video"]) else t["video"]
        ed = t.get("edit") or {}
        if not ed.get("cuts"): print(t["name"], ": no edit plan cuts"); continue
        vo = bp.extract_vo(video, os.path.join(week, "plan"))
        spans = bp.speech_spans(vo, bp.mp4_info(vo)[0])
        total = sum(b - a for a, b in spans) / bp.VO_SPEED + bp.CTA_HOLD
        times = ed.get("times") or (bp.pilot_times(t, spans, total, vo, ed.get("ends")) if t.get("pilot") else
                                      bp.vo_times(t["vo"], spans, total, vo, ed.get("ends"), bp.line_map(t)) if t.get("vo") else None)
        st = times["starts"] if times and "starts" in times else None
        at = lambda x: x if not isinstance(x, str) else st[int(x[1]) - 1] + (float(x[3:]) if "+" in x else 0.0)
        cuts = [[at(c[0])] + list(c[1:]) for c in ed["cuts"]]
        pieces, zooms = bp.cuts_to_pieces(cuts, total, os.path.dirname(video), shots, own=video, pool=bp.group_pool(cfg, t, shots), tension=bp.tension_of(t, times))
        sents = list(t["pilot"]["parts"]) if t.get("pilot") else [x for x in re.split(r"(?<=[.?!])\s+", t.get("vo", "").strip()) if x]
        starts = (st or [0.0])[1:]; tl, at_t = [], 0.0
        for p in pieces: tl.append(at_t); at_t += p[3]
        def sentence(x):
            k = sum(1 for s0 in starts if s0 <= x + 0.05)
            return "s%d %s" % (k + 1, sents[k][:48]) if k < len(sents) else ""
        top = H + 18  # the product photo heads the sheet: every row is judged against it
        sheet = Image.new("RGB", (W * 8, top + (H + 18) * len(pieces)), "white"); d = ImageDraw.Draw(sheet)
        sku = t["name"].split("|")[-1].strip().split(" ")[0]
        photos = [p for p in glob.glob(os.path.join(week, "product-photos", "*")) + glob.glob(os.path.join(os.path.dirname(week), "product-photos", "*")) if sku in os.path.basename(p)]
        if photos:
            ph = Image.open(photos[0]).convert("RGB"); ph.thumbnail((W * 3, H)); sheet.paste(ph, (0, 0))
            d.text((ph.width + 8, 8), "PRODUCT PHOTO: every frame below must match this outline", fill="#c00000")
        sizes = [row_of(rows, f, a + min(length, 1.0) / 2) for f, a, length, _ in pieces]
        same = []  # only where the video's shot structure changes size at every cut (argued, follow, tableau, montage)
        for r in range(1, len(pieces)) if bp.STRUCTURES.get(t.get("structure", ""), {}).get("size_changes") else []:
            (f0, a0, l0, _), (f1, a1, _, _) = pieces[r - 1], pieces[r]
            run_on = f0 == f1 and abs(a0 + l0 - a1) < 0.15  # the same shot carried on (a fill), not a new cut
            if not run_on and sizes[r][1] != "?" and sizes[r][1] == sizes[r - 1][1]:
                same.append("cut%d %s %s" % (r + 1, sizes[r][1], sentence(tl[r]).split(" ")[0]))
        for r, ((f, a, length, shown), zz) in enumerate(zip(pieces, zooms)):
            other = bp.variant(f) != bp.variant(video)
            ts = [a + k for k in (0, .1, .2, .3, .4)] + [a + length - k for k in (.3, .2, .1)]
            for k, tt in enumerate(ts):
                im = frame(f, tt)
                if isinstance(zz, dict):  # show the crop the timeline shows
                    z, cx, cy = zz["zoom"], zz["cx"], zz["cy"]; w2, h2 = W / z / 2, H / z / 2
                    im = im.crop((int(cx * W - w2), int(cy * H - h2), int(cx * W + w2), int(cy * H + h2))).resize((W, H))
                sheet.paste(im, (k * W, top + r * (H + 18)))
                lab = "%.1f" % tt
                if k == 0: lab = "cut%d in %.1f%s" % (r + 1, tt, " OTHER VARIANT" if other else "")
                if k == 5: lab = "out %.1f" % tt
                if k == 1: lab = sentence(tl[r])[:22]
                if k == 2: lab = sentence(tl[r])[22:44]
                if k == 3: lab = "%s %s" % sizes[r]
                d.text((k * W + 2, top + r * (H + 18) + H + 3), lab, fill="#c00000" if other and k == 0 else "black")
        name = re.sub(r"[^A-Za-z0-9]+", "_", t["name"].split("|")[-1]).strip("_")
        dst = os.path.join(out_dir, name + ".jpg"); sheet.save(dst, quality=80)
        print("%-50s %2d cuts, %d from another variant -> %s" % (t["name"][-50:], len(pieces),
              sum(bp.variant(p[0]) != bp.variant(video) for p in pieces), dst))
        print("    sizes: %s" % " ".join(s for _, s in sizes))
        if same: print("    SAME SIZE: %s (the size changes at every cut: pick another shot)" % "; ".join(same))


if __name__ == "__main__":
    main()
