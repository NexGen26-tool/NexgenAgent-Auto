"""The fundamentals gate (references/fundamentals.md): no timeline is saved unless every shot of its final cut was
reviewed against the reality tests at full size, and its voice matches its person.

  sheets(week_dir, tls, ffmpeg)   after a dry run: work/<week>/plan/cut.json + work/<week>/qc/<timeline>.jpg
  gate(week_dir, tls)             before --save / --replace: [reason] per timeline that may not be written

qc.json (written by the reviewer): {"<timeline name>": {"cut": "<hash>", "pass": true|false, "fails": [[shot, why]]}}
"""
import glob, hashlib, io, json, os, re, subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FW, FH = 360, 640  # full phone-size frame on the sheet


def cut_hash(pieces):
    """Changes whenever the final cut changes: which file, from where, how long."""
    key = json.dumps([[os.path.basename(f), round(a, 2), round(n, 2), round(s, 2)] for f, a, n, s in pieces])
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:10]


def _week(week_dir):
    p = os.path.join(week_dir, "week.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {"groups": []}


def _video(week, name):
    """(group, video) of a timeline, by its SKU group and its code (the name's last word)."""
    code = name.split()[-1]
    for g in week.get("groups", []):
        for v in g.get("videos", []):
            if v.get("code") == code and g.get("sku", "")[:10] in name:
                return g, v
    return None, None


def _frame(ffmpeg, f, t):
    out = subprocess.run([ffmpeg, "-v", "error", "-ss", "%.2f" % max(0.0, t), "-i", f, "-frames:v", "1", "-vf",
                          "scale=%d:%d" % (FW, FH), "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    return Image.open(io.BytesIO(out)).convert("RGB") if out else Image.new("RGB", (FW, FH), (90, 90, 90))


def _font(px):
    for p in ("C:/Windows/Fonts/arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf"):
        if os.path.exists(p): return ImageFont.truetype(p, px)
    return ImageFont.load_default()


def sheets(week_dir, tls, ffmpeg):
    """One sheet per timeline: every shot of the final cut as first, middle and last frame at full size."""
    week = _week(week_dir); cut = {}; os.makedirs(os.path.join(week_dir, "qc"), exist_ok=True)
    for t in tls:
        pieces = getattr(t, "pieces", None)
        if not pieces: continue
        h = cut_hash(pieces); g, v = _video(week, t.name)
        cut[t.name] = {"cut": h, "shots": [[os.path.basename(f), round(a, 2), round(n, 2), round(s, 2)] for f, a, n, s in pieces]}
        sku = (g or {}).get("sku", "")
        photo = next(iter(sorted(glob.glob(os.path.join(week_dir, "product-photos", "*%s*" % sku[:10])))), None) if sku else None
        who = ((v or {}).get("cast") or {}).get("who", "(no cast in week.json)")
        rows = []
        for i, (f, a, n, s) in enumerate(pieces):
            fr = [_frame(ffmpeg, f, a + x) for x in (0.05, n / 2, max(0.05, n - 0.08))]
            row = Image.new("RGB", (FW * 3, FH + 30), "white"); d = ImageDraw.Draw(row)
            d.text((6, 4), "shot %d   %s   %.2f-%.2f s" % (i + 1, os.path.basename(f)[-60:], a, a + n), fill=(0, 0, 0), font=_font(18))
            for k, im in enumerate(fr): row.paste(im, (k * FW, 30))
            rows.append(row)
        head = Image.new("RGB", (FW * 3, 300), "white"); d = ImageDraw.Draw(head)
        if photo:
            ph = Image.open(photo).convert("RGB"); ph.thumbnail((420, 290)); head.paste(ph, (5, 5))
        else:
            for k, line in enumerate(("NO PRODUCT PHOTO", "in product-photos/:", "test 1 cannot be judged")):
                d.text((10, 100 + k * 32), line, fill=(200, 0, 0), font=_font(24))
        d.text((440, 10), t.name, fill=(0, 0, 0), font=_font(20))
        d.text((440, 40), "cut %s" % h, fill=(0, 0, 0), font=_font(16))
        d.text((440, 60), "ACTOR A: " + who[:62], fill=(0, 0, 0), font=_font(16))
        if len(who) > 62: d.text((440, 80), "         " + who[62:124], fill=(0, 0, 0), font=_font(16))
        d.text((440, 102), "voice: %s" % ((v or {}).get("voice") or "?"), fill=(0, 0, 0), font=_font(16))
        tests = ["1 the product keeps its shape, parts, size, place, finish (vs the photo)",
                 "2 nothing moves without a hand moving it", "3 one person, the same person as ACTOR A",
                 "4 bodies possible, nobody cut in half", "5 picture matches the words; voice gender",
                 "6 no blend, burned text, cloned props, hallucination"]
        for k, line in enumerate(tests): d.text((440, 130 + k * 27), line, fill=(150, 0, 0), font=_font(16))
        sheet = Image.new("RGB", (FW * 3, 300 + sum(r.height for r in rows)), "white"); sheet.paste(head, (0, 0)); y = 300
        for r in rows: sheet.paste(r, (0, y)); y += r.height
        sheet.save(os.path.join(week_dir, "qc", re.sub(r'[\/:*?"<>|]', "-", t.name) + ".jpg"), quality=82)
    json.dump(cut, open(os.path.join(week_dir, "plan", "cut.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return cut


def _gender_of_voice(voice):
    b = json.load(open(os.path.join(ROOT, "brand", "brands.json"), encoding="utf-8"))
    for br in b.values() if isinstance(b, dict) else []:
        if isinstance(br, dict):
            for gen, name in (br.get("voices") or {}).items():
                if name == voice: return gen
    return None


def gate(week_dir, tls):
    """Reasons a timeline may not be written: no passed review of this exact cut, or a voice of the other gender."""
    p = os.path.join(week_dir, "qc.json"); qc = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    week = _week(week_dir); out = []
    for t in tls:
        pieces = getattr(t, "pieces", None)
        if not pieces: out.append("%s: no final cut to review" % t.name); continue
        if (getattr(t, "cfg", {}) or {}).get("catalog", True) is False:  # Nov 19: "catalog": false let unreviewed footage through
            out.append("%s: \"catalog\": false switches off the shot review; remove it" % t.name); continue
        r = qc.get(t.name) or {}
        if r.get("cut") != cut_hash(pieces): out.append("%s: this cut (%s) was never reviewed against references/fundamentals.md" % (t.name, cut_hash(pieces)))
        elif not r.get("pass"): out.append("%s: review failed: %s" % (t.name, r.get("fails")))
        g, v = _video(week, t.name)
        sku = (g or {}).get("sku", "")[:10]
        if not (sku and glob.glob(os.path.join(week_dir, "product-photos", "*%s*" % sku))):
            out.append("%s: no product photo in product-photos/ (test 1, the product's shape, cannot be judged)" % t.name)
        if v:
            pg, vg = (v.get("cast") or {}).get("gender"), _gender_of_voice(v.get("voice"))
            if pg in ("man", "woman") and vg and pg != vg:
                out.append("%s: a %s on screen voiced by %s (a %s's voice): re-voice it" % (t.name, pg, v.get("voice"), vg))
    return out
