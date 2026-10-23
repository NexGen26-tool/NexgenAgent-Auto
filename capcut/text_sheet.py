#!/usr/bin/env python3
"""Fallback when CapCut on this computer cannot take built projects (build_project.py --check says so):
write one text sheet with every video's on-screen lines, times and house-edit styling, to type in by hand.

  python capcut/text_sheet.py work/<week>/capcut.json        ->  work/<week>/text-sheet.md
"""
import json, os, sys

BRANDS = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "brand", "brands.json"),
                        encoding="utf-8"))


def main():
    if len(sys.argv) != 2: sys.exit(__doc__)
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    out = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "text-sheet.md")
    rows = ["# " + cfg.get("project", "Text sheet"), "",
            "House edit: Montserrat, white with a thin black stroke, no background. Mute the clip's own sound and put",
            "the voice-over on its own track (right-click the clip > Extract audio). Logo on top all the way through.",
            "Out-animation Smoke on the video at the end.", ""]
    for t in cfg["timelines"]:
        brand = BRANDS[t["brand"]]
        l1, l2, l3, l5 = t["line1"], t["line2"], t["line3"], t["line5"]
        rows += ["## " + t["name"], "",
                 "- File: `%s`  Logo: `brand/%s`" % (os.path.basename(t["video"]), brand["logo"]),
                 "- 0.0-2.7 s, upper middle: **%s** (big) / %s (small) + *%s* (orange italic, PT Sans)" % (l1[0], l1[1].strip(), l1[2]),
                 "- 2.7-6.0 s, animated title (Zoom 1 in): *%s* (small italic) + **%s** (big, cream, HV-Analogue)" % (l2[0].strip(), l2[1]),
                 "- 6.4-10.0 s, lower left: %s   then 7.3-10.0 s, lower right: %s" % (l3[0], l3[1]),
                 "- 10.0-13.5 s, lower middle: %s" % t["line4"],
                 "- 13.5-17.0 s, lower middle: %s / **%s** (bigger, yellow)" % (l5[0], l5[1]),
                 "- 17.1-20.0 s, CTA: %s" % (t.get("cta") or brand["cta"]), ""]
    open(out, "w", encoding="utf-8").write("\n".join(rows))
    print("saved:", out)


if __name__ == "__main__":
    main()
