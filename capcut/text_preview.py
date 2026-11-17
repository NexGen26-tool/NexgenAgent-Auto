#!/usr/bin/env python3
"""Text preview: every on-screen line drawn over the frame it plays on, as the build will place it (fonts, sizes,
colours, positions, the soft shadow), so the text design is judged by eye before saving (CLAUDE.md step 7, plan check;
references/typography.md). It builds each timeline in memory, as build_project.py does, and touches nothing in CapCut.

  python capcut/text_preview.py work/<week>/capcut.json [name part,...]  ->  work/<week>/plan/text/<timeline>.jpg

One frame per moment the text on screen changes (each clip's middle), the time and the lines on screen under it.
Look for: text over a face, a hand at work or the product's outline; a line too small to read at phone size or
crowding the frame edge; two lines fighting for the eye; the accent on the wrong word.
"""
import json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_project as bp  # noqa: E402

W, H = 540, 960          # preview frame (half of 1080 x 1920)
PX = W / 2               # canvas units (x and y run -1 .. 1) to preview pixels


def frame_at(d, t, ffmpeg, tmp):
    """The footage frame on the timeline at t seconds (the main video track), cropped as the clip's zoom shows it."""
    from PIL import Image
    M = {m["id"]: m for m in d["materials"]["videos"]}
    sp = {m["id"]: m.get("speed", 1.0) for m in d["materials"].get("speeds", [])}
    for tr in d["tracks"]:
        if tr["type"] != "video": continue
        for s in tr["segments"]:
            m = M.get(s["material_id"]); tt = s["target_timerange"]
            if not m or not m.get("path", "").lower().endswith(".mp4"): continue
            if tt["start"] <= t * 1e6 < tt["start"] + tt["duration"]:
                k = next((sp[x] for x in s.get("extra_material_refs", []) if x in sp), 1.0)
                src = s["source_timerange"]["start"] / 1e6 + (t - tt["start"] / 1e6) * k
                subprocess.run([ffmpeg, "-v", "error", "-y", "-ss", "%.2f" % src, "-i", m["path"], "-frames:v", "1",
                                "-vf", "scale=%d:%d" % (W, H), tmp], check=True)
                im = Image.open(tmp).convert("RGB")
                z = s["clip"]["scale"]["x"]
                if z > 1.01:
                    cw, ch = W / z, H / z; cx = W / 2 - s["clip"]["transform"]["x"] * PX / z; cy = H / 2 + s["clip"]["transform"]["y"] * PX * H / W / z
                    im = im.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H))
                return im
    return Image.new("RGB", (W, H), "#333333")


def texts_at(d, t):
    """The text clips on screen at t: [(segment, material)]."""
    M = {m["id"]: m for m in d["materials"].get("texts", [])}
    return [(s, M[s["material_id"]]) for tr in d["tracks"] if tr["type"] == "text" for s in tr["segments"]
            if s["material_id"] in M and s["target_timerange"]["start"] <= t * 1e6 < s["target_timerange"]["start"] + s["target_timerange"]["duration"]]


_F = {}
def font(path, px):
    from PIL import ImageFont
    key = (path, int(px))
    if key not in _F:
        try: _F[key] = ImageFont.truetype(path, max(6, int(px)))
        except OSError: _F[key] = ImageFont.load_default()
    return _F[key]


