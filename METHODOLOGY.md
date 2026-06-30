# Methodology

**AI-assisted, best-effort.** This document explains how the Section 1260H software catalog and the
host-artifact detectors were produced, and — just as important — what they do and do not claim.

## Source of truth

The U.S. DoD **Section 1260H** notice (Public Law 116-283; list dated **2026-06-08**) — the official
list of entities identified as "Chinese military companies" operating in the United States. A 1260H
designation reflects **corporate affiliation** with China's military-civil-fusion apparatus. It is
**not** a sanctions action and **not** a finding that the company's commercial software is malicious.
Everything here is **exposure / inventory** analysis, not malware detection.

## How it was built

1. **Entities (complete).** The 80 designated parent entities, 108 named subsidiaries, and 10 delisted
   entities were extracted reproducibly from the notice with a parser that self-checks against a
   committed count and a full name-diff, so a future list revision cannot silently corrupt the data.

2. **Software catalog (complete coverage, tiered).** Every one of the 80 entities was assessed for
   whether it publishes installable Windows software. Most do not (aerospace, shipping, nuclear,
   chemical, hardware/chip makers); 20 do. Each software product is recorded only with a fetched source
   URL and a trust tier:
   - **verified** — confirmed on a vendor-official source;
   - **reported** — confirmed on a reputable third party (winget, Microsoft Store, vendor wiki);
   - **candidate** — named but the Windows build/distribution is not yet confirmed.

3. **Host-artifact detectors (best-effort, PARTIAL).** Where possible, the installed file / registry /
   service / DLL artifacts that reveal a product's presence were verified through a tiered pipeline
   (winget package metadata, NIST NVD CPE naming, VirusTotal code-signer attribution, and read-only
   confirmation that the vendor's own CDN serves an installer). Each detector carries a confidence tier
   and an evidence trail of typed claims. **This layer is intentionally incomplete** — many install-time
   artifacts cannot be verified from public sources without installing the software, which was not done.

## Discipline (why you can trust what is here)

- **Verified, not derived.** No software name, file name, registry key, service, or DLL is included
  unless it traces to a real, fetched source. Nothing is guessed.
- **No installation.** No designated-vendor software was installed or executed to produce this. It is a
  starting point built from the public notice and public sources.
- **Recognition-grade altitude.** Indicators are named, version-independent artifacts — no file hashes,
  no version-pinned values. They are durable across updates (and therefore collide more than a hash
  would, so corroborate across two artifact classes).
- **Designation ≠ malware.** Nothing here is modeled as malware. Report findings for human review; do
  not auto-block lawful software.
- **An earlier AI run was discarded.** A first automated pass produced placeholder and unsourced data;
  it was quarantined as untrusted and the work was rebuilt from the notice. That failure is why the
  data model makes unsourced or orphaned indicators structurally impossible.

## What this is not

Not a complete detection set, not a malware feed, not a sanctions/compliance determination, not active
OT/ICS scanning. The **software catalog is the high-confidence deliverable**; the detectors are a
labeled best-effort starting point that requires verification and enrichment before operational use.

## Reproducibility

The dataset is generated from the source notice by the included code (`data/`, `pipeline/`,
`exporters/`); the master JSON is the single source of truth and all other formats (Markdown, CSV,
YAML, STIX 2.1) are generated from it.
