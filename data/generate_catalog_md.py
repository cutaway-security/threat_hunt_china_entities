#!/usr/bin/env python3
"""Generate the human-readable Layer-2 software catalog (Markdown) from the master.
Admin/analyst-facing recognition list (REQUIREMENTS FR-06). Generated, never hand-edited."""
import json, os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, "master", "entities.master.json")
OUT = os.path.join(HERE, os.pardir, "CATALOG.md")

m = json.load(open(MASTER, encoding="utf-8"))
ents = m["entities"]
disp = Counter(e["disposition"] for e in ents)
n_sw = sum(len(e["software"]) for e in ents)
sw_status = Counter(s["catalog_status"] for e in ents for s in e["software"])

L = []
L.append("# Section 1260H Software Catalog (Layer 2)")
L.append("")
L.append(f"AI-assisted, best-effort. Source: DoD Section 1260H list dated {m['meta']['source_date']}. "
         "This is **exposure/inventory** analysis, not malware detection — a 1260H designation is a "
         "corporate-affiliation flag, not a finding that the software is malicious. **Report, do not "
         "auto-block.** Generated from the dataset; do not hand-edit.")
L.append("")
L.append("## Coverage (all 80 designated parent entities assessed)")
L.append("")
L.append("| Disposition | Count |")
L.append("|---|---|")
labels = {"software_no_verified_indicators": "Publishes installable Windows software",
          "candidate_pending_verification": "Candidate — software likely, not yet confirmed",
          "no_windows_software_found": "No installable Windows software found",
          "hardware_or_firmware_only": "Hardware / firmware only",
          "server_or_linux_only": "Server / Linux platforms only"}
for k, v in sorted(disp.items(), key=lambda x: -x[1]):
    L.append(f"| {labels.get(k, k)} | {v} |")
L.append(f"| **Total** | **{len(ents)}** |")
L.append("")
L.append(f"**Software products catalogued:** {n_sw} "
         f"({sw_status.get('verified',0)} verified vendor-official, {sw_status.get('reported',0)} reported third-party, "
         f"{sw_status.get('candidate',0)} candidate). Verified/reported are usable now; candidates need confirmation.")
L.append("")


def sw_table(entities, title, note=""):
    rows = [e for e in entities if e["software"]]
    if not rows:
        return
    L.append(f"## {title}")
    if note:
        L.append("")
        L.append(note)
    L.append("")
    L.append("| Vendor (1260H entity) | Software product | Type | Status | Source |")
    L.append("|---|---|---|---|---|")
    for e in rows:
        for s in e["software"]:
            vendor = e["short_alias"] or e["name"]
            L.append(f"| {vendor} | {s['name']} | {s.get('category','')} | {s['catalog_status']} | <{s['source_url']}> |")
    L.append("")


sw_table([e for e in ents if e["disposition"] == "software_no_verified_indicators"],
         "Vendors with confirmed installable Windows software",
         "These vendors publish Windows software (vendor-official = verified; third-party = reported). "
         "Host-artifact detectors (exact installed file/registry/service names) are Layer 3 and are "
         "not yet attached.")
sw_table([e for e in ents if e["disposition"] == "candidate_pending_verification"],
         "Candidate vendors (software named but not yet confirmed Windows)",
         "Leads only — product names appear on vendor or third-party pages but a Windows build/"
         "distribution was not confirmed. Do not treat as confirmed until verified.")

# Candidate vendors without any named product
cand_empty = [e for e in ents if e["disposition"] == "candidate_pending_verification" and not e["software"]]
if cand_empty:
    L.append("### Candidate vendors with no named product yet")
    L.append("")
    for e in cand_empty:
        L.append(f"- **{e['short_alias'] or e['name']}** — {e['disposition_justification']}")
    L.append("")

# Host-artifact detectors (Layer 3) — best-effort, partial
dets = [(e, s, i) for e in ents for s in e["software"] for i in s["indicators"]]
L.append("## Host-artifact detectors (best-effort — PARTIAL, requires verification)")
L.append("")
L.append("> **Read this before using the detectors.** This section is a *best-effort starting point*, "
         "**not a complete or authoritative detection set.** Only host artifacts we could verify from "
         "public sources (without installing the software) are listed, each with a confidence tier. "
         "**The absence of a detector does NOT mean the software is absent** — it means we have not yet "
         "verified a stable host artifact for it. Most install-time artifacts (installed exe names, "
         "install paths, service names, SDK DLLs) require enrichment — vendor SDK manuals, VirusTotal "
         "code-signer lookups, or controlled lab observation — and MUST be confirmed before operational "
         "use. The **software catalog above is the high-confidence deliverable**; these detectors are "
         "supplementary.")
L.append("")
L.append("Confidence tiers: **VERIFIED** = vendor-official + a second independent source for this exact "
         "artifact; **CORROBORATED** = multiple reputable sources, none vendor-official. Lower tiers are "
         "not shown here (they stay in the backlog).")
L.append("")
if dets:
    L.append("| Vendor | Software | Detector type | Value | Confidence |")
    L.append("|---|---|---|---|---|")
    for e, s, i in dets:
        L.append(f"| {e['short_alias'] or e['name']} | {s['name']} | {i['indicator_type']} | `{i['value']}` | {i['confidence_tier']} |")
    L.append("")
L.append(f"**{len(dets)} verified/corroborated detector(s)** attached so far, across "
         f"{sum(len(e['software']) for e in ents)} catalogued products. Coverage is deliberately not claimed.")
L.append("")

# No-software vendors (summary list)
L.append("## Vendors assessed as producing no installable Windows software")
L.append("")
by_disp = defaultdict(list)
for e in ents:
    if e["disposition"] in ("no_windows_software_found", "hardware_or_firmware_only", "server_or_linux_only"):
        by_disp[e["disposition"]].append(e["short_alias"] or e["name"])
for k in ("no_windows_software_found", "hardware_or_firmware_only", "server_or_linux_only"):
    if by_disp[k]:
        L.append(f"**{labels[k]} ({len(by_disp[k])}):** " + "; ".join(sorted(by_disp[k])))
        L.append("")

open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print(f"wrote {OUT} ({len(ents)} entities, {n_sw} products)")
