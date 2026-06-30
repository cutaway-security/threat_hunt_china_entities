# PLAN — threat_hunt_china_entities

## Project Goal

Produce a provenance-first, ETAC-shareable dataset + threat-hunt guide identifying
computer-installable software from DoD Section 1260H entities and the verified Windows host artifacts
that prove its presence — verified-not-derived, recognition-grade, exposure-not-malware. Each phase
ships real, tested work behind an objective acceptance gate.

## Current Phase

**COMPLETE — deliverable built, validated, QA'd, and shipped; paused at Don's direction (2026-06-30).**
The project ran all the way through: v0.1 (entity foundation + schema + gates), Layer 2 (full software
catalog, all 80 assessed), Layer 3 (best-effort detectors), consolidation to the real deliverable,
real-Windows-10 validation of the PowerShell sweep, and a link-liveness + accuracy QA pass. Shipped to
the private repo `cutaway-security/threat_hunt_china_entities`: `main` = deliverable (default),
`claude-dev` = full project. See RESUME.md for the current snapshot.

**Scope (final, Don):** the deliverable is the **company -> software list** (readable report +
JSON/CSV tool-feed) plus the validated PowerShell vendor/software sweep. The website / STIX / YAML /
export-machinery were dropped from the deliverable (tooling kept in `claude-dev` for history). **ETAC
gets the same content as the public release** (consolidated — no separate ETAC package); ETAC sharing
is private and not referenced in any public-facing doc. Bounded client deliverable; ETAC may enrich.

**Remaining (optional, downstream, user-driven):** humanize README/METHODOLOGY for the blog;
the ETAC hand-off and CutSec blog post (separate efforts off `main`); optional candidate/detector
enrichment.

## Phases

### v0.1 — Trusted entity foundation
Deliverables:
- [done] `parse_1260h.py` reads repo-local input, count gate (80/108/10), trailing-paren alias fix, UTF-8.
- [done] committed `entities_1260h.json`.
- [done] committed auditable name manifest (`entities_manifest.txt`: 80 parents + 108 subs + 10 delisted).
- [done] **`test_parser.py`** — golden-output regression + name-diff gate (TSC-01); validated to catch
  mis-attribution that preserves totals.
- [done] parser hardening: `encoding="utf-8"`; hard-stop on missing markers; subsidiary-merge fragility
  for FUTURE PDFs now caught (not silent) by the golden/name-diff/count gates.
- [done] committed **JSON schema** `data/schema/master.schema.json` — nested entity→software→indicator,
  atomic **claim-typed evidence model**, `presence_class`/`disposition` enums; structurally rejects
  hashes, version-pinned CPEs, and claim-less/orphan indicators (validated, positive + 3 negatives).
- [done] entities-only **master stub** `data/master/entities.master.json` (80 + 10), honest
  `candidate_pending_verification` dispositions, validates against schema.
- [todo] `AUTHORITY_MAP.md` (done) and `ADRS.md` (done) committed; consistency matrix started.

**Acceptance gate (Gate A):** TSC-01 passes (counts AND full name diff), TSC-08 (secret hygiene). Ship
nothing external. *Provisions the test environment (see TEST_ENVIRONMENT.md) as part of this phase.*

### v0.2 — Verified seed + enforcement
Deliverables:
- Verification pipeline as code (Tier-1: winget/NVD/VT) producing **typed claims**, assembled into
  indicators by rules that forbid unsupported promotions.
- Immutable verification log (JSONL); sandboxed Playwright as fallback only.
- 3–5 product VERIFIED seed from easy vendors (Tencent, Huawei, DJI, 360).
- Structural shipped/backlog separation; **tier-leak gate** (TSC-03), **re-fetch + staleness gate**
  (TSC-04); Markdown summary generated from master.

**Acceptance gate (Gate B):** TSC-02, TSC-03, TSC-04, TSC-09 (incl. ≥1 host-presence indicator
stronger than executable-name attribution). First ETAC-capable artifact.

