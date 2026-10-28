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
  python capcut/build_project.py work/<week>/capcut.json --replace  # rebuild these timelines inside the existing project
  python capcut/build_project.py --check                            # can this computer's CapCut take built projects?

On a Mac use python3. Windows needs ffmpeg (setup_check.py says how to install it).

Config format: see capcut/example.json.
"""
import json, os, sys, copy, shutil, subprocess, time, re, uuid, struct, glob, itertools

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
SENT_PAUSE = 0.25  # the shortest pause read as a break between sentences (Negen's voices pause 0.3-0.4 s there)
EXTRA_PAUSE = 0.3  # how much a pause inside a sentence beyond its commas counts against a reading of the sentence ends
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


def speech_spans(path, dur, pause=SENT_PAUSE):
    """The parts of the voice-over to keep, in seconds: everything except the start and end silence, with every
    pause of PAUSE or more cut down to GAP. Without ffmpeg the voice-over stays whole."""
    ffmpeg = find_ffmpeg()
    if not ffmpeg: return [(0.0, dur)]
    # voice band only: Negen's file mixes the clip's room sound (birds, room tone) under the voice, which hides the
    # 0.3-0.4 s pauses between sentences from a plain level check
    err = subprocess.run([ffmpeg, "-hide_banner", "-i", path, "-af",
                          "highpass=f=120,lowpass=f=6000,silencedetect=n=-30dB:d=%s" % pause, "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    pad, spans, pos = GAP / 2, [], 0.0
    for a, b in zip(starts, ends + [dur] * (len(starts) - len(ends))):
        if a <= 0.05: pos = max(0.0, b - pad); continue  # silence before the first word
        spans.append((pos, min(dur, a + pad))); pos = b - pad
    if pos < dur - 0.05 and (not ends or len(ends) == len(starts) and ends[-1] < dur - 0.05): spans.append((pos, dur))
    return [(a, b) for a, b in spans if b - a > 0.05] or [(0.0, dur)]


def sentence_ends(spans, sentences):
    """Where sentences 1..n-1 end in the voice-over file (seconds, the middle of the pause after each). A comma pause
    can be as long as a sentence pause, so the n-1 sentence ends are the pauses that let every sentence hold no more
    pauses than it has commas and keep the speaking pace (seconds per letter) most even across sentences, longer
    pauses winning a tie (right on all 12 voice-overs of the Oct 31 batch). None when nothing fits."""
    n = len(sentences)
    gaps = [spans[i + 1][0] - spans[i][1] for i in range(len(spans) - 1)]
    talk = [b - a for a, b in spans]
    letters = [max(1, len(re.sub(r"[^A-Za-z0-9]", "", s))) for s in sentences]; commas = [s.count(",") for s in sentences]
    best = None
    for c in itertools.combinations(range(len(gaps)), n - 1):
        bounds = [-1] + list(c) + [len(spans) - 1]
        groups = [range(bounds[k] + 1, bounds[k + 1] + 1) for k in range(n)]
        # pauses inside a sentence beyond its commas (a dip of the fine pass, where two spans overlap, is not a pause)
        extra = sum(max(0, sum(1 for i in list(g)[:-1] if gaps[i] > 0) - commas[k]) for k, g in enumerate(groups))
        rate = [sum(talk[i] for i in g) / letters[k] for k, g in enumerate(groups)]
        mean = sum(rate) / n
        score = (sum((x - mean) ** 2 for x in rate) / n) ** 0.5 / mean - 0.1 * sum(gaps[i] for i in c) + EXTRA_PAUSE * extra
        if best is None or score < best[0]: best = (score, c)
    if not best: return None
    return [(spans[i][1] + spans[i + 1][0]) / 2 for i in best[1]]


PACE_OFF = 1.5  # a reading whose slowest or fastest sentence is this far off the voice's median pace is suspect


def pace_off(spans, ends, sentences):
    """How far the most uneven sentence of a reading is from the voice's median pace (letters a second, 1.0 = even;
    the right readings of Oct 28 stayed under 1.5, the wrong ones were about 3)."""
    bounds = [spans[0][0]] + list(ends) + [spans[-1][1]]
    talk = lambda a, b: sum(max(0.0, min(y, b) - max(x, a)) for x, y in spans)
    rate = [max(1, len(re.sub(r"[^A-Za-z0-9]", "", s))) / max(talk(bounds[k], bounds[k + 1]), 0.05)
            for k, s in enumerate(sentences)]
    body = sorted(rate[:-1]); m = body[len(body) // 2]
    return max(max(r / m, m / r) for r in rate[:-1])


def on_timeline(spans, x):
    """A moment of the voice-over file (seconds) on the timeline, where the kept spans play end to end at VO_SPEED."""
    at = 0.0
    for a, b in spans:
        if x <= a: return round(at, 2)
        if x < b: return round(at + (x - a) / VO_SPEED, 2)
        at += (b - a) / VO_SPEED
    return round(at, 2)


def vo_times(vo_text, spans, total, path=None, ends=None):
    """The edit plan's "times" from the brief's voice-over script, each line on screen while its sentences are spoken.
    7 sentences (the argument: hook, tension, turn, reason, doubt cleared, offer, CTA): Line 1 stays up through the
    tension and Line 2, the punchline, starts with sentence 3. 6 sentences (older briefs): sentence n says Line n.
    "starts" holds every sentence's start for cuts named "s1".."s7". Some voices (Negen's default) pause under
    SENT_PAUSE between sentences; then a finer pass over the file finds them."""
    sentences = [s for s in re.split(r"(?<=[.?!])\s+", vo_text.strip()) if s]
    if len(sentences) < 6: return None
    # "ends" in the edit plan: where each sentence but the last ends in the voice file, in seconds, when the match
    # picked a comma pause (the voice can run two sentences together and pause at a comma instead)
    if not ends:
        ends = sentence_ends(spans, sentences)
        # the voice can run two sentences together with no pause between them (the offer into the CTA): then the
        # reading above splits at a comma instead, and one sentence comes out far too fast. The finer pause pass
        # finds the short dip between them; keep whichever reading is more even.
        if path and (not ends or pace_off(spans, ends, sentences) > PACE_OFF):
            fine = speech_spans(path, mp4_info(path)[0], 0.12)
            other = sentence_ends(fine, sentences)
            if other and (not ends or pace_off(spans, other, sentences) < pace_off(spans, ends, sentences)): ends = other
    if not ends: return None
    s = [0.0] + [on_timeline(spans, x) for x in ends]  # s[k] = start of sentence k+1
    p = 2 if len(s) >= 7 else 1  # index of the punchline sentence
    return {"line1": [0, s[p]], "line2": s[p], "line3": [s[p + 1], s[p + 2]], "line4": [s[p + 2], s[p + 3]],
            "line5": [s[p + 3], s[p + 4]], "cta": s[p + 4], "starts": s, "punch": "s%d" % (p + 1)}


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


def pick_music(brand, cfg, slot):
    """The music bed for one timeline: the timeline's own "music" (a track name from the brand's music_pool) if set,
    else the pool rotated by the timeline's slot among its brand's timelines, so the V1-V3 of a group never share a
    track. A brand with no pool keeps its single "music"."""
    pool = brand.get("music_pool") or ([brand["music"]] if brand.get("music") else [])
    if not pool: return None
    if cfg.get("music"):
        named = [m for m in pool if m["name"] == cfg["music"]]
        if named: return named[0]
    return pool[slot % len(pool)]


SFX = json.load(open(HERE + "/templates/sfx.json", encoding="utf-8"))


def add_sfx(d, events):
    """Sound effects on their own track: events = [(time in seconds, role)], role a key of templates/sfx.json.
    A sound not yet on this computer (never used in CapCut) is left out and reported."""
    tp = json.load(open(HERE + "/templates/music_track.json", encoding="utf-8"))
    segs, missing = [], []
    for t, role in sorted(events):
        fx = SFX[role]; path = MUSIC + "/" + fx["file"]
        if not os.path.exists(path): missing.append(fx["name"]); continue
        m = copy.deepcopy(tp["mat"]); m.update({"id": uid(), "type": "sound", "path": path, "name": fx["name"],
                                                "music_id": "", "effect_id": fx["effect_id"], "category_name": "Favorites",
                                                "category_id": "-100", "duration": us(fx["duration"])})
        d["materials"].setdefault("audios", []).append(m)
        s = copy.deepcopy(tp["seg"]); s["id"] = uid(); s["material_id"] = m["id"]; refs = []
        for k, items in tp["extra"].items():
            for it in items:
                n = copy.deepcopy(it); n["id"] = uid(); d["materials"].setdefault(k, []).append(n); refs.append(n["id"])
        start = max(0, us(t - fx.get("lead", 0))); length = min(us(fx["duration"]), max(0, d["duration"] - start))
        if length <= 0: continue
        s["extra_material_refs"] = refs; s["source_timerange"] = {"start": 0, "duration": length}
        s["target_timerange"] = {"start": start, "duration": length}; s["volume"] = fx["volume"]
        s["last_nonzero_volume"] = 1.0; s["speed"] = 1.0; s["render_index"] = 0; s["track_render_index"] = len(d["tracks"])
        segs.append(s)
    if segs:
        d["tracks"].append({"id": uid(), "type": "audio", "segments": segs, "flag": 0, "attribute": 0,
                            "name": "Sound effects", "is_default_name": False})
    return len(segs), sorted(set(missing))


def sfx_events(d, r):
    """When the cards come in on the finished timeline: a whoosh into the punchline (Line 2), a pop for Lines 3-5,
    the CTA sound when the call to action appears."""
    def start(role):
        s = next((s for t in d["tracks"] for s in t["segments"]
                  if r[role] == s["material_id"] or r[role] in s["extra_material_refs"]), None)
        return s["target_timerange"]["start"] / US if s else None
    ev = [(start("compound"), "punch")] + [(start(k), "card") for k in ("line3a", "line4", "line5")] + [(start("cta"), "cta")]
    return [(t, role) for t, role in ev if t is not None]


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
    short = total - t
    if 0.01 < short < REPLACE_MIN and pieces and pieces[-1][2] / (pieces[-1][2] + short) >= 0.8:
        f, s, l = pieces[-1]; pieces[-1] = (f, s, l, l + short)  # the main video ran a little short: slow its last shot
    elif short >= 0.05:  # it ran out: finish with pool footage
        for f, s, l in fill(short, 0): pieces.append((f, s, l)); t += l
    return [p if len(p) == 4 else p + (p[2],) for p in pieces], notes


def lay_footage(d, r, pieces, media_dir):
    """Replace the single footage segment with one segment per piece; Smoke out stays on the last one."""
    v = mat(d, "videos", r["video"]); s = seg_of(d, v["id"]); track = next(t for t in d["tracks"] if s in t["segments"])
    anim = {a["id"] for a in d["materials"]["material_animations"]}
    mats_by_path, segs, at = {v["path"]: v}, [], 0
    for i, (f, start, length, shown) in enumerate(pieces):
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
            if k == "speeds": c["speed"] = length / shown
            if ref in anim:
                for an in c["animations"]:
                    if an["type"] == "out": an["start"] = us(shown) - an["duration"]
        n["extra_material_refs"] = refs; n["speed"] = length / shown
        n["source_timerange"] = {"start": us(start), "duration": us(length)}
        n["target_timerange"] = {"start": at, "duration": us(shown)}; at += us(shown)
        segs.append(n)
    last = segs[-1]; shown_end = d["duration"] - last["target_timerange"]["start"]  # no rounding gap at the end
    last["source_timerange"]["duration"] = int(shown_end * last["speed"]); last["target_timerange"]["duration"] = shown_end
    track["segments"] = segs
    return segs


def role_seg(d, r, role):  # the title clip's segment points at its draft through extra_material_refs
    return next(s for t in d["tracks"] for s in t["segments"] if r[role] == s["material_id"] or r[role] in s["extra_material_refs"])


def place_times(d, r, times, total):
    """An edit plan's text times (seconds): line1/line3/line4/line5 [start, end], line2 (the animated title) and cta
    a start. Line 3's right half comes in 0.9 s after the left one, as in the house edit."""
    def place(role, a, b): role_seg(d, r, role)["target_timerange"] = {"start": us(a), "duration": us(b) - us(a)}
    place("line1", *times["line1"])
    role_seg(d, r, "compound")["target_timerange"]["start"] = us(times["line2"])
    a3, e3 = times["line3"]; place("line3a", a3, e3); place("line3b", min(a3 + 0.9, e3 - 0.8), e3)
    place("line4", *times["line4"]); place("line5", *times["line5"]); place("cta", times["cta"], total / US)


