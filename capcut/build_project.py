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
import glob, json, os, sys, copy, shutil, subprocess, time, re, uuid, struct, itertools

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
sys.path.insert(0, HERE)
import typeset  # noqa: E402  the type system (templates/type_styles.json) and the key-word timing
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
    if os.path.exists(dst) and not os.path.samefile(src, dst) and (
            os.path.getsize(dst) != os.path.getsize(src) or os.path.getmtime(dst) < os.path.getmtime(src)):
        os.remove(dst)  # the video was downloaded again (a new voice-over, say): the old copy must not stay
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
    if os.path.exists(dst) and os.path.getmtime(dst) < os.path.getmtime(video):
        os.remove(dst)  # the video is newer than its voice-over extract: take the voice-over again
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


FORMATS = json.load(open(HERE + "/templates/formats.json", encoding="utf-8"))
# how an ad is filmed and cut, picked per video (ad-brief-compiler section 2); its "transitions" override the format's
STRUCTURES = {k: v for k, v in json.load(open(HERE + "/templates/structures.json", encoding="utf-8")).items() if k != "_about"}


def line_map(t):
    """Which sentence each on-screen line starts on, for a timeline of capcut.json: the edit plan's "lines", else its
    "format" (templates/formats.json), else None (the 7- or 6-sentence default in vo_times)."""
    ed = t.get("edit") or {}
    if ed.get("lines"): return ed["lines"]
    f = FORMATS.get(t.get("format", ""))
    return f["lines"] if f else None


def vo_times(vo_text, spans, total, path=None, ends=None, lines=None):
    """The edit plan's "times" from the brief's voice-over script, each line on screen while its sentences are spoken.
    "lines" (from the ad's format, templates/formats.json) names the sentence each line starts on, Line 1 on the
    first; a line stays up until the next one starts and Line 2 is the punchline. Without it: 7 sentences (hook,
    tension, turn, reason, doubt cleared, offer, CTA) put Line 2 on sentence 3, 6 sentences (older briefs) sentence
    n on Line n. "starts" holds every sentence's start for cuts named "s1".."s9". Some voices (Negen's default) pause
    under SENT_PAUSE between sentences; then a finer pass over the file finds them."""
    # a list is a script already split into its parts (a "scripted" timeline: the parts end at ; and , too)
    sentences = list(vo_text) if isinstance(vo_text, list) else [s for s in re.split(r"(?<=[.?!])\s+", vo_text.strip()) if s]
    if len(sentences) < 5 or (not lines and len(sentences) < 6): return None
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
    if lines:
        keys = ("line2", "line3", "line4", "line5", "cta")
        n = [int(lines[k]) for k in keys]
        if n != sorted(set(n)) or n[0] < 2 or n[-1] > len(s):
            raise SystemExit("format lines %s do not fit a %d-sentence voice-over: each line on a later sentence than "
                             "the one before, the CTA on the last at most" % (lines, len(s)))
        at = {k: s[i - 1] for k, i in zip(keys, n)}
        return {"line1": [0, at["line2"]], "line2": at["line2"], "line3": [at["line3"], at["line4"]],
                "line4": [at["line4"], at["line5"]], "line5": [at["line5"], at["cta"]], "cta": at["cta"],
                "starts": s, "punch": "s%d" % n[0]}
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
CAT, OWN_CTX = {}, {}  # the footage catalogue (capcut/inventory.py) and the timeline being built: {"actor", "rooms"}


def load_catalog(week):
    """catalog.json of the week: {file: [shot]}; a shot has a, b and, once reviewed, pass/why/size/room/person."""
    p = os.path.join(week, "catalog.json")
    CAT.clear()
    if os.path.exists(p):
        for f, e in json.load(open(p, encoding="utf-8")).items():
            sh = e.get("shots", []); d = max([x["b"] for x in sh] or [0])
            for x in sh: x["_dur"] = d; x["before"] = x.get("before") or (x.get("shows") or "").startswith("before")
            CAT[f] = sh


def catalog_blocks(name, own=None):
    """What the catalogue keeps off a timeline (references/fundamentals.md): a shot that failed review, the gaps
    between shots (cuts, crossfades), a person other than the timeline's actor, and, unless it is a close-up, a shot
    in a room that is not one of the timeline's rooms (owner, Nov 18: reuse takes where the room does not change
    much; close-ups first)."""
    sh = CAT.get(os.path.basename(name))
    if not sh:  # Nov 19: an unreviewed file counted as clean, so fills pulled unreviewed footage into desk V7-V9
        return [(0.0, 9999.0, "not reviewed (no catalogue entry)")] if CAT else []
    out, pos = [], 0.0
    actor, rooms = OWN_CTX.get("actor"), OWN_CTX.get("rooms")
    for x in sorted(sh, key=lambda x: x["a"]):
        a, b = x["a"], x["b"]
        if a - pos > 0.05: out.append((pos, a, "between catalogue shots"))
        pos = max(pos, b)
        if "pass" not in x: continue
        why = x.get("why", "") or ""
        if not x["pass"]:
            ok = [(float(u), float(v)) for u, v in re.findall(r"(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)", why.split("clean", 1)[1])] if "clean" in why else []
            pos2 = a  # a long shot that failed only at its crossfades keeps the clean stretches the reviewer listed
            for u, v in sorted(ok):
                if u - pos2 > 0.05: out.append((pos2, u, "catalogue: " + why[:60]))
                pos2 = max(pos2, v)
            if b - pos2 > 0.05: out.append((pos2, b, "catalogue: " + (why[:60] or "failed review")))
            if not ok: continue  # with clean stretches listed, the person and room checks below still apply
        m = re.search(r"trim (start|end) ([\d.]+)", why)
        if m: out.append((a, a + float(m.group(2))) + ("catalogue: crossfade",) if m.group(1) == "start" else (b - float(m.group(2)), b, "catalogue: crossfade"))
        if a > 0.05: out.append((a, a + 0.3, "catalogue: blend edge"))  # Negen blends hide in the first and last frames
        if b < x.get("_dur", 99) - 0.05: out.append((b - 0.35, b, "catalogue: blend edge"))
        # owner's V8 (Nov 19): a hand with no face in a close-up may come from another take, and another room counts
        # only for a wide or medium that shows the video's person (empty product shots and close-ups travel)
        if actor and x.get("person") not in (None, actor) and not x.get("hands_only"): out.append((a, b, "another person (%s)" % x.get("person")))
        elif rooms and x.get("size") != "close" and x.get("person") and x.get("room") not in rooms: out.append((a, b, "another room (%s)" % x.get("room")))
    return out


FADE_PAD = 0.35   # Negen's crossfades last 0.8-1.0 s; a marked blend is widened this much on each side


