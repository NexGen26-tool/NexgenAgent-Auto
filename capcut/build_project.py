#!/usr/bin/env python3
"""Build a CapCut project (CapCut 9.x on Mac or Windows) with one timeline per video, every timeline already in the house edit:
Montserrat text with black stroke, a big/small/orange hook (Line 1), the animated two-part title (Line 2), the split
Line 3, the yellow last phrase of Line 5, the CTA, the brand logo on top, Smoke out at the end, and the voice-over on
its own track with the clip's own sound off.

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
TEMPLATE_EFFECTS = "{HOME}/Library/Containers/com.lemon.lvoverseas/Data/Movies/CapCut/User Data/Cache/effect"
US = 1_000_000
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


def add_vo(d, path):
    tp = json.load(open(HERE + "/templates/vo_track.json", encoding="utf-8"))
    dur = mp4_info(path)[0]  # an .m4a has the same header as an .mp4
    m = copy.deepcopy(tp["mat"]); m["id"] = uid()
    m.update({"path": path, "name": os.path.splitext(os.path.basename(path))[0], "duration": us(dur)})
    d["materials"].setdefault("audios", []).append(m)
    s = copy.deepcopy(tp["seg"]); s["id"] = uid(); s["material_id"] = m["id"]; refs = []
    for k, items in tp["extra"].items():
        for it in items:
            n = copy.deepcopy(it); n["id"] = uid(); d["materials"].setdefault(k, []).append(n); refs.append(n["id"])
    s["extra_material_refs"] = refs
    span = min(us(dur), d["duration"])
    s["source_timerange"] = {"start": 0, "duration": span}; s["target_timerange"] = {"start": 0, "duration": span}
    s["volume"] = 1.0; s["last_nonzero_volume"] = 1.0; s["speed"] = 1.0
    s["render_index"] = 0; s["track_render_index"] = len(d["tracks"])
    d["tracks"].append({"id": uid(), "type": "audio", "segments": [s], "flag": 0, "attribute": 0,
                        "name": "Voice-over", "is_default_name": False})


class Timeline:
    def __init__(self, cfg, media_dir):
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

        add_vo(d, self.vo)
        self.d = d

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
    tls = [Timeline(c, media_dir) for c in cfg["timelines"]]
    for t in tls:
        miss, ok = t.check()
        print("%-34s %.1fs | VO %s | missing refs %d | media ok %s" % (t.name, t.dur / US, os.path.basename(t.vo), miss, ok))
    if "--save" in sys.argv: save(cfg["project"], tls)