def cuts_to_pieces(cuts, total, folder, shots=None):
    """An edit plan's cut list [[timeline second, video, source second, zoom?], ...] -> pieces and zooms. A video is
    a file name in the timeline's videos folder or its spare folder. A shot that would run past the end of its file
    or into the video's next generated part (its cuts in shots.json) or its next bad stretch (a blend usually marks the
    next scene) is slowed to fit instead."""
    def find(v):
        for p in (v, os.path.join(folder, v), os.path.join(folder, "spare", v)):
            for q in (p, p + ".mp4"):
                if os.path.isfile(q): return q
        raise SystemExit("Edit plan: video not found: " + v)
    cuts = sorted(cuts, key=lambda c: c[0]); pieces, zooms = [], []
    for i, c in enumerate(cuts):
        end = cuts[i + 1][0] if i + 1 < len(cuts) else total
        f = find(c[1]); shown = end - c[0]
        sh = (shots or {}).get(os.path.basename(f), {})
        stops = sh.get("cuts", []) + [b[0] for b in sh.get("bad", [])]
        part_end = min([x for x in stops if x > c[2] + 0.15] + [mp4_info(f)[0]])
        src = min(shown, part_end - c[2])
        pieces.append((f, c[2], src, shown)); zooms.append(c[3] if len(c) > 3 else 1.0)
    return pieces, zooms


