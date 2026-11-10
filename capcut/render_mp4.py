#!/usr/bin/env python3
"""Render finished MP4s straight from the edit, without CapCut's Export button.

  python capcut/render_mp4.py work/<week>/capcut.json --out "<the owner's batch folder>" "<part of a name>" [...]
      -> <batch folder>/<Angle>  <SKU> - V1.mp4   (1080x1920, 30 fps, H.264 + AAC, ready for Meta)

One file per ad, written only to --out (the owner's batch folder, e.g. Desktop/NexGen/Others/AI Test/Live Batch
OCT24/Batch 3 - Nov6), named like the owner's own CapCut exports there. No second copy anywhere. An existing file is
never overwritten.

It builds each timeline exactly as build_project.py does (same shots, speeds, crops and zooms, the voice-over cut to
its pauses at 1.08x, the music bed, the sound effects, the line timing) and draws the house-edit text and the logo on
top. Differences from a CapCut export: the text has no CapCut animations (Line 2's title and Smoke out are cut, not
animated), and when the CapCut fonts are not on this computer it uses Arial Black / Georgia.
"""
import json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_project as bp  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

OW, OH, FPS = 1080, 1920, 30
FONTS = "C:/Windows/Fonts/" if os.name == "nt" else "/Library/Fonts/"
def font(name, size, fallback="arialbd.ttf"):
    for f in (name, fallback, "arialbd.ttf"):
        try: return ImageFont.truetype(FONTS + f, size)
        except OSError: continue
    return ImageFont.load_default()
BIG, SMALL, ACCENT = font("ariblk.ttf", 92), font("arialbd.ttf", 58), font("arialbi.ttf", 70, "arialbd.ttf")
TITLE_S, TITLE_B = font("georgiai.ttf", 64), font("georgiaz.ttf", 112)
WHITE, ORANGE, YELLOW, CREAM = (255, 255, 255), (255, 90, 31), (255, 212, 0), (246, 236, 208)


