# REQUIREMENTS — threat_hunt_china_entities

Status: Phase 4 draft (pre multi-AI validation). RFC 2119 keywords (MUST/SHOULD/MAY).
Scope tags: [MVP] / [Scale] / [vNext]. Origins point to DISCOVERY_NOTES decisions (D1–D7) and the
research survey (`20260630_..._RESEARCH.md`). Date: 2026-06-30.

## §0 Context & scope

This product is a **verified dataset + threat-hunt guide + shareable exports** identifying
commercial, computer-installable software produced by DoD Section 1260H-designated entities, and
the host-based artifacts that prove its presence on Windows.

<!-- AI review 20260630-080409 (anthropic+mistral+openai): the original single MVP bundled an entire
release ("JSON master + pipeline + seed + Markdown + PowerShell + STIX + ETAC-ready") with nothing
built. Re-phased narrow-and-deep (Fork B). See consolidated_review.md finding #2,#7. -->
**Phased scope — narrow-and-deep, schema-and-gates before coverage:**

- **v0.1 — Trusted entity foundation.** The reproducible entity parser (repo-local input + count
  gate), the committed entity JSON, and the **committed master JSON schema**. Ship nothing external.
  Gates: TSC-01, TSC-08. *Substantially achievable now.*
- **v0.2 — Verified seed + enforcement.** The verification pipeline as actual Tier-1 tooling
  (winget/NVD/VT), a 3–5 product VERIFIED seed from the easy consumer-app vendors (Tencent, Huawei,
  DJI, 360), the nested entity→software→indicator master, a machine-enforced shipped/backlog
  separation, and the tier-leak + re-fetch gate scripts. First artifact that could reach ETAC.
  Gates: TSC-02, TSC-03, TSC-04, TSC-09.
- **v0.3 — Exchange artifacts.** Markdown hunt guide with the PowerShell examples generated from real
  shipped indicators; STIX 2.1 exporter; CSV/YAML on demand. Gates: TSC-05, TSC-06, TSC-07.
- **v1.0 — Hard vendors + handoff.** Tier-2/3 for WAF-blocked portals and SDK DLLs
  (Hikvision/Dahua), the annual-rerun runbook, and the ETAC handoff package. Gates: BSC-01, BSC-04.

All external artifacts are labeled best-effort/AI-assisted regardless of tier. "Full coverage" means
**a justified disposition assigned to every entity** (FR-05), not a host-artifact harvested for each.

**Altitude principle (anti-creep).** This is **higher-level, recognition-grade** analysis: named,
**version-independent** artifacts an administrator or software inventory can recognize and match
(executable/DLL/folder/service/registry-key names) — deliberately **not** a forensic IOC feed. Hashes
and version-pinned values are out of bounds as indicators by design (DR-09). Point-in-time tools
(VirusTotal) are used to *confirm* naming/attribution and to *detect embedded libraries*, never to
enumerate coverage or to pin a specific build. *Origin: Don, 2026-06-30 (scope-balance check).*

## §1 Functional requirements (FR)

- **FR-01 [MVP]** The system MUST maintain the authoritative entity list parsed reproducibly from
  the 1260H PDF — parents, subsidiaries, and delisted entities — date-stamped to the source version
  (June 8 2026). *Origin: D-pivot; `data/source_extraction/`.*
- **FR-02 [MVP]** The system MUST map each in-scope entity to its software products, including only
  software installable on computers (desktop apps, management tools, SDKs); hardware/firmware-only
  products MUST be excluded and marked as such. *Origin: user mandate; D3.*
- **FR-03 [MVP]** Each software product MUST support host-based indicators of these types:
  `FILE_NAME`, `FILE_PATH`, `FOLDER_PATH`, `REGISTRY_KEY`, `SERVICE_NAME`, `DLL_NAME`,
  `PROCESS_NAME`. *Origin: research §4.1.*
- **FR-03a [MVP]** Each indicator MUST record a `presence_class` distinguishing **`product_installed`**
  (the vendor's own product is installed on the host) from **`sdk_embedded`** (the vendor's SDK/DLL is
  shipped inside an unrelated third-party product). `sdk_embedded` indicators MUST NOT claim the
  vendor's *product* is present and are inherently higher-false-positive (cap at CORROBORATED unless a
  second class corroborates). *Origin: anthropic+openai review. <!-- AI review 20260630-080409: an
  embedded SDK DLL means vendor CODE is present, not the vendor PRODUCT; do not overclaim. -->*
