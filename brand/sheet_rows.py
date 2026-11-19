"""Step 8: one paste-ready row per video for the tracking sheet, in that tab's own column order, every dropdown cell
one of the sheet's own options (owner, Nov 18: "use the options available, don't invent").

  python brand/sheet_rows.py work/<week>

Needs work/<week>/sheet-options.json (negen/read_options.js run on the sheet's Spry and ETW tabs, saved as
{"Spry": {header, options}, "ETW": {...}}) and a "collection" on every group of week.json picked from that tab's
Collection list. Writes sheet-rows-spry.tsv and sheet-rows-etw.tsv (one per tab: the tabs' columns differ). Stops,
writing nothing, when any dropdown cell is not one of the sheet's options.
"""
import json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
STYLE = {"PD": "Product demo", "UG": "UGC", "BA": "B&A"}
AW = {"T": "TOF", "M": "MOF", "B": "BOF"}
HOOK = {"HC": "Call out Hook", "HP": "Product Hook", "HI": "Intrigue Hook"}
OFFER = {"NA": "Không có offer", "FS": "Free shipping", "CO": "Combo 6 (Free Shipping + Customize)"}
TAB = {"spry": "Spry", "etw": "ETW"}


def hook_text(cfg):
    """The hook as it reads on screen, the parts joined with single spaces."""
    if cfg.get("hook_final"): return cfg["hook_final"]  # the hook as the owner finished it by hand in CapCut
    l1 = cfg.get("line1") or []
    parts = [str(x).strip() for x in (l1 if isinstance(l1, list) else [l1]) if str(x).strip()]
    if cfg.get("line1_order") == "setup_first" and len(parts) == 3: parts = parts[1:] + parts[:1]
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def main(wk):
    week = json.load(open(os.path.join(wk, "week.json"), encoding="utf-8"))
    opts = json.load(open(os.path.join(wk, "sheet-options.json"), encoding="utf-8"))
    cap = json.load(open(os.path.join(wk, "capcut.json"), encoding="utf-8")) if os.path.exists(os.path.join(wk, "capcut.json")) else {"timelines": []}
    out, bad = {}, []
    for g in week["groups"]:
        tab = TAB[g["store"]]; spec = opts[tab]; H = spec["header"]
        for v in g["videos"]:
            name = v["name"]; creator, angle, rest = [x.strip() for x in name.split("|")]
            sku, code, date = [x.strip() for x in rest.split(" - ")]
            st, aw, hk, order, off = code[3:5], code[5], code[6:8], code[8], code[9:]
            d, m, y = date.split("/"); month = "Tháng %d/%s" % (int(m), y)
            tl = next((t for t in cap["timelines"] if t["name"].endswith(code) and sku[:10] in t["group"]), {})
            val = {"Tháng": month, "Date": month, "Date Sync": month, "Ref Sync": "%s-%s-01" % (y, m), "Ref sync": "%s-%s-01" % (y, m),
                   "Assigned": creator, "Assigned Array": creator, "Collection": g.get("collection", ""),
                   "Collection (Sync)": g.get("collection", ""), "SKU": sku, "Persona": g.get("persona", ""), "Angle": angle,
                   "Offer": OFFER[off], "Offer (Sync)": OFFER[off], "Offer Code": off, "Type": "Video", "Type Code": "VID",
                   "Type Sync": "Video", "Ads Style": STYLE[st], "Ads Style (Video Format)": STYLE[st], "Ads Style (Sync)": STYLE[st],
                   "Ads Style (Video Sync)": STYLE[st], "Ads Style Code": st, "Level of Awareness": AW[aw], "Awareness (Sync)": AW[aw],
                   "LOA Code": aw, "Loại Hook": HOOK[hk], "Loại Hook (Sync)": HOOK[hk], "Loại Hook Code": hk,
                   "Hook": hook_text(tl), "Stt hook": order, "Stt Hook": order,
                   "Deadline": "%s-%s" % (d, ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][int(m) - 1]),
                   "Tên Video": name, "Tên Ads": name, "Trạng thái video": "Chờ duyệt",
                   "Link Asset mới (đã đổi tên)": os.path.basename(v.get("file", "")), "Link asset mới (đã đổi tên)": os.path.basename(v.get("file", ""))}
            row = [val.get(h, "") for h in H]
            for h, x in zip(H, row):
                if h in spec["options"] and x and x not in spec["options"][h]:
                    bad.append("%s %s: %s = %r is not in the sheet's list %s" % (tab, code, h, x, spec["options"][h]))
                if h in ("Collection", "Assigned", "Tháng") and not x:
                    bad.append("%s %s: %s is empty (week.json group \"collection\"?)" % (tab, code, h))
            out.setdefault(tab, []).append("\t".join(row))
    if bad:
        print("NOT WRITTEN. Cells that are not the sheet's own options:"); [print("  -", b) for b in bad]; sys.exit(2)
    for tab, rows in out.items():
        p = os.path.join(wk, "sheet-rows-%s.tsv" % tab.lower())
        open(p, "w", encoding="utf-8", newline="\r\n").write("\n".join(rows) + "\n"); print("wrote", p, len(rows), "rows")


if __name__ == "__main__":
    main(sys.argv[1])