def add_transitions(d, segs, at_times, zooms):
    """A Slide Blur into the shot that starts at each given time (on the shot before it, as CapCut keeps it), and the
    edit plan's punch-in zoom on each shot. Returns the times that got no transition (effect not downloaded)."""
    for s, z in zip(segs, zooms):
        if z != 1.0: s["clip"]["scale"] = {"x": z, "y": z}; s["uniform_scale"] = {"on": True, "value": 1.0}
    tp = json.load(open(HERE + "/templates/transition_slide_blur.json", encoding="utf-8"))
    path = EFFECTS + "/" + tp.pop("path_rel")
    missing = []
    for t in at_times:
        prev = next((s for s in segs if abs(s["target_timerange"]["start"] + s["target_timerange"]["duration"] - us(t)) < us(0.06)), None)
        if prev is None or not os.path.exists(path): missing.append(t); continue
        m = copy.deepcopy(tp); m["id"] = uid(); m["path"] = path
        d["materials"].setdefault("transitions", []).append(m); prev["extra_material_refs"].append(m["id"])
    return missing


class Timeline:
    def __init__(self, cfg, media_dir, shots=None, pool=(), slot=0):
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
        s4 = seg_of(d, r["line4"]); sc = s4["clip"]["scale"]["x"]  # a long Line 4 shrinks to the house width
        if width(cfg["line4"], 7, sc) > 1.8:
            sc *= 1.8 / width(cfg["line4"], 7, sc); s4["clip"]["scale"] = {"x": sc, "y": sc}; s4["uniform_scale"]["value"] = sc
        p, q = cfg["line5"]; set_text(mat(d, "texts", r["line5"]), [(p + "\n", 0), (q, 1)])
        set_text(mat(d, "texts", r["cta"]), [(cfg.get("cta") or brand["cta"], 0)])

        # cut to the voice-over: pauses shortened, the timeline ends CTA_HOLD after the last word
        spans = speech_spans(self.vo, mp4_info(self.vo)[0])
        total = min(dur, us(sum(b - a for a, b in spans) / VO_SPEED + CTA_HOLD)); self.dur = total
        joints, at = [], 0  # where the shortened pauses sit on the timeline
        for a, b in spans[:-1]: at += us((b - a) / VO_SPEED); joints.append(at)
        self.retime(d, r, total, joints)
        # shot check: bad stretches (shots.json) cut out or replaced with clean footage from the spare / the group
        self.notes = None; self.times = None
        src =os.path.expanduser(cfg["video"]); ed = dict(cfg.get("edit") or {})
        if not ed.get("times") and cfg.get("vo"):  # times from the script's sentences and the voice's own pauses
            ed["times"] = vo_times(cfg["vo"], spans, total / US, self.vo, ed.get("ends"))
            self.times = ed["times"]
            if ed["times"] and ed.get("cuts"):  # cut points named by sentence ("s2", "s4+0.9") take the sentence's start
                st = ed["times"]["starts"]
                at = lambda x: x if not isinstance(x, str) else st[int(x[1]) - 1] + (float(x[3:]) if "+" in x else 0.0)
                ed["cuts"] = [[at(c[0])] + list(c[1:]) for c in ed["cuts"]]
                ed["transitions"] = [at(t) for t in ed.get("transitions", [ed["times"]["punch"]])]
        if any(isinstance(c[0], str) for c in ed.get("cuts", [])):
            raise SystemExit("%s: could not find where each sentence of the voice-over starts. Give \"times\" by hand "
                             "in the edit plan (CLAUDE.md step 7)." % self.name)
        if ed.get("times"): place_times(d, r, ed["times"], total)
        if ed.get("cuts"):  # Claude's edit plan: footage chosen per sentence of the voice-over
            pieces, zooms = cuts_to_pieces(ed["cuts"], total / US, os.path.dirname(src), shots)
            segs = lay_footage(d, r, pieces, media_dir)
            missing = add_transitions(d, segs, ed.get("transitions", []), zooms)
            self.notes = ["edit plan: %d shots, %d transitions" % (len(pieces), len(ed.get("transitions", [])) - len(missing))]
            for f, a, length, shown in pieces:  # a bad stretch in a planned shot, or a shot slowed below 0.75x, is reported
                bad = [b for b in (shots or {}).get(os.path.basename(f), {}).get("bad", []) if a < b[1] and b[0] < a + length]
                if bad: self.notes.append("%s %.2f-%.2f s uses a bad stretch: %s" % (os.path.basename(f)[-28:], a, a + length, bad[0][2]))
                elif length / shown < 0.75: self.notes.append("%s from %.2f s slowed to %.2fx to fill %.1f s; split the sentence into two shots"
                                                              % (os.path.basename(f)[-28:], a, length / shown, shown))
            if missing: self.notes.append("transition Slide Blur not downloaded in CapCut, left out at %s s" % missing)
        elif shots and shots.get(os.path.basename(src), {}).get("checked"):
            pieces, self.notes = plan_footage(src, total / US, shots, pool)
            lay_footage(d, r, pieces, media_dir)
        add_vo(d, self.vo, spans)
        track = pick_music(brand, cfg, slot); self.music_name = track["name"] if track else "-"
        self.music = add_music(d, track) if track else None
        self.sfx = add_sfx(d, sfx_events(d, r)) if cfg.get("sfx", True) else (0, [])
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


