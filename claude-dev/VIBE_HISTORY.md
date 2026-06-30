# VIBE_HISTORY — threat_hunt_china_entities

Append-only, newest entry first. Durable narrative of decisions and rationale across sessions.
Claude writes and reads this for continuity. Not a human chore.

---

## 2026-06-30 (most recent) — Output documented; QA pass; paused at a clean stopping point

- **PowerShell output defined + documented.** `Find-DesignatedVendorSoftware.ps1` now writes matched
  items to STDOUT as objects (pipeable to Export-Csv / EDR), keeps the status/summary on the console
  stream so it never pollutes a pipe/redirect, and adds `-OutputCsv` for direct file output. README has
  an "Output" subsection; comment-based help has .OUTPUTS/.PARAMETER/.EXAMPLE. All three save modes
  validated on the Win10 target.
- **QA pass (pre-share quality gate).** Link-liveness: 44 source URLs, 41 live, 3 WAF-403
  (authoritative/candidate), **0 dead** (tool: `data/check_links.py`). Accuracy: 52 verified/reported
  entries re-verified by 3 independent agents -> **no fabricated vendors/products, tiers correct.**
  Four corrections applied: Knownsec ZoomEye-python clarified (pip CLI, not a Windows installer);
  Unitree `unilidar_sdk` removed (Linux/ROS, not Windows; **60 -> 59 products**); Hikvision HikCentral
  source URL fixed (had pointed at an iVMS-4200 page); Geosun "Windows implied, OS not stated" caveat.
  Several vendor pages are JS-rendered and were corroborated via search. Detectors re-attached (2) on
  the corrected catalog; all ship gates pass. Write-up: `claude-dev/QA_20260630_link_and_accuracy.md`.
- **Status:** shipped to `cutaway-security/threat_hunt_china_entities` (private); `main` = deliverable
  (default), `claude-dev` = full project. **Paused here at Don's direction.** Remaining is optional and
  downstream (humanize the prose for the blog; ETAC hand-off; the blog post; candidate/detector enrichment).

## 2026-06-30 (latest) — PowerShell validated on real Windows 10; BOM bug fixed

Tested `Find-DesignatedVendorSoftware.ps1` against the CutSec Proxmox lab per the CHAPS method
(`/home/cutaway/Projects/chaps/claude-dev/REMOTE_TESTING.md`): Windows VMs are reached over **SSH**
using aliases in `~/.ssh/config` (real IPs/keys/VMIDs live only there, never in a repo); the
`vm-lookup` helper resolves the Proxmox VMID; pattern is start-VM -> `scp` script to `C:/Temp/` ->
`ssh` run -> capture -> clean up. (Did NOT copy any CHAPS content into this repo.)

**Bug caught by real-host testing:** Windows PowerShell 5.1 reads BOM-less UTF-8 `.ps1` as ANSI, so
the non-ASCII (CJK) vendor publisher patterns were mangled -> parse error. Fixed by saving the script
as **UTF-8 with BOM** (committed to both branches). Re-validated on **Windows 10 Pro,
PS 5.1.18362** (`DESKTOP-582JB74`): the script parses and runs; correctly reports no
designated-vendor software on a clean host; and with a `-Vendors` override the registry-uninstall
enumeration + Publisher/DisplayName match path returned the expected hits (Microsoft Edge/WebView2/
OneDrive/Update Health Tools) with the review-don't-block message and pipeline objects. The earlier
"registry-match path untested" caveat is now resolved.

Lab note: the Win10 alias IP in `~/.ssh/config` was stale and the QEMU guest agent was not running;
Don brought sshd up. Default SSH shell on these VMs is `cmd` (use `powershell -File`/`-Command`).

## 2026-06-30 — Consolidated to the real deliverable; repo plan

Don's scope call: drop the broad ambitions (no public website, no STIX/YAML, no export machinery in
the deliverable). **The deliverable is the company -> software list in two forms: a readable report
for admins (`README.md` findings-first + `CATALOG.md`) and a tool-feed (`data/master/entities.master.json`
+ flat `companies_software.csv`), plus the PowerShell vendor/software sweep
(`Find-DesignatedVendorSoftware.ps1`, with false-negatives explicitly called out).** The research
tooling (`pipeline/`, `exporters/`, `data/` builders) is KEPT for history / future enrichment, not
presented as part of the deliverable. The superseded `guide/` was removed (its useful hunt folded into
README + the .ps1; the per-indicator section was misleading given only 2 detectors). STIX/YAML dropped.
ETAC consolidated into the same content as public (no separate package).