def variant(name):
    """The video a file belongs to: its spare counts as the same video (same person, same takes)."""
    return os.path.splitext(os.path.basename(name))[0].replace(" - spare", "")


def blocked(name, shots, own=None):
    """[(start, end, why)] of one file that a timeline may not show: the bad stretches of the shot check (a blend
    widened by FADE_PAD, since the fade shows before and after the frames marked), the crossfades shot_sheet.py found
    ("fades"), and, when the file is another variant of the group than the timeline's own video (own), the stretches
    where that variant's person is on screen ("person"), so one timeline never shows two different people."""
    e = (shots or {}).get(os.path.basename(name), {}); out = []
    for a, b, *why in e.get("bad", []):
        w = why[0] if why else "bad"
        if w.startswith("first take: not used") and CAT.get(os.path.basename(name)): continue  # the catalogue judges it now
        pad = FADE_PAD if "blend" in w and not e.get("fades_padded") else 0.0  # "fades_padded": widened by hand already
        out.append((max(0.0, a - pad), b + pad, w))
    out += [(max(0.0, a - 0.1), b + 0.1, "crossfade (found by shot_sheet.py)") for a, b in e.get("fades", [])]
    if own is not None and variant(name) != variant(own) and not OWN_CTX.get("actor"):
        out += [(a, b, "another variant's person") for a, b in e.get("person", [])]
    out += catalog_blocks(name, own)
    return sorted(out)


def clean_parts(name, dur, shots, own=None):
    """The usable stretches of one video, from its shot check: everything minus what blocked() lists, widened to a
    hard cut within 0.3 s."""
    e = shots.get(name, {}); cut_at = e.get("cuts", [])
    def snap(t, side):
        near = [c for c in cut_at if abs(c - t) <= 0.3 and (c <= t if side < 0 else c >= t)]
        return min(near, key=lambda c: abs(c - t)) if near else t
    bad = sorted((max(0.0, snap(a, -1)), min(dur, snap(b, 1))) for a, b, _ in blocked(name, shots, own))
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
        for a, b in clean_parts(os.path.basename(f), mp4_info(f)[0], shots, own=main)[0]:
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


LEAD = 0.1  # a line comes up this much before the voice says its first key word (the eye reads as the ear hears)
MIN_ON = 0.8  # and stays at least this long


def key_onsets(cfg, times, spans, vo_path, total, notes):
    """Each line appears when the voice says the first word it carries (typeset.onset), not at the start of its
    sentence: Windows' own speech recogniser finds the words in the voice-over (capcut/vo_align.ps1); elsewhere the
    word's place among the sentence's letters estimates it. A line whose words the voice never says in its sentence is
    reported (TEXT-VOICE): the on-screen line must echo the voice's own words."""
    lm = line_map(cfg)
    if not lm or not cfg.get("vo"): return times
    sents = [x for x in re.split(r"(?<=[.?!])\s+", cfg["vo"].strip()) if x]
    st = list(times["starts"]) + [total - CTA_HOLD]
    wt = typeset.align_windows(vo_path, sents, find_ffmpeg())
    flat = lambda x: " ".join(x) if isinstance(x, list) else str(x)
    def at(n, text, label, report=True):
        i = n - 1; a, b = st[i], st[min(i + 1, len(st) - 1)]
        w = [on_timeline(spans, t) for t in wt[i]] if i in wt else None
        t, word = typeset.onset(text, sents[i], w, a, b)
        if word is None and report: notes.append("TEXT-VOICE: %s \"%s\" carries no word the voice says in sentence %d (\"%s\"): "
                                      "write it from the voice's own words" % (label, text, n, sents[i][:50]))
        return max(a, t - LEAD)
    l2 = at(lm["line2"], flat(cfg["line2"]), "Line 2"); l3 = at(lm["line3"], flat(cfg["line3"]), "Line 3")
    l3b = at(lm["line3"], flat(cfg["line3"][1]), "Line 3 right", report=False)
    l4 = at(lm["line4"], flat(cfg["line4"]), "Line 4"); l5 = at(lm["line5"], flat(cfg["line5"]), "Line 5")
    cta = times["cta"]
    l5 = min(l5, cta - MIN_ON); l4 = min(l4, l5 - MIN_ON); l3 = min(l3, l4 - MIN_ON); l2 = min(l2, l3 - MIN_ON)
    out = dict(times)
    # a numbered style (list) shows Line 3 as its number over the whole reason: the reason comes with its number
    # (owner, Nov 17: the "2" stood alone for 1.2 s while the voice already said the reason)
    if (typeset.style_for(cfg)[1] or {}).get("numbered"): l3b = l3 + 0.15
    else: l3b = max(l3b, l3 + 0.4)
    # the hook leaves when the punchline's sentence starts, not when the title comes up (owner, Nov 17: V8's hook
    # moved to end at the sentence, the title then comes with its own words)
    e1 = min(l2, st[lm["line2"] - 1] - TEXT_GAP) if st[lm["line2"] - 1] > 1.0 else l2
    # the hook's link words and accent come with their own words (the subject is up from the start)
    l1b = at(1, flat(cfg["line1"][1:]), "Line 1", report=False) if isinstance(cfg.get("line1"), list) and len(cfg["line1"]) == 3 else 0.0
    l1b = l1b if 0.3 <= l1b <= e1 - MIN_ON else 0.0
    # the scarcity words of the offer sentence ("Free shipping, handcrafted in small batches."): when the voice reaches
    # them, the brand's scarcity line takes Line 5's place (typeset.restyle, owner Nov 17)
    i5 = lm["line5"] - 1; l5s = 0.0
    if i5 < len(sents) and "," in sents[i5]:
        l5s = at(lm["line5"], sents[i5].split(",", 1)[1], "Line 5 scarcity", report=False)
        l5s = max(l5s, l5 + 0.9) if l5s > l5 else 0.0  # the offer stays long enough to read
        l5s = l5s if l5s <= cta - 0.8 else 0.0
    out.update(line1=[0, e1], line1b=l1b, line5s=l5s, line2=l2, line3=[l3, l4], line4=[l4, l5], line5=[l5, cta],
               line3b=min(l3b, l4 - 0.5), timing="voice recogniser" if wt else "letter estimate")
    return out


def add_text_track(d, seg, m, src=None):
    """A copy of a text clip (segment seg of material m; src = the draft they come from, default d) on a new text
    track of d. Its animations come along. Returns (new segment, new material)."""
    src = src or d
    nm = copy.deepcopy(m); nm["id"] = uid(); d["materials"]["texts"].append(nm)
    ns = copy.deepcopy(seg); ns["id"] = uid(); ns["material_id"] = nm["id"]; refs = []
    for x in seg.get("extra_material_refs", []):
        kind, xm = next(((k, y) for k, v in src["materials"].items() if isinstance(v, list)
                         for y in v if isinstance(y, dict) and y.get("id") == x), (None, None))
        if xm is None: continue
        cp = copy.deepcopy(xm); cp["id"] = uid(); d["materials"].setdefault(kind, []).append(cp); refs.append(cp["id"])
    ns["extra_material_refs"] = refs
    tr = copy.deepcopy(next(t for t in d["tracks"] if t["type"] == "text")); tr["id"] = uid(); tr["segments"] = [ns]
    d["tracks"].append(tr)
    return ns, nm