def replace_in(project, tls, backup_root):
    """Put the built timelines into an existing project in place of the timelines with the same names (the others,
    and the project itself, stay as they are). Each replaced timeline folder is backed up first."""
    if capcut_running(): raise SystemExit("CapCut is open. Quit it first, or it overwrites the change.")
    out = DRAFTS + "/" + project
    lay = json.load(open(out + "/timeline_layout.json", encoding="utf-8"))["dockItems"][0]
    by_name = dict(zip(lay["timelineNames"], lay["timelineIds"]))
    name = "draft_content.json" if os.path.exists(out + "/draft_content.json") else "draft_info.json"
    backup = os.path.join(backup_root, "capcut-backup", time.strftime("%Y%m%d-%H%M%S"))  # short path: Windows limit
    for t in tls:
        tid = by_name.get(t.name)
        if not tid: raise SystemExit("No timeline named %r in %s" % (t.name, project))
        folder = out + "/Timelines/" + tid
        shutil.copytree(folder, os.path.join(backup, tid))
        t.d["id"] = tid; raw = json.dumps(t.d, ensure_ascii=False)
        for p in (name, name + ".bak", "template-2.tmp"): open(folder + "/" + p, "w", encoding="utf-8").write(raw)
        sub_id, inner = t.compound; sub = out + "/subdraft/" + sub_id
        os.makedirs(sub, exist_ok=True); shutil.copy(HERE + "/templates/compound/draft_cover.jpg", sub)
        open(sub + "/draft_content.json", "w", encoding="utf-8").write(json.dumps(inner, ensure_ascii=False))
        sc = json.load(open(HERE + "/templates/compound/sub_draft_config.json", encoding="utf-8")); sc.update({"id": sub_id, "project_id": sub_id})
        open(sub + "/sub_draft_config.json", "w", encoding="utf-8").write(json.dumps(sc))
        if lay["timelineIds"][0] == tid:  # the project's main copy mirrors its first timeline
            for p in (name, name + ".bak", "template-2.tmp"): open(out + "/" + p, "w", encoding="utf-8").write(raw)
        print("replaced:", t.name)
    print("backup of the old timelines:", os.path.normpath(backup))


