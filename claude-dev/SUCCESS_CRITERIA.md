# SUCCESS CRITERIA — threat_hunt_china_entities

Status: Phase 5 draft (pre multi-AI validation). Business + technical criteria, measurable.
Date: 2026-06-30. Traces to VISION §7 and REQUIREMENTS.

---

## §1 Business success criteria

- **BSC-01 — ETAC can validate, not rebuild.** The ETAC contact can take the dataset + guide and
  confirm the seed indicators against their cited sources to produce their own publication, without
  redoing the research. *Measure:* ETAC review feedback confirms sources resolve and method is
  sound; no "we had to start over." *Origin: VISION §3, §7; BSC-tied to FR-04/TR-01.*
- **BSC-02 — Blog-ready exemplar.** A Markdown package exists that documents the AI-assisted
  method, the verified results, and the corrupted-first-run story, ready to seed the CutSec blog.
  *Measure:* artifact set complete and self-consistent; best-effort labeling present.
- **BSC-03 — Defenders can act immediately.** An admin or hunter can read the guide and run a
  PowerShell example against a host within minutes. *Measure:* examples run as written on a stock
  Windows PowerShell; reviewers confirm usability.
- **BSC-04 — Durability across list updates.** Re-running the method against a future 1260H update
  is a re-run, not a rewrite. *Measure:* the runbook (OPS-01) executes end-to-end on the current
  list with no structural change.

## §2 Technical success criteria

- **TSC-01 — Entity fidelity.** The entity list matches the **June 8 2026 PDF text** (not
  secondary-source totals): 80 parents, 108 subsidiaries, 10 delisted, reproducible from the parser.
  *Threshold:* automated count assertion (parser exits non-zero on mismatch — implemented) AND an
  automated name diff of all 80 parents and **all 108 subsidiaries** (not a sample) against a checked
  list. *<!-- AI review 20260630-080409 (anthropic+openai): threshold "100%" contradicted its
  "manual spot check" method, and sampling subsidiaries is too weak for a fidelity claim. -->*
- **TSC-02 — Zero unsourced shipped indicators.** Every indicator in the shipped/exported set has a
  resolvable `source_url` and a `source_tier`/`confidence_tier`. *Threshold:* 100%; 0 exceptions.
- **TSC-03 — Tier discipline.** No `REPORTED` or `CANDIDATE` indicator appears in any ETAC/exported
  artifact. *Threshold:* 0 leaks (automated check against the master).
- **TSC-04 — Re-verification with freshness.** Every `VERIFIED`/`CORROBORATED` indicator has at least
  one logged, successful fetch against its cited source, and its `date_verified` is within the
  staleness window (default 180 days). *Threshold:* 100% logged AND 0 stale at ship time (TR-01).
  *<!-- AI review 20260630-080409 (anthropic+openai): a 6-month-old fetch is not "current"; tie to a
  freshness threshold. -->*
- **TSC-05 — Schema + export integrity.** The master validates against its JSON schema; every
  export regenerates deterministically; the STIX bundle validates against STIX 2.1 and uses no
  `malware` SDO and no `malicious-activity` indicator type. *Threshold:* all pass.
- **TSC-06 — Method correctness.** PowerShell examples are valid and use Uninstall-key reads
  (never `Win32_Product`); each shipped indicator type has one example. *Threshold:* examples
  **executed against a test fixture** (not merely reviewed) and pass; reviewed against Microsoft docs.
  Generate examples only for indicator types present in the shipped data (no empty-taxonomy padding).
  *<!-- AI review 20260630-080409 (openai): "runnable" must mean executed, not inspected. -->*
- **TSC-09 — Pipeline efficacy gate.** The verification pipeline successfully produces at least one
  `VERIFIED` indicator for each seed vendor (Tencent, Huawei, DJI, 360) before v0.2 ships.
  *Threshold:* ≥1 per seed vendor, each with a verification log, **and** at least one seed record must
  carry a host-presence indicator stronger than vendor-attributed executable naming alone (a
  vendor-official registry/service/install-path claim) — so the gate is not satisfied by easy
  attribution-only wins. *Origin: mistral + openai pass-2 review.*
