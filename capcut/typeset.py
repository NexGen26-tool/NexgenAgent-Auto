"""The type system of the CapCut build (references/typography.md, templates/type_styles.json).

Two jobs, both called by build_project.Timeline:
  restyle(...)  sets every on-screen line in the style the ad's argument asks for (font pairing, size hierarchy,
                colour, the one emphasis, placement, finish) instead of one fixed house look;
  key_times(...) finds when the voice says the words each line carries, so a line appears with its words, not at
                the start of a sentence whose first words are about something else (owner, Nov 16: "text overlays
                tend to appear way before the scripts say anything related").
"""
import copy, glob, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TS = json.load(open(os.path.join(HERE, "templates", "type_styles.json"), encoding="utf-8"))
SAFE_X = 0.86          # text stays inside x +-0.86 of the canvas (Reels icons sit on the right edge)
LEAD = 1.12  # line height / size: stacked lines sit close, one block (owner, Nov 18: "don't put it too far")
SHADOW = {"has_shadow": True, "shadow_color": "#000000", "shadow_alpha": 0.85, "shadow_smoothing": 0.9,
          "shadow_distance": 3.0, "shadow_angle": -45.0, "shadow_point": {"x": 0.6363961030678928, "y": -0.6363961030678927}}
STOP = set("a an the and or but so to of in on at for with by from it its it's is are was were my your our their this "
           "that these those i you we they me be as not no just one than then into up out all".split())
DIGIT_WORD = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight",
              "9": "nine", "10": "ten", "16": "sixteen", "20": "twenty", "22": "twenty", "42": "forty", "45": "forty",
              "48": "forty", "54": "fifty", "55": "fifty", "60": "sixty", "65": "sixty", "70": "seventy", "75": "seventy",
              "85": "eighty"}


def style_for(cfg):
    """The timeline's style name and spec: capcut.json "type", else the format's (templates/type_styles.json
    "by_format"); "house" (or no match) keeps the original house edit."""
    name = cfg.get("type") or TS["by_format"].get(cfg.get("format", ""), "house")
    return name, TS["styles"].get(name)


# ---------------------------------------------------------------------------------------------------- fonts, measure
def fonts(effects, notes):
    """{key: (resource id, file path)} for the style fonts CapCut has downloaded; a missing one falls back to the sans."""
    out, fb = {}, None
    for key, f in TS["fonts"].items():
        hits = glob.glob("%s/%s/*/%s" % (effects, f["id"], f["file"]))
        out[key] = (f["id"], hits[0].replace("\\", "/")) if hits else None
    fb = out.get("sans")
    for key, v in list(out.items()):
        if v is None:
            notes.append("font %s not downloaded in CapCut: %s set in the sans for now (use it once in CapCut, then "
                         "--replace)" % (TS["fonts"][key]["name"], key))
            out[key] = fb
    return out


_PIL = {}
def _font(path):
    from PIL import ImageFont
    if path not in _PIL: _PIL[path] = ImageFont.truetype(path, 100)
    return _PIL[path]


def line_widths(parts, F, K, scale):
    """Canvas width (x units, 2 = frame width) of each text line of a rich text, parts = [(text, font, size, col)]."""
    lines, cur = [], 0.0
    for t, fk, size, _ in parts:
        chunks = t.split("\n")
        for i, ch in enumerate(chunks):
            if i: lines.append(cur); cur = 0.0
            if ch: cur += _font(F[fk][1]).getlength(ch) * size * scale * K
    lines.append(cur)
    return [w for w in lines]


def heights(parts, scale, K):
    """Canvas height (y units, 2 = frame height) of a rich text: each text line at 1.25 x its largest size."""
    rows, cur = [], 0.0
    for t, fk, size, _ in parts:
        for i, ch in enumerate(t.split("\n")):
            if i: rows.append(cur); cur = 0.0
            cur = max(cur, size)
    rows.append(cur)
    return sum(r * 100 * scale * K * LEAD for r in rows if r) * (1080 / 1920)


