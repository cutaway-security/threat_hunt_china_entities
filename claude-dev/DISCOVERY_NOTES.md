# DISCOVERY_NOTES — threat_hunt_china_entities

Status: Phase 0b/1 (intake + discovery). Single source of truth for later phases.
Date: 2026-06-30

---

## Intake

**Inputs**
- Authoritative source: DoD **Section 1260H** PDF — "Entities Identified as Chinese Military
  Companies Operating in the United States" (Public Law 116-283 §1260H). 16 pages.
  Public URL: `background/original_report_url.txt` (media.defense.gov, dated 2026-Jun-08).
- A prior enterprise-CoPilot research run intended to parse the PDF, identify vendor software,
  and produce verified Windows detection indicators. **Its output is corrupted (see below).**

**Outputs / deliverables**
- A vetted, consolidated, machine- and human-usable dataset of designated entities → software
  products → verified host-based detection indicators, with confidence and citations.
- A threat-hunt guide + indicator set for the **Energy Threat Analysis Center (ETAC)** contact,
  ideally so ETAC only has to *verify* (not redo) the research before publishing.
- A CutSec blog post (separate effort) documenting the AI-assisted method and giving the
  shareable artifact. Must be tagged **AI-assisted / best-effort**.
- Distribution-format conversions for sharing (STIX/TAXII, YAML, CSV).

**Audience / principals**
- ETAC analyst (primary external consumer; energy-sector threat intel).
- Enterprise + OT/ICS administrators (recognize/triage software on endpoints/servers).
- Threat-hunt / detection-engineering teams (run the indicators).
- CutSec blog readers (industry).

**Environment / constraints**
- Hunt targets: Windows workstations & servers first; Linux/server platforms second;
  OT/ICS environment third (passive/read-only posture — do NOT actively scan OT).
- Research is **notice-only**: no software was installed to enrich indicators. This is a
  starting point, not a finished IOC feed.
- Hard rule: **verified, not derived.** No guessed/invented software names, file names,
  folder names, registry paths/keys, service names, or hashes.

**Definition of done**
- Every shareable indicator carries a real citation and a defined confidence tier.
- Zero placeholder/synthetic/hallucinated content.
- ETAC can validate rather than rebuild.

**Non-goals**
- Hardware/firmware-only detection (device-side); excluded.
- Network IOCs and hashes (version-unstable); excluded from v1 detection set.
- Writing/publishing the blog post itself (separate downstream effort).
- Active OT scanning.

---

## Goal as stated (user, 2026-06-30)

> "We need to run the full analysis again, ourselves. The data contained in the ZIP files
> cannot be trusted, the summary cannot be trusted, and the process can only be trusted in as
> far as the method used to gather and document the information. … pivot to reviewing the data
> from the original ENTITIES list. Correlate the list of companies and subsidiaries. Then …
> generate a list of software products that can be installed on computers. We are not concerned
> about hardware or firmware for devices. Searches will be conducted to identif[y] software that
> is installed, DLLs that might be packaged with other software, SDKs, and other indicators
> (service names, registry keys, filenames, folder names) that have been verified, not derived."

---

## CRITICAL FINDING — prior CoPilot output is corrupted

All prior CoPilot deliverables are **quarantined** under
`background/_quarantine_untrusted_copilot/` and treated as untrusted:

| Artifact | Problem |
| --- | --- |
| `FINAL_FULL_DATASET.zip` | 100% synthetic placeholder scaffold: `Company_1..190`, `Software_1..100`, `proc_1..150`, mechanical `subsidiary_of` (+2 wraparound) links, uniform confidence. No real content. |
| `verified_dataset_bundle.zip` | Only 13 indicators. `source_reference` values are labels ("Hikvision docs") not citations; attribution file maps every row to `software_id=UNKNOWN, company_id=UNKNOWN`. `boe_display.sys` appears fabricated. |
| `china_entities_review_process.md` / `_summary.md` | Real vendor/software names (Hikvision, Dahua, Qihoo, Tencent, Huawei, TP-Link, DJI, NetPosa, Inspur, BGI/MGI, BOE) but **uncited**; usable only as leads to verify, not as data. |

**Lesson for the rebuild:** the failure modes to design against are (1) plausible-but-unsourced
indicators, and (2) structurally orphaned attribution (indicators not linked to software/company).
The new data model must make both structurally impossible.

---

## Verified work completed this session (Step 1 — entity correlation)

Reproducible extraction from the PDF (`data/source_extraction/parse_1260h.py` →
`entities_1260h.json`, parser output hand-verified against `1260h_pdftotext_layout.txt`):

- **80** designated parent entities
- **108** named subsidiaries (correlated under parents) → **188** designated entities total
- **10** delisted entities (previously listed, removed — out of scope, retained for reference)

Each parent record carries: full legal name, short alias, subsidiary list, and the verbatim
§1260H affiliation rationale (MIIT / MSS / SASAC / SASTIND / PLA / PAP, "Little Giant" /
"Single Champion" designations, military-civil-fusion zone, etc.).

