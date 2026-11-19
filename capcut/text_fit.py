"""Text placed by the picture under it (owner, Nov 18: text sat over the product, over people, and the logo vanished
into foliage, because every style put each line at one fixed spot of the frame, blind to the shot).

  fit(d, pieces, K, ffmpeg, notes, preview=None)   called by build_project.Timeline once the timeline is laid out

For each group of texts that are on screen together (a line and its halves), it looks at every shot that plays under
it (start, middle and end of each shot) and moves the group up or down, keeping its alignment, to the calmest band of
the safe area: few edges (no product, no person, no busy foliage), not blinding white under light text, as close to
the style's own spot as the picture allows. The logo goes to the top position (left, centre, right) where it reads:
a calm, light background under the dark logo. With preview, it writes one sheet per timeline with the text drawn on
the frames it plays over, so the placement is judged before the project is saved (CLAUDE.md step 7, plan check).
"""
import io, json, os, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat

W, H = 108, 192            # analysis frame (9:16)
Y_TOP, Y_BOT = 0.70, -0.52  # the safe area (references/typography.md)
_FR, _PIL = {}, {}


def _font(path, px=100):
    k = (path, px)
    if k not in _PIL: _PIL[k] = ImageFont.truetype(path, px)
    return _PIL[k]


def _frame(ffmpeg, f, t, size=(W, H)):
    k = (f, round(t, 1), size)
    if k not in _FR:
        out = subprocess.run([ffmpeg, "-v", "error", "-ss", "%.2f" % max(0.0, t), "-i", f, "-frames:v", "1", "-vf",
                              "scale=%d:%d" % size, "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
        _FR[k] = Image.open(io.BytesIO(out)).convert("RGB") if out else Image.new("RGB", size, (128, 128, 128))
    return _FR[k]


def source_at(pieces, t):
    """(file, source second) of the footage on screen at timeline second t; pieces = [(file, start, length, shown)]."""
    at = 0.0
    for f, a, length, shown in pieces:
        if t < at + shown or (f, a, length, shown) == pieces[-1]:
            return f, a + min(max(t - at, 0.0), shown) * (length / shown if shown else 1.0)
        at += shown
    return pieces[-1][0], pieces[-1][1]


def shots_in(pieces, a, b):
    """[(start, end)] of every shot on screen between timeline seconds a and b (each piece is one shot)."""
    at, out = 0.0, []
    for _, _, _, shown in pieces:
        o0, o1 = max(a, at), min(b, at + shown)
        if o1 - o0 > 0.15: out.append((o0, o1))
        at += shown
    return out or [(a, b)]


def _parts(m):
    """[(text, font path, size, colour)] of a CapCut text material."""
    c = json.loads(m["content"]); txt = c["text"]; out = []
    for st in c["styles"]:
        a, b = st["range"]; col = st.get("fill", {}).get("content", {}).get("solid", {}).get("color", [1, 1, 1])
        out.append((txt[a:b], (st.get("font") or {}).get("path") or m.get("font_path"), st.get("size", 6.0), col))
    return out


def box(m, s, K):
    """(x0, x1, y0, y1) of a text clip in canvas units (x and y in -1..1, y up)."""
    sc = s["clip"]["scale"]["x"]; rows, ws, cw, ch = [], [], 0.0, 0.0
    for t, path, size, _ in _parts(m):
        for i, chunk in enumerate(t.split("\n")):
            if i: ws.append(cw); rows.append(ch); cw = ch = 0.0
            if chunk and path and os.path.exists(path): cw += _font(path).getlength(chunk) * size * sc * K
            ch = max(ch, size)
    ws.append(cw); rows.append(ch)
    w = max(ws) if ws else 0.1; h = sum(r * 100 * sc * K * 1.12 for r in rows if r) * (1080 / 1920)
    x, y = s["clip"]["transform"]["x"], s["clip"]["transform"]["y"]
    return x - w / 2, x + w / 2, y - h / 2, y + h / 2


def _px(b):  # canvas box -> pixel box on the analysis frame
    x0, x1, y0, y1 = b
    return (max(0, int((x0 + 1) / 2 * W)), max(0, int((1 - y1) / 2 * H)), min(W, int((x1 + 1) / 2 * W) + 1), min(H, int((1 - y0) / 2 * H) + 1))


def _score(frames, b, light_text=True):
    """How bad a box is over these frames: edges (product, people, foliage) and, under light text, a white background."""
    p = _px(b); e = l = 0.0
    if p[2] <= p[0] or p[3] <= p[1]: return 9.0
    for edges, gray in frames:
        e += ImageStat.Stat(edges.crop(p)).mean[0] / 255.0
        lum = ImageStat.Stat(gray.crop(p)).mean[0] / 255.0
        l += max(0.0, lum - 0.72) * 2.0 if light_text else max(0.0, 0.5 - lum) * 2.0
    n = len(frames) or 1
    return e / n * 4.0 + l / n


def _prep(img):
    """edges + wood map (the products are wood: warm, saturated) as one cost image, and the grey image."""
    g = img.convert("L"); e = g.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.BoxBlur(2))
    h, sat, v = img.convert("HSV").split()
    wood = Image.eval(h, lambda x: 255 if 7 <= x <= 32 else 0)  # hue about 10-45 degrees
    wood = Image.composite(wood, Image.new("L", img.size, 0), Image.eval(sat, lambda x: 255 if x > 95 else 0))
    wood = Image.composite(wood, Image.new("L", img.size, 0), Image.eval(v, lambda x: 255 if x > 60 else 0))
    cost = Image.blend(e, wood.filter(ImageFilter.BoxBlur(1)), 0.35)
    return cost, g


def fit(d, pieces, K, ffmpeg, notes, logo_mid=None, preview=None, title="", logo_light=None, text_y=None):
    """text_y: [y centre or None per text group, in order], set by eye from the preview sheet; overrides the search."""
    if not pieces or not ffmpeg: return
    texts = {m["id"]: m for m in d["materials"]["texts"]}
    segs = [s for t in d["tracks"] if t.get("type") == "text" for s in t["segments"] if s["material_id"] in texts]
    us = 1e6
    win = lambda s: (s["target_timerange"]["start"] / us, (s["target_timerange"]["start"] + s["target_timerange"]["duration"]) / us)
    total = sum(p[3] for p in pieces)
    frames_at = lambda ts: [_prep(_frame(ffmpeg, *source_at(pieces, t))) for t in ts]

    # the logo: the top position where a dark logo reads (calm and light behind it)
    logo_box = None
    if logo_mid:
        ls = next((s for t in d["tracks"] for s in t["segments"] if s["material_id"] == logo_mid), None)
        if ls:
            y = ls["clip"]["transform"]["y"]; fr = frames_at([i * 1.5 + 0.3 for i in range(int(total / 1.5))])
            best = (0.0, 0.0)  # the logo is locked top centre (owner, Nov 18); only its light or dark version is chosen
            if best[1] != ls["clip"]["transform"]["x"]:
                notes.append("logo moved to x %.2f (calmer, lighter background)" % best[1])
            ls["clip"]["transform"]["x"] = best[1]; logo_box = (best[1] - 0.34, best[1] + 0.34, y - 0.09, y + 0.09)
            lum = sum(ImageStat.Stat(gr.crop(_px(logo_box))).mean[0] for _, gr in fr) / (len(fr) or 1) / 255.0
            if lum < 0.55 and logo_light:  # a dark background: the brand's light logo reads, the dark one vanishes
                m = next(x for x in d["materials"]["videos"] if x["id"] == logo_mid); m["path"] = logo_light()
                m["material_name"] = os.path.basename(m["path"]); notes.append("logo: light version (dark background %.2f)" % lum)

    # groups: texts on screen at the same time move together
    segs.sort(key=lambda s: win(s)[0]); groups = []
    for s in segs:
        a, b = win(s)
        g = next((g for g in groups if any(min(b, win(o)[1]) - max(a, win(o)[0]) > 0.05 for o in g)), None)
        (g.append(s) if g else groups.append([s]))
    sheet = []
    for g in groups:
        a = min(win(s)[0] for s in g); b = max(win(s)[1] for s in g)
        if b - a < 0.2: continue
        # every shot the text plays over, not one frame of it (owner, Nov 18: a line placed clear of her in one shot
        # ran into her face in the next shot of the same line)
        sh = shots_in(pieces, a, b)
        fr = frames_at([t for o0, o1 in sh for t in (o0 + 0.1, (o0 + o1) / 2, o1 - 0.1)])
        bx = [box(texts[s["material_id"]], s, K) for s in g]
        x0, x1 = min(q[0] for q in bx), max(q[1] for q in bx); y0, y1 = min(q[2] for q in bx), max(q[3] for q in bx)
        best = None; dy = Y_BOT - y0
        while y1 + dy <= Y_TOP + 1e-6:
            cand = (x0, x1, y0 + dy, y1 + dy)
            yc = (cand[2] + cand[3]) / 2
            # the product and the person mostly fill the middle of a wide shot; smooth cushions or a plain top have few
            # edges but are still the product, so the middle band costs extra (owner, Nov 18: lines over the table)
            sc = _score(fr, cand) + 0.25 * abs(dy) + 0.45 * max(0.0, 0.32 - abs(yc + 0.02)) / 0.32
            if logo_box and not (cand[1] < logo_box[0] or cand[0] > logo_box[1] or cand[3] < logo_box[2] or cand[2] > logo_box[3]):
                sc += 5.0
            if best is None or sc < best[0]: best = (sc, dy)
            dy += 0.02
        gi = len(sheet)
        if text_y and gi < len(text_y) and text_y[gi] is not None:
            best = (0.0, text_y[gi] - (y0 + y1) / 2)
        if best is None: continue
        if abs(best[1]) > 0.019:
            for s in g: s["clip"]["transform"]["y"] += best[1]
            notes.append("text %.1f-%.1f s moved %+.2f to a calmer band" % (a, b, best[1]))
        sheet.append(([(o0 + o1) / 2 for o0, o1 in sh], g))
    lp = next((x["path"] for x in d["materials"]["videos"] if x["id"] == logo_mid), None) if logo_mid else None
    if preview: _preview(d, pieces, ffmpeg, texts, sheet, K, preview, title, logo_box, lp)


def _preview(d, pieces, ffmpeg, texts, sheet, K, path, title, logo_box, logo_path=None):
    """One tile per shot under each text group (270x480), the text drawn at its size, place and colour, with the logo."""
    w, h = 270, 480; tiles = []
    for gi, (ts, g) in enumerate(sheet):
      for k, t in enumerate(ts):  # one tile per shot under the text: every shot is judged, not one frame
        im = _frame(ffmpeg, *source_at(pieces, t), size=(w, h)).copy(); dr = ImageDraw.Draw(im)
        for s in g:
            m = texts[s["material_id"]]; sc = s["clip"]["scale"]["x"]; x0, x1, y0, y1 = box(m, s, K)
            yy = (1 - y1) / 2 * h; rows = [[]]
            for txt, fp, size, col in _parts(m):
                for i, chunk in enumerate(txt.split("\n")):
                    if i: rows.append([])
                    if chunk: rows[-1].append((chunk, fp, size, col))
            al = m.get("alignment", 1)
            for row in rows:
                if not row: continue
                px = [max(6, int(size * sc * K * 100 * 540 * w / 1080)) for _, _, size, _ in row]
                fonts = [_font(fp, p) if fp and os.path.exists(fp) else ImageFont.load_default() for (_, fp, _, _), p in zip(row, px)]
                rw = sum(f.getlength(c) for f, (c, _, _, _) in zip(fonts, row)); rh = max(px) * 1.12
                xx = {0: (x0 + 1) / 2 * w, 1: (w - rw) / 2 + (x0 + x1) / 4 * w, 2: (x1 + 1) / 2 * w - rw}.get(al, (x0 + 1) / 2 * w)
                for f, (c, _, _, col), p in zip(fonts, row, px):
                    rgb = tuple(int(v * 255) for v in col[:3])
                    dr.text((xx + 2, yy + rh - p + 2), c, font=f, fill=(0, 0, 0))
                    dr.text((xx, yy + rh - p), c, font=f, fill=rgb); xx += f.getlength(c)
                yy += rh
        if logo_box and logo_path and os.path.exists(logo_path):
            q = logo_box; lg = Image.open(logo_path).convert("RGBA"); bw = int((q[1] - q[0]) / 2 * w * 0.85)
            lg = lg.resize((bw, max(1, int(lg.height * bw / lg.width))))
            im.paste(lg, (int((q[0] + q[1] + 2) / 4 * w - bw / 2), int((1 - (q[2] + q[3]) / 2) / 2 * h - lg.height / 2)), lg)
        dr.text((4, h - 14), "line %d  shot %d/%d  %.1f s" % (gi, k + 1, len(ts), t), fill=(255, 255, 0)); tiles.append(im)
    if not tiles: return
    cols = min(8, len(tiles)); rows_n = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (w * cols, h * rows_n + 18), "white"); ImageDraw.Draw(sheet).text((4, 2), title, fill=(0, 0, 0))
    for i, im in enumerate(tiles): sheet.paste(im, (i % cols * w, 18 + i // cols * h))
    os.makedirs(os.path.dirname(path), exist_ok=True); sheet.save(path, quality=85)
