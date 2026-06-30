# Consolidated Architecture Review — threat_hunt_china_entities

- Synthesizer: Claude (orchestrator)
- Date: 2026-06-30
- Panel: anthropic (claude-opus-4-8), mistral (mistral-medium-latest), openai (gpt-5.4) — all `ok`
- Bundle: VISION, REQUIREMENTS, SUCCESS_CRITERIA (reviewed); research survey, DISCOVERY_NOTES,
  verification + STIX notes, parser + entity JSON, quarantined narratives (grounding)

## Verdict

Unanimous: **the concept is sound and worth building** — a provenance-first map of 1260H entities
to verifiable Windows software-presence indicators, correctly framed as exposure (not malware).
Equally unanimous: **the first milestone is mislabeled and over-scoped.** The docs imply an
ETAC-ready deliverable, but the only built thing is the entity parser; the data model, schema,
verification tooling, gates, exporters, and hunt guide are design, not code. All three independently
warn: optimize for coverage before the enforcing machinery exists and you recreate the exact
CoPilot failure "with better prose."

This is a fair hit. Note one framing adjustment: this is a cutsec-init **pre-implementation gate**,
so "not implemented yet" is expected — the valid, actionable defects are (a) the docs **overclaim
done-ness**, (b) the **parser is genuinely broken**, (c) **TSC-01 contradicts itself**, and (d) the
**scope/sequencing must be restated**. Those I fix now. The pipeline *code* remains the first
implementation slice (PLAN.md), now correctly sequenced schema-and-gates-first.

## Consensus findings (2+ reviewers, high confidence)

1. **[ALL] "Done, proven" overclaim.** VISION §5 / D7 call the verification pipeline done/proven;
   it is method + manual spot-checks, no tooling. → Restate honestly. *Single most consequential fix.*
2. **[ALL] MVP over-scoped; re-phase narrow-and-deep (Fork B).** Cut STIX, all-types PowerShell,
   exports, full coverage, ETAC packaging from the first cut. Converged tiers:
   - **v0.1** entity foundation + committed JSON schema + reproducible parser + automated count check.
   - **v0.2** Tier-1 pipeline (winget/NVD/VT) + 3–5 easy-vendor VERIFIED seed (Tencent, Huawei, DJI,
     360) + machine-enforced shipped/backlog separation + tier-leak & re-fetch gates + Markdown
     generated from master.
   - **v0.3** STIX exporter + hunt guide w/ PowerShell + STIX/round-trip validation.
   - **v1.0** hard vendors (Hikvision/Dahua SDK DLLs via Tier-2/VT) + annual-rerun runbook + ETAC handoff.
3. **[ALL] `parse_1260h.py` hardcodes a `/tmp` scratch path** → breaks MR-01/TSC-01 reproducibility.
   Fix to read the committed `1260h_pdftotext_layout.txt` (CLI arg / default); add count/golden test
   and error handling. *Fixing now.*
4. **[anthropic+openai] TSC-01 self-contradicts** ("100% match" via "manual spot check") → automated
   count+diff (parent=80/sub=108/delisted=10) + full (not sampled) subsidiary check; define "match"
   = matches the June 8 2026 PDF text, not secondary-source totals.
5. **[ALL] SDK-DLL / embedded-SDK overclaim.** "Vendor product installed" ≠ "vendor SDK embedded in
   third-party product." Distinguish in data model + STIX; DLL indicators are higher-FP, CORROBORATED
   at best. Don't oversell.
6. **[anthropic+openai] short_alias bug** — "SDIC Intelligence (Xiamen) Information Co., Ltd." →
   alias "Xiamen" (a mid-name location). Data-quality defect (aliases drive matching). *Fixing now.*
7. **[ALL] Schema is the load-bearing artifact** — commit it now; gate scripts (tier-leak, re-fetch)
   are cheap and protect the whole value prop; build them before coverage.
8. **[anthropic+openai] Quarantine separation is path-name-only** — add machine-readable `UNTRUSTED —
   DO NOT USE AS DATA SOURCE` banners; keep backlog a separate namespace (defense in depth). *Fixing now.*
