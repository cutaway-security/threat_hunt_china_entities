# TEST_ENVIRONMENT — threat_hunt_china_entities

Where and how this project is tested. The success-claim guardrail (no "shipped" without a real fetch
against a real source) is only enforceable if there is a defined place those fetches and host checks
happen.

## Baseline (Cutaway standard)

- **Proxmox** development VM (Cutaway standard) running Linux for the pipeline, parser, gates, and
  exporters. Python 3.12; `curl`/`jq`/`pdftotext` (poppler); Playwright + Chromium in the project
  `.venv/`. Direct network egress required (winget raw/API, NVD CPE API, VirusTotal v3, vendor sites).
- **Secrets:** VirusTotal key via the `KEYS_DIR` contract (default `/home/cutaway/.claude/keys`),
  never in the repo.

## Per-test-class environment

| Test class | Where | Notes |
|---|---|---|
| Parser / schema / gate unit tests | dev VM, offline | Golden-output regression test (parse committed text == committed JSON); name-diff against committed lists. No network. |
| Verification pipeline (live) | dev VM, online | Real fetches: winget (GitHub), NVD CPE, VirusTotal, vendor PDFs. The "real call" that satisfies the load-bearing clause. Honor NVD back-off and VT quota. |
| Playwright tier | dev VM, **sandboxed** | Executes untrusted vendor/WAF JavaScript — run isolated, pin Chromium 149, do not pipe rendered DOM into the master without passing the claim/verification layer. |
| PowerShell hunt examples (TSC-06) | **Windows test VM** | Examples MUST be executed against a fixture (a Windows VM with one or more seed apps installed in a lab, OR a synthetic Uninstall-key fixture). Never `Win32_Product`. This is the one component needing a Windows host. |
| STIX export (TSC-05) | dev VM, offline | Validate against STIX 2.1; confirm no `malware` SDO / `malicious-activity`; CPE version wildcarded, no SCO `version`. |

## Explicitly NOT in the test environment
- **No installation of designated-vendor software** in any Cutaway production or OT environment
  (SR-02). The Windows test VM for TSC-06 is an isolated lab; a deliberate lab-VM install for
  ground-truth host artifacts (Vision Bet 5) is a future, user/ETAC-led option, not part of this work.
- No active OT/ICS scanning.

## Provisioning
The first v0.1 implementation slice provisions: the dev VM toolchain (above, mostly in place this
session) and a minimal Windows test VM (or synthetic registry fixture) for TSC-06 before v0.3.
