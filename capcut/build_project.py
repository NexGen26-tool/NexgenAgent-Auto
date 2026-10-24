#!/usr/bin/env python3
"""Build a CapCut project (CapCut 9.x on Mac or Windows) with one timeline per video, every timeline already in the house edit:
Montserrat text with black stroke, a big/small/orange hook (Line 1), the animated two-part title (Line 2), the split
Line 3, the yellow last phrase of Line 5, the CTA, the brand logo on top, Smoke out at the end, the voice-over on
its own track with the clip's own sound off, and the brand's music bed (brand/brands.json "music").

Each timeline is cut to its voice-over: pauses are shortened, the text lines are fitted to the speech, and the
timeline ends CTA_HOLD seconds after the last word (Negen's 20 s video usually has 3-4 s of silence at the end).

The house edit is a real edited timeline (capcut/templates/house_edit.json). It is cloned for each video and only the
words, the footage and the logo change, so every timeline opens looking like the approved one.

  python capcut/build_project.py work/<week>/capcut.json            # dry run, prints what it would build
  python capcut/build_project.py work/<week>/capcut.json --save     # writes the project (CapCut must be closed)
  python capcut/build_project.py --check                            # can this computer's CapCut take built projects?

On a Mac use python3. Windows needs ffmpeg (setup_check.py says how to install it).

Config format: see capcut/example.json.
"""
import json, os, sys, copy, shutil, subprocess, time, re, uuid, struct, glob

HERE = os.path.dirname(os.path.abspath(__file__))
for _s in (sys.stdout, sys.stderr): _s.reconfigure(encoding="utf-8", errors="replace")  # names can be Vietnamese
ROOT = os.path.dirname(HERE)
WINDOWS = os.name == "nt"
HOME = os.path.expanduser("~").replace("\\", "/")  # CapCut writes paths with forward slashes on both systems
if WINDOWS:
    _CAPCUT = os.environ.get("LOCALAPPDATA", HOME + "/AppData/Local").replace("\\", "/") + "/CapCut/User Data"
    DRAFTS = _CAPCUT + "/Projects/com.lveditor.draft"
    EFFECTS = _CAPCUT + "/Cache/effect"
    MEDIA = HOME + "/Videos/CapCut Media"
else:
    DRAFTS = HOME + "/Movies/CapCut/User Data/Projects/com.lveditor.draft"
    EFFECTS = HOME + "/Library/Containers/com.lemon.lvoverseas/Data/Movies/CapCut/User Data/Cache/effect"
    MEDIA = HOME + "/Movies/CapCut Media"  # CapCut on Mac is sandboxed: it reads ~/Movies without asking
