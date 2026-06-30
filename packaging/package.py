#!/usr/bin/env python3
"""Assemble the two distributions from the same source tree:

  release/public/ -- stripped, defender-oriented public release (for the repo + CutSec blog).
                     EXCLUDES dev planning, the quarantined first-run data, AI-review history, and the
                     venv. NO mention of ETAC.
  release/etac/   -- the private ETAC package (the same data/guide/method + verification log + a cover
                     note framed for ETAC). Not part of the public repo.

Run after exporters/export.py + data/generate_catalog_md.py.
Run:  .venv/bin/python packaging/package.py
"""
import os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REL = os.path.join(ROOT, "release")

# Files/dirs included in BOTH distributions (public-safe; no dev/quarantine/history).
COMMON = [
    "LICENSE", "METHODOLOGY.md", "CATALOG.md",
    "guide/THREAT_HUNT_GUIDE.md",
    "dist/",                              # generated CSV / YAML / STIX exports
    "data/master/entities.master.json",  # the dataset (single source of truth)
    "data/schema/master.schema.json",
    "data/source_extraction/parse_1260h.py",
    "data/source_extraction/test_parser.py",
    "data/source_extraction/entities_manifest.txt",
    "data/source_extraction/1260h_pdftotext_layout.txt",
    "data/build_master_stub.py", "data/build_catalog.py", "data/generate_catalog_md.py",
    "pipeline/", "exporters/",
    "background/original_report_url.txt",
]
# ETAC-only additions (private provenance + cover note written below).
ETAC_EXTRA = ["data/logs/verification_log.jsonl"]

PUBLIC_README = """# Section 1260H Designated-Vendor Software (Windows) — Catalog & Hunt Guide

**AI-assisted, best-effort.** A catalog of commercial, computer-installable software produced by
entities on the U.S. DoD **Section 1260H** list, and best-effort host-artifact detectors for finding it
on Windows. A 1260H designation is a corporate-affiliation flag — **not** a malware finding. This is
**exposure/inventory** analysis: **report findings for human review; do not auto-block.**

## Contents
- `CATALOG.md` — the software catalog: all 80 entities assessed; 20 publish Windows software, each
  product sourced and trust-tiered. **High-confidence deliverable.**
- `guide/THREAT_HUNT_GUIDE.md` — how to hunt on Windows (runnable PowerShell), incl. a Publisher-based
  installed-software sweep.
- `dist/` — generated exports: `csv/`, `yaml/catalog.yaml`, `stix/1260h_software_bundle.json` (STIX 2.1).
- `data/` + `pipeline/` + `exporters/` — the dataset (`entities.master.json`), its schema, and the code
  that reproduces every export from it.

## Status & limitations
The **software catalog is reasonably complete** (every entity assessed). The **host-artifact detectors
are best-effort and PARTIAL** — most install-time artifacts need verification/enrichment (vendor SDK
manuals, code-signer lookups, or controlled lab observation). **Absence of a detector does not mean the
software is absent.** Windows first; OT/ICS hunting should be passive. No file hashes, no version pins.

## License
MIT (see `LICENSE`).
"""

ETAC_COVER = """# Section 1260H Software Catalog & Detectors — package for review

**Private hand-off. AI-assisted, best-effort.** This is a *starting point* you can use as-is or build
from and enrich — not a finished or complete product.

## What is solid
- **Entities:** all 80 designated parents (+108 subsidiaries, 10 delisted) extracted reproducibly from
  the 2026-06-08 notice, with a name-diff fidelity gate.
- **Software catalog:** every entity assessed; 20 publish installable Windows software (60 products),
  each with a fetched source and a trust tier (verified / reported / candidate). This is the
  high-confidence layer and the main value here.

## What is best-effort and PARTIAL (your enrichment opportunity)
- **Host-artifact detectors.** Only artifacts verifiable from public sources without installing the
  software are included (currently a small, high-confidence set). The install-time artifacts you would
  want for hunting — installed exe names, install paths, services, SDK DLLs such as `HCNetSDK.dll` /
  `dhnetsdk.dll` for Hikvision/Dahua — require enrichment: vendor SDK manuals, code-signer (VirusTotal)
  lookups, or controlled isolated-lab observation. We deliberately did not fabricate these.
- `data/logs/verification_log.jsonl` is the evidence trail (every source fetch) for your validation.

## Discipline
Verified-not-derived; no installation of the target software; no hashes/version pins; designation is
affiliation, not malware (report, don't block). See `METHODOLOGY.md`.

The framing and caveats above must be preserved if any of this is republished.
"""


def copy_item(rel_path, dest_root):
    src = os.path.join(ROOT, rel_path)
    dst = os.path.join(dest_root, rel_path)
    if not os.path.exists(src):
        return f"MISSING {rel_path}"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    else:
        shutil.copy2(src, dst)
    return f"  + {rel_path}"


def build(dest_root, items, readme_name, readme_text, cover=None):
    if os.path.exists(dest_root):
        shutil.rmtree(dest_root)
    os.makedirs(dest_root)
    notes = [copy_item(p, dest_root) for p in items]
    open(os.path.join(dest_root, readme_name), "w", encoding="utf-8").write(readme_text)
    if cover:
        open(os.path.join(dest_root, "ETAC_COVER.md"), "w", encoding="utf-8").write(cover)
    return notes


def main():
    pub = build(os.path.join(REL, "public"), COMMON, "README.md", PUBLIC_README)
    etac = build(os.path.join(REL, "etac"), COMMON + ETAC_EXTRA, "README.md", PUBLIC_README, cover=ETAC_COVER)
    miss = [n for n in pub + etac if n.startswith("MISSING")]
    print(f"release/public/  ({sum(1 for n in pub if n.startswith('  +'))} items)")
    print(f"release/etac/    ({sum(1 for n in etac if n.startswith('  +'))} items, + verification log + ETAC_COVER.md)")
    print("EXCLUDED from both: claude-dev/, background/_quarantine_untrusted_copilot/, .ai-reviews/, .venv/")
    if miss:
        print("WARNING missing inputs:")
        for n in sorted(set(miss)):
            print("  ", n)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