Repo plan (cutaway-security, private, `threat_hunt_china_entities`): `claude-dev` branch = the full
project (research + tooling + planning + quarantine record); `main` = a clean orphan branch holding
only the deliverable, the working area for continued refinement. The .ps1 parses and runs cleanly
(no-match path verified on Linux); the registry-match path is logic-verified but untested against real
Windows installs — flagged as such.

## 2026-06-30 — Packaging complete; client deliverable assembled

Generated all shareable artifacts from the master (single source of truth): CSV/YAML/STIX 2.1 exports
(`exporters/export.py`; STIX built+validated with the stix2 library, 149 objects, software+identity+
anomalous-activity indicators, NO malware SDO, CPE wildcarded); the threat-hunt guide
(`guide/THREAT_HUNT_GUIDE.md`, PowerShell incl. a Publisher-based installed-software sweep — the
highest-value, detector-independent hunt); `METHODOLOGY.md`; and a public `README.md`.
`packaging/package.py` assembles `release/public/` (stripped — no claude-dev/quarantine/.ai-reviews/
.venv, no ETAC mention) and `release/etac/` (private — adds the verification log + an ETAC cover note).
All ship gates pass; leak-checked the public tree. Every external artifact carries the
best-effort / designation-not-malware / report-don't-block caveats. The deliverable is a client
hand-off; the CutSec blog post is a separate downstream effort.

## 2026-06-30 — Layer 2 software catalog COMPLETE (all 80 assessed)

Built the full Layer-2 catalog: every one of the 80 designated parents has a justified disposition,
and software-producing vendors have their Windows products catalogued with provenance. Method: 5
parallel research agents (16 entities each) under strict no-fabrication rules (a product is named
only with a fetched source URL), synthesized into `data/build_catalog.py` -> `entities.master.json`
(+ generated `CATALOG.md`, human-readable). catalog_status tiers each software fact: verified
(vendor-official) / reported (third-party) / candidate (lead).

Result: **20 vendors publish confirmed installable Windows software**, 12 candidates pending, 48
none (26 no-software, 19 hardware/firmware, 3 server/Linux). **60 software products** (41 verified,
11 reported, 8 candidate). High-signal threat-hunt vendors all confirmed: Hikvision (iVMS-4200,
HikCentral, SADP), Dahua (SmartPSS, DSS Express, ConfigTool...), Huawei (PC Manager, HiSuite, eNSP),
DJI (Assistant 2, Terra, Thermal Analysis Tool 3), Tencent (WeChat, QQ, Meeting, WeCom, Docs),
TP-Link (Omada, Pharos Control), Qihoo 360. Notable additions beyond the obvious: China Telecom
(Cloud 189), Alibaba (DingTalk), Baidu (Netdisk), Autel, Quectel, Hesai/Robosense/Unitree (LiDAR
tools), SDIC/Meiya Pico (forensics), YMTC (SSD tools), Geosun, GTCOM, Knownsec.

Citation-audit spot-check caught one dead vendor link (Robosense `resources-81` -> 404); corrected
to the live RSView FAQ URL. The schema was extended with software-level provenance
(catalog_status / source_url / windows_installable).

**Layer 3 (detectors) — option #3, best-effort, done.** Don's direction: detectors are nice-to-have,
best-effort, MUST NOT be represented as complete (overclaiming adds risk and undermines confidence);
user confidence in what IS shown must be HIGH; the software list is the solid deliverable.
`pipeline/build_detectors.py` attaches detectors to priority-vendor catalog software with confidence
tiers; only VERIFIED/CORROBORATED attach. Result: **2 high-confidence detectors** (WeChat
`WeChatSetup.exe` VERIFIED via official Tencent CDN; QQ uninstall registry key CORROBORATED via winget
ARP), all gates pass. Tencent Meeting/WeCom, HiSuite, DJI Assistant/Terra yielded no clean
public-source artifact: their winget installer URLs are version-stamped or servlet-based (rejected by
DR-10 validation) and **VirusTotal's public quota was exhausted this session (429 on every call)**.
Hikvision/Dahua install-time artifacts (iVMS-4200.exe, HCNetSDK.dll, SmartPSS.exe, dhnetsdk.dll)
cannot be verified from public sources without installing (SR-02) — left honestly absent, not
fabricated. `CATALOG.md` carries a prominent best-effort/partial caveat; coverage is not claimed. This
is the project thesis holding under pressure: a thin, honest, high-confidence detector set beats a
broad fabricated one.

## 2026-06-30 — v0.2 pipeline built; honest yield finding

The verification pipeline is built and runs end-to-end with real calls (winget, NVD CPE, VirusTotal,
vendor-CDN liveness): `pipeline/sources.py`, `verify.py` (typed claims + tiering), `gates.py`,
`build_seed.py`. The master + `data/logs/verification_log.jsonl` are produced; all ship gates pass
(schema, provenance TSC-02, tier-leak TSC-03, staleness TSC-04, value-sanity DR-10).