DRAFTS = os.environ.get("CAPCUT_DRAFTS", DRAFTS).replace("\\", "/")  # override if CapCut keeps projects elsewhere
MUSIC = os.path.dirname(EFFECTS) + "/music"  # CapCut's library tracks, saved here once they are used in the app
TEMPLATE_EFFECTS = "{HOME}/Library/Containers/com.lemon.lvoverseas/Data/Movies/CapCut/User Data/Cache/effect"
US = 1_000_000
PAUSE = 0.4     # a voice-over pause at least this long is shortened ...
GAP = 0.25      # ... to this
CTA_HOLD = 1.5  # the CTA stays this long after the voice-over ends; the timeline ends there
VO_SPEED = 1.08 # the Negen voice-over is a little slow for a ~16 s ad
BRANDS = json.load(open(ROOT + "/brand/brands.json", encoding="utf-8"))
ROLES = json.load(open(HERE + "/templates/house_edit_roles.json", encoding="utf-8"))
UUID = re.compile(r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$")

# fonts and animations the house edit uses; CapCut downloads them the first time they are picked in the app
NEEDED = {"7542214368361057553": "font Montserrat", "7152810713856086529": "font PT Sans",
          "7462286539255500037": "font HV-Analogue-Bold-Italic", "7229983825080619522": "animation Smoke (out)",
          "6740868384637850120": "animation Zoom 1 (in)"}


def uid(): return str(uuid.uuid4()).upper()
def us(x): return int(round(x * US))
def u16(s): return len(s.encode("utf-16-le")) // 2


def _measure_font():
    from PIL import ImageFont
    found = glob.glob(EFFECTS + "/7542214368361057553/*/font.ttf")
    fallback = "C:/Windows/Fonts/arialbd.ttf" if WINDOWS else "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    path = found[0] if found else fallback
    return ImageFont.truetype(path, 100)


MEASURE = _measure_font()
K = 1.8 / (7 * 1.833 * MEASURE.getlength("It casts its own shadow"))  # canvas units per size*scale*px (Line 4 = 90% wide)
EDGE = 0.90  # the split Line 3 sits on the -0.90 / +0.90 edges


def width(text, size, scale):
    return max(MEASURE.getlength(l) for l in text.split("\n")) * size * scale * K


def mp4_info(p):
    b = open(p, "rb").read()
    i = b.find(b"mvhd"); ver = b[i + 4]
    ts, dur = struct.unpack(">II", b[i + 16:i + 24]) if ver == 0 else struct.unpack(">IQ", b[i + 24:i + 36])
    j = b.find(b"tkhd"); off = 76 if b[j + 4] == 0 else 88
    w, h = struct.unpack(">II", b[j + 4 + off:j + 4 + off + 8])
    return dur / ts, (w >> 16) or 720, (h >> 16) or 1280


def image_size(p):
    from PIL import Image
    with Image.open(p) as im: return im.size


def capcut_running():
    if WINDOWS:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq CapCut.exe"], capture_output=True, text=True).stdout
        return "CapCut.exe" in out
    return subprocess.run(["pgrep", "-x", "CapCut"], capture_output=True).returncode == 0


def draft_format():
    """Which file CapCut keeps a project in here (draft_info.json on Mac, often draft_content.json on Windows),
    and whether it is plain JSON. Newer CapCut builds can encrypt it; then no script can build projects here."""
    names = ("draft_info.json", "draft_content.json")
    projects = sorted((p for p in glob.glob(DRAFTS + "/*/") if any(os.path.exists(p + n) for n in names)),
                      key=os.path.getmtime, reverse=True)
    if not projects: return None, "No CapCut project found in " + DRAFTS + ". Make any project in CapCut, then retry."
    for p in projects[:5]:
        for n in names:
            if os.path.exists(p + n):
                try:
                    json.load(open(p + n, encoding="utf-8")); return n, "ok"
                except (ValueError, UnicodeDecodeError):
                    pass
    return None, ("This CapCut keeps its projects encrypted, so projects cannot be built for it. "
                  "Use the text sheet instead: python capcut/text_sheet.py work/<week>/capcut.json")


def link_media(src, folder, name=None):
    os.makedirs(folder, exist_ok=True)
    dst = folder + "/" + (name or os.path.basename(src))
    if not os.path.exists(dst):
        try: os.link(src, dst)
        except OSError: shutil.copy(src, dst)
    return dst


def find_ffmpeg():
    """ffmpeg on PATH, or where winget put it (a fresh winget install is not on PATH until Claude Desktop restarts)."""
    found = shutil.which("ffmpeg")
    if found or not WINDOWS: return found
    winget = os.environ.get("LOCALAPPDATA", HOME + "/AppData/Local") + "/Microsoft/WinGet"
    hits = glob.glob(winget + "/Links/ffmpeg.exe") + glob.glob(winget + "/Packages/Gyan.FFmpeg*/*/bin/ffmpeg.exe")
    return hits[0] if hits else None


def extract_vo(video, folder):
    """The Negen file has the voice-over mixed in; pull it out as its own audio file."""
    dst = folder + "/" + os.path.splitext(os.path.basename(video))[0] + " - VO.m4a"
    if not os.path.exists(dst):
        ffmpeg = find_ffmpeg()
        if ffmpeg:
            subprocess.run([ffmpeg, "-v", "error", "-y", "-i", video, "-vn", "-c:a", "copy", dst], check=True)
        elif shutil.which("afconvert"):
            subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "192000", video, dst], check=True)
        else:
            raise SystemExit("ffmpeg is missing: run setup_check.py and install it.")
    return dst