This is the **count-verified** foundation (the parser gate asserts 80/108/10). It becomes the
*trusted* foundation once the TSC-01 **full-name-diff** gate against committed expected-name lists is
implemented (a v0.1 slice; AI review 20260630-085540 flagged counts-alone as insufficient). Software
identification and indicator verification are NOT yet done — they are the next work per the
methodology below.

---

## Decisions (confirmed by Don, 2026-06-30)

- **D1 — Storage:** JSON master (`entities.json`), nested entity→software→indicator so indicators
  cannot be orphaned. Confirmed.
- **D2 — Confidence:** evidence-tied tiers (VERIFIED / CORROBORATED / REPORTED / CANDIDATE) +
  mandatory citation; only VERIFIED/CORROBORATED ship. Confirmed.
- **D3 — Project type: generic.** No scanning tool. Deliverable is data + guidance to kickstart
  team searches; teams bring their own tooling.
- **D4 — Distribution (minimized):** standing outputs = **JSON** (master, machines) + **Markdown**
  (human-readable guide + vendor/software tables) + **STIX 2.1** (ETAC ingestion; modeled as
  `software` SCO + `identity`, explicitly NOT malware IOCs, labeled so teams don't auto-block).
  **CSV dropped** as a standing output (redundant with JSON+Markdown; on-demand export only).
  **YAML / Sigma** = on-demand exports only, not maintained files.
- **D5 — Working PowerShell "how to use this information" examples; no full hunt tool.** The guide
  includes a "how to search by indicator type" section with **runnable PowerShell examples** —
  one per indicator type (FILE_NAME, FOLDER_PATH, REGISTRY_KEY/uninstall, SERVICE_NAME, DLL_NAME,
  PROCESS_NAME) — so an analyst can copy-paste and start hunting. Matches ETAC hunt-guide style
  (provide working search examples). **PowerShell only** by deliberate choice: it's the common
  Windows baseline, and non-PowerShell teams can translate the method. These are illustrative
  starting points wired to real indicator values, **not** a packaged scanner/script suite and not
  per-platform query packs (no Splunk/KQL/Sigma/OSQuery generation as standing output).
- **D6 — Init depth: full pipeline WITH multi-AI validation**, scope extended to critique the
  **collected information and assumptions** (indicator sourcing, confidence justification,
  overclaim risk), not just Vision/Requirements/Architecture. "Critique ourselves before ETAC does."
- **D7 — Verification pipeline + tooling (added 2026-06-30, Don approved "Go").** Adopt a tiered,
  source-grounded verification pipeline as a first-class project component (see
  `verification_pipeline_notes.md`). Tools: curl/jq/pdftotext (preinstalled, bash egress works) for
  Tier 1 (winget-pkgs, NVD CPE, vendor PDF extraction); **Playwright+Chromium** installed in
  `.venv/` for Tier 2 (renders JS/WAF-blocked vendor portals — proven against Hikvision); and
  **VirusTotal** (key via the `KEYS_DIR` contract, verified) for Tier 3 (code-signer
  verification). Distinguish factual data validation (source-grounding stack, NOT a second LLM)
  from reasoning/doc validation (multi-AI passes). Pipeline feeds REQUIREMENTS (DR/AR/SR) and is a
  named component in ARCHITECTURE.
  **Status (post AI review 20260630-080409):** tools installed and each tier validated by a manual
  spot-check (winget→WeChat, NVD→CPEs, VT→Tencent signer, Playwright→Hikvision render). The pipeline
  **as code, with shipped/backlog gates, is NOT yet built** — it is the first implementation slice
  (v0.2). "Proven" means method-validated, not implemented. Key resolution uses a keys-dir/env
  contract (SR-01), not a hardcoded personal path.

- **D8 — Altitude / anti-specificity (Don 2026-06-30).** This is higher-level, recognition-grade
  analysis: named, version-independent artifacts only. **No hashes and no version-pinned values** as
  indicators or in exports (REQUIREMENTS DR-09); indicators are normalized to a stable form (DR-10).
  Point-in-time tools (VirusTotal) are bounded to naming confirmation, vendor attribution via
  code-signer, and embedded-library detection — never enumeration, build-pinning, or hashes. Going
  too specific is failure, the same as going unsourced.

## Open questions / forks (carried forward)

1. STIX semantics detail — final SDO/SCO modeling for "designated-vendor-software exposure"
   (not malware). Resolve in Architecture (Phase 7).
2. Whether ETAC/CISA have already published an equivalent — dedup check in Phase 2 research.
3. Software-identification scope: all 80 parents, or prioritize the subset with real
   Windows-installable software first? (Leads from quarantined narratives: Qihoo, Hikvision,
   Dahua, Tencent, Huawei, TP-Link, DJI, NetPosa, Inspur, BGI/MGI — to be re-verified, not trusted.)

---

## References
- `background/ENTITIES-…-SECTION-1260H.PDF` — authoritative entity list (ground truth)
- `background/original_report_url.txt` — public source URL
- `data/source_extraction/` — verified entity correlation + parser + raw text
- `background/_quarantine_untrusted_copilot/` — untrusted prior run (provenance only)