**Durable findings:**
- **VT-independent VERIFIED path works and is the workhorse.** VirusTotal's public API rate-limits
  hard (429), so we confirm the vendor's *own CDN* serves the named installer via a read-only HEAD
  (SR-02). WeChat: `WeChatSetup.exe` from `dldir1v6.qq.com` (HTTP 200) + NVD naming + winget = VERIFIED.
- **The "verified, not derived" discipline caught its own garbage.** First clean run shipped
  `public` (Huawei servlet path), `QQ9.7.23.29392.exe` (version-pinned, a DR-10 leak the schema
  missed), and a mangled DJI name. Added strict installer-name validation + a DR-10 value gate; those
  values are now correctly REJECTED, not shipped. This is the core failure mode being prevented in code.
- **Clean Tier-1 host artifacts are scarcer than the quarantined CoPilot run pretended.** Reliable
  signals: a clean version-free installer name (rare), the ARP **registry uninstall key** (ProductCode,
  from winget — clean), and VT-confirmed observed exe names (when quota allows). Most winget InstallerUrls
  are version-stamped or servlet-based and yield nothing clean.
- **Implication:** reaching VERIFIED *host-presence* per vendor needs the Tier-2 enrichment — Playwright
  vendor-page / SDK-PDF parsing for real installed exe names, service names, and install paths — which
  is exactly the v1.0 "hard vendor" work. The easy consumer apps give strong attribution + clean
  installer/registry artifacts, not a full host-presence set. Gate B: TSC-02/03/04/DR-10 pass; TSC-09
  partial (Tencent VERIFIED; vendor-official host-presence pending Tier-2).

## 2026-06-30 — Distribution model, license, ETAC-first sequencing

- **License: MIT** (Don: "normal license, people can use it but attribution is nice"). MIT preserves
  attribution via the retained copyright/permission notice. Applied at repo root. Option noted: CC-BY-4.0
  for the data/docs if a content-license is later preferred.
- **ETAC is a separate, private, end-of-line deliverable — NOT a gate, NOT first, NOT in public docs.**
  (Corrected from an earlier "ETAC-first" misread.) Finish the full, well-developed deliverable, THEN
  distribute two ways: a **private ETAC package** (a separate "aside" they can use or start from/enrich)
  and the **public release + blog** (industry, no ETAC mention). **Bounded client deliverable** — no
  ongoing enrichment unless ETAC requests collaboration later. ETAC may enrich gaps themselves, so the
  hard vendors don't block distribution, but we still aim for complete/polished, not a minimal seed.
- **Two-tier packaging.** Dev repo / `claude-dev` branch holds everything (planning, quarantine,
  `.ai-reviews`, history). The **public release / `main` is stripped** (per Cutaway `GIT_RELEASE_STEPS.md`):
  no `claude-dev/`, no quarantine, no `.ai-reviews`, no dev intermediates — a clean defender-oriented
  README + `dataset/` + `guide/` + LICENSE + METHODOLOGY. Public README is distinct from the dev README.

## 2026-06-30 — Project init (cutsec-init pipeline, Phases 0–6 + scope-balance)

**What landed (by path):**
- `background/` — 1260H PDF + URL kept as trusted seed; prior CoPilot output quarantined under
  `background/_quarantine_untrusted_copilot/` with `_README_UNTRUSTED.md` + per-file UNTRUSTED banners.
- `data/source_extraction/parse_1260h.py` (+ `1260h_pdftotext_layout.txt`, `entities_1260h.json`) —
  reproducible entity correlation: 80 parents / 108 subsidiaries / 10 delisted, with a count gate.
- `claude-dev/DISCOVERY_NOTES.md` (intake + discovery + decisions D1–D8), `20260630_..._RESEARCH.md`
  (Phase 2 survey, citation-audited), `verification_pipeline_notes.md`, `stix_modeling_notes.md`,
  `VISION.md`, `REQUIREMENTS.md`, `SUCCESS_CRITERIA.md`.
- `.ai-reviews/20260630-080409/` — first multi-AI pass (anthropic/mistral/openai) + consolidated synthesis.
- `.gitignore` (pulled forward); `.venv/` with Playwright+Chromium.

**Durable decisions:**
1. **Prior CoPilot run is corrupted — discarded.** Full dataset was synthetic placeholder
   (Company_1/Software_1/proc_1), attribution all-UNKNOWN, narratives uncited. Rebuild from the 1260H
   PDF only. This failure mode (uncited + orphaned attribution) is what the data model is built against.