def draw_text(img, seg, m):
    """One CapCut rich text: lines of runs (font, size, colour), centred on the clip's position, at its scale."""
    from PIL import Image, ImageDraw
    c = json.loads(m["content"]); text = c["text"]; sc = seg["clip"]["scale"]["x"]
    unit = bp.K * 100 * sc * PX   # preview pixels per CapCut size point (the build's own width measure)
    runs = []
    for st in c["styles"]:
        a, b = st["range"]; col = st.get("fill", {}).get("content", {}).get("solid", {}).get("color", [1, 1, 1])
        runs.append((text[a:b], st.get("font", {}).get("path", ""), st.get("size", 6) * unit, tuple(int(x * 255) for x in col)))
    lines, cur = [], []
    for t, fp, px, col in runs:
        for i, ch in enumerate(t.split("\n")):
            if i: lines.append(cur); cur = []
            if ch: cur.append((ch, fp, px, col))
    lines.append(cur)
    lines = [l for l in lines if l]
    widths = [sum(font(fp, px).getlength(ch) for ch, fp, px, _ in l) for l in lines]
    heights = [max(px for _, _, px, _ in l) * 1.25 for l in lines]
    bw, bh = max(widths or [0]), sum(heights)
    cx = W / 2 + seg["clip"]["transform"]["x"] * PX; cy = H / 2 - seg["clip"]["transform"]["y"] * PX * H / W
    al = m.get("alignment", 1); d = ImageDraw.Draw(img); y = cy - bh / 2
    for l, w, h in zip(lines, widths, heights):
        x = {0: cx - bw / 2, 1: cx - w / 2, 2: cx + bw / 2 - w}.get(al, cx - w / 2)
        for ch, fp, px, col in l:
            f = font(fp, px); yy = y + h - px * 1.1
            if m.get("has_shadow"):
                a = int(255 * m.get("shadow_alpha", 0.45)); sh = Image.new("RGBA", img.size); ImageDraw.Draw(sh).text((x + 2, yy + 2), ch, font=f, fill=(0, 0, 0, a))
                img.paste(sh, (0, 0), sh)
            if m.get("border_width", 0) > 0:
                d.text((x, yy), ch, font=f, fill=col, stroke_width=2, stroke_fill=(0, 0, 0))
            else: d.text((x, yy), ch, font=f, fill=col)
            x += f.getlength(ch)
        y += h
    return bw, bh


def safe_area(img):
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    top, bot = H / 2 - 0.70 * PX * H / W, H / 2 + 0.52 * PX * H / W
    for yy in (top, bot): d.line([(0, yy), (W, yy)], fill=(255, 60, 60), width=1)
    d.line([(W / 2 + 0.86 * PX, 0), (W / 2 + 0.86 * PX, H)], fill=(255, 60, 60), width=1)


def main():
    if len(sys.argv) < 2: raise SystemExit(__doc__)
    from PIL import Image, ImageDraw
    cfgp = os.path.abspath(sys.argv[1]); week = os.path.dirname(cfgp); want = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    cfg = json.load(open(cfgp, encoding="utf-8"))
    jp = os.path.join(week, "shots.json"); shots = json.load(open(jp, encoding="utf-8")) if os.path.exists(jp) else {}
    media_dir = bp.MEDIA + "/" + cfg.get("media", cfg["project"]); out_dir = os.path.join(week, "plan", "text")
    os.makedirs(out_dir, exist_ok=True); ffmpeg = bp.find_ffmpeg() or "ffmpeg"; tmp = os.path.join(tempfile.mkdtemp(), "f.jpg")
    slots = {}
    for c in cfg["timelines"]:
        slots[c["brand"]] = slots.get(c["brand"], -1) + 1
        if want and not any(w in c["name"] for w in want): continue
        t = bp.Timeline(c, media_dir, shots, bp.group_pool(cfg, c, shots), slots[c["brand"]]); d = t.d
        marks = sorted({round((s["target_timerange"]["start"] + min(s["target_timerange"]["duration"], 1.2e6) * 0.6) / 1e6, 2)
                        for tr in d["tracks"] if tr["type"] == "text" for s in tr["segments"]})
        tiles = []
        for tm in marks:
            img = frame_at(d, tm, ffmpeg, tmp); safe_area(img); on = texts_at(d, tm)
            for s, m in on: draw_text(img, s, m)
            label = Image.new("RGB", (W, 44), "white"); dl = ImageDraw.Draw(label)
            dl.text((6, 4), "%.2f s" % tm, fill="black")
            dl.text((6, 22), " | ".join(json.loads(m["content"])["text"].replace("\n", " / ")[:40] for _, m in on)[:90], fill="black")
            tile = Image.new("RGB", (W, H + 44), "white"); tile.paste(img, (0, 0)); tile.paste(label, (0, H)); tiles.append(tile)
        per = 4; rows = (len(tiles) + per - 1) // per
        sheet = Image.new("RGB", (per * W, rows * (H + 44)), "white")
        for i, tl in enumerate(tiles): sheet.paste(tl, ((i % per) * W, (i // per) * (H + 44)))
        name = re.sub(r"[^A-Za-z0-9]+", "_", t.name.split("|")[-1]).strip("_")
        dst = os.path.join(out_dir, name + ".jpg"); sheet.save(dst, quality=85)
        print("%-50s %2d moments -> %s" % (t.name[-50:], len(tiles), dst))


if __name__ == "__main__":
    main()
