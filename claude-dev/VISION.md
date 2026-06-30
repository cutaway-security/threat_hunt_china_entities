# VISION — threat_hunt_china_entities

Status: Phase 3 draft (pre multi-AI validation). Strategic north star — not engineering scope.
Author: Cutaway Security (Don C. Weber). Date: 2026-06-30.

---

## 1. The vision, in one paragraph

By the second half of 2026, this project delivers a **provenance-first, continuously improvable
dataset and threat-hunt guide** that lets enterprise and OT defenders — and the Department of
Energy's Energy Threat Analysis Center (ETAC) — find commercial software produced by the companies
on the DoD **Section 1260H** list on Windows hosts, using **only artifacts proven against
authoritative sources**. The substrate is a single consolidated JSON dataset with generated
exports (Markdown, STIX 2.1); the posture is defensive inventory/exposure discovery, explicitly
**not** malware detection; and the discipline is **verified, not derived** — every file name,
registry key, service, and DLL carries a citation and a confidence tier, or it does not ship. It
is AI-assisted and labeled best-effort, built so a partner like ETAC can *validate* rather than
*rebuild* it.

## 2. Why this exists — a dataset and method, not a one-off report

The obvious alternative is a static "list of risky software" memo. That fails the moment it is
written: the 1260H list is updated at least annually, vendor software changes, and an unsourced
memo cannot be trusted for a real hunt. This project exists because the durable asset is the
**method plus the verified data structure**, not any single snapshot. A prior AI run produced a
large, professional-looking dataset that turned out to be synthetic placeholder data with
all-`UNKNOWN` attribution — the exact failure this project is built to prevent. The value is a
data model where an indicator *cannot exist* without its software, its company, and its
citation; a verification pipeline that grounds each value in winget/NVD/VirusTotal/vendor docs;
and a guide that teams and ETAC can act on and extend. Build the machine that produces trustworthy
indicators, and every future list update is a re-run-plus-verify, not a rewrite. <!-- AI review
20260630-080409 (anthropic+openai): the entity parser is assisted extraction, not fully autonomous;
it now carries a count gate that fails loudly on PDF-layout drift rather than silently mis-splitting,
so the annual rerun is reproducible-with-human-verification, not blind automation. -->

## 3. Principal map

| Principal | Role | What they care about |
|---|---|---|
| ETAC analyst (DOE/CESER contact) | Primary external consumer | Being able to *validate and publish* without redoing the research; energy-sector relevance; defensible sourcing |
| Enterprise IT/security admins | Recognize & triage | A readable list of what to look for; low false positives; "is this on our endpoints?" |
| Threat-hunt / detection teams | Execute the hunt | Runnable starting points (PowerShell), indicator data in usable form, clear confidence |
| OT/ICS administrators | Passive review | Knowing which designated software might appear on engineering hosts, without active scanning |
| Cutaway Security (Don) | Author / publisher | Rigor that protects the CutSec name; a publishable blog artifact; reusable method |
| CutSec blog readers / industry | Downstream users | A credible, honest, AI-assisted exemplar they can use and trust |

## 4. The strategic bets

**Bet 1 — Provenance beats coverage.** A small *verified* set is worth more than a large
*asserted* one for threat hunting. *Why right:* false indicators waste hunt cycles and burn trust;
ETAC needs to validate, not re-verify from scratch. *How it could be wrong:* consumers may want
breadth fast. *Mitigation:* keep a transparent CANDIDATE backlog and a roadmap to expand coverage
tier by tier.

**Bet 2 — Presence is not compromise.** Framing the data as *exposure/inventory* — not malware —
is what makes it safe to adopt. *Why right:* a 1260H designation is a corporate-affiliation flag
(upheld on those grounds in *DJI v. DoD*), not a finding that the software is malicious;
auto-blocking legitimate user software causes real harm. *How it could be wrong:* some consumers
want a drop-in block-list. *Mitigation:* ship the data with a report-don't-block caveat and let
each org set its own policy.