### v0.3 — Exchange artifacts
Deliverables: STIX 2.1 exporter (non-malware, wildcarded CPE, no SCO version); hunt guide with
PowerShell examples generated from shipped indicators; CSV/YAML on demand.

**Acceptance gate (Gate C):** TSC-05 (schema + STIX 2.1 validate + round-trip), TSC-06 (examples
executed against a fixture), TSC-07 (caveats on every artifact).

### v1.0 — Hard vendors (well-developed, not a blocker)
Tier-2/3 for WAF-blocked portals + SDK DLLs (Hikvision/Dahua) and broader coverage, pursued with the
built tooling (Playwright/VT/SDK PDFs) as far as the verified-not-derived bar allows. Where public
sources cannot verify an artifact, it stays CANDIDATE / honest disposition — never fabricated. ETAC may
enrich these gaps themselves, so they do not block distribution. Annual-rerun runbook (OPS-01) here.

### Distribution (at the end, after the deliverable is complete)
Two separate channels, neither shared early:

**A. Private ETAC package** — a separate, well-developed "aside" (its own document/package) ETAC can
use as-is or start from and enrich: the dataset, the Markdown guide, and a method writeup, with full
provenance. **Private; not in the public repo; not referenced in any public-facing doc.** This is a
bounded client deliverable — no ongoing enrichment unless ETAC requests collaboration later.

**B. Public release (stripped repo + CutSec blog)** — a clean, usable public artifact distinct from the
dev repo, **with no mention of ETAC**. **Strips dev/history/old data**: removes `claude-dev/`,
`background/_quarantine_untrusted_copilot/`, `.ai-reviews/`, raw extraction intermediates, `.venv/`
(per Cutaway `GIT_RELEASE_STEPS.md`, claude-dev → main strip). Proposed public structure:
```
README.md            public-facing (defender/analyst oriented): what it is, how to use, caveats, license
LICENSE              MIT
METHODOLOGY.md       how built; AI-assisted/best-effort; notice-only limitations
dataset/             entities.json (public projection) + stix/bundle.json (+ csv/yaml on request)
guide/               THREAT_HUNT_GUIDE.md + powershell/ examples
CHANGELOG.md
```
**Gate:** public README usable by a defender with no project context; no dev/quarantine/history
artifacts present; all caveats + AI-assisted label intact; LICENSE present. Feeds the CutSec blog post
(separate downstream effort).

## Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-06-30 | Discard all prior CoPilot output as corrupted | synthetic placeholder + orphaned attribution; rebuild from 1260H PDF |
| 2026-06-30 | Nested JSON master + generated exports | structurally prevents orphaned attribution and file-sprawl drift |
| 2026-06-30 | Tiered verification pipeline + claim-typed evidence | enforces "verified, not derived" and DR-02a in schema |
| 2026-06-30 | Recognition-grade altitude (no hashes/version pins) | durable, higher-level analysis; avoids point-in-time IOC creep |
| 2026-06-30 | Non-malware STIX; designation ≠ malware | a 1260H listing is affiliation, not a malware finding |
| 2026-06-30 | Narrow-and-deep phasing v0.1→v1.0 | first multi-AI pass: original MVP over-scoped |
| 2026-06-30 | Name-diff gate required before "trusted foundation" | second multi-AI pass: counts alone insufficient |
| 2026-06-30 | License: MIT (permissive, attribution via retained notice) | Don: "normal license, people can use it but attribution is nice" |
| 2026-06-30 | ETAC private hand-off FIRST; ETAC enriches; hard vendors NOT a blocker | Don: share with ETAC first; they enrich themselves |
| 2026-06-30 | Two-tier packaging: dev repo vs stripped public release | Don: public needs usable README + structure; old/dev data excluded |

## Out of Scope (phase-level deferrals)
- Tier-2/3 hard vendors before v1.0 (do not let "high-signal" pull Hikvision/Dahua into the seed).
- STIX/exporters before the master + gates are real (v0.3).
- Project-level scope lives in REQUIREMENTS §11 and VISION §6.