9. **[mistral+openai] Add an authority map + consistency matrix + ADRs** (canonical vs historical vs
   quarantined vs generated; requirement→schema→generator→test→artifact traceability).

## High-merit singletons

- **[openai] "Full coverage" = full *triage/disposition*, not artifact harvest.** Most of the 80
  parents yield no Windows indicators; per-entity outcome should be a justified disposition
  (no-windows-software / server-or-linux-only / hardware-only / candidate-pending). More honest and
  useful. → Sharpen FR-05.
- **[openai] Don't oversell each source.** VT signer proves *publisher linkage of a binary*, not
  uninstall keys/services/paths; NVD CPE is *naming*, not Windows-installability or host-artifact
  proof. Each source verifies a specific claim type → encode a source→claim-type mapping in the rubric.
- **[anthropic+openai] TSC-04 needs a staleness window** — a 6-month-old fetch ≠ current; tie to a
  `date_verified` freshness threshold.
- **[mistral] Add TSC-09** — pipeline must verify ≥1 indicator per seed vendor (v0.2 gate).
- **[openai] TSC-06: examples executed against fixtures, not merely reviewed.**
- **[openai] Move the personal secret path out of docs** — use an env-var/keys-dir contract, not
  `~/.claude/keys/virustotal.key.txt` verbatim.
- **[openai/mistral] Don't freeze STIX `anomalous-activity`** until ETAC ingestion preference is
  confirmed (already open question §8.4 — keep open).

## Referee notes (where the panel is wrong/imprecise)

- **mistral** suggested the parser read `background/original_report_url.txt` — that is the URL file,
  not the PDF text. Correct default is `data/source_extraction/1260h_pdftotext_layout.txt`
  (anthropic/openai got this right). Disregard mistral's target.
- **mistral** listed "reads from a fixed source file" as both a strength and a defect — the defect
  framing is the correct one.
- **mistral** suggested PyPDF2 for "structural metadata" — `pdftotext -layout` already provides the
  layout we use; no benefit. Disregard.
- **All three** treat "pipeline not implemented" as a defect; for a pre-implementation init gate it
  is expected. Valid core = the overclaim + parser + gates-sequencing, which is adopted.

## No missing research vector

The panel surfaced scope/honesty/sequencing issues, not a research gap. Phase 2 does not reopen.

## Unified remediation plan

**P0 — applied this pass (docs + the one existing script):**
- Restate VISION §5 / D7: pipeline = method validated by spot-checks, tooling not yet built.
- Restate REQUIREMENTS §0 as phased v0.1–v1.0; move STIX/PowerShell/exports/ETAC out of v0.1.
- TSC-01 → automated count+diff, full subsidiary check, "matches PDF" defined.
- Fix `parse_1260h.py` (repo-local input via argv/default; trailing-paren alias rule; count assert);
  re-verify 80/108/10 unchanged.
- Add `UNTRUSTED` banners to quarantined files.
- Distinguish product-installed vs SDK-embedded (FR-02/FR-03); FR-05 → disposition coverage.
- Sharpen DR-02 with the source→claim-type mapping; add staleness window; add TSC-09; TSC-06 execute.
- Env-var/keys-dir contract instead of personal path.

**P1 — for ARCHITECTURE (Phase 7) and PLAN (Phase 10):**
- Commit the master JSON schema as the v0.1 load-bearing artifact.
- Machine-enforced shipped/backlog separation + tier-leak/re-fetch gate scripts before coverage.
- One end-to-end verified seed record with a verification log (Tencent WeChat / Huawei HiSuite).
- Generate Markdown from master (never hand-authored).
- Authority map, consistency matrix, ADRs.

**P2 — deferred (correctly):** STIX export, hunt-guide example completeness, hard vendors.

## Bottom line

Keep the thesis; cut the first milestone to narrow-and-deep; stop calling the pipeline done; make
the parser reproducible; commit the schema and gates before chasing coverage. The panel's strongest
contribution is the disposition-not-harvest reframe and the source→claim-type precision — both
adopted.
