# RESUME — threat_hunt_china_entities

## Current State
- **Repo:** `cutaway-security/threat_hunt_china_entities` (GitHub, **private**). Default branch **main**.
  - **`main`** = the deliverable: `README.md` (findings-first), `CATALOG.md` (readable list),
    `data/master/entities.master.json` + `companies_software.csv` (tool-feed),
    `Find-DesignatedVendorSoftware.ps1`, `METHODOLOGY.md`, `LICENSE`.
  - **`claude-dev`** = full project: deliverable + research tooling (`pipeline/`, `exporters/`,
    `data/` builders, `packaging/`) + planning set (`claude-dev/`) + multi-AI reviews + quarantine record.
- **Status:** **Deliverable complete, QA'd, and shipped.** Paused here at Don's direction (2026-06-30).
- **Local:** on `claude-dev`, clean, in sync with origin.

## What the deliverable is
A company -> software list for the DoD Section 1260H entities, in a readable form (report) and a
tool-feed (JSON/CSV), plus a validated PowerShell vendor/software sweep. Best-effort, AI-assisted;
designation = corporate affiliation, NOT malware; report-don't-block.

- **Entities:** 80 designated parents (+108 subsidiaries, 10 delisted), reproducibly extracted + name-diff gated.
- **Software catalog (complete coverage):** all 80 assessed -> **20 publish Windows software**,
  3 server/Linux, 19 device/firmware, 26 none, 12 candidates. **59 software products** (post-QA),
  each sourced and trust-tiered (verified / reported / candidate).
- **Detectors (best-effort, PARTIAL):** 2 high-confidence (WeChat `WeChatSetup.exe` VERIFIED;
  QQ uninstall key CORROBORATED). Explicitly not complete; the rest is enrichment.

## Done this engagement (high level)
- cutsec-init: pivot off corrupted CoPilot data; verified entity extraction; Phase 2 research; the
  tiered verification pipeline + schema + gates; two multi-AI validation passes.
- Layer 2 catalog (5 research agents) and Layer 3 best-effort detectors.
- Consolidated scope to the real deliverable (dropped website/STIX/YAML/export-machinery from the
  deliverable; kept tooling for history).
- **PowerShell sweep validated on real Windows 10 Pro** (PS 5.1) via the CHAPS SSH method; caught +
  fixed a UTF-8 BOM parse bug; documented output (stdout objects + status to console + `-OutputCsv`).
- **QA pass:** link-liveness (44 URLs, 41 live, 0 dead) + accuracy re-verification (52 entries, 3
  independent agents; no fabrications, tiers correct); applied 4 corrections. See
  `claude-dev/QA_20260630_link_and_accuracy.md`.

## In Progress
- Nothing. Stopped at a clean point.

## Next Steps (optional / downstream, user-driven)
1. **Humanize** `README.md` + `METHODOLOGY.md` for the CutSec blog (they are AI-written).
2. **ETAC hand-off** (private) and the **CutSec blog post** — separate downstream efforts off `main`.
3. Optional enrichment: resolve the 12 candidate vendors; deepen detectors (Tier-2/VT) — bounded, ETAC may do it.
4. Lab note: refresh the stale Win10 alias IP / QEMU guest agent in `~/.ssh/config` (Don to fix later).

## Open Questions
- STIX `indicator_types` value — only relevant if STIX export is revived (dropped from the deliverable).
- Whether ETAC has internal/unpublished 1260H work — confirm with the contact before/at hand-off.

## Blockers
- None.