- **FR-04 [MVP]** Every indicator MUST carry: `indicator_type`, `value`, `source_url`,
  `source_tier`, `confidence_tier`, `date_verified`. An indicator without a resolvable citation
  MUST NOT exist in the shipped set. *Origin: D2, D7; verified-not-derived.*
- **FR-05 [MVP]** The system MUST assign every in-scope entity a justified **disposition** — coverage
  means disposition-assigned, not artifact-harvested. Values: `indicators_identified` /
  `software_no_verified_indicators` / `server_or_linux_only` / `hardware_or_firmware_only` /
  `no_windows_software_found` / `candidate_pending_verification`. Each MUST carry a one-line
  justification. *Origin: research §6; openai review (disposition-not-harvest). <!-- AI review
  20260630-080409 (openai): most of the 80 parents yield no Windows indicators; "full coverage" =
  full triage. -->*
- **FR-06 [MVP]** The system MUST produce a human-readable, admin-facing summary (vendor → product
  → what it is → where it shows up) for recognition and conversations. *Origin: user; D4.*
- **FR-07 [MVP]** The hunt guide MUST include runnable PowerShell "how to search" examples, one per
  indicator type, wired to real indicator values. *Origin: D5.*
- **FR-08 [Scale, v0.3]** The system MUST generate a STIX 2.1 bundle export modeling software presence
  as `software`+`identity`+`indicator`+`relationship` with **non-malware semantics** — never the
  `malware` SDO and never `malicious-activity`. The exact `indicator_types` value (`anomalous-activity`
  vs `benign`) is confirmed with ETAC before the v0.3 freeze, not fixed today. CPE version fields MUST
  be wildcarded and the SCO `version` property omitted (DR-09/DR-10). *Origin: D4; research §5;
  `stix_modeling_notes.md`. <!-- AI review 20260630-085540 (openai+anthropic): un-fixed the STIX type
  pending ETAC; enforced no version-pin in the export. -->*
- **FR-09 [Scale]** The system SHOULD generate CSV and YAML exports on demand from the master; it
  MUST NOT maintain them as standing hand-edited files. *Origin: D4.*
- **FR-10 [MVP]** The system MUST keep a CANDIDATE backlog (plausible-but-unverified artifacts,
  incl. the quarantined CoPilot values) separate from and excluded from the shipped/exported set.
  *Origin: D2; corrupted-run lesson.*
- **FR-11 [Scale]** The system SHOULD record entity affiliation rationale (MIIT/SASAC/PLA/etc.) and
  overlapping-regime membership (889/FCC Covered List/NS-CMIC) for context. *Origin: research §3.*

## §2 Non-functional requirements (NFR)

- **NFR-01 [MVP]** The master dataset MUST be a text format that diffs cleanly in git. *JSON.*
- **NFR-02 [MVP]** All exports MUST be deterministically regenerable from the master with no manual
  edits. *Single source of truth.*
- **NFR-03 [MVP]** Throughput is not a constraint; correctness and provenance are. No performance
  SLA is set for MVP.

## §3 Security requirements (SR)

