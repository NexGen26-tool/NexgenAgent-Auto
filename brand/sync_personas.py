#!/usr/bin/env python3
"""Copy the team's persona registry into brand/personas.json, the persona pack the briefs are built from.

  python brand/sync_personas.py [path to persona-db-team_codified.md]

Default source: ~/Desktop/NexGen/spry-creative-system/analysis/persona-db-team_codified.md (the team's code registry,
an English snapshot of their persona sheet). Run it again whenever the team edits the sheet. It reads every persona
table (any columns) and every "full team-schema record" block, and keeps per code: name, awareness, desire (LF8),
barrier (the objection in the buyer's words), angle, hook seed, tier, status, and from a full record the persona
snapshot, the benefit, the hook ideas, the proof the ad must show and the HARD NO list. brand/personas.json also
keeps hand-written "objections", "category_proof" and "rules" (not in the registry); they survive a sync.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.expanduser("~/Desktop/NexGen/spry-creative-system/analysis/persona-db-team_codified.md")
COLS = {"persona (en)": "name", "soa": "awareness", "lf8": "desire", "core barrier": "barrier",
        "angle territory": "angle", "hook seed": "hook_seed", "v2 tier": "tier", "status": "status"}
FIELDS = {"persona snapshot": "snapshot", "core desire": "desire_full", "customer thought": "barrier_full",
          "lợi ích chính": "benefit", "angle (góc": "angles", "hook gợi ý": "hook_ideas", "proof / demo": "proof"}


def clean(s): return re.sub(r"\*\*|\*|`", "", s).strip()


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    lines = open(src, encoding="utf-8").read().splitlines()
    out_path = os.path.join(HERE, "personas.json")
    old = json.load(open(out_path, encoding="utf-8")) if os.path.exists(out_path) else {}
    personas, family, header, record = {}, "", None, None
    for ln in lines:
        if ln.startswith("## "): family = clean(ln[3:]); header = None
        if ln.startswith("|") and "---" not in ln:
            cells = [clean(c) for c in ln.strip().strip("|").split("|")]
            if cells[0].lower() == "code": header = [c.lower() for c in cells]; continue
            m = re.match(r"([A-Z]{3}-\d+[a-z]?)", cells[0])
            if header and m:
                p = personas.setdefault(m.group(1), {"family": family})
                for h, v in zip(header[1:], cells[1:]):
                    if h in COLS and v: p[COLS[h]] = v
                if "[candidate]" in cells[0]: p["status"] = "candidate"
        m = re.match(r"### ([A-Z]{3}-\d+[a-z]?)\b", ln)
        if m: record = m.group(1); continue
        if record and ln.startswith("- **"):
            key = clean(ln[2:].split(":", 1)[0]).lower()
            val = clean(ln.split(":", 1)[1]) if ":" in ln else ""
            for k, f in FIELDS.items():
                if key.startswith(k):
                    if f == "proof":
                        hard = re.split(r"HARD NO:", val, maxsplit=1)
                        personas[record]["proof"] = [x.strip(" .") for x in hard[0].split("·") if x.strip(" .")]
                        if len(hard) > 1: personas[record]["hard_no"] = [x.strip(" .") for x in re.split(r"·|;", hard[1]) if x.strip(" .")]
                    else: personas.setdefault(record, {})[f] = val
        if ln.startswith("---"): record = None
    data = {"_about": "Persona pack for the briefs (ad-brief-compiler, Conversion). Synced from %s by "
                      "brand/sync_personas.py; objections and category_proof are written by hand." % os.path.basename(src),
            "personas": personas, "objections": old.get("objections", {}), "category_proof": old.get("category_proof", {}), "rules": old.get("rules", {})}
    json.dump(data, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("%d personas -> %s" % (len(personas), out_path))
    for code in ("CST-03", "CFT-03", "TBS-07", "SDB-01"):
        if code in personas: print(" ", code, {k: (v if isinstance(v, str) else v[:2]) for k, v in personas[code].items() if k in ("barrier", "hook_seed", "proof")})


if __name__ == "__main__":
    main()