- **TSC-07 — Honest caveats present.** Designation-≠-malware, report-don't-block, notice-only, and
  AI-assisted/best-effort statements appear on every external artifact. *Threshold:* 100%.
- **TSC-08 — Secret hygiene.** No `*.key.txt` or other secret is tracked. *Threshold:*
  `git status` and `.gitignore` confirm; 0 secrets committed.

## §2a Gate staging by milestone

<!-- AI review 20260630-080409 (all): gates were attached to a single MVP that does not exist; stage
them so v0.1 is not held to gates that need exports. BSC-01/02 are release/non-technical, not MVP. -->

| Gate | Milestone | Criteria that must pass |
|---|---|---|
| **A** — Foundation | v0.1 | TSC-01 (entity fidelity), TSC-08 (secret hygiene) |
| **B** — First verified record | v0.2 | TSC-02, TSC-03, TSC-04, TSC-09 (one end-to-end verified record + logs, no tier leaks) |
| **C** — Exchange artifacts | v0.3 | TSC-05, TSC-06, TSC-07 |
| **D** — ETAC / distribution | v1.0 | BSC-01, BSC-04; STIX validates and consumer (ETAC) ingestion semantics confirmed |

BSC-02 (blog-ready exemplar) is a publication milestone and MUST NOT gate any technical/dataset
release. v0.1 is NOT held to gates that require exports or a verification pipeline.

**Internal readiness vs external acceptance (AI review 20260630-085540, openai).** Gate D's
*internal* readiness (STIX validates, all artifacts caveated, gates A–C green) is an engineering
completion criterion the team controls. BSC-01 (ETAC validates) is *external acceptance* and depends
on ETAC's review timeline — it is a release objective, NOT an internal ship gate. Do not block an
internal release on a review the team does not schedule.

## §3 Test plan (criterion → test → source → threshold → cadence)

| Criterion | Test | Data source | Threshold | Cadence |
|---|---|---|---|---|
| TSC-01 | Automated count gate + **full name diff** of all parents/subs/delisted vs committed lists | `data/source_extraction/` + committed name lists | 100% (counts AND names) | each list update |
| TSC-02 | Script: assert every shipped indicator has source_url+tiers | master JSON | 0 missing | pre-ship + CI |
| TSC-03 | Script: assert exported set excludes REPORTED/CANDIDATE | master + exports | 0 leaks | pre-ship + CI |
| TSC-04 | Re-fetch each cited source, log result | live winget/NVD/VT/portal/PDF | 100% success | pre-ship; quarterly recheck |
| TSC-05 | JSON-schema validate; STIX 2.1 validate; export round-trip | master + exports | all pass | each build |
| TSC-06 | **Execute** PowerShell examples against a test fixture; lint; review vs MS docs | hunt guide + fixture | execute-pass, all shipped types, no Win32_Product | on guide change |
| TSC-07 | Checklist presence scan | all external artifacts | 100% | pre-ship |
| TSC-08 | `git status --porcelain` + `.gitignore` review | repo | 0 secrets | every commit |

## §4 What does NOT count as success

- A large indicator count achieved by including unverified or guessed values. Coverage without
  provenance is failure, not progress.
- Indicators "verified" by asking another LLM. Model agreement is not source verification; factual
  correctness comes only from a fetched authoritative source.
- An export that looks complete but contains `CANDIDATE`/`REPORTED` values, or a STIX bundle that
  labels lawful commercial software as malware.
- Shipping the quarantined CoPilot artifacts, in whole or in part, without independent re-sourcing.
- "Done" declared while the designation-≠-malware / report-don't-block / best-effort caveats are
  missing from any external artifact.
- A file hash or a version-pinned value shipped as an indicator or present in any export — going
  below the project's recognition-grade altitude (DR-09/DR-10). Going too specific is failure, the
  same as going unsourced.

### The load-bearing clause (acceptance gate)

> No indicator, dataset version, or export is "shipped," "verified," or "ETAC-ready" until at least
> one **real fetch against the real authoritative source** has confirmed the artifact value.
> Asserted-but-unfetched values are CANDIDATEs, not indicators. Stub data, second-LLM agreement,
> and "it looks right" are not validation.