def flatten_title(d, r, inner):
    """Line 2 as plain text clips on the timeline instead of the house edit's animated title clip (a compound clip).
    The owner replaced the title clip by hand with two text lines in six of twelve videos of the 13/11 set (Nov 17):
    plain text can be edited in place and reads cleanly. The setup and the payoff keep their style, place and time."""
    c = role_seg(d, r, "compound"); c0, cd = c["target_timerange"]["start"], c["target_timerange"]["duration"]
    k = (c.get("clip") or {}).get("scale", {}).get("x", 1.0)
    for t in inner["tracks"]:
        if t["type"] != "text": continue
        for s in t["segments"]:
            a = s["target_timerange"]["start"]
            if a >= cd: continue
            ns, _ = add_text_track(d, s, mat(inner, "texts", s["material_id"]), inner)
            ns["target_timerange"] = {"start": c0 + a, "duration": min(s["target_timerange"]["duration"], cd - a)}
            if k != 1.0:
                for ax in ("x", "y"): ns["clip"]["scale"][ax] *= k
    for t in d["tracks"]:
        if c in t["segments"]: t["segments"].remove(c)
    d["materials"]["drafts"] = [x for x in d["materials"].get("drafts", []) if x["id"] != r["compound"]]
    d["tracks"] = [t for t in d["tracks"] if t["segments"]]


TEXT_GAP = 0.05  # one line leaves this long before the next comes in


def trim_title(d, r, inner):
    """Line 2, the animated title clip, has a fixed length (3.3 s) from the house edit. With each line timed to its own
    words, Line 3 often comes in sooner; the type styles stack both in one place, so the title ran over Line 3 (owner,
    Nov 17: "1" over "2", "It first" over "Blocks joined"). The title (and its inner draft) now ends when Line 3
    starts. Then every pair of lines on screen at once is reported (TEXT-OVERLAP), Line 3's two halves excepted."""
    seg = lambda role: role_seg(d, r, role)
    c, a3 = seg("compound"), seg("line3a")["target_timerange"]["start"]
    c0, cdur = c["target_timerange"]["start"], c["target_timerange"]["duration"]
    new = min(cdur, a3 - us(TEXT_GAP) - c0)
    if us(0.6) <= new < cdur:
        c["target_timerange"]["duration"] = new; c["source_timerange"]["duration"] = new
        if inner is not None:
            inner["duration"] = new
            for t in inner["tracks"]:
                for s in t["segments"]:
                    s["target_timerange"]["duration"] = min(s["target_timerange"]["duration"], new)
                    if s.get("source_timerange"): s["source_timerange"]["duration"] = min(s["source_timerange"]["duration"], new)
    rng = {k: (seg(k)["target_timerange"]["start"] / US, (seg(k)["target_timerange"]["start"] + seg(k)["target_timerange"]["duration"]) / US)
           for k in ("line1", "compound", "line3a", "line3b", "line4", "line5", "cta")}
    out, ks = [], list(rng)
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            if {a, b} == {"line3a", "line3b"}: continue
            o = min(rng[a][1], rng[b][1]) - max(rng[a][0], rng[b][0])
            if o > 0.1: out.append("TEXT-OVERLAP: %s and %s on screen together for %.1f s at %.1f s" % (a, b, o, max(rng[a][0], rng[b][0])))
    return out


def role_seg(d, r, role):  # the title clip's segment points at its draft through extra_material_refs
    return next(s for t in d["tracks"] for s in t["segments"] if r[role] == s["material_id"] or r[role] in s["extra_material_refs"])


def place_times(d, r, times, total):
    """An edit plan's text times (seconds): line1/line3/line4/line5 [start, end], line2 (the animated title) and cta
    a start. Line 3's right half comes in 0.9 s after the left one, as in the house edit."""
    def place(role, a, b): role_seg(d, r, role)["target_timerange"] = {"start": us(a), "duration": us(b) - us(a)}
    place("line1", *times["line1"])
    role_seg(d, r, "compound")["target_timerange"]["start"] = us(times["line2"])
    a3, e3 = times["line3"]; place("line3a", a3, e3)
    place("line3b", times["line3b"] if "line3b" in times else min(a3 + 0.9, e3 - 0.8), e3)
    place("line4", *times["line4"]); place("line5", *times["line5"]); place("cta", times["cta"], total / US)


ROWS = [0, 2, 5, 8, 10, 13, 15, 18, 99]  # where Negen's 8 scene rows start in every 20 s video (2+3+3+2+3+2+3+2 s)
TENSION_ROW = 1                          # row 2 (A02, 2-5 s): the before-state, filled only from the same row
FILL_SLOW = 0.85                         # a shot that would play slower than this gets a second shot instead
                                         # (owner's V8, Nov 19: he covered every shot slowed to 0.62-0.73x)


def hero_shot(own, pool):
    """The group's hero product shot (owner's V8, Nov 19): a catalogue shot marked "hero" (the empty piece at its best,
    in its best room, no person) that passed review. Returns (file name, start) or None."""
    names = {os.path.basename(p) for p in [own] + list(pool or [])}
    best = None
    for f, sh in CAT.items():
        if f not in names: continue
        for x in sh:
            if x.get("hero") and x.get("pass") and x["b"] - x["a"] > 1.2:
                if best is None or x["b"] - x["a"] > best[2]: best = (f, x["a"] + 0.3, x["b"] - x["a"])
    return best[:2] if best else None


def row_of(t): return max(i for i in range(8) if ROWS[i] <= t)


def group_pool(cfg, c, shots):
    """The footage a timeline may borrow: its own spare first, then the other videos (and spares) of its group;
    checked footage only."""
    def spare(video):
        p = os.path.join(os.path.dirname(video), "spare", os.path.splitext(os.path.basename(video))[0] + " - spare.mp4")
        return [p] if os.path.exists(p) else []
    v = os.path.expanduser(c["video"]); out = spare(v)
    for o in cfg["timelines"]:
        if o is not c and c.get("group") and o.get("group") == c["group"]:
            ov = os.path.expanduser(o["video"]); out += [ov] + spare(ov)
    parts = os.path.basename(v).split(" - "); sku = parts[2] if len(parts) > 3 else ""  # "<Name> - <Angle> - <SKU> - <code> ..."
    if sku:  # other generations of the same product: first takes (pool/) and earlier takes kept beside the videos
        out += sorted(glob.glob(os.path.join(os.path.dirname(v), "pool", "*%s*.mp4" % sku)))
        out += sorted(x for x in glob.glob(os.path.join(os.path.dirname(v), "*%s*take*.mp4" % sku)) if x not in out)
    return [p for p in out if shots.get(os.path.basename(p), {}).get("checked") or CAT.get(os.path.basename(p))]


