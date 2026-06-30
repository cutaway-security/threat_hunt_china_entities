# RESUME — threat_hunt_china_entities

## Current State
- **Branch:** claude-dev
- **Phase:** v0.1 complete (Gate A). Detector pipeline built + gates pass (`pipeline/`). **Layer 2
  software catalog COMPLETE** — all 80 entities assessed; 20 software-producing vendors, 60 products
  (41 verified / 11 reported / 8 candidate); `CATALOG.md` generated. Layer-2 software carries empty
  indicators. **Layer 3 (detectors): best-effort #3 run done** — focused on priority vendors;
  2 high-confidence detectors attached (WeChat VERIFIED FILE_NAME, QQ CORROBORATED REGISTRY_KEY),
  all gates pass. Rest yield no clean public-source artifact (VT quota exhausted this session;
  version-stamped/servlet installer URLs) and are honestly left for enrichment. CATALOG.md labels
  the detector layer best-effort/partial. NOT represented as complete.
- **Date:** 2026-06-30

## What Was Accomplished (init)
- Pivot: prior CoPilot output found corrupted, quarantined with UNTRUSTED banners; rebuild from the
  1260H PDF.
- Verified entity correlation: 80 parents / 108 subsidiaries / 10 delisted, reproducible + count-gated
  (`data/source_extraction/`).
- Phase 2 research survey (citation-audited): §1260H framing, Windows hunting methods, STIX
  non-malware modeling, vendor source feasibility. Dedup gate passed (no existing equivalent).
- Tiered verification pipeline established and proven by spot-check (winget → WeChat; NVD → CPEs;
  VirusTotal → Tencent code-signer; Playwright → rendered the WAF-blocked Hikvision portal). Tools
  installed (curl/jq/pdftotext; Playwright+Chromium in `.venv/`; VT key via KEYS_DIR).
- Full planning + architecture set written: VISION, REQUIREMENTS, SUCCESS_CRITERIA, ARCHITECTURE,
  plus DISCOVERY_NOTES, verification/STIX notes, AUTHORITY_MAP, ADRS, VIBE_HISTORY.
- Two multi-AI validation passes (3/3 reviewers each), findings synthesized and applied
  (`.ai-reviews/20260630-080409/`, `.ai-reviews/20260630-085540/`).

## v0.1 — DONE (Gate A passed)
- `data/source_extraction/`: parser hardened (UTF-8), `entities_manifest.txt`, `test_parser.py`
  (golden + name-diff, validated to catch corruption). TSC-01 passes.
- `data/schema/master.schema.json`: claim-typed model; rejects hashes/version pins/orphans (validated).
- `data/master/entities.master.json`: 80 entities + 10 delisted, candidate_pending_verification.
- `data/build_master_stub.py`: regenerates the stub from the verified extraction.

## Packaging — DONE (v0.3 distribution)
- Exports generated from the master: `dist/csv/{entities,software,detectors}.csv`,
  `dist/yaml/catalog.yaml`, `dist/stix/1260h_software_bundle.json` (STIX 2.1, validated via stix2 lib;
  149 objects, non-malware semantics confirmed).
- `guide/THREAT_HUNT_GUIDE.md` (PowerShell hunt examples incl. Publisher sweep), `METHODOLOGY.md`,
  public `README.md`.
- `packaging/package.py` assembles `release/public/` (stripped: no claude-dev/quarantine/.ai-reviews/
  .venv/log, no ETAC mention) and `release/etac/` (private: + verification log + ETAC_COVER.md).
- All ship gates pass; everything regenerates from the master.

## In Progress
- Nothing mid-edit. The client deliverable is assembled. The CutSec blog post is a separate downstream effort.

## Blockers
- None.

## Next Steps (v0.2 — verification pipeline + seed)
1. Build the Tier-1 pipeline as code (`pipeline/sources/` adapters: winget, NVD CPE, VT) emitting
   **typed claims**, assembled into indicators by rules that forbid unsupported promotions.
2. Immutable verification log (JSONL); sandboxed Playwright as fallback only.
3. Produce the 3–5 vendor VERIFIED seed (Tencent, Huawei, DJI, 360) into the master; structural
   shipped/backlog split; tier-leak + re-fetch/staleness gates (`pipeline/gates.py`).
4. Markdown summary generated from master. Pass Gate B (TSC-02/03/04/09).

## Open Questions
- STIX `indicator_types` (`anomalous-activity` vs `benign`) — confirm with ETAC before v0.3.
- Whether ETAC has internal/unpublished 1260H work — confirm with the contact.

## Files Modified (this session)
Entire `claude-dev/` set; `CLAUDE.md`, `README.md`, `.gitignore`; `data/source_extraction/*`;
`background/_quarantine_untrusted_copilot/*` (banners); `.ai-reviews/*`.