def save(project, tls):
    if capcut_running():
        raise SystemExit("CapCut is open. Quit it first (Cmd+Q on Mac; on Windows close it and check the tray), "
                         "or it overwrites the new project.")
    name, msg = draft_format()
    if not name: raise SystemExit(msg)
    files = (name, name + ".bak", "template-2.tmp")
    out = DRAFTS + "/" + project
    if os.path.exists(out): raise SystemExit("A CapCut project with this name exists already: " + project + ". To rebuild its timelines in "
                                     "place, run again with --replace instead of --save (old timelines are backed up).")
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

    slots, tls = {}, []  # the music pool rotates per brand, in the order the timelines are listed
    for c in cfg["timelines"]:
        slots[c["brand"]] = slots.get(c["brand"], -1) + 1
        tls.append(Timeline(c, media_dir, shots, pool(c), slots[c["brand"]]))
    for t in tls:
        miss, ok = t.check()
        print("%-34s %.1fs | VO %s | music %s (%s) | sfx %d | missing refs %d | media ok %s" % (
            t.name, t.dur / US, os.path.basename(t.vo), t.music_name[:28],
            {None: "-", True: "yes", False: "NOT DOWNLOADED"}[t.music], t.sfx[0], miss, ok))
        if t.sfx[1]: print("    sound effects not in CapCut yet, left out:", ", ".join(t.sfx[1]))
        if t.times: print("    sentences start at", [round(x, 2) for x in t.times["starts"][1:]], "punchline", t.times["punch"])
        if t.notes is None: print("    shot check: not done for this video, footage used as it is")
        for n in t.notes or []: print("    shot check:", n)
    gone = sorted({t.music_name for t in tls if t.music is False})
    if gone: print("NOTE: music not in CapCut yet, so left out: %s. Use it once in CapCut (Audio > search the name), "
                   "then build again." % ", ".join(gone))
    if "--save" in sys.argv: save(cfg["project"], tls)
    if "--replace" in sys.argv: replace_in(cfg["project"], tls, os.path.dirname(os.path.abspath(sys.argv[1])))
