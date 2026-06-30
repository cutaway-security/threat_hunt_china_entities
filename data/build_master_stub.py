#!/usr/bin/env python3
"""Build the entities-only master stub (v0.1) from the verified entity extraction.

Every entity is assigned `candidate_pending_verification` — the honest pre-assessment disposition.
Specific dispositions (no_windows_software_found, hardware_or_firmware_only, etc.) and the `software`
arrays are populated during v0.2 software identification, each with a defensible justification/source.
No software or indicators are invented here (verified-not-derived).

Output is validated against data/schema/master.schema.json.
Run:  python3 data/build_master_stub.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source_extraction", "entities_1260h.json")
SCHEMA = os.path.join(HERE, "schema", "master.schema.json")
OUT = os.path.join(HERE, "master", "entities.master.json")

ext = json.load(open(SRC, encoding="utf-8"))
parents = ext["designated_parents"]

entities = []
for i, p in enumerate(parents, 1):
    subs = []
    for s in p["subsidiaries"]:
        # subsidiary short alias only from a name-terminating parenthetical (same rule as the parser)
        alias = None
        sn = s.strip()
        if sn.endswith(")"):
            import re
            m = re.findall(r"\(([^()]*)\)$", sn)
            if m and not m[-1].lower().startswith(("formerly", "also known")):
                alias = m[-1].strip()
        subs.append({"name": s, "short_alias": alias})
    entities.append({
        "company_id": f"C{i:04d}",
        "name": p["name"],
        "short_alias": p.get("short_alias"),
        "affiliation_rationale": p.get("rationale", ""),
        "subsidiaries": subs,
        "disposition": "candidate_pending_verification",
        "disposition_justification": "Software footprint not yet assessed; disposition and any software are assigned during v0.2 software identification, each with a cited justification.",
        "software": []
    })

master = {
    "meta": {
        "source_pdf": "ENTITIES-IDENTIFIED-AS-CHINESE-MILITARY-COMPANIES-OPERATING-IN-THE-UNITED-STATES-IN-ACCORDANCE-WITH-SECTION-1260H.PDF",
        "source_url": "https://media.defense.gov/2026/Jun/08/2003945537/-1/-1/1/ENTITIES-IDENTIFIED-AS-CHINESE-MILITARY-COMPANIES-OPERATING-IN-THE-UNITED-STATES-IN-ACCORDANCE-WITH-SECTION-1260H.PDF",
        "source_date": "2026-06-08",
        "list_version": "2026-06-08",
        "best_effort": True
    },
    "entities": entities,
    "delisted": list(ext["delisted_entities"]),
    "backlog": []
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(master, f, ensure_ascii=False, indent=2)

# Validate against the schema (jsonschema is in the project .venv).
try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("jsonschema not available; run with the project .venv: .venv/bin/python data/build_master_stub.py")
schema = json.load(open(SCHEMA, encoding="utf-8"))
errs = sorted(Draft202012Validator(schema).iter_errors(master), key=lambda e: list(e.path))
if errs:
    print("SCHEMA VALIDATION FAILED:")
    for e in errs[:10]:
        print("  ", list(e.path), e.message)
    sys.exit(1)
print(f"OK: master stub written ({len(entities)} entities, {len(master['delisted'])} delisted), validates against schema.")
