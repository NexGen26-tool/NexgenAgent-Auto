#!/usr/bin/env python3
"""Pick who is on screen in each video of the week (CLAUDE.md step 1).

  python brand/pick_cast.py work/<week>            # fills "cast" on every video that has none
  python brand/pick_cast.py work/<week> --again    # picks everyone again

Each video gets one person from brand/cast.json, from the pool its group's persona belongs to (a video's own
persona wins). An explore group's three videos get three different people (an iterate group one person for all three,
so only the hook changes), mixing relatable (looks like the buyer today) and aspirational (who the buyer
wants to become); nobody is used twice in a week while the pool has others, and people from the last two weeks are
skipped while the pool allows. The pick changes from week to week but is the same if run again on the same week.
The brief writes the video's "cast" as ACTOR A in every row (ad-brief-compiler, 5).

It also gives every video its voice-over voice ("voice"), so the voice matches the person on screen: the brand's
"voices" in brand/brands.json by the person's gender ("man", "woman"), else the brand's "voice" (a couple, or a
brand with no voice for that gender). A voice set by hand on the video stays.
"""
import glob, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    if len(sys.argv) < 2: raise SystemExit(__doc__)
    week_dir = os.path.abspath(sys.argv[1]); again = "--again" in sys.argv
    path = os.path.join(week_dir, "week.json")
    week = json.load(open(path, encoding="utf-8"))
    cast = json.load(open(os.path.join(HERE, "cast.json"), encoding="utf-8"))
    people = {p["id"]: p for p in cast["people"]}
    brands = json.load(open(os.path.join(HERE, "brands.json"), encoding="utf-8"))

    # people on screen in the two weeks before this one
    recent, last = set(), set()  # people of the last two weeks, and of the week before only
    others = []
    for f in glob.glob(os.path.join(os.path.dirname(week_dir), "*", "week.json")):
        if os.path.abspath(os.path.dirname(f)) == week_dir: continue
        try: w = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError): continue
        if w.get("week", "") < week.get("week", ""): others.append(w)
    for n, w in enumerate(sorted(others, key=lambda w: w.get("week", ""), reverse=True)[:2]):
        ids = {v["cast"]["id"] for g in w.get("groups", []) for v in g.get("videos", []) if v.get("cast")}
        recent |= ids
        if n == 0: last = ids

    used = set() if again else {v["cast"]["id"] for g in week["groups"] for v in g["videos"] if v.get("cast")}
    shuffle = lambda ids, salt: sorted(ids, key=lambda i: hashlib.sha1((week.get("week", "") + salt + i).encode()).hexdigest())
    rows = []
    for gi, g in enumerate(week["groups"]):
        in_group = set() if again else {v["cast"]["id"] for v in g["videos"] if v.get("cast")}
        for vi, v in enumerate(g["videos"]):
            code = v.get("persona") or g.get("persona", "")  # each video's own buyer (Nov 10); older weeks: the group's
            pool = cast["personas"].get(code) or cast["personas"].get(code.rstrip("abcdefghijklmnopqrstuvwxyz")) or "everyday"
            if v.get("cast") and not again:
                rows.append((g, v)); continue
            if g.get("mode") == "iterate" and vi and g["videos"][0].get("cast"):  # one body, three hooks: one person,
                v["cast"] = dict(g["videos"][0]["cast"]); rows.append((g, v)); continue  # so only the hook changes
            kind = ("relatable", "aspirational")[(vi + gi) % 2]  # alternate, and alternate the pattern between groups
            # freshness first, then the relatable/aspirational mix, then anyone not already in this group
            tiers = [lambda p: p["kind"] == kind and p["id"] not in used | recent,
                     lambda p: p["kind"] == kind and p["id"] not in used | last,
                     lambda p: p["id"] not in used | last | in_group,
                     lambda p: p["kind"] == kind and p["id"] not in used,
                     lambda p: p["id"] not in used | in_group,
                     lambda p: p["id"] not in in_group]
            for test in tiers:
                ids = [i for i in shuffle([p["id"] for p in cast["people"] if p["pool"] == pool], (v.get("angle") or g.get("angle", "")) + str(vi))
                       if test(people[i])]
                if ids: break
            p = people[ids[0]]
            v["cast"] = {"id": p["id"], "kind": p["kind"], "who": p["who"]}
            used.add(p["id"]); in_group.add(p["id"])
            rows.append((g, v))
    for g, v in rows:  # the voice follows the person on screen
        brand = brands.get(g.get("store", ""), {})
        m = re.search(r"\b(woman|man)\b", v["cast"]["who"]); gender = m.group(1) if m else "couple"
        v["cast"]["gender"] = gender
        if not v.get("voice_set_by_hand"):
            v["voice"] = brand.get("voices", {}).get(gender) or g.get("voice") or brand.get("voice", "")
    json.dump(week, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for g, v in rows:
        print("%-16s %-16s %s  %-3s %-12s %-6s %-5s %s" % (g.get("product", "")[:16], g.get("angle", "")[:16], v["variant"],
              v["cast"]["id"], v["cast"]["kind"], v["cast"]["gender"], v["voice"], v["cast"]["who"][:60]))


if __name__ == "__main__":
    main()