# ---------------------------------------------------------------------------------------------------- restyle
def hex_rgb(h): return [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
def u16(s): return len(s.encode("utf-16-le")) // 2


def set_rich(mat, parts, F, finish, align="center", spacing=None, italic=False):
    """parts = [(text, font key, size, "#rrggbb")]: one CapCut rich text in the style's faces and colours; italic
    slants the sans (the display face is italic by itself)."""
    c = json.loads(mat["content"]); base = c["styles"][0]; styles, text = [], ""
    for t, fk, size, col in parts:
        st = copy.deepcopy(base); fid, fpath = F[fk]
        st["font"] = {"path": fpath, "id": fid}; st["size"] = size
        st["fill"] = {"content": {"solid": {"color": hex_rgb(col)}, "render_type": "solid"}}
        st.pop("italic", None)
        if italic: st["italic"] = True
        if finish == "outline": st["strokes"] = [{"width": 0.06, "mode": 0, "content": {"solid": {"color": [0, 0, 0]}, "render_type": "solid"}}]
        else: st.pop("strokes", None)
        st["range"] = [u16(text), u16(text) + u16(t)]; styles.append(st); text += t
    mat["content"] = json.dumps({"styles": styles, "text": text}, ensure_ascii=False)
    fid, fpath = F[parts[0][1]]
    mat.update(font_path=fpath, font_resource_id=fid, text_color=parts[0][3], alignment={"left": 0, "center": 1, "right": 2}[align])
    mat["border_width"] = 0.05 if finish == "outline" else 0.0
    mat.update(copy.deepcopy(SHADOW))  # every text, every style: the overlay reads on any picture (owner, Nov 18)
    mat["letter_spacing"] = min(spacing or 0.0, 0.02)  # letters close enough to read as one word (owner, Nov 18)
    mat["line_spacing"] = 0.0
    for k in ("words", "current_words"): mat[k] = {"start_time": [], "end_time": [], "text": []}


def place(seg, parts, F, K, align, y, max_w, top=None):
    """Scale a text to fit max_w and set its position; y is the centre (or, with top, the top edge). Returns the
    height it takes (y units)."""
    w = max(line_widths(parts, F, K, 2.0)) or 0.01
    sc = min(2.0, 2.0 * max_w / w); w = w * sc / 2.0
    h = heights(parts, sc, K)
    if top is not None: y = top - h / 2
    x = {"left": -SAFE_X + w / 2, "center": 0.0, "right": SAFE_X - w / 2}[align]
    seg["clip"]["scale"] = {"x": sc, "y": sc}; seg["uniform_scale"] = {"on": True, "value": sc}
    seg["clip"]["transform"] = {"x": x, "y": y}
    return h


def place_at(seg, parts, F, K, align, sc, y, x=None):
    """Set a text at scale sc with its centre at y (and x, else by its alignment). Returns its width (x units)."""
    w = max(line_widths(parts, F, K, sc)) / 1.0
    if x is None: x = {"left": -SAFE_X + w / 2, "center": 0.0, "right": SAFE_X - w / 2}[align]
    seg["clip"]["scale"] = {"x": sc, "y": sc}; seg["uniform_scale"] = {"on": True, "value": sc}
    seg["clip"]["transform"] = {"x": x, "y": y}
    return w


def cased(t, case): return t.upper() if case == "upper" else t


def bare(t):
    """On-screen words end without a full stop (owner, Nov 17: removed by hand from "sits within reach.", "Stand on
    wood.", "On a shelf."); a question mark or an exclamation stays."""
    s = t.rstrip()
    while s.endswith(".") and not s.endswith(".."): s = s[:-1].rstrip()
    return s + t[len(t.rstrip()):]


def restyle(d, r, cfg, spec, K, effects, mat, seg_of, notes, inner=None, clone=None):
    """Sets every text of a timeline (house edit roles r) in the style spec. cfg holds the house-edit line texts
    (line1 [subject, link, tension], line2 [setup, payoff], line3 [left, right], line4, line5 [first, punch], cta) and
    from the build: _line1b (when the hook's link words are spoken, 0 = with the subject), _line5s (when the voice
    reaches the scarcity words, 0 = none) and _scarcity ([accent, rest] of the brand's scarcity line on screen).
    clone(seg, mat) copies a text clip onto a new track (build_project.add_text_track)."""
    F = fonts(effects, notes); fin = spec.get("finish", "shadow"); num = spec.get("numbered")
    join = lambda x: re.sub(r"\s+", " ", " ".join(x) if isinstance(x, list) else str(x)).strip()
    us = lambda s: int(round(s * 1e6))

    # Line 1: subject on its own line, then the linking words and the tension word(s). The subject is up from the
    # first frame; the rest comes with its own words when the voice says them (owner, Nov 17: V3's hook built up
    # word by word), as a second clip in the same place.
    s1 = spec["line1"]; (f0, z0, c0), (f1, z1, c1), (f2, z2, c2) = s1["parts"]
    big, small, accent = cfg["line1"]
    head = [(cased(big.strip(), s1.get("case0")), f0, z0, c0)]
    if small.strip() and (f1, z1) != (f2, z2): small = small.rstrip() + "  "  # a visible gap where the face or size changes (owner, Nov 18: "our eveningsmoved outside")
    rest = [(small, f1, z1, c1), (bare(accent), f2, z2, c2)]
    parts = [(head[0][0] + "\n",) + head[0][1:]] + rest
    setup_first = (cfg.get("line1_order") or s1.get("order")) == "setup_first"
    if setup_first:  # owner, Nov 18 ("Every year / I redecorate"): the small setup and its accent lead, the statement big under it
        parts = [(small, f1, z1, c1), (bare(accent) + "\n", f2, z2, c2)] + head
    m = mat(d, "texts", r["line1"]); set_rich(m, parts, F, fin, s1["align"]); s = seg_of(d, m["id"])
    h = place(s, parts, F, K, s1["align"], s1["y"], s1["max_w"])
    t1 = cfg.get("_line1b") or 0.0
    if t1 > 0 and clone is not None and not setup_first:
        sc = s["clip"]["scale"]["x"]; y = s["clip"]["transform"]["y"]
        ha, hb = heights(head, sc, K), heights(rest, sc, K)
        nb, mb = clone(s, m)
        set_rich(m, head, F, fin, s1["align"]); place_at(s, head, F, K, s1["align"], sc, y + h / 2 - ha / 2)
        set_rich(mb, rest, F, fin, s1["align"]); place_at(nb, rest, F, K, s1["align"], sc, y - h / 2 + hb / 2)
        a0 = s["target_timerange"]["start"]; e0 = a0 + s["target_timerange"]["duration"]
        nb["target_timerange"] = {"start": us(t1), "duration": e0 - us(t1)}

    # Line 2: the punchline (setup + payoff); numbered: "1" over the first reason
    s2 = spec["line2"]; setup, payoff = cfg["line2"][0], bare(in_sentence(cfg["line2"][1]))
    if num: setup, payoff = "1", join([cfg["line2"][0], payoff])
    if inner is not None:
        sm, pm = mat(inner, "texts", r["setup"]), mat(inner, "texts", r["payoff"])
        al = spec["line3"]["align"]
        ps = [(setup.rstrip() if num else setup, s2["setup"][0], s2["setup"][1], s2["setup"][2])]
        pp = [(payoff, s2["payoff"][0], s2["payoff"][1], s2["payoff"][2])]
        set_rich(sm, ps, F, fin, al); set_rich(pm, pp, F, fin, al)
        ss, sp = seg_of(inner, sm["id"]), seg_of(inner, pm["id"])
        hs = place(ss, ps, F, K, al, 0, 1.6); hp = place(sp, pp, F, K, al, 0, s1["max_w"])
        y = s2["y"]; ss["clip"]["transform"]["y"] = y + hp / 2 + hs / 2; sp["clip"]["transform"]["y"] = y
        comp = next(s for t in d["tracks"] for s in t["segments"] if r["compound"] == s["material_id"] or r["compound"] in s["extra_material_refs"])
        comp["clip"]["transform"] = {"x": 0.0, "y": 0.0}

    # Line 3: two halves, stacked; "stagger" sets the first half to the left and the second below it to the right
    # (owner, Nov 17: done by hand on V1, V2, V8, V9 and V10)
    s3 = spec["line3"]; a, b = cfg["line3"]; a, b = bare(a), bare(b)
    if num: a, b = "2", "\n".join(bare(join(x)) for x in cfg["line3"])  # the two halves on two lines, never run together
    (fa, za, ca), (fb, zb, cb) = s3["parts"]
    pa, pb = [(a, fa, za, ca)], [(b, fb, zb, cb)]
    ma, mb = mat(d, "texts", r["line3a"]), mat(d, "texts", r["line3b"])
    al3 = "center" if s3.get("layout") == "stagger" else s3["align"]
    set_rich(ma, pa, F, fin, al3); set_rich(mb, pb, F, fin, al3)
    sa, sb = seg_of(d, ma["id"]), seg_of(d, mb["id"])
    if num:  # the numeral sits right above its reason at the reason's own scale, never floating apart (owner, Nov 18)
        place(sb, pb, F, K, al3, s3["y"], s3["max_w"]); scb = sb["clip"]["scale"]["x"]
        hb = heights(pb, scb, K); hn = heights(pa, scb, K)
        place_at(sa, pa, F, K, al3, scb, s3["y"] + hb / 2 + hn / 2 + 0.005)
    else:
        ha = place(sa, pa, F, K, al3, s3["y"], s3["max_w"])
        place(sb, pb, F, K, al3, 0, s3["max_w"], top=s3["y"] - ha / 2)
    if s3.get("layout") == "stagger":
        edge = s3.get("edge", 0.8)
        wa = max(line_widths(pa, F, K, sa["clip"]["scale"]["x"])); wb = max(line_widths(pb, F, K, sb["clip"]["scale"]["x"]))
        sa["clip"]["transform"]["x"] = min(0.0, -edge + wa / 2); sb["clip"]["transform"]["x"] = max(0.0, edge - wb / 2)

    # Line 4, Line 5, CTA
    s4 = spec["line4"]; t4 = bare(cfg["line4"])
    if num: parts = [("3\n", "display", 11.0, s4["parts"][0][2]), (t4, s4["parts"][-1][0], s4["parts"][-1][1], s4["parts"][-1][2])]
    else: parts = [(cased(t4, s4.get("case")), s4["parts"][0][0], s4["parts"][0][1], s4["parts"][0][2])]
    m = mat(d, "texts", r["line4"]); set_rich(m, parts, F, fin, s4["align"], s4.get("spacing"), s4.get("italic", False))
    place(seg_of(d, m["id"]), parts, F, K, s4["align"], s4["y"], s4["max_w"])
    s5 = spec["line5"]; p, q = cfg["line5"]; (f5, z5, c5), (g5, y5, d5) = s5["parts"]
    parts = [(p.strip() + "\n", f5, z5, c5), (bare(q), g5, y5, d5)]
    m5 = mat(d, "texts", r["line5"]); set_rich(m5, parts, F, fin, s5["align"])
    s5g = seg_of(d, m5["id"]); place(s5g, parts, F, K, s5["align"], s5["y"], s5["max_w"])
    sc = spec["cta"]; ct = cased(bare(cfg["_cta"]), sc.get("case")); (fc, zc, cc), = sc["parts"]
    parts = [(ct, fc, zc, cc)]
    m = mat(d, "texts", r["cta"]); set_rich(m, parts, F, fin, sc["align"], sc.get("spacing"))
    place(seg_of(d, m["id"]), parts, F, K, sc["align"], sc["y"], sc["max_w"])

    # the scarcity beat: the offer, then the brand's scarcity line in the same place when the voice reaches it
    # (owner, Nov 17: "Limited / monthly order" added by hand to V1, V5, V6 and V10)
    t5 = cfg.get("_line5s") or 0.0; sca = cfg.get("_scarcity")
    if t5 > 0 and sca and clone is not None:
        a0 = s5g["target_timerange"]["start"]; e0 = a0 + s5g["target_timerange"]["duration"]
        if us(t5) - a0 >= us(0.8) and e0 - us(t5) >= us(0.8):
            ns, nm = clone(s5g, m5)
            parts = [(sca[0].strip() + "\n", g5, y5, d5), (sca[1].strip(), f5, z5 + 1.0, c5)]
            set_rich(nm, parts, F, fin, s5["align"]); place(ns, parts, F, K, s5["align"], s5["y"], s5["max_w"])
            s5g["target_timerange"]["duration"] = us(t5) - us(0.05) - a0
            ns["target_timerange"] = {"start": us(t5), "duration": e0 - us(t5)}


def in_sentence(p):
    """The house edit capitalises Line 2's payoff ("Give it a Focal point"); in the type styles the payoff continues its
    setup's sentence, so it keeps the sentence's case ("Your cup has a home", "Now I reach for it first"). "I", an
    acronym and the store names keep their capitals."""
    w = (p.strip().split() or [""])[0]
    if w in ("I", "I'm", "I'd", "I've", "I'll") or (len(w) > 1 and w.isupper()) or w in ("Spry", "ET"): return p
    return p[:1].lower() + p[1:] if p[:1].isupper() else p


# ---------------------------------------------------------------------------------------------------- key words
def words_of(sentence):  # the same words, in the same order, as vo_align.ps1 gives the recogniser
    return re.sub(r"[^a-z0-9' ]", " ", sentence.lower().replace("-", " ")).split()


def _norm(w): return re.sub(r"[^a-z0-9]", "", w.lower())


def align_windows(vo_path, sentences, ffmpeg):
    """Windows' own recogniser (capcut/vo_align.ps1) on the voice-over: {sentence index: [start s of each word]}
    in voice-file seconds, or {} when it is not available (Mac, no recogniser)."""
    if os.name != "nt" or not ffmpeg: return {}
    tmp = tempfile.mkdtemp(); wav, txt = os.path.join(tmp, "vo.wav"), os.path.join(tmp, "vo.txt")
    try:
        subprocess.run([ffmpeg, "-v", "error", "-y", "-i", vo_path, "-af", "highpass=f=120,lowpass=f=6000", "-ac", "1",
                        "-ar", "16000", wav], check=True, capture_output=True)
        open(txt, "w", encoding="utf-8").write("\n".join(sentences) + "\n")
        out = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                              os.path.join(HERE, "vo_align.ps1"), wav, txt], capture_output=True, text=True, timeout=120).stdout
    except (OSError, subprocess.SubprocessError):
        return {}
    res = {}
    for line in out.splitlines():
        p = line.split()
        if len(p) < 4: continue
        try: i, a = int(p[0]), float(p[1]); ws = [a + float(x) for x in p[3].split(",") if x != "-"]
        except ValueError: continue
        if i not in res and len(ws) == len(words_of(sentences[i])): res[i] = ws
    return res


def onset(line_text, sentence, word_t, start, end):
    """When the voice says the first word the line carries (a word of the line that is not a stop word, by its first
    four letters; a number by its spoken first word). word_t: start of each word of the sentence, or None (then the
    word's place in the sentence by letters estimates it). Returns (time, matched word or None)."""
    sw = words_of(sentence)
    keys = []
    for w in words_of(line_text):
        n = _norm(w)
        if not n or n in STOP: continue
        keys.append(DIGIT_WORD.get(n, n))
    for k, w in enumerate(sw):
        n = _norm(w)
        if n in STOP or not n: continue
        if any(n == x or (len(n) >= 4 and len(x) >= 4 and n[:4] == x[:4]) for x in keys):
            if word_t: return word_t[k], w
            before = sum(len(_norm(x)) for x in sw[:k]); total = sum(len(_norm(x)) for x in sw) or 1
            return start + (end - start) * before / total, w
    return start, None