def fill_short(pieces, zooms, pool, shots, own, notes, tension=None):
    """A piece that runs out of clean footage before its sentence ends keeps its clean run and is followed by clean
    footage of the same scene row (the same video and its spare first, so the person stays the same, then the group's
    other videos outside their person stretches), footage the timeline does not use yet. The before-state row is
    filled only from itself; other rows may fall back to any row but the before-state."""
    if not pool: return pieces, zooms
    key = lambda p: os.path.normcase(os.path.normpath(p))  # the same file may be written with / or \
    used = {}
    for f, a, l, _ in pieces: used.setdefault(key(f), []).append((a - 0.3, a + l + 0.3))
    def free(f, row, any_row):
        out = []
        for a, b in clean_parts(os.path.basename(f), mp4_info(f)[0], shots, own=own)[0]:
            if any_row and os.path.basename(f) in CAT:  # a reviewed file names its own before-state (Nov 19: row 2 of
                bef = [(x["a"], x["b"]) for x in CAT[os.path.basename(f)] if x.get("before")]  # a take is not always one)
                for u0, u1 in bef:
                    if u0 - 0.3 <= a < u1: a = u1
                    if a < u0 < b: b = u0
                if b - a < MIN_PIECE: continue
            elif any_row:  # any row but the before-state: its footage would put the problem under a later sentence
                if ROWS[TENSION_ROW] - 0.3 <= a < ROWS[TENSION_ROW + 1]: a = ROWS[TENSION_ROW + 1]
                if a < ROWS[TENSION_ROW] < b: b = ROWS[TENSION_ROW]
            else: a, b = max(a, ROWS[row] + 0.1), min(b, ROWS[row + 1] + 0.5)
            for u0, u1 in sorted(used.get(key(f), [])):
                if u0 < b and a < u1:
                    if u0 - a >= MIN_PIECE: out.append((a, u0))
                    a = max(a, u1)
            if b - a >= MIN_PIECE: out.append((a, b))
        return out
    new_p, new_z = [], []
    wins = tension if isinstance(tension, list) else ([tension] if tension else [])
    t_at = 0.0
    for (f, a, l, shown), z in zip(pieces, zooms):
        t0, t_at = t_at, t_at + shown
        in_t = any(w[0] - 0.05 <= t0 < w[1] - 0.05 for w in wins) if wins else None
        if l >= FILL_SLOW * shown or shown - l < 0.2:
            new_p.append((f, a, l, shown)); new_z.append(z); continue
        row = row_of(a); left = shown - l; got = [(f, a, l, l)]
        if any(b0 <= a < b1 for b0, b1 in (shots.get(os.path.basename(f), {}).get("before") or [])):
            new_p.append((f, a, l, shown)); new_z.append(z); continue  # the before-state is never patched with other footage
        if l < 0.3: left, got = shown, []  # a flash this short is dropped: the fill takes the whole sentence
        for any_row in (False, True):
            if any_row and (in_t if in_t is not None else row == TENSION_ROW): break  # the tension sentence keeps its own row
            while left >= 0.3:
                cands = [(variant(p) == variant(own), b - s, p, s) for p in {key(x): x for x in [own] + list(pool)}.values() for s, b in free(p, row, any_row)]
                if not cands: break
                _, ln, p, s = max(cands); take = min(ln, left)
                if left - take < 0.3 or ln >= FILL_SLOW * left: take = min(ln, left); show = left if ln >= FILL_SLOW * left else take
                else: show = take
                got.append((p, s, take, show)); used.setdefault(key(p), []).append((s - 0.3, s + take + 0.3)); left -= show
            if left < 0.3: break
        if not got: got = [(f, a, l, l)]  # nothing to fill with: keep the short shot, slowed
        if left >= 0.01:  # what is still missing is taken up by slowing the pieces a little
            k = shown / sum(x[3] for x in got); got = [(p, s, t, sh * k) for p, s, t, sh in got]
        if notes is not None and len(got) > 1:
            notes.append("%s from %.2f s ran out of clean footage: filled with %s" % (os.path.basename(f)[-28:], a,
                         ", ".join("%s %.2f s" % (os.path.basename(p)[-28:], t) for p, _, t, _ in got[1:])))
        new_p += got; new_z += [z] + [1.0 if isinstance(z, dict) else z] * (len(got) - 1)  # a crop is for its own shot only
    return new_p, new_z


JUMP_DIFF = 29.0  # two shots this alike at the cut (mean grey difference, 0-255) read as a jump cut, not a new shot
MIN_SHOT = 0.8    # a shot shown shorter than this reads as a flash


