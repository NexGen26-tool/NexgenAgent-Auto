#!/usr/bin/env python3
"""Which products this week's fast lane makes (CLAUDE.md step 1, "Pick the products").

  python brand/pick_products.py work/<week>

Reads, from the week folder:
  sheet.json  what negen/read_sheet.js returned for the tracking sheet's tabs, as {"Spry": {...}, "ETW": {...}}
              (each with "header" and "rows"), this month and last month;
  meta.json   one row per Meta ad over the last 90 days, as a list of {"store": "spry|etw", "name", "spend", "atc",
              "purchases", "value"} (from the Meta Ads connector, or an Ads Manager export saved the same way);
  week.json   "creator" (the person's name in the sheet's Assigned column) and "date".
and the earlier weeks' week.json beside it.

1. Assigned first: rows of this month where Assigned is the creator and Trạng thái video is still empty are products
   the team already gave this person. They are this week's products, with their persona and angle when the row has one.
2. Otherwise it picks: per store, the SKUs that sell on Meta (purchases in the last 90 days), ranked by purchases, then
   purchase value per dollar spent; skipping SKUs someone else holds an open assignment for this month and SKUs this
   fast lane made in the last 14 days. A SKU whose best ad is this creator's own video goes iterate on it (the control);
   the rest explore. Only what Meta shows is used: no store orders, no margins.
Prints the plan per store and writes it to work/<week>/pick.json for the step-1 popup.
"""
import glob, json, os, re, sys
from datetime import date, datetime

SKU_IN_NAME = re.compile(r"\|\s*([A-Z0-9]{8,24})\s*-")  # "<Name> | <Angle> | <SKU> - <Code> - <date>"


def base(sku):
    """The SKU without its variant suffix: SILDTCSC009TBNA -> SILDTCSC009 (ads and sheet rows join on it)."""
    m = re.match(r"^([A-Z]+\d{3})", sku or "")
    return m.group(1) if m else (sku or "")


def load(p, default=None):
    if not os.path.exists(p): return default
    return json.load(open(p, encoding="utf-8-sig"))


def main(week_dir):
    week = load(os.path.join(week_dir, "week.json"), {})
    creator = (week.get("creator") or "").strip()
    sheet = load(os.path.join(week_dir, "sheet.json"), {})
    ads = load(os.path.join(week_dir, "meta.json"), [])
    month = "Tháng %d/%d" % (date.today().month, date.today().year)

    # what this fast lane made in the last 14 days (earlier weeks of this repo)
    recent = set()
    for f in glob.glob(os.path.join(os.path.dirname(os.path.abspath(week_dir)), "*", "week.json")):
        if os.path.dirname(os.path.abspath(f)) == os.path.abspath(week_dir): continue
        w = load(f, {})
        try: when = datetime.strptime(w.get("week", "")[:10], "%Y-%m-%d").date()
        except ValueError: continue
        if (date.today() - when).days <= 14:
            recent |= {base(g.get("sku", "")) for g in w.get("groups", [])}

    plan = {}
    for tab, store in (("Spry", "spry"), ("ETW", "etw")):
        t = sheet.get(tab) or {}
        h = t.get("header") or []
        rows = [dict(zip(h, r)) for r in t.get("rows") or []]
        open_rows = [r for r in rows if r.get("Tháng") == month and not r.get("Trạng thái video")]
        mine = [r for r in open_rows if r.get("Assigned") == creator]
        others = {base(r["SKU"]) for r in open_rows if r.get("Assigned") != creator}

        # Meta: per SKU, from the codified ad names
        score = {}
        for a in ads:
            if a.get("store") != store: continue
            m = SKU_IN_NAME.search(a.get("name", ""))
            if not m: continue
            s = score.setdefault(base(m.group(1)), {"sku": m.group(1), "spend": 0.0, "atc": 0, "purchases": 0,
                                                    "value": 0.0, "best": None})
            for k in ("spend", "value"): s[k] += float(a.get(k) or 0)
            for k in ("atc", "purchases"): s[k] += int(float(a.get(k) or 0))
            key = (int(float(a.get("purchases") or 0)), float(a.get("value") or 0))
            if key[0] and (not s["best"] or key > s["best"][0]): s["best"] = (key, a["name"])

        if mine:
            seen, picks = set(), []
            for r in mine:
                if base(r["SKU"]) in seen: continue
                seen.add(base(r["SKU"]))
                s = score.get(base(r["SKU"]), {})
                picks.append({"sku": r["SKU"], "why": "assigned to %s in the sheet" % creator,
                              "persona": r.get("Persona", ""), "angle": r.get("Angle", ""),
                              **mode_of(s, creator)})
            plan[store] = {"source": "assigned", "picks": picks}
            continue

        ranked = sorted((s for b, s in score.items() if s["purchases"] and b not in others and b not in recent),
                        key=lambda s: (-s["purchases"], -(s["value"] / s["spend"] if s["spend"] else 0)))
        picks = []
        for s in ranked[:4]:
            roas = s["value"] / s["spend"] if s["spend"] else 0
            picks.append({"sku": s["sku"], "why": "%d purchases, %.1fx on $%.0f (90 days)" % (s["purchases"], roas, s["spend"]),
                          "persona": "", "angle": "", **mode_of(s, creator)})
        plan[store] = {"source": "meta", "picks": picks,
                       "skipped": {"held by others this month": sorted(others & set(score)),
                                   "made by this lane in 14 days": sorted(recent & set(score))}}

    json.dump(plan, open(os.path.join(week_dir, "pick.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for store, p in plan.items():
        print("%s (%s):" % (store, "assigned in the sheet" if p["source"] == "assigned" else "picked from Meta"))
        for x in p["picks"]:
            print("  %-18s %-8s %s%s" % (x["sku"], x["mode"], x["why"], ("  control: " + x["control"]) if x.get("control") else ""))
        if not p["picks"]: print("  nothing: no assignment and no selling SKU left (ask the person)")
        for k, v in (p.get("skipped") or {}).items():
            if v: print("  skipped, %s: %s" % (k, ", ".join(v)))


def mode_of(s, creator):
    """iterate on the SKU's best ad when that ad is this creator's own video; explore otherwise."""
    best = (s or {}).get("best")
    if best and creator and best[1].startswith(creator + " |"):
        return {"mode": "iterate", "control": best[1]}
    return {"mode": "explore", "control": ""}


if __name__ == "__main__":
    if len(sys.argv) != 2: raise SystemExit(__doc__)
    main(sys.argv[1])