**Bet 3 — The niche is unfilled and stays relevant.** No public work maps the 1260H list to
host-based software-presence indicators (dedup check found none; CISA's China work targets APT
compromise, a different question). *Why right:* the gap is real and the annual list refresh keeps
it live. *How it could be wrong:* a government body could publish first. *Mitigation:* move now and
coordinate directly with the ETAC contact.

**Bet 4 — A consolidated master with generated exports scales; file sprawl does not.** *Why
right:* one nested JSON source makes orphaned/unsourced indicators structurally impossible and
makes every export deterministic. *How it could be wrong:* each consumer wants their own format.
*Mitigation:* generate Markdown/STIX/CSV/YAML from the master on demand rather than maintaining
parallel files.

**Bet 5 — Verification can be automated enough without installing the software.** winget, NVD CPE,
VirusTotal code-signer lookups, headless rendering of blocked vendor portals, and vendor SDK PDFs
together verify most artifacts. *Why right:* proven live for consumer apps (WeChat signer = Tencent;
Hikvision portal rendered past its WAF). *How it could be wrong:* SDK DLLs and partner-gated
portals are hard. *Mitigation:* VirusTotal signer evidence + SDK manual PDFs + honest confidence
tiering; an isolated lab-VM install remains a deliberate future option for ground truth.

## 5. The arc

<!-- AI review 20260630-080409 (anthropic+mistral+openai): corrected "done, proven" overclaim;
honest status + narrow-and-deep phasing. See .ai-reviews/.../consolidated_review.md finding #1,#2. -->
**Window 1 — Foundation (now).** *Done:* authoritative entity correlation from the June 8 2026 list
(80 parents / 108 subsidiaries / 10 delisted, reproducible). *Method validated by manual
spot-checks, tooling not yet built:* the tiered verification pipeline (winget/NVD/VT/Playwright proven
by hand once each, not yet implemented as code). *Still to build, smallest-first:* the committed JSON
schema + nested master; the verification pipeline as actual tooling with its shipped/backlog gates;
and only then a first ETAC hand-off = **method + a small VERIFIED seed** drawn from the consumer-app
vendors verifiable today (Tencent, Huawei, DJI, 360), plus the PowerShell hunt guide. The
implementation tiers are sequenced in REQUIREMENTS §0 (v0.1→v1.0).

**Window 2 — Coverage.** Work through the high-signal vendors including the harder SDK/DLL and
WAF-blocked cases (Hikvision, Dahua), grow the VERIFIED set, finalize STIX and the other exports,
and harden the admin-facing summary.

**Window 3 — Sustain & extend.** Re-run the pipeline against each annual 1260H update; extend
guidance to Linux/server platforms and passive OT review; ship the CutSec blog post and share the
method as a repeatable exemplar.

## 6. What this is not

- Not a legal/sanctions-compliance tool — 1260H is not a sanctions list; consult counsel for that.
- Not a malware feed and not a block-list — it reports presence; humans set policy.
- Not a forensic/hash/version IOC feed — recognition-grade, version-independent named artifacts only.
  Point-in-time tools (VirusTotal) confirm naming/attribution and detect embedded libraries; they do
  not set the altitude or pin specific builds.
- Not a scanner, agent, or EDR product — it is data + guidance; teams use their own tooling.
- Not active OT/ICS scanning — OT guidance is passive and read-only.
- Not hardware/firmware fingerprinting — software installable on computers only.
- Not exhaustive on day one — coverage grows with verification; gaps are stated, not hidden.
- Not the blog post itself — that is a separate downstream effort built on this output.

## 7. What success looks like at the horizon

- ETAC can take the dataset and guide, **validate** the seed indicators against their cited
  sources, and publish their own product without redoing the research.
- Every externally shared indicator resolves to a real, fetchable source and a stated confidence
  tier; zero unsourced values ship.
- Defenders run the PowerShell examples and the indicator set in real hunts and surface real
  installs for human review (not auto-blocked).
- The CutSec blog post ships as an honest, AI-assisted exemplar — including the story of catching
  and discarding the corrupted first run.
- The dataset stays current across annual 1260H updates because re-running the method is cheap.