- **SR-01 [MVP]** API keys (VirusTotal) MUST NOT be committed; `.gitignore` MUST cover `*.key.txt`
  on its first line. Tooling MUST resolve keys via a documented **keys-dir/env-var contract** (e.g.
  `KEYS_DIR` defaulting to the user's Claude keys dir), and project docs MUST reference that contract
  rather than a verbatim personal path. *Origin: framework rule; D7; openai review (move personal
  secret path out of docs).*
- **SR-02 [MVP]** The verification pipeline MUST operate read-only against external sources and MUST
  NOT install or execute any designated-vendor software in any project or production environment.
  *Origin: notice-only constraint; user.*
- **SR-03 [MVP]** Every externally shared artifact MUST carry the designation-≠-malware and
  report-don't-block caveats. *Origin: research §3.3, §4.4.*
- **SR-04 [MVP]** Every externally shared artifact MUST be labeled AI-assisted / best-effort with
  the notice-only research limitation stated. *Origin: user; framework honesty rule.*

## §4 Integration requirements (IR) — verification sources

Each external source the pipeline depends on, with contract and error semantics.

- **IR-01 [MVP]** winget-pkgs via GitHub raw/contents API (HTTPS, unauth, JSON/YAML). Provides
  InstallerUrl, InstallerType, ProductCode, AppsAndFeaturesEntries, SHA256. Errors: 404 = package
  absent (route to other tiers). *Proven 2026-06-30.*
- **IR-02 [MVP]** NIST NVD CPE API (`services.nvd.nist.gov/rest/json/cpes/2.0`, HTTPS, JSON).
  Provides canonical `cpe:2.3:a:vendor:product:version` and OS markers. Rate-limited; back off.
- **IR-03 [MVP]** VirusTotal API v3 (`/files/{sha256}`, `x-apikey` header). Provides
  `meaningful_name`, observed names, `signature_info.signers`/`verified`/`product`. Errors: 404 =
  unknown hash; 401 = key problem (STOP). *Key verified.*
- **IR-04 [MVP]** Playwright + Chromium (project `.venv/`) for JS-rendered/WAF-blocked vendor
  portals. Provides rendered DOM text + discoverable PDF/installer URLs. Errors: WAF/geo block →
  fall back to SDK PDF / VT. *Proven against Hikvision.*
- **IR-05 [MVP]** Vendor SDK/user-manual PDFs via `curl` + `pdftotext`. Provides DLL names, service
  names, install paths from vendor-official docs. Errors: gated/absent → CANDIDATE.

## §5 Data requirements (DR)

- **DR-01 [MVP]** A single JSON master MUST nest entity → software → indicator so indicators cannot
  be orphaned (no separate attribution file). *Origin: D1; corrupted-run lesson.*
- **DR-02 [MVP]** Confidence tiers MUST be evidence-tied with explicit rules: `VERIFIED` requires
  **≥2 independent artifact classes, at least one vendor-official** (vendor doc/portal/SDK PDF, OR VT
  code-signer = the designated vendor, OR official-vendor-domain installer URL); `CORROBORATED` =
  multiple reputable sources agree, none vendor-official; `REPORTED` = single reputable third-party;
  `CANDIDATE` = unsourced. *Origin: D2; mistral review (tier subjectivity).*
- **DR-02a [MVP]** Each source MUST be credited only for the **claim type it actually proves**, not
  the whole indicator: VirusTotal signer → *publisher linkage of a binary* (NOT uninstall keys,
  services, or paths); NVD CPE → *canonical vendor/product naming* (NOT Windows-installability or
  host-artifact fidelity); winget → *installer filename/ProductCode/ARP entries*; vendor SDK/user PDF
  → *DLL/service/install-path names*. A `REGISTRY_KEY`/`SERVICE_NAME`/install-path claim therefore
  cannot reach VERIFIED on a VT signer or NVD CPE alone. *Origin: openai review. <!-- AI review
  20260630-080409: don't oversell VT/NVD; each source verifies a specific claim, not the indicator. -->*
- **DR-03 [MVP]** Only `VERIFIED` and `CORROBORATED` indicators MUST be included in ETAC/exported
  sets; `REPORTED`/`CANDIDATE` MUST be quarantined to the backlog. *Origin: D2.*
- **DR-04 [MVP]** Provenance fields (`source_url`, `source_tier`, `date_verified`, `verifier_tool`)
  MUST be present on every indicator. *Origin: D7.*
- **DR-05 [Scale]** Delisted entities MUST be retained as reference, flagged out-of-scope. *Origin:
  research §2.*
- **DR-06 [MVP]** All data is derived from public sources; the dataset MUST contain no secrets and
  no classified content. *Origin: D7; SR-01.*
- **DR-07 [MVP]** The master MUST validate against a published JSON schema, committed as the v0.1
  load-bearing artifact (before any indicator coverage). *Origin: NFR-02; TR-02; all reviewers.*
- **DR-08 [MVP]** Shipped and backlog indicators MUST be structurally separated — a status field plus
  an export filter that excludes non-shippable tiers, AND a separate namespace so an export bug cannot
  pull `CANDIDATE`/`REPORTED` into a shipped bundle (defense in depth, beyond the TSC-03 gate).
  *Origin: anthropic+openai review. <!-- AI review 20260630-080409: quarantine-by-path-name is not
  enough; make leakage structurally impossible. -->*

- **DR-09 [MVP]** No indicator value MAY be a file hash or a version-pinned string, and no hash or
  version-pinned value MAY appear in any shipped indicator or any export. A hash used *during*
  verification (e.g., the SHA256 sent to VirusTotal) lives **only** in the internal verification log
  as provenance, never as a called-out indicator. *Origin: Don 2026-06-30; research §4.3. Hard rule
  replacing the prior softer "hashes MAY be retained as provenance."*
- **DR-10 [MVP]** Every indicator value MUST be the **stable, version-independent** form (base
  executable name, install folder, service short name, SDK DLL base name). Version-specific source
  outputs (e.g., `WeChatSetup_3.9.12.57_x64.exe`, `iVMS-4200 V3.14.0.6_E`) MUST be normalized to that
  stable form before becoming an indicator; the raw source string is kept only in the verification
  log. *Origin: Don 2026-06-30 (point-in-time/version-drift concern).*

## §6 Observability requirements (OR)

- **OR-01 [MVP]** Each indicator MUST log `date_verified` and the source/tool that verified it.
- **OR-02 [Scale]** The pipeline SHOULD emit a per-run verification log (artifact, source, result)
  for audit and for the ETAC validation trail.

## §7 Operational requirements

- **OPS-01 [Scale]** A runbook MUST exist for re-running the pipeline against each annual 1260H
  update (re-parse, re-verify, regenerate exports). *Origin: Vision §5 Window 3.*
- **OPS-02 [Scale]** Shipped indicators SHOULD carry a re-verification cadence; stale citations are
  flagged for recheck.

## §8 Architectural requirements (AR)

- **AR-01 [MVP]** Master-and-exports pattern: one source of truth, all other formats generated.
- **AR-02 [MVP]** The verification pipeline MUST be a discrete, tiered component (IR-01..05) with a
  source-tier → confidence-tier mapping (DR-02).
- **AR-03 [MVP]** Detection data and attribution MUST be unified by nesting (DR-01), eliminating the
  orphaned-attribution failure mode of the prior run.
- **AR-04 [MVP]** STIX modeling MUST use non-malware semantics (FR-08).

## §9 Maintainability requirements (MR)

- **MR-01 [MVP]** Entity extraction MUST be reproducible from repo-committed inputs (parser reads a
  repo-local text via CLI arg/default; no machine-specific paths) and MUST self-check against the
  committed counts (80/108/10), failing loudly on PDF-layout drift. *Implemented 2026-06-30 per AI
  review 20260630-080409 (all): hardcoded /tmp path + spot-check-only output were the flagged break.*
- **MR-02 [MVP]** New indicators MUST be addable without schema changes.
- **MR-03 [Scale]** Adding a new verification source SHOULD not require restructuring the master.
- **MR-04 [MVP]** The project MUST maintain an **authority map** (which docs are canonical vs
  historical vs quarantined vs generated) and SHOULD maintain a **consistency matrix** (requirement →
  schema field → generator → test → output artifact) and **ADRs** for irreversible decisions (nested
  JSON over relational; shipped/backlog separation; STIX non-malware semantics; no-install policy).
  *Origin: mistral+openai review (documentation governance).*

## §10 Testing requirements (TR)

- **TR-01 [MVP]** Every shipped indicator MUST be re-verified against its cited source (a real
  successful fetch) before it is marked VERIFIED/CORROBORATED. *The real-call rule.*
- **TR-02 [MVP]** The master MUST pass JSON-schema validation in CI/local check.
- **TR-03 [MVP]** Each generated export (STIX/Markdown/CSV/YAML) MUST round-trip from the master
  without divergence; the STIX bundle MUST validate against STIX 2.1.
- **TR-04 [MVP]** PowerShell examples MUST be syntactically valid and reviewed against Microsoft
  docs (no `Win32_Product`). *Origin: research §4.2.*

## §11 Out of scope (with re-entry points)

- Hardware/firmware-only indicators — excluded by mandate (re-entry: never, unless scope changes).
- Network IOCs, file hashes, and version-pinned values as indicators — unstable and below this
  project's altitude (research §4.3; DR-09/DR-10). A hash MAY exist only inside the internal
  verification log as provenance, never as a shipped indicator or in an export. Re-entry: a separate
  forensic/IOC effort if ever needed — explicitly out of scope here.
- Active OT/ICS scanning — excluded; OT guidance is passive (Vision §6).
- Auto-blocking / remediation logic — excluded; report-only (SR-03).
- Installing target software to harvest artifacts — excluded (SR-02); re-entry: a deliberate
  isolated lab-VM enrichment (Vision Bet 5), user/ETAC-led.
- Deep non-Windows coverage — Linux/server relevance noted only; re-entry: Scale/vNext.
- Authoring the CutSec blog post — separate downstream effort.
