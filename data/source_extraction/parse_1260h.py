#!/usr/bin/env python3
"""Parse the 1260H pdftotext -layout output into a verifiable entity structure.

Conservative parser. Output is checked against committed expected counts (80 parents,
108 subsidiaries, 10 delisted) at the end; it exits non-zero on mismatch so a future
1260H layout change cannot silently corrupt the extraction.

Usage:  parse_1260h.py [SRC_TEXT]
  SRC_TEXT defaults to the committed `1260h_pdftotext_layout.txt` next to this script,
  which is produced by:  pdftotext -layout <1260H PDF> 1260h_pdftotext_layout.txt
"""
import json, os, re, sys

EXPECTED = {"parents": 80, "subsidiaries": 108, "delisted": 10}

_HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "1260h_pdftotext_layout.txt")

if not os.path.isfile(SRC):
    sys.exit(f"ERROR: source text not found: {SRC}\n"
             f"Produce it with: pdftotext -layout <1260H PDF> {SRC}")

with open(SRC, encoding="utf-8") as f:
    raw = f.readlines()

# Strip trailing newlines, keep leading whitespace for indent detection
lines = [l.rstrip("\n") for l in raw]

# Identify section boundaries
# Header ends after line 9 ("section 1260H:"). Designated list runs until the footnote
# "* Subsidiaries Listed with Parent Companies" (line 652, index 651).
# Delisted section starts after the "Following Previously Listed Entities Did Not Meet" paragraph.
designated_start = None
delist_marker = None
for i, l in enumerate(lines):
    if l.strip() == "section 1260H:":
        designated_start = i + 1
    if l.strip().startswith("* Subsidiaries Listed with Parent Companies"):
        delist_marker = i
        break

if designated_start is None or delist_marker is None:
    sys.exit("ERROR: expected section markers not found ('section 1260H:' / "
             "'* Subsidiaries Listed with Parent Companies'). Source layout may have "
             "changed; re-verify the parse against the PDF before trusting output.")

# Find the delisted entities: they come after the paragraph that ends with
# "10 U.S.C. § 113 note)." following the footnote marker.
delist_start = None
for i in range(delist_marker, len(lines)):
    if "10 U.S.C. § 113 note)." in lines[i]:
        delist_start = i + 1
        break

designated_block = lines[designated_start:delist_marker]
delisted_block = [l.strip() for l in lines[delist_start:] if l.strip()]

def indent(l):
    return len(l) - len(l.lstrip(" "))

def is_bullet(l):
    return l.lstrip().startswith("•")

entities = []
cur = None
pending_name = None  # for paren-unbalanced continuation

def paren_balanced(s):
    return s.count("(") <= s.count(")")

i = 0
n = len(designated_block)
while i < n:
    l = designated_block[i]
    s = l.strip()
    if not s:
        i += 1
        continue
    if is_bullet(l):
        # rationale line(s) for current entity; collect contiguous bullet+continuation
        if cur is not None:
            cur["rationale_lines"].append(s.lstrip("• ").strip())
        i += 1
        # subsequent indented non-bullet, non-col0 lines that continue the rationale
        while i < n and designated_block[i].strip() and not is_bullet(designated_block[i]) and indent(designated_block[i]) >= 3:
            cur["rationale_lines"][-1] += " " + designated_block[i].strip()
            i += 1
        continue
    if indent(l) == 0:
        # A wrapped rationale line can land at column 0. Org names never start
        # lowercase, so a col-0 line starting lowercase is rationale continuation.
        if s[:1].islower():
            if cur is not None and cur["rationale_lines"]:
                cur["rationale_lines"][-1] += " " + s
            i += 1
            continue
        # Could be a parent name, or a continuation of the previous parent name
        if pending_name is not None:
            # previous name had unbalanced parens -> this is its continuation
            pending_name = pending_name + " " + s
            cur["name"] = pending_name
            if paren_balanced(pending_name):
                pending_name = None
            i += 1
            continue
        # New parent entity
        cur = {"name": s, "subsidiaries": [], "rationale_lines": []}
        entities.append(cur)
        if not paren_balanced(s):
            pending_name = s
        i += 1
        continue
    else:
        # indented, non-bullet. Subsidiaries always precede the affiliation bullet;
        # once a bullet has been seen, an indented line is wrapped rationale.
        if cur is not None:
            if cur["rationale_lines"]:
                cur["rationale_lines"][-1] += " " + s
            else:
                cur["subsidiaries"].append(s)
        i += 1
        continue

# Merge obviously-wrapped subsidiary continuation lines (heuristic: a subsidiary line
# with unbalanced parens merges the next subsidiary line)
for e in entities:
    merged = []
    skip = False
    for j, sub in enumerate(e["subsidiaries"]):
        if skip:
            skip = False
            continue
        if not paren_balanced(sub) and j + 1 < len(e["subsidiaries"]):
            merged.append(sub + " " + e["subsidiaries"][j+1])
            skip = True
        else:
            merged.append(sub)
    e["subsidiaries"] = merged

# Derive short alias ONLY from a parenthetical that TERMINATES the name, e.g.
# "... (Qihoo 360)". A mid-name parenthetical is a qualifier, not an alias:
# "SDIC Intelligence (Xiamen) Information Co., Ltd." has no short alias (it must NOT
# return "Xiamen"). "(formerly ...)"/"(also known ...)" are not aliases either.
def short_alias(name):
    name = name.strip()
    if not name.endswith(")"):
        return None
    m = re.findall(r"\(([^()]*)\)$", name)
    if not m:
        return None
    last = m[-1].strip()
    if last.lower().startswith("formerly") or last.lower().startswith("also known"):
        return None
    return last

out = {
    "designated_parents": [],
    "delisted_entities": delisted_block,
}
for e in entities:
    out["designated_parents"].append({
        "name": e["name"],
        "short_alias": short_alias(e["name"]),
        "subsidiary_count": len(e["subsidiaries"]),
        "subsidiaries": e["subsidiaries"],
        "rationale": " ".join(e["rationale_lines"]).strip(),
    })

print(json.dumps(out, ensure_ascii=False, indent=2))

# Reproducibility gate (backs TSC-01): the parse MUST reproduce the committed counts.
got = {
    "parents": len(out["designated_parents"]),
    "subsidiaries": sum(p["subsidiary_count"] for p in out["designated_parents"]),
    "delisted": len(out["delisted_entities"]),
}
sys.stderr.write(f"COUNTS got={got} expected={EXPECTED}\n")
if got != EXPECTED:
    sys.exit(f"ERROR: count mismatch — got {got}, expected {EXPECTED}. "
             f"The source layout may have changed; re-verify against the PDF.")
sys.stderr.write("OK: counts match committed expectation.\n")
