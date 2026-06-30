#!/usr/bin/env python3
"""TSC-01 fidelity gate for the 1260H entity extraction.

Two independent checks, both must pass:
  1. GOLDEN OUTPUT: re-running parse_1260h.py on the committed input reproduces the committed
     entities_1260h.json exactly (structure, names, attribution, rationale) — not just counts.
  2. NAME DIFF: the parser's parent / subsidiary / delisted NAME SETS exactly match the committed,
     human-auditable entities_manifest.txt.

A structural parse bug that preserves the 80/108/10 totals but mis-attributes a subsidiary or
mis-splits a name fails check 1 and/or 2. Exit non-zero on any mismatch.

Run:  python3 test_parser.py
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PARSER = os.path.join(HERE, "parse_1260h.py")
COMMITTED = os.path.join(HERE, "entities_1260h.json")
MANIFEST = os.path.join(HERE, "entities_manifest.txt")
EXPECTED = {"parents": 80, "subsidiaries": 108, "delisted": 10}

fail = []

# --- run the parser fresh ---
proc = subprocess.run([sys.executable, PARSER], capture_output=True, text=True)
if proc.returncode != 0:
    print("FAIL: parser exited non-zero\n" + proc.stderr.strip())
    sys.exit(1)
parsed = json.loads(proc.stdout)
committed = json.load(open(COMMITTED, encoding="utf-8"))

# --- check 1: golden output ---
if parsed != committed:
    fail.append("golden-output mismatch: fresh parse != committed entities_1260h.json")

# --- counts ---
got = {
    "parents": len(parsed["designated_parents"]),
    "subsidiaries": sum(p["subsidiary_count"] for p in parsed["designated_parents"]),
    "delisted": len(parsed["delisted_entities"]),
}
if got != EXPECTED:
    fail.append(f"count mismatch: {got} != {EXPECTED}")

# --- check 2: name diff vs the auditable manifest ---
man = open(MANIFEST, encoding="utf-8").read()
def section(name):
    # lines under "## NAME (n)" until the next "## " or EOF, stripped of the "NN. " / "NNN. " index
    body = re.split(rf"## {name} \(\d+\)\n", man)[1].split("\n## ")[0]
    out = []
    for ln in body.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        out.append(re.sub(r"^\d+\.\s*", "", ln))
    return out

man_parents = set(section("PARENTS"))
man_delisted = set(section("DELISTED"))
man_subs = set(s.split("] ", 1)[1] for s in section("SUBSIDIARIES"))  # drop "[parent] " prefix

p_parents = set(p["name"] for p in parsed["designated_parents"])
p_subs = set(s for p in parsed["designated_parents"] for s in p["subsidiaries"])
p_delisted = set(parsed["delisted_entities"])

for label, a, b in [("parents", p_parents, man_parents),
                    ("subsidiaries", p_subs, man_subs),
                    ("delisted", p_delisted, man_delisted)]:
    if a != b:
        miss = sorted(b - a)[:3]
        extra = sorted(a - b)[:3]
        fail.append(f"{label} name diff: missing={miss} extra={extra}")

if fail:
    print("TSC-01 FAIL:")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print(f"TSC-01 PASS: golden output matches; names match manifest; counts {got}.")