def set_text(mat, parts):
    """parts = [(text, index of the template style to copy)]: font, size, colour and italic stay the house edit's."""
    c = json.loads(mat["content"]); styles, text = [], ""
    for t, i in parts:
        st = copy.deepcopy(c["styles"][i]); st["range"] = [u16(text), u16(text) + u16(t)]
        styles.append(st); text += t
    mat["content"] = json.dumps({"styles": styles, "text": text}, ensure_ascii=False)
    for k in ("words", "current_words"): mat[k] = {"start_time": [], "end_time": [], "text": []}


def remap_ids(d):
    ids = set()
    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ("id", "combination_id") and isinstance(v, str) and UUID.match(v): ids.add(v)
                walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(d)
    raw = json.dumps(d, ensure_ascii=False); m = {i: uid() for i in ids}
    for a, b in m.items(): raw = raw.replace(a, b)
    return json.loads(raw), m


def mat(d, key, mid): return next(x for x in d["materials"][key] if x["id"] == mid)
def seg_of(d, mid): return next(s for t in d["tracks"] for s in t["segments"] if s["material_id"] == mid)


def speech_spans(path, dur):
    """The parts of the voice-over to keep, in seconds: everything except the start and end silence, with every
    pause of PAUSE or more cut down to GAP. Without ffmpeg the voice-over stays whole."""
    ffmpeg = find_ffmpeg()
    if not ffmpeg: return [(0.0, dur)]
    err = subprocess.run([ffmpeg, "-hide_banner", "-i", path, "-af", "silencedetect=n=-35dB:d=%s" % PAUSE, "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    pad, spans, pos = GAP / 2, [], 0.0
    for a, b in zip(starts, ends + [dur] * (len(starts) - len(ends))):
        if a <= 0.05: pos = max(0.0, b - pad); continue  # silence before the first word
        spans.append((pos, min(dur, a + pad))); pos = b - pad
    if pos < dur - 0.05 and (not ends or len(ends) == len(starts) and ends[-1] < dur - 0.05): spans.append((pos, dur))
    return [(a, b) for a, b in spans if b - a > 0.05] or [(0.0, dur)]


def add_audio(d, tp, mat, spans, volume, name, speed=1.0):
    """One audio track; spans = [(source start, source end)] in microseconds, laid end to end from 0."""
    m = copy.deepcopy(tp["mat"]); m["id"] = uid(); m.update(mat)
    d["materials"].setdefault("audios", []).append(m)
    segs, at = [], 0
    for a, b in spans:
        s = copy.deepcopy(tp["seg"]); s["id"] = uid(); s["material_id"] = m["id"]; refs = []
        for k, items in tp["extra"].items():
            for it in items:
                n = copy.deepcopy(it); n["id"] = uid(); d["materials"].setdefault(k, []).append(n); refs.append(n["id"])
                if k == "speeds": n["speed"] = speed
        s["extra_material_refs"] = refs; length = int((b - a) / speed)
        s["source_timerange"] = {"start": a, "duration": b - a}; s["target_timerange"] = {"start": at, "duration": length}
        s["volume"] = volume; s["last_nonzero_volume"] = 1.0; s["speed"] = speed
        s["render_index"] = 0; s["track_render_index"] = len(d["tracks"])
        segs.append(s); at += length
    d["tracks"].append({"id": uid(), "type": "audio", "segments": segs, "flag": 0, "attribute": 0,
                        "name": name, "is_default_name": False})


def add_vo(d, path, spans):
    tp = json.load(open(HERE + "/templates/vo_track.json", encoding="utf-8"))
    dur = mp4_info(path)[0]  # an .m4a has the same header as an .mp4
    cut, at = [], 0
    for a, b in spans:  # keep inside the timeline
        a, b = us(a), us(b); b = min(b, a + int((d["duration"] - at) * VO_SPEED))
        if b > a: cut.append((a, b)); at += int((b - a) / VO_SPEED)
    add_audio(d, tp, {"path": path, "name": os.path.splitext(os.path.basename(path))[0], "duration": us(dur)}, cut, 1.0,
              "Voice-over", VO_SPEED)


def add_music(d, music):
    """The brand's music bed (a CapCut library track) under the whole timeline, with a short fade out."""
    path = MUSIC + "/" + music["file"]
    if not os.path.exists(path): return False
    tp = json.load(open(HERE + "/templates/music_track.json", encoding="utf-8"))
    mat = {"path": path, "name": music["name"], "music_id": music["music_id"],
           "duration": us(music["duration"])}
    add_audio(d, tp, mat, [(0, min(d["duration"], us(music["duration"])))], music["volume"], "Music")
    return True


MIN_PIECE = 0.5   # clean footage shorter than this is not used
REPLACE_MIN = 1.0 # a bad stretch this long or longer is replaced; a shorter one (a blend) is simply cut out


def clean_parts(name, dur, shots):
    """The usable stretches of one video, from its shot check: everything minus the bad stretches, which are
    widened to a hard cut within 0.3 s."""
    e = shots[name]; cut_at = e.get("cuts", [])
    def snap(t, side):
        near = [c for c in cut_at if abs(c - t) <= 0.3 and (c <= t if side < 0 else c >= t)]
        return min(near, key=lambda c: abs(c - t)) if near else t
    bad = sorted((max(0.0, snap(a, -1)), min(dur, snap(b, 1))) for a, b, *_ in e["bad"])
    parts, pos = [], 0.0
    for a, b in bad:
        if a - pos >= MIN_PIECE: parts.append((pos, a))
        pos = max(pos, b)
    if dur - pos >= MIN_PIECE: parts.append((pos, dur))
    return parts, bad


def plan_footage(main, total, shots, pool):
    """[(file, source start, length)] in seconds filling 0..total: the main video without its bad stretches. A bad
    stretch of REPLACE_MIN or more is filled with clean, unused footage from the pool (the same video's spare first,
    at the same moment when that is clean, then the group's other videos); a shorter one is cut and the main video
    runs on. Returns the pieces and a note per replacement."""
    name = os.path.basename(main); dur = mp4_info(main)[0]
    parts, bad = clean_parts(name, dur, shots)
    avail = []  # [(priority, file, start, end)] clean pool footage, the first 0.3 s of each stretch skipped
    for i, f in enumerate(pool):
        for a, b in clean_parts(os.path.basename(f), mp4_info(f)[0], shots)[0]:
            if b - a - 0.3 >= MIN_PIECE: avail.append([i, f, a + 0.3, b])
    pieces, notes, t = [], [], 0.0

    def fill(need, at):
        got = []
        while need >= MIN_PIECE and avail:
            same = [x for x in avail if x[0] == 0 and x[2] <= at and x[3] >= at + need]  # the spare, same moment
            long = sorted((x for x in avail if x[3] - x[2] >= need), key=lambda x: x[0])
            x = same[0] if same else long[0] if long else max(avail, key=lambda x: x[3] - x[2])
            a = at if same else x[2]; take = min(need, x[3] - a)
            got.append((x[1], a, take)); need -= take
            avail.remove(x)  # each stretch of pool footage is used once
            if a - x[2] >= MIN_PIECE: avail.append([x[0], x[1], x[2], a])
            if x[3] - (a + take) >= MIN_PIECE: avail.append([x[0], x[1], a + take, x[3]])
        return got

    for kind, a, b in sorted([("ok", a, b) for a, b in parts] + [("bad", a, b) for a, b in bad], key=lambda x: x[1]):
        if t >= total - 0.01: break
        if kind == "ok":
            take = min(b - a, total - t); pieces.append((main, a, take)); t += take
        elif b - a >= REPLACE_MIN:
            got = fill(min(b - a, total - t), a)
            for f, s, l in got: pieces.append((f, s, l)); t += l
            notes.append("%.1f-%.1f s replaced from %s" % (a, b, ", ".join(sorted({os.path.basename(f) for f, _, _ in got})) or "nothing (no clean footage left)"))
    if total - t >= 0.05:  # the main video ran out: finish with pool footage
        for f, s, l in fill(total - t, 0): pieces.append((f, s, l)); t += l
    return pieces, notes


def lay_footage(d, r, pieces, media_dir):
    """Replace the single footage segment with one segment per piece; Smoke out stays on the last one."""
    v = mat(d, "videos", r["video"]); s = seg_of(d, v["id"]); track = next(t for t in d["tracks"] if s in t["segments"])
    anim = {a["id"] for a in d["materials"]["material_animations"]}
    mats_by_path, segs, at = {v["path"]: v}, [], 0
    for i, (f, start, length) in enumerate(pieces):
        f = link_media(f, media_dir)
        if f not in mats_by_path:
            m = copy.deepcopy(v); m["id"] = uid(); dur_s, w, h = mp4_info(f)
            m.update({"path": f, "material_name": os.path.basename(f), "duration": us(dur_s), "width": w, "height": h})
            d["materials"]["videos"].append(m); mats_by_path[f] = m
        n = copy.deepcopy(s); n["id"] = uid(); n["material_id"] = mats_by_path[f]["id"]; refs = []
        last = i == len(pieces) - 1
        for ref in s["extra_material_refs"]:
            if ref in anim and not last: continue
            k, x = next((k, x) for k, xs in d["materials"].items() if isinstance(xs, list) for x in xs if isinstance(x, dict) and x.get("id") == ref)
            c = copy.deepcopy(x); c["id"] = uid(); d["materials"][k].append(c); refs.append(c["id"])
            if ref in anim:
                for an in c["animations"]:
                    if an["type"] == "out": an["start"] = us(length) - an["duration"]
        n["extra_material_refs"] = refs
        n["source_timerange"] = {"start": us(start), "duration": us(length)}
        n["target_timerange"] = {"start": at, "duration": us(length)}; at += us(length)
        segs.append(n)
    segs[-1]["target_timerange"]["duration"] = d["duration"] - segs[-1]["target_timerange"]["start"]  # no rounding gap
    segs[-1]["source_timerange"]["duration"] = segs[-1]["target_timerange"]["duration"]
    track["segments"] = segs


class Timeline:
    def __init__(self, cfg, media_dir, shots=None, pool=()):
        self.name = cfg["name"]
        brand = BRANDS[cfg["brand"]]
        video = link_media(os.path.expanduser(cfg["video"]), media_dir)
        logo = link_media(ROOT + "/brand/" + brand["logo"], media_dir)
        self.vo = extract_vo(video, media_dir)
        raw = open(HERE + "/templates/house_edit.json", encoding="utf-8").read()
        raw = raw.replace(TEMPLATE_EFFECTS, EFFECTS).replace("{HOME}", HOME)
        d, idm = remap_ids(json.loads(raw)); r = {k: idm[v] for k, v in ROLES.items()}

        # footage, clip sound off, Smoke out moved to the real end
        v = mat(d, "videos", r["video"]); dur_s, w, h = mp4_info(video); dur = us(dur_s)
        v.update({"path": video, "material_name": os.path.basename(video), "duration": dur, "width": w, "height": h})
        s = seg_of(d, v["id"]); s["volume"] = 0.0; s["last_nonzero_volume"] = 1.0
        s["source_timerange"] = {"start": 0, "duration": dur}; s["target_timerange"] = {"start": 0, "duration": dur}
        d["duration"] = dur; self.dur = dur
        for a in d["materials"]["material_animations"]:
            if a["id"] in s["extra_material_refs"]:
                for an in a["animations"]:
                    if an["type"] == "out": an["start"] = dur - an["duration"]

        # logo
        lg = mat(d, "videos", r["logo"]); lw, lh = image_size(logo)
        lg.update({"path": logo, "material_name": os.path.basename(logo), "width": lw, "height": lh})
        ls = seg_of(d, lg["id"]); sc = brand["logo_scale"]
        ls["clip"]["scale"] = {"x": sc, "y": sc}; ls["uniform_scale"] = {"on": True, "value": sc}

        # Line 1: big subject / small link words / accent phrase (orange italic)
        m = mat(d, "texts", r["line1"]); big, small, accent = cfg["line1"]
        set_text(m, [(big + " \n", 0), (small, 1), (accent, 2)])
        s1 = seg_of(d, m["id"]); sc = s1["clip"]["scale"]["x"]
        wmax = max(MEASURE.getlength(big) * 8.5, MEASURE.getlength(small) * 5.5 + MEASURE.getlength(accent) * 6) * sc * K
        if wmax > 2 * EDGE:
            sc *= 2 * EDGE / wmax; s1["clip"]["scale"] = {"x": sc, "y": sc}; s1["uniform_scale"]["value"] = sc

        # Line 2: the animated title clip, small italic setup + payoff word in the display font
        dm = mat(d, "drafts", r["compound"]); inner = dm["draft"]; setup, payoff = cfg["line2"]
        sm, pm = mat(inner, "texts", r["setup"]), mat(inner, "texts", r["payoff"]); ss = seg_of(inner, sm["id"])
        left = ss["clip"]["transform"]["x"] - width(json.loads(sm["content"])["text"], 6, ss["clip"]["scale"]["x"]) / 2
        set_text(sm, [(setup, 0)]); set_text(pm, [(payoff, 0)])
        ss["clip"]["transform"]["x"] = left + width(setup, 6, ss["clip"]["scale"]["x"]) / 2
        self.compound = (r["compound_draft"], inner)

        # Line 3: two staggered halves on the edges, one shared scale
        a, b = cfg["line3"]; ma, mb = mat(d, "texts", r["line3a"]), mat(d, "texts", r["line3b"])
        set_text(ma, [(a, 0)]); set_text(mb, [(b, 0)])
        sa, sb = seg_of(d, ma["id"]), seg_of(d, mb["id"]); sc = sa["clip"]["scale"]["x"]
        sc = min(sc, sc * 1.5 / max(width(a, 7, sc), width(b, 7, sc)))
        for sg, txt, side in ((sa, a, -1), (sb, b, 1)):
            sg["clip"]["scale"] = {"x": sc, "y": sc}; sg["uniform_scale"] = {"on": True, "value": sc}
            sg["clip"]["transform"]["x"] = side * (EDGE - width(txt, 7, sc) / 2)

        # Line 4, Line 5 (second line bigger, yellow), CTA
        set_text(mat(d, "texts", r["line4"]), [(cfg["line4"], 0)])
        p, q = cfg["line5"]; set_text(mat(d, "texts", r["line5"]), [(p + "\n", 0), (q, 1)])
        set_text(mat(d, "texts", r["cta"]), [(cfg.get("cta") or brand["cta"], 0)])

        # cut to the voice-over: pauses shortened, the timeline ends CTA_HOLD after the last word
        spans = speech_spans(self.vo, mp4_info(self.vo)[0])
        total = min(dur, us(sum(b - a for a, b in spans) / VO_SPEED + CTA_HOLD)); self.dur = total
        joints, at = [], 0  # where the shortened pauses sit on the timeline
        for a, b in spans[:-1]: at += us((b - a) / VO_SPEED); joints.append(at)
        self.retime(d, r, total, joints)
        # shot check: bad stretches (shots.json) cut out or replaced with clean footage from the spare / the group
        self.notes = None
        src = os.path.expanduser(cfg["video"])
        if shots and shots.get(os.path.basename(src), {}).get("checked"):
            pieces, self.notes = plan_footage(src, total / US, shots, pool)
            lay_footage(d, r, pieces, media_dir)
        add_vo(d, self.vo, spans)
        self.music = add_music(d, brand["music"]) if brand.get("music") else None
        self.d = d

    @staticmethod
    def retime(d, r, total, joints):
        """Shrink the house edit's 0-17 s text block to end where the voice ends; a change of line lands on a pause
        in the voice-over when one is within 0.8 s. Line 2's animated title keeps its own length."""
        def seg(role):  # the title clip's segment points at its draft through extra_material_refs
            return next(s for t in d["tracks"] for s in t["segments"]
                        if r[role] == s["material_id"] or r[role] in s["extra_material_refs"])
        def place(s, start, end): s["target_timerange"] = {"start": int(start), "duration": int(end - start)}
        def snap(t, lo, hi):
            near = [j for j in joints if lo < j < hi and abs(j - t) <= us(0.8)]
            return min(near, key=lambda j: abs(j - t)) if near else t
        tt = lambda role: seg(role)["target_timerange"]
        end5 = tt("line5")["start"] + tt("line5")["duration"]
        content = total - us(CTA_HOLD); f = content / end5
        t = {k: (tt(k)["start"] * f, (tt(k)["start"] + tt(k)["duration"]) * f) for k in ("line1", "line3a", "line3b", "line4", "line5")}
        c = seg("compound"); cdur = c["target_timerange"]["duration"]
        c0 = snap(tt("compound")["start"] * f, us(1.2), content); place(seg("line1"), 0, c0)
        c["target_timerange"]["start"] = int(c0)
        a3 = max(t["line3a"][0], c0 + cdur); b3 = a3 + (t["line3b"][0] - t["line3a"][0])
        e3 = snap(t["line3a"][1], b3 + us(1), content - us(2))
        e4 = snap(t["line4"][1], e3 + us(1), content - us(1))
        place(seg("line3a"), a3, e3); place(seg("line3b"), b3, e3); place(seg("line4"), e3, e4); place(seg("line5"), e4, content)
        place(seg("cta"), content + us(0.1), total)
        for role in ("video", "logo"):
            s = seg(role); s["target_timerange"]["duration"] = total; s["source_timerange"]["duration"] = total
            for a in d["materials"]["material_animations"]:
                if a["id"] in s["extra_material_refs"]:
                    for an in a["animations"]:
                        if an["type"] == "out": an["start"] = total - an["duration"]
        d["duration"] = total

    def check(self):
        d = self.d
        allm = {x["id"] for v in d["materials"].values() if isinstance(v, list) for x in v if isinstance(x, dict) and "id" in x}
        miss = [r for t in d["tracks"] for s in t["segments"] for r in [s["material_id"]] + s["extra_material_refs"] if r not in allm]
        media = [m["path"] for m in d["materials"]["videos"] + d["materials"]["audios"] if m["path"]]  # the title clip has no file
        return len(miss), all(os.path.exists(p) for p in media)


def save(project, tls):
    if capcut_running():
        raise SystemExit("CapCut is open. Quit it first (Cmd+Q on Mac; on Windows close it and check the tray), "
                         "or it overwrites the new project.")
    name, msg = draft_format()
    if not name: raise SystemExit(msg)
    files = (name, name + ".bak", "template-2.tmp")
    out = DRAFTS + "/" + project
    if os.path.exists(out): raise SystemExit("A CapCut project with this name exists already: " + project)
    shutil.copytree(HERE + "/skeleton", out, ignore=shutil.ignore_patterns(".keep"))
    tmpl = out + "/Timelines/TEMPLATE"; now = int(time.time() * 1e6); ids, entries = [], []
    for t in tls:
        tid = uid(); ids.append(tid); folder = out + "/Timelines/" + tid
        shutil.copytree(tmpl, folder)
        t.d["id"] = tid; raw = json.dumps(t.d, ensure_ascii=False)
        for p in files: open(folder + "/" + p, "w", encoding="utf-8").write(raw)
        sub_id, inner = t.compound; sub = out + "/subdraft/" + sub_id
        os.makedirs(sub); shutil.copy(HERE + "/templates/compound/draft_cover.jpg", sub)
        open(sub + "/draft_content.json", "w", encoding="utf-8").write(json.dumps(inner, ensure_ascii=False))
        sc = json.load(open(HERE + "/templates/compound/sub_draft_config.json", encoding="utf-8")); sc.update({"id": sub_id, "project_id": sub_id})
        open(sub + "/sub_draft_config.json", "w", encoding="utf-8").write(json.dumps(sc))
        entries.append({"create_time": now, "id": tid, "is_marked_delete": False, "name": t.name, "update_time": now})
    shutil.rmtree(tmpl)
    raw = json.dumps(tls[0].d, ensure_ascii=False)
    for p in files: open(out + "/" + p, "w", encoding="utf-8").write(raw)
    pj = json.load(open(out + "/Timelines/project.json", encoding="utf-8"))
    pj.update({"id": uid(), "main_timeline_id": ids[0], "timelines": entries, "create_time": now, "update_time": now})
    for p in ("Timelines/project.json", "Timelines/project.json.bak"): open(out + "/" + p, "w", encoding="utf-8").write(json.dumps(pj))
    layout = {"dockItems": [{"dockIndex": 0, "ratio": 1, "timelineIds": ids, "timelineNames": [t.name for t in tls]}], "layoutOrientation": 1}
    open(out + "/timeline_layout.json", "w", encoding="utf-8").write(json.dumps(layout, ensure_ascii=False))
    total = max(t.dur for t in tls); did = uid()
    meta = json.load(open(out + "/draft_meta_info.json", encoding="utf-8"))
    meta.update({"draft_id": did, "draft_name": project, "draft_fold_path": out, "draft_root_path": DRAFTS,
                 "tm_duration": total, "tm_draft_create": now, "tm_draft_modified": now})
    open(out + "/draft_meta_info.json", "w", encoding="utf-8").write(json.dumps(meta, ensure_ascii=False))
    rootp = DRAFTS + "/root_meta_info.json"
    if not os.path.exists(rootp):
        print("saved:", out, "(CapCut has no project list file here; if the project does not show, restart CapCut)")
        return
    shutil.copy(rootp, rootp + ".bak-fastlane-" + time.strftime("%Y%m%d-%H%M%S"))
    root = json.load(open(rootp, encoding="utf-8"))
    e = json.load(open(HERE + "/templates/root_entry.json", encoding="utf-8"))
    e.update({"draft_cover": out + "/draft_cover.jpg", "draft_fold_path": out, "draft_id": did, "draft_json_file": out + "/" + name,
              "draft_name": project, "draft_root_path": DRAFTS, "tm_draft_create": now, "tm_draft_modified": now,
              "tm_duration": total, "draft_timeline_materials_size": 0})
    root["all_draft_store"].insert(0, e); root["draft_ids"] = root.get("draft_ids", 0) + 1
    open(rootp, "w", encoding="utf-8").write(json.dumps(root, ensure_ascii=False))
    print("saved:", out)


if __name__ == "__main__":
    if len(sys.argv) < 2: raise SystemExit(__doc__)
    missing = [n for k, n in NEEDED.items() if not glob.glob(EFFECTS + "/" + k + "/*")]
    if missing: print("WARNING, not downloaded in CapCut yet (see README, Install):", ", ".join(missing))
    if sys.argv[1] == "--check":
        name, msg = draft_format()
        print("CapCut projects: " + (name + " readable, building works here" if name else msg))
        sys.exit(0 if name else 1)
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    if not cfg.get("project") or "<" in cfg["project"] or "<" in cfg.get("media", ""):
        raise SystemExit("Set the project name first: ask the person what to call this week's outputs.")
    media_dir = MEDIA + "/" + cfg.get("media", cfg["project"])
    jpath = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "shots.json")
    shots = json.load(open(jpath, encoding="utf-8")) if os.path.exists(jpath) else {}

    def spare(video):
        p = os.path.join(os.path.dirname(video), "spare", os.path.splitext(os.path.basename(video))[0] + " - spare.mp4")
        return [p] if os.path.exists(p) else []

    def pool(c):  # own spare first, then the other videos (and spares) of the same group; checked footage only
        v = os.path.expanduser(c["video"]); out = spare(v)
        for o in cfg["timelines"]:
            if o is not c and c.get("group") and o.get("group") == c["group"]:
                ov = os.path.expanduser(o["video"]); out += [ov] + spare(ov)
        return [p for p in out if shots.get(os.path.basename(p), {}).get("checked")]

    tls = [Timeline(c, media_dir, shots, pool(c)) for c in cfg["timelines"]]
    for t in tls:
        miss, ok = t.check()
        print("%-34s %.1fs | VO %s | music %s | missing refs %d | media ok %s" % (
            t.name, t.dur / US, os.path.basename(t.vo), {None: "-", True: "yes", False: "NOT DOWNLOADED"}[t.music], miss, ok))
        if t.notes is None: print("    shot check: not done for this video, footage used as it is")
        for n in t.notes or []: print("    shot check:", n)
    gone = sorted({BRANDS[c["brand"]]["music"]["name"] for c, t in zip(cfg["timelines"], tls) if t.music is False})
    if gone: print("NOTE: music not in CapCut yet, so left out: %s. Use it once in CapCut (Audio > search the name), "
                   "then build again." % ", ".join(gone))
    if "--save" in sys.argv: save(cfg["project"], tls)