def _tiny(f, t):
    raw = subprocess.run([find_ffmpeg() or "ffmpeg", "-v", "error", "-ss", "%.2f" % max(0.0, min(t, mp4_info(f)[0] - 0.1)), "-i", f,
                          "-frames:v", "1", "-vf", "scale=36:64,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return raw[:36 * 64]


def smooth(pieces, zooms, notes=None, before=None):
    """Merges a shot into the one before it when the two look alike at the cut (a jump cut: the same wide twice from two
    takes) or when it is a flash under MIN_SHOT: the shot before runs on, slowed when it must. The punchline (a shot
    with a zoom) is never merged away."""
    if len(pieces) < 2: return pieces, zooms
    out_p, out_z = [list(pieces[0])], [zooms[0]]
    for (f, a, l, shown), z in zip(pieces[1:], zooms[1:]):
        pf, pa, pl, ps = out_p[-1]
        x, y = _tiny(pf, pa + pl - 0.05), _tiny(f, a + 0.05)
        diff = sum(abs(i - j) for i, j in zip(x, y)) / max(1, len(x))
        why = "jump cut (%.0f)" % diff if diff < JUMP_DIFF else "flash (%.2f s)" % shown if shown < MIN_SHOT else ""
        still = sum(abs(i - j) for i, j in zip(_tiny(pf, pa + 0.05), x)) / max(1, len(x)) < 10  # a locked-off shot may hold long
        if any(b0 <= a < b1 for b0, b1 in (before or {}).get(os.path.basename(f), [])): why = ""  # never merge the before-state away
        if why and z == 1.0 and (pl / (ps + shown) >= 0.5 or still):
            out_p[-1][3] = ps + shown  # the shot before runs on
            if notes is not None: notes.append("%s at %.2f s merged into the shot before: %s" % (os.path.basename(f)[-28:], a, why))
            continue
        out_p.append([f, a, l, shown]); out_z.append(z)
    return [tuple(p) for p in out_p], out_z


def before_of(f, shots): return (shots or {}).get(os.path.basename(f), {}).get("before")


def tension_of(cfg, times):
    """Where the before-state may (and must) play on the timeline: the tension sentence (s2), or from the first
    sentence when the hook itself states the problem (edit plan "problem_from": "s1"; owner, Nov 16: a problem hook
    over our own product reads as ours being the problem). An edit plan's "tension" [["s4", "s5"], ...] names the
    windows itself (a script whose problem or doubt is not sentence 2); then a list of windows comes back."""
    st = (times or {}).get("starts") or []
    win = (cfg.get("edit") or {}).get("tension")
    if win and st:
        at = lambda x: st[int(x[1:]) - 1] if int(x[1:]) <= len(st) else 99.0
        return [(at(a), at(b)) for a, b in win]
    if len(st) <= 2: return None
    first = 0 if ((cfg.get("edit") or {}).get("problem_from") == "s1") else 1
    return (st[first], st[2])


def cuts_to_pieces(cuts, total, folder, shots=None, own=None, notes=None, pool=None, tension=None):
    """An edit plan's cut list [[timeline second, video, source second, zoom?], ...] -> pieces and zooms. A video is
    a file name in the timeline's videos folder or its spare folder. A shot that would run past the end of its file
    or into the video's next generated part (its cuts in shots.json) or its next bad stretch (a blend usually marks the
    next scene) is slowed to fit instead."""
    def find(v):
        for p in (v, os.path.join(folder, v), os.path.join(folder, "spare", v), os.path.join(folder, "pool", v)):
            for q in (p, p + ".mp4"):
                if os.path.isfile(q): return q
        raise SystemExit("Edit plan: video not found: " + v)
    cuts = sorted(cuts, key=lambda c: c[0]); pieces, zooms = [], []
    for i, c in enumerate(cuts):
        end = cuts[i + 1][0] if i + 1 < len(cuts) else total
        f = find(c[1]); shown = end - c[0]; start = c[2]
        sh = (shots or {}).get(os.path.basename(f), {}); block = blocked(f, shots, own)
        wins = tension if isinstance(tension, list) else ([tension] if tension else [])
        bef = before_of(f, shots); in_t = any(w[0] - 0.05 <= c[0] < w[1] - 0.05 for w in wins)
        if bef is not None:  # the shot check marked where this video shows the before-state (no product)
            if in_t and not any(a <= start < b for a, b in bef) and notes is not None:
                notes.append("NOT A BEFORE-STATE: %s at %.2f s plays under the tension sentence" % (os.path.basename(f)[-28:], start))
            if in_t: block = block + [(0.0, a, "not the before-state") for a, b in bef[:1]] + [(b, 99.0, "not the before-state") for a, b in bef[-1:]]
            else: block = block + [(a, b, "before-state") for a, b in bef]
        person = False
        for a, b, why in block:  # a cut that starts inside a fade or a bad stretch moves past it
            if a <= start < b:
                if why == "another variant's person": person = True; break  # dropped: fill_short() takes the sentence
                if notes is not None: notes.append("%s cut at %.2f s moved to %.2f s (%s)" % (os.path.basename(f)[-28:], start, b, why))
                start = b
        stops = sh.get("cuts", []) + [a for a, _, _ in block]
        part_end = min([x for x in stops if x > start + 0.15] + [mp4_info(f)[0]])
        src = 0.1 if person else max(0.1, min(shown, part_end - start))
        if person and notes is not None: notes.append("%s at %.2f s shows another variant's person: replaced" % (os.path.basename(f)[-28:], start))
        pieces.append((f, start, src, shown)); zooms.append(c[3] if len(c) > 3 else 1.0)
    if pool is not None and own is not None:
        if tension:  # a fill never brings before-state footage into another sentence (row-based fills keep to the row)
            shots = {k: dict(v, bad=v.get("bad", []) + [[a, b, "before-state"] for a, b in v.get("before", [])]) for k, v in shots.items()}
        pieces, zooms = fill_short(pieces, zooms, pool, shots, own, notes, tension)
        pieces, zooms = smooth(pieces, zooms, notes, {k: v.get("before") or [] for k, v in shots.items()})
        if notes is not None and len(pieces) > 10:
            notes.append("CHOPPY: %d shots in %.1f s; this video has too little clean footage of its own: regenerate it "
                         "(a new batch is a spend: ask) or accept" % (len(pieces), total))
    return pieces, zooms


def add_transitions(d, segs, at_times, zooms):
    """The punchline transition (templates/transitions.json) into the shot that starts at each given time (on the shot before it, as CapCut keeps it), and the
    edit plan's punch-in zoom on each shot. Returns the times that got no transition (effect not downloaded)."""
    for s, z in zip(segs, zooms):
        if isinstance(z, dict):  # a crop: {"zoom": 2.4, "cx": 0.21, "cy": 0.65} keeps that point of the frame centred
            k = z["zoom"]; s["clip"]["scale"] = {"x": k, "y": k}; s["uniform_scale"] = {"on": True, "value": 1.0}
            s["clip"]["transform"] = {"x": 2 * (0.5 - z["cx"]) * k, "y": 2 * (z["cy"] - 0.5) * k}
        elif z != 1.0: s["clip"]["scale"] = {"x": z, "y": z}; s["uniform_scale"] = {"on": True, "value": 1.0}
    # the first transition CapCut has downloaded, in the owner's order (templates/transitions.json: Pale Clarity, the
    # owner's own pick on Nov 17, then the house edit's Slide Blur)
    base = json.load(open(HERE + "/templates/transition_slide_blur.json", encoding="utf-8")); base.pop("path_rel")
    tp, path = None, ""
    for o in json.load(open(HERE + "/templates/transitions.json", encoding="utf-8"))["order"]:
        o = dict(o); p = EFFECTS + "/" + o.pop("path_rel")
        if os.path.exists(p): tp, path = dict(base, **o), p; break
    missing = []
    for t in at_times:
        prev = next((s for s in segs if abs(s["target_timerange"]["start"] + s["target_timerange"]["duration"] - us(t)) < us(0.06)), None)
        if prev is None or tp is None: missing.append(t); continue
        m = copy.deepcopy(tp); m["id"] = uid(); m["path"] = path
        d["materials"].setdefault("transitions", []).append(m); prev["extra_material_refs"].append(m["id"])
    return missing


# ------------------------------------------------------------------------------------------------ scripted card lists
# A "scripted" timeline carries a finished script, word for word: its hook
# overlay and a list of cards, each card mapped to the voice-over part it comes in with. capcut.json timeline:
#   "scripted": {"parts": [hook VO, body VO 1, body VO 2, ...],          the script split at the writer's own numbering
#             "cards": [{"text": ["line", "line 2"], "vo": 1}, ..., {"logo": true}]}
# with "line1" [big, small, accent] = the hook overlay's own words. Each card comes on LEAD before the voice starts
# its part and stays until the next card; the hook overlay stays until the first card; a {"logo": true} card shows
# the brand logo alone (no words added) for CTA_HOLD after the voice. The cards' words are the writer's, not the
# voice's, so they are not checked against the voice (no TEXT-VOICE). Every card is set in the style's Line 4 face.

def scripted_cfg(cfg):
    """A scripted timeline gets placeholder Lines 2-5 so the house edit can be filled; their clips are removed later."""
    if not cfg.get("scripted"): return cfg
    return dict(cfg, line2=["·", "·"], line3=["·", "·"], line4="·", line5=["·", "·"], cta="·")


def scripted_times(cfg, spans, total, vo_path, ends=None):
    """Where each part of a scripted script starts on the timeline: the pauses (vo_times on the parts), then the first
    word of each part from the speech recogniser where it found the part (more exact at a ; or , joint)."""
    parts = cfg["scripted"]["parts"]
    times = vo_times(parts, spans, total, vo_path, ends, None)
    if not times: return None
    s = list(times["starts"])
    if not ends:
        wt = typeset.align_windows(vo_path, parts, find_ffmpeg())
        for i in range(1, len(parts)):
            if i in wt and wt[i]:
                t = on_timeline(spans, wt[i][0])
                if s[i - 1] + 0.3 < t < (s[i + 1] if i + 1 < len(s) else total) - 0.3: s[i] = t
        times["timing"] = "voice recogniser" if wt else "pauses"
    times["starts"] = s
    return times


def scripted_cards(d, r, cfg, times, total, spec, notes):
    """Lay the scripted cards on the timeline (see above) as copies of Line 4 in the style; remove the house edit's
    Lines 2-5 and CTA clips. Returns the sound-effect events [(time, kind)]."""
    P = cfg["scripted"]; st = times["starts"]; T = total / US; voice_end = T - CTA_HOLD
    cards = [c for c in P["cards"] if not c.get("logo")]; logo = any(c.get("logo") for c in P["cards"])
    ons = []
    for c in cards:
        t = max(0.6, st[c["vo"]] - LEAD) if c["vo"] < len(st) else voice_end - MIN_ON
        ons.append(max(t, ons[-1] + MIN_ON) if ons else t)
    role_seg(d, r, "line1")["target_timerange"] = {"start": 0, "duration": us(ons[0] - TEXT_GAP)}
    base = role_seg(d, r, "line4"); bm = mat(d, "texts", r["line4"])
    track = next(t for t in d["tracks"] if base in t["segments"])
    F = typeset.fonts(EFFECTS, notes) if spec else None
    events = []
    for k, c in enumerate(cards):
        a = ons[k]
        b = ons[k + 1] - TEXT_GAP if k + 1 < len(cards) else (voice_end + 0.1 if logo else T)
        m = copy.deepcopy(bm); m["id"] = uid(); d["materials"]["texts"].append(m)
        s = copy.deepcopy(base); s["id"] = uid(); s["material_id"] = m["id"]; refs = []
        for x in s["extra_material_refs"]:
            an = next((y for y in d["materials"]["material_animations"] if y["id"] == x), None)
            if an is None: refs.append(x); continue
            an = copy.deepcopy(an); an["id"] = uid(); d["materials"]["material_animations"].append(an); refs.append(an["id"])
        s["extra_material_refs"] = refs
        s["target_timerange"] = {"start": us(a), "duration": us(b) - us(a)}
        track["segments"].append(s)
        text = "\n".join(x.strip() for x in c["text"])  # the writer's words and case, as written
        if spec:
            s4 = spec["line4"]; f, z, col = s4["parts"][0]
            parts = [(text, f, z, col)]
            typeset.set_rich(m, parts, F, spec.get("finish", "shadow"), s4["align"], s4.get("spacing"))
            typeset.place(s, parts, F, typeset_K(), s4["align"], s4["y"], s4["max_w"])
        else:
            set_text(m, [(text, 0)])
        events.append((a, "card"))
    for role in ("compound", "line3a", "line3b", "line4", "line5", "cta"):
        sg = role_seg(d, r, role)
        for t in d["tracks"]:
            if sg in t["segments"]: t["segments"].remove(sg)
    d["tracks"] = [t for t in d["tracks"] if t["segments"] or t["type"] not in ("text",)]
    d["tracks"] = [t for t in d["tracks"] if t["segments"]]
    track["segments"].sort(key=lambda s: s["target_timerange"]["start"])
    if logo: events.append((voice_end + 0.1, "cta"))
    return events


def typeset_K(): return K


class Timeline:
    def __init__(self, cfg, media_dir, shots=None, pool=(), slot=0):
        cfg = scripted_cfg(cfg)
        self.name = cfg["name"]; self.cfg = cfg
        OWN_CTX.clear(); CAT.clear()
        if cfg.get("catalog", True):  # "catalog": false = a voice update: the footage as it already was in CapCut
            OWN_CTX.update({k: cfg[k] for k in ("actor", "rooms") if cfg.get(k)})
            load_catalog(os.path.dirname(os.path.dirname(os.path.abspath(os.path.expanduser(cfg["video"])))))
        brand = BRANDS[cfg["brand"]]
        video = link_media(os.path.expanduser(cfg["video"]), media_dir)
        logo = link_media(ROOT + "/brand/" + brand["logo"], media_dir)
        self.vo = extract_vo(os.path.expanduser(cfg["vo_from"]) if cfg.get("vo_from") else video, media_dir)  # "vo_from": the voice of another take (owner, Nov 18)
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
        spans = speech_spans(self.vo, mp4_info(self.vo)[0]); self.vo_cut = False
        total = min(dur, us(sum(b - a for a, b in spans) / VO_SPEED + CTA_HOLD)); self.dur = total
        joints, at = [], 0  # where the shortened pauses sit on the timeline
        for a, b in spans[:-1]: at += us((b - a) / VO_SPEED); joints.append(at)
        self.retime(d, r, total, joints)
        # shot check: bad stretches (shots.json) cut out or replaced with clean footage from the spare / the group
        self.notes = None; self.times = None
        src =os.path.expanduser(cfg["video"]); ed = dict(cfg.get("edit") or {})
        if cfg.get("scripted") and not ed.get("times"):  # a scripted card list: parts start where the voice starts them
            ed["times"] = scripted_times(cfg, spans, total / US, self.vo, ed.get("ends"))
            self.times = ed["times"]; self.text_notes = []
            if self.times:
                parts = cfg["scripted"]["parts"]; st = list(self.times["starts"]) + [total / US - CTA_HOLD]
                rate = [len(re.sub(r"[^A-Za-z0-9]", "", x)) / max(st[i + 1] - st[i], 0.01) for i, x in enumerate(parts[:len(st) - 1])]
                if len(rate) > 2: self.vo_cut = rate[-1] > 1.5 * sorted(rate[:-1])[len(rate[:-1]) // 2]
                if ed.get("cuts"):
                    st = ed["times"]["starts"]
                    at = lambda x: x if not isinstance(x, str) else st[int(x[1:].split("+")[0]) - 1] + (float(x.split("+")[1]) if "+" in x else 0.0)
                    ed["cuts"] = [[at(c[0])] + list(c[1:]) for c in ed["cuts"]]
                    ed["transitions"] = [at(t) for t in ed.get("transitions", [])]
        elif not ed.get("times") and cfg.get("vo"):  # times from the script's sentences and the voice's own pauses
            ed["times"] = vo_times(cfg["vo"], spans, total / US, self.vo, ed.get("ends"), line_map(cfg))
            self.times = ed["times"]; self.text_notes = []
            if self.times and "starts" in self.times:  # each line up with its own words (key_onsets)
                self.times = ed["times"] = key_onsets(cfg, self.times, spans, self.vo, total / US, self.text_notes)
            if self.times and ed.get("line1_end") == "s2":  # Line 1 leaves when the before-state starts (a product hook
                self.times["line1"][1] = self.times["starts"][1]  # must not stand over the room without the product)
            if self.times and "starts" in self.times:  # the last sentence spoken far faster than the rest: the voice was cut off
                sents = [x for x in re.split(r"(?<=[.?!])\s+", cfg["vo"].strip()) if x]
                st = list(self.times["starts"]) + [total / US - CTA_HOLD]
                rate = [len(re.sub(r"[^A-Za-z0-9]", "", x)) / max(st[i + 1] - st[i], 0.01) for i, x in enumerate(sents[:len(st) - 1])]
                if len(rate) > 2: self.vo_cut = rate[-1] > 1.5 * sorted(rate[:-1])[len(rate[:-1]) // 2]
            if ed["times"] and ed.get("cuts"):  # cut points named by sentence ("s2", "s4+0.9") take the sentence's start
                st = ed["times"]["starts"]
                at = lambda x: x if not isinstance(x, str) else st[int(x[1]) - 1] + (float(x[3:]) if "+" in x else 0.0)
                ed["cuts"] = [[at(c[0])] + list(c[1:]) for c in ed["cuts"]]
                hero = hero_shot(src, pool) if cfg.get("hero", True) else None
                if hero:  # owner's V8 (Nov 19): the punchline and the end card show the hero product shot
                    p_at = at(ed["times"]["punch"]); end_at = total / US - CTA_HOLD
                    pz = [c[3] for c in ed["cuts"] if abs(c[0] - p_at) < 0.05 and len(c) > 3]
                    ed["cuts"] = [c for c in ed["cuts"] if not (abs(c[0] - p_at) < 0.05 or c[0] >= end_at - 0.05)]
                    last = max([c for c in ed["cuts"] if c[0] < end_at], key=lambda c: c[0], default=None)
                    ed["cuts"] += [[p_at, hero[0], hero[1]] + pz[:1]]
                    if not (last and os.path.basename(str(last[1])) == hero[0]):  # already on the hero: it runs on
                        ed["cuts"] += [[end_at, hero[0], hero[1]]]
                    ed["cuts"].sort(key=lambda c: c[0])
                    self.hero_note = "hero shot %s %.1f s on the punchline and the end card" % (hero[0][-28:], hero[1])
                fmt = dict(FORMATS.get(cfg.get("format", ""), {}))  # a format or structure may set its own ([] = none: follow)
                if "transitions" in STRUCTURES.get(cfg.get("structure", ""), {}):  # follow cuts on action, no transition
                    fmt["transitions"] = STRUCTURES[cfg["structure"]]["transitions"]
                ed["transitions"] = [at(t) for t in ed.get("transitions", fmt.get("transitions", [ed["times"]["punch"]]))]
        if any(isinstance(c[0], str) for c in ed.get("cuts", [])):
            raise SystemExit("%s: could not find where each sentence of the voice-over starts. Give \"times\" by hand "
                             "in the edit plan (CLAUDE.md step 7)." % self.name)
        if ed.get("times") and not cfg.get("scripted"): place_times(d, r, ed["times"], total)
        self.text_overlaps = [] if cfg.get("scripted") else trim_title(d, r, inner)  # Line 2 leaves when Line 3 comes in (owner, Nov 17)
        if ed.get("cuts"):  # Claude's edit plan: footage chosen per sentence of the voice-over
            moved = []
            tens = tension_of(cfg, self.times)
            pieces, zooms = cuts_to_pieces(ed["cuts"], total / US, os.path.dirname(src), shots, own=src, notes=moved, pool=pool, tension=tens)
            segs = lay_footage(d, r, pieces, media_dir)
            self.pieces = pieces
            missing = add_transitions(d, segs, ed.get("transitions", []), zooms)
            self.notes = ["edit plan: %d shots, %d transitions" % (len(pieces), len(ed.get("transitions", [])) - len(missing))] + moved
            if getattr(self, "hero_note", ""): self.notes.append(self.hero_note)
            for f, a, length, shown in pieces:  # unusable footage in a planned shot, or a shot slowed below 0.75x, is reported
                if variant(f) != variant(src) and "person" not in (shots or {}).get(os.path.basename(f), {}):
                    self.notes.append("%s is another variant's footage and its shot check has no \"person\" list: "
                                      "check by eye that its person is not on screen" % os.path.basename(f)[-28:])
                bad = [b for b in blocked(f, shots, src) if a < b[1] and b[0] < a + length]
                if bad: self.notes.append("%s %.2f-%.2f s uses a bad stretch: %s" % (os.path.basename(f)[-28:], a, a + length, bad[0][2]))
                elif length / shown < 0.75: self.notes.append("%s from %.2f s slowed to %.2fx to fill %.1f s; split the sentence into two shots"
                                                              % (os.path.basename(f)[-28:], a, length / shown, shown))
            if missing: self.notes.append("no punchline transition downloaded in CapCut (Pale Clarity or Slide Blur), left out at %s s" % missing)
        elif shots and shots.get(os.path.basename(src), {}).get("checked"):
            pieces, self.notes = plan_footage(src, total / US, shots, pool)
            lay_footage(d, r, pieces, media_dir)
            self.pieces = pieces
        self.style, spec = typeset.style_for(cfg)
        if spec and cfg.get("scripted"):  # a scripted script's words keep the writer's case (no upper-casing by the style)
            spec = copy.deepcopy(spec); spec["line1"].pop("case0", None)
        if spec:  # the type system: this ad's style instead of the one house look (references/typography.md)
            tn = []
            tm = self.times or {}
            typeset.restyle(d, r, dict(cfg, _cta=cfg.get("cta") or brand["cta"], _line1b=tm.get("line1b", 0.0),
                                       _line5s=tm.get("line5s", 0.0) if cfg.get("scarcity", True) else 0.0,
                                       _scarcity=brand.get("scarcity_on_screen")),
                            spec, K, EFFECTS, mat, seg_of, tn, inner=inner, clone=lambda s, m: add_text_track(d, s, m))
            self.notes = (self.notes or []) + ["type: %s" % self.style] + tn
        self.scripted_sfx = None
        if cfg.get("scripted"):
            if not self.times: raise SystemExit("%s: could not find where each part of the scripted script starts. Give "
                                                "\"ends\" in the edit plan." % self.name)
            pn = []; self.scripted_sfx = scripted_cards(d, r, cfg, self.times, total, spec, pn)
            st = self.times["starts"]
            self.notes = (self.notes or []) + pn + ["scripted cards: hook 0.00-%s, %s%s (%s)" % (
                "%.2f" % self.scripted_sfx[0][0], ", ".join("%.2f" % t for t, k in self.scripted_sfx if k == "card"),
                ", logo %.2f" % self.scripted_sfx[-1][0] if self.scripted_sfx[-1][1] == "cta" else "",
                self.times.get("timing", "pauses"))]
        if getattr(self, "text_notes", None):
            self.notes = (self.notes or []) + ["text timing: %s" % (self.times or {}).get("timing", "-")] + self.text_notes
        if getattr(self, "text_overlaps", None): self.notes = (self.notes or []) + self.text_overlaps
        add_vo(d, self.vo, spans)
        track = pick_music(brand, cfg, slot); self.music_name = track["name"] if track else "-"
        self.music = add_music(d, track) if track else None
        self.sfx = add_sfx(d, self.scripted_sfx if self.scripted_sfx is not None else sfx_events(d, r)) if cfg.get("sfx", True) else (0, [])
        if spec and not cfg.get("scripted") and inner is not None:  # the type styles: Line 2 as plain text (owner, Nov 17)
            flatten_title(d, r, inner); self.compound = None
        if getattr(self, "pieces", None) and not cfg.get("text_fixed"):  # text placed by the picture (owner, Nov 18)
            import text_fit
            wk = os.path.dirname(os.path.dirname(os.path.abspath(os.path.expanduser(cfg["video"]))))
            fn = []; text_fit.fit(d, self.pieces, K, find_ffmpeg(), fn, logo_mid=r.get("logo"),
                                  preview=os.path.join(wk, "plan", "text", re.sub(r'[\/:*?"<>|]', "-", self.name) + ".jpg"), title=self.name,
                                  logo_light=(lambda: link_media(ROOT + "/brand/" + brand["logo"].replace("black", "white").replace("brown", "white"), media_dir)) if os.path.exists(ROOT + "/brand/" + brand["logo"].replace("black", "white").replace("brown", "white")) else None, text_y=cfg.get("text_y"))
            self.notes = (self.notes or []) + fn
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
        if t.compound:  # the house look's animated title clip (the type styles lay Line 2 as plain text)
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
        if t.compound:
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

    def pool(c): return group_pool(cfg, c, shots)

    def _old_pool(c):  # kept for reference: group_pool() is the same, shared with plan_sheet.py and cut_sheet.py
        v = os.path.expanduser(c["video"]); out = spare(v)
        for o in cfg["timelines"]:
            if o is not c and c.get("group") and o.get("group") == c["group"]:
                ov = os.path.expanduser(o["video"]); out += [ov] + spare(ov)
        return [p for p in out if shots.get(os.path.basename(p), {}).get("checked")]

    slots, tls = {}, []  # the music pool rotates per brand, in the order the timelines are listed
    for c in cfg["timelines"]:
        slots[c["brand"]] = slots.get(c["brand"], -1) + 1
        if c.get("locked"):  # finished or exported by hand (owner): never rebuilt, never replaced
            print("%-34s LOCKED, left as it is: %s" % (c["name"], c["locked"])); continue
        tls.append(Timeline(c, media_dir, shots, pool(c), slots[c["brand"]]))
    for t in tls:
        miss, ok = t.check()
        print("%-34s %.1fs | VO %s | music %s (%s) | sfx %d | missing refs %d | media ok %s" % (
            t.name, t.dur / US, os.path.basename(t.vo), t.music_name[:28],
            {None: "-", True: "yes", False: "NOT DOWNLOADED"}[t.music], t.sfx[0], miss, ok))
        if t.sfx[1]: print("    sound effects not in CapCut yet, left out:", ", ".join(t.sfx[1]))
        if t.times: print("    sentences start at", [round(x, 2) for x in t.times["starts"][1:]], "punchline", t.times["punch"])
        if getattr(t, "vo_cut", False): print("    VOICE-OVER CUT OFF: the last sentence plays far faster than the rest, so the video ends before it does. "
                                             "Make a new voice-over in Negen (Review > the video > New voice-over) or shorten the script.")
        if t.notes is None: print("    shot check: not done for this video, footage used as it is")
        for n in t.notes or []: print("    shot check:", n)
    gone = sorted({t.music_name for t in tls if t.music is False})
    if gone: print("NOTE: music not in CapCut yet, so left out: %s. Use it once in CapCut (Audio > search the name), "
                   "then build again." % ", ".join(gone))
    import qc  # the fundamentals gate (references/fundamentals.md): every shot reviewed, the voice matches the person
    wk = os.path.dirname(os.path.abspath(sys.argv[1]))
    if "--save" not in sys.argv and "--replace" not in sys.argv:
        qc.sheets(wk, tls, find_ffmpeg()); print("review sheets: %s (judge every shot against references/fundamentals.md, write qc.json)" % os.path.join(wk, "qc"))
    if "--only" in sys.argv:
        want = sys.argv[sys.argv.index("--only") + 1].split(","); tls = [t for t in tls if any(w in t.name for w in want)]
    if "--save" in sys.argv or "--replace" in sys.argv:
        no = qc.gate(wk, tls)
        if "--vo-update" in sys.argv:  # removed Nov 19: it rebuilt the footage too and saved desk V7-V9 unreviewed
            print("NOT SAVED: --vo-update is gone. Every save passes the full gate (references/fundamentals.md)."); sys.exit(2)
        if no:
            print("NOT SAVED. The fundamentals gate refused:"); [print("  -", x) for x in no]; sys.exit(2)
    if "--save" in sys.argv: save(cfg["project"], tls)
    if "--only" in sys.argv: print("only:", [t.name for t in tls])  # rebuild just these timelines, leave the rest
    if "--replace" in sys.argv: replace_in(cfg["project"], tls, os.path.dirname(os.path.abspath(sys.argv[1])))