def text_png(path, rows):
    """rows = [(y fraction, [(text, font, colour), ...]), ...]: each row centred, black stroke."""
    im = Image.new("RGBA", (OW, OH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for y, parts in rows:
        widths = [d.textlength(t, font=f) for t, f, _ in parts]
        if sum(widths) > OW * 0.9:  # too wide: every font of the row shrinks until it fits
            k = OW * 0.9 / sum(widths)
            parts = [(t, ImageFont.truetype(f.path, max(20, int(f.size * k))), c) for t, f, c in parts]
            widths = [d.textlength(t, font=f) for t, f, _ in parts]
        x = (OW - sum(widths)) / 2
        h = max(f.size for _, f, _ in parts)
        for (t, f, c), w in zip(parts, widths):
            d.text((x, y * OH - h / 2 + (h - f.size) * 0.8), t, font=f, fill=c, stroke_width=max(3, f.size // 14), stroke_fill=(0, 0, 0))
            x += w
    im.save(path)


def wrap(t, f, maxw=OW * 0.88):
    words, lines, cur = t.split(), [], ""
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    for w in words:
        if cur and d.textlength(cur + " " + w, font=f) > maxw: lines.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return lines + [cur] if cur else lines


def render(tl, cfg, out, tmp):
    d = tl.d; total = d["duration"] / bp.US; mats = {m["id"]: m for k, v in d["materials"].items() if isinstance(v, list) for m in v if isinstance(m, dict) and "id" in m}
    inputs, vf, af = [], [], []
    def inp(p):
        inputs.extend(["-i", p]); return len(inputs) // 2 - 1
    # footage: the video track whose materials are the mp4s (not the logo)
    vids = []
    for t in d["tracks"]:
        if t["type"] != "video": continue
        for s in t["segments"]:
            m = mats.get(s["material_id"], {})
            if str(m.get("path", "")).lower().endswith(".mp4"): vids.append((s, m["path"]))
    vids.sort(key=lambda x: x[0]["target_timerange"]["start"])
    labels = []
    for n, (s, p) in enumerate(vids):
        i = inp(p); a = s["source_timerange"]["start"] / bp.US; l = s["source_timerange"]["duration"] / bp.US
        shown = s["target_timerange"]["duration"] / bp.US
        k = (s.get("clip") or {}).get("scale", {}).get("x", 1.0) or 1.0; tr = (s.get("clip") or {}).get("transform", {})
        cx = 0.5 - tr.get("x", 0.0) / (2 * k); cy = 0.5 + tr.get("y", 0.0) / (2 * k)
        crop = "crop=iw/%f:ih/%f:iw*%f-iw/%f/2:ih*%f-ih/%f/2," % (k, k, cx, k, cy, k) if k > 1.001 else ""
        vf.append("[%d:v]trim=start=%.3f:duration=%.3f,setpts=(PTS-STARTPTS)*%.5f,%sscale=%d:%d,fps=%d,setsar=1[v%d]" % (i, a, l, shown / l, crop, OW, OH, FPS, n))
        labels.append("[v%d]" % n)
    vf.append("%sconcat=n=%d:v=1:a=0,trim=duration=%.3f[base]" % ("".join(labels), len(labels), total))
    # text and logo
    T = tl.times or {}; L = cfg; last = "[base]"; layers = []
    def layer(rows, a, b):
        p = os.path.join(tmp, "t%d.png" % len(layers)); text_png(p, rows); layers.append((p, a, b))
    st = T.get("starts", [])
    big, small, acc = L["line1"]
    layer([(0.40, [(big.strip(), BIG, WHITE)]), (0.46, [(small, SMALL, WHITE), (acc, ACCENT, ORANGE)])], *T["line1"])
    l3a = T["line3"][0]
    layer([(0.27, [(L["line2"][0], TITLE_S, CREAM)]), (0.33, [(L["line2"][1], TITLE_B, CREAM)])], T["line2"], l3a)
    layer([(0.78, [(L["line3"][0], BIG if len(L["line3"][0]) < 14 else SMALL, WHITE)])], *T["line3"])
    layer([(0.84, [(L["line3"][1], SMALL, YELLOW)])], min(l3a + 0.9, T["line3"][1] - 0.8), T["line3"][1])
    layer([(0.80 + 0.06 * i, [(x, SMALL, WHITE)]) for i, x in enumerate(wrap(L["line4"], SMALL))], *T["line4"])
    layer([(0.78, [(L["line5"][0], SMALL, WHITE)]), (0.84, [(L["line5"][1], BIG if len(L["line5"][1]) < 15 else SMALL, YELLOW)])], *T["line5"])
    layer([(0.80, [(L["cta"], BIG, WHITE)])], T["cta"], total)
    brand = bp.BRANDS[cfg["brand"]]; logo = bp.ROOT + "/brand/" + brand["logo"]
    li = inp(logo); vf.append("[%d:v]scale=%d:-1[logo]" % (li, int(OW * brand["logo_scale"] * 1.25)))
    vf.append("%s[logo]overlay=(W-w)/2:H*0.105[lg]" % last); last = "[lg]"
    for n, (p, a, b) in enumerate(layers):
        i = inp(p); vf.append("%s[%d:v]overlay=0:0:enable='between(t,%.3f,%.3f)'[o%d]" % (last, i, a, b, n)); last = "[o%d]" % n
    vf.append("%sfade=t=out:st=%.3f:d=0.4,format=yuv420p[vout]" % (last, total - 0.4))
    # audio: every audio segment (voice-over pieces, music, sound effects) at its time, speed and volume
    alabels = []
    for t in d["tracks"]:
        if t["type"] != "audio": continue
        for s in t["segments"]:
            m = mats.get(s["material_id"], {}); p = m.get("path")
            if not p or not os.path.exists(p): continue
            i = inp(p); a = s["source_timerange"]["start"] / bp.US; l = s["source_timerange"]["duration"] / bp.US
            at = s["target_timerange"]["start"] / bp.US; sp = s.get("speed", 1.0) or 1.0; vol = s.get("volume", 1.0)
            n = len(alabels)
            af.append("[%d:a]atrim=start=%.3f:duration=%.3f,asetpts=PTS-STARTPTS,atempo=%.4f,volume=%.3f,adelay=%d:all=1[a%d]" % (i, a, l, sp, vol, int(at * 1000), n))
            alabels.append("[a%d]" % n)
    af.append("%samix=inputs=%d:normalize=0:dropout_transition=0,atrim=duration=%.3f,afade=t=out:st=%.3f:d=0.6,loudnorm=I=-14:TP=-1.5:LRA=11[aout]" % ("".join(alabels), len(alabels), total, total - 0.6))
    graph = ";".join(vf + af)
    gp = os.path.join(tmp, "graph.txt"); open(gp, "w", encoding="utf-8").write(graph)
    cmd = [bp.find_ffmpeg() or "ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex_script", gp, "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)


def main():
    if len(sys.argv) < 3: raise SystemExit(__doc__)
    args = sys.argv[2:]
    if "--out" not in args: raise SystemExit("Give --out: the owner's batch folder (one copy only, no work/<week>/export).")
    i = args.index("--out"); out_dir = args[i + 1]; want = args[:i] + args[i + 2:]
    cfg_path = os.path.abspath(sys.argv[1]); week = os.path.dirname(cfg_path)
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    jp = os.path.join(week, "shots.json"); shots = json.load(open(jp, encoding="utf-8")) if os.path.exists(jp) else {}
    media = bp.MEDIA + "/" + cfg.get("media", cfg["project"]); os.makedirs(out_dir, exist_ok=True)
    slots = {}
    for c in cfg["timelines"]:
        slots[c["brand"]] = slots.get(c["brand"], -1) + 1
        if not any(w in c["name"] for w in want): continue
        tl = bp.Timeline(c, media, shots, bp.group_pool(cfg, c, shots), slots[c["brand"]])
        _, angle, rest = [x.strip() for x in c["name"].split("|")]
        sku, code = rest.split(" - ")
        out = os.path.join(out_dir, "%s  %s - V%s.mp4" % (angle, sku, code[8]))  # the owner's naming: "<Angle>  <SKU> - V1.mp4"
        if os.path.exists(out): print("exists, not overwritten:", out); continue
        with tempfile.TemporaryDirectory() as tmp: render(tl, c, out, tmp)
        print("rendered:", out, "%.1f s" % (tl.d["duration"] / bp.US))


if __name__ == "__main__":
    main()