2. **Provenance-first, nested JSON master** (entity→software→indicator) so an indicator cannot exist
   without its software, company, and citation (D1).
3. **Evidence-tied confidence tiers** VERIFIED/CORROBORATED/REPORTED/CANDIDATE; only the top two ship.
   Each source credited only for the claim it proves (VT=signer/naming, NVD=naming, winget=installer,
   SDK-PDF=DLL/service/path) (D2, DR-02a).
4. **Tiered verification pipeline** built and proven by spot-check: curl/jq (winget, NVD), Playwright
   (renders WAF-blocked Hikvision), VirusTotal (Tencent code-signer). Pipeline *as code with gates* is
   the first implementation slice (v0.2), NOT yet built (D7).
5. **Designation ≠ malware** — affiliation/provenance flag (1260H is not sanctions; teeth are FY24
   NDAA §805 DoD procurement). STIX uses software/identity + `anomalous-activity`, never `malware`.
   Report-don't-block everywhere.
6. **Distribution minimized**: JSON master + Markdown + STIX; CSV/YAML/Sigma on demand only (D4).
   PowerShell-only hunt examples, runnable, not a tool (D5).
7. **Altitude / anti-specificity (D8)**: recognition-grade, version-independent named artifacts only.
   No hashes, no version-pinned values as indicators or in exports (DR-09/DR-10). VT is point-in-time
   confirmation/attribution/embedded-library detection — never enumeration or build-pinning.

**Lessons from the first multi-AI pass (3/3 reviewers, strong consensus):**
- The original single MVP over-scoped a whole release with nothing built; re-phased narrow-and-deep
  v0.1→v1.0 (schema + gates before coverage).
- Stop calling the pipeline "done/proven" — it was method + spot-checks; corrected the language.
- The parser hardcoded a `/tmp` path and was spot-check-only — fixed to repo-local input + a count
  gate (80/108/10), and the `short_alias` "Xiamen" bug fixed.
- Coverage = **disposition assigned**, not artifacts harvested (most of 80 parents yield no Windows
  software). Distinguish `product_installed` vs `sdk_embedded`. Don't oversell VT/NVD.
- Referee note: reviewers treated "pipeline not implemented" as a defect; for a pre-implementation
  init gate that's expected — adopted the valid core (overclaim, parser, gates-first), deferred
  pipeline *code* to the plan.

**Project context:** ETAC (DOE/CESER) is the key external consumer; goal is they *validate* not
*rebuild*. Same no-hallucination discipline as ControlProbe. Blog post is a separate downstream effort.
The "65 new entities" figure is WilmerHale's secondary count and remains unreconciled against our own
parse (80 parents / 108 subs / 10 delisted from the June 8 2026 PDF); treat secondary totals as
unreconciled wherever cited.

## 2026-06-30 (later) — Second multi-AI pass (architecture) applied

Pass 2 (`.ai-reviews/20260630-085540/`, 3/3 ok) confirmed the phasing and caught deeper items, applied:
- **CRITICAL:** the STIX skeleton embedded a version-pinned `version`/`cpe`, contradicting the new
  no-version-pin altitude rule — fixed (wildcard CPE version, drop SCO `version`, normalize at export).
- **CRITICAL (openai):** VERIFIED wording let attribution (VT signer / installer domain) be promoted
  to host-presence — tightened to require vendor-official support per indicator type; adopted an
  **atomic claim-typed evidence model** (ARCHITECTURE §4a) so DR-02a is schema-enforced, not policy.
- Un-fixed FR-08's STIX `indicator_types` (pending ETAC); softened "structurally impossible" to a
  realized-by-v0.1/v0.2 property; scrubbed the literal key path to the `KEYS_DIR` contract; named the
  Playwright trust boundary + source-deception threat; reconciled TSC-06 (execute) and TSC-01
  (name-diff); added a TSC-09 qualitative constraint; split internal readiness from external ETAC acceptance.
- **Referee:** rejected mistral's false "short_alias still broken" finding (the fix is in; JSON shows
  `null` for SDIC; anthropic verified).
- **Carried to PLAN (v0.1/v0.2 code, NOT built in init):** committed JSON schema with the claim model;
  committed expected name lists + **name-diff gate** + golden-output regression test; parser hardening
  (UTF-8, subsidiary-merge robustness); gate scripts; sandboxed Playwright; authority map + ADRs.
  **TSC-01 / Gate A do not pass until the name-diff gate exists** — v0.1 is in progress, not landed.

**Next session:** Phase 7 — Architecture (JSON schema, verification pipeline as a discrete tiered
component with shipped/backlog gates, STIX projection, module layout, disposition model), then the
second multi-AI pass on the architecture, then Phases 9–11 (orientation files, PLAN/RESUME, verify).
