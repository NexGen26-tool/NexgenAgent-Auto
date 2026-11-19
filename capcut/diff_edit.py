"""What the owner changed by hand in a CapCut timeline, against the version the build saved (capcut-backup/).

  python capcut/diff_edit.py <project folder> <backup folder> [<name part> ...]

Prints, per timeline, both versions side by side: every video shot (file, source in/out, place on the timeline,
speed), every text (words, place, size, timing), the audio (voice, music, effects, volume) and the transitions. The
lessons go into references/typography.md, the build and rule-changes.md (owner, Nov 18: learn from the hand edits).
"""
import json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
US = 1e6


def load(folder):
    for n in ("draft_content.json", "draft_info.json"):
        p = os.path.join(folder, n)
        if os.path.exists(p): return json.load(open(p, encoding="utf-8"))
    return None


def summary(d):
    mats = {}
    for kind, arr in d.get("materials", {}).items():
        if isinstance(arr, list):
            for m in arr:
                if isinstance(m, dict) and "id" in m: mats[m["id"]] = (kind, m)
    out = {"dur": d.get("duration", 0) / US, "video": [], "text": [], "audio": [], "trans": []}
    for tr in d.get("tracks", []):
        for s in tr.get("segments", []):
            kind, m = mats.get(s.get("material_id"), ("?", {}))
            tt = s.get("target_timerange") or {}; st = s.get("source_timerange") or {}
            a, b = tt.get("start", 0) / US, (tt.get("start", 0) + tt.get("duration", 0)) / US
            if tr.get("type") == "video" and kind == "videos":
                name = os.path.basename(m.get("path", ""))
                if "logo" in name.lower() or m.get("type") == "photo": continue
                tag = re.sub(r"^.*? - ([A-Z0-9]+ - VID[A-Z0-9]+)", r"\1", name.replace(" - 20-11-2026", "").replace(".mp4", ""))
                out["video"].append((round(a, 2), round(b, 2), tag, round(st.get("start", 0) / US, 2),
                                     round(s.get("speed", 1.0), 2), round(s.get("clip", {}).get("scale", {}).get("x", 1), 2)))
            elif kind == "texts":
                try: txt = json.loads(m.get("content", "{}")).get("text", "")
                except Exception: txt = m.get("content", "")
                c = s.get("clip", {}); tf = c.get("transform", {})
                out["text"].append((round(a, 2), round(b, 2), txt.replace("\n", " / ")[:48], round(tf.get("x", 0), 2),
                                    round(tf.get("y", 0), 2), round(c.get("scale", {}).get("x", 1), 2)))
            elif kind == "audios":
                out["audio"].append((round(a, 2), round(b, 2), (m.get("name") or os.path.basename(m.get("path", "")))[-40:],
                                     round(s.get("volume", 1), 2), round(s.get("speed", 1.0), 2)))
    for t in d.get("materials", {}).get("transitions", []):
        out["trans"].append((t.get("name"), round(t.get("duration", 0) / US, 2)))
    for k in ("video", "text", "audio"): out[k].sort()
    return out


def show(title, s):
    print("  %s  %.1f s" % (title, s["dur"]))
    for v in s["video"]: print("    V %5.2f-%5.2f  %-28s from %5.2f  x%.2f  zoom %.2f" % v)
    for t in s["text"]: print("    T %5.2f-%5.2f  %-48s  x %.2f y %.2f  scale %.2f" % t)
    for a in s["audio"]: print("    A %5.2f-%5.2f  %-40s vol %.2f  x%.2f" % a)
    if s["trans"]: print("    transitions:", s["trans"])


def main(project, backup, parts):
    for tid in sorted(os.listdir(os.path.join(project, "Timelines"))):
        now = load(os.path.join(project, "Timelines", tid))
        if not now: continue
        s = summary(now); key = " ".join(v[2] for v in s["video"][:1])
        if parts and not any(p in json.dumps([v[2] for v in s["video"]]) for p in parts): continue
        print("=" * 100); print(tid, key)
        old = load(os.path.join(backup, tid)) if backup and os.path.isdir(os.path.join(backup, tid)) else None
        if old: show("BUILD (before the owner)", summary(old))
        show("OWNER (now)", s)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "", sys.argv[3:])
