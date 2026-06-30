# CLAUDE.md - Project Rules and Guidelines

## Project Overview

**Project**: threat_hunt_china_entities
**Repository**: https://github.com/cutaway-security/threat_hunt_china_entities
**Development Branch**: claude-dev
**Description**: A provenance-first, AI-assisted (best-effort) dataset and threat-hunt guide that
identifies commercial, computer-installable software produced by entities on the DoD Section 1260H
"Chinese military companies" list, and the verified host-based artifacts that prove its presence on
Windows. Built so the Energy Threat Analysis Center (ETAC) and enterprise/OT defenders can *validate*
rather than *rebuild*. It is exposure/inventory discovery, NOT malware detection.

---

## Essential Documents (Read in Order)

Before starting any development session, read these documents in order:

1. **CLAUDE.md** - This file. Project rules, constraints, and conventions
2. **claude-dev/ARCHITECTURE.md** - System design, decisions, constraints, data flow
3. **claude-dev/PLAN.md** - Roadmap, current phase and focus, next steps, blockers, milestones, acceptance gates
4. **claude-dev/VIBE_HISTORY.md** - Decision trail and lessons. AI session-continuity memory: Claude writes and reads it, it is not a document you are expected to maintain by hand

Also load when relevant: VISION.md, REQUIREMENTS.md, SUCCESS_CRITERIA.md, DISCOVERY_NOTES.md,
verification_pipeline_notes.md, stix_modeling_notes.md, AUTHORITY_MAP.md, ADRS.md, and the dated
RESEARCH survey.

**At session start**: Confirm you have read these documents before proceeding. List your understanding
of the current state and next steps. Wait for confirmation before proceeding.

---

## Development Process Rules

When encountering issues during development:

1. **STOP** - Do not continue to next task
2. **DIAGNOSE** - Identify root cause with specific error messages and line numbers
3. **FIX** - Implement a solution
4. **VERIFY** - Confirm the fix works with actual testing
5. **DOCUMENT** - Record the issue and solution in PLAN.md; capture any durable lesson in VIBE_HISTORY.md
6. **ASK** - If unable to resolve after reasonable attempts, STOP and ask for clarifying directions

**Never assume code works without testing. Never move forward with unresolved issues.**

### Phase Completion Process

Before moving to the next phase:

1. **Verify** - All components of current phase working
2. **Test** - Run tests relevant to the phase
3. **Gate** - Confirm the phase's objective acceptance gate passes (a pass/fail test, not "looks done")
4. **Document** - Update PLAN.md with status and next steps
5. **Summarize** - Provide summary of completed work
6. **Plan** - List steps for next phase
7. **Confirm** - Wait for user confirmation before proceeding

---

## Absolute Requirements

- NO emoji, icons, or Unicode symbols in source code, output, or documentation
- NO stubs, placeholders, or fake data -- implement real functionality or mark clearly as TODO with explanation
- NO claiming code works without testing -- be honest about untested code
- NO moving forward when issues are unresolved
- NO spaces in file or folder names
- All output files must contain a timestamp in the filename (format: YYYYMMDD_HHMMSS)
- Never declare any iteration, MVP, or version "shipped," "closed," or "complete" until at least one real call against the real external service or device has returned data. Stub-based tests are wiring checks, not validation.

---

## Secret Hygiene

- API keys are plaintext `*.key.txt` files resolved via the `KEYS_DIR` contract (default keys-dir,
  `/home/cutaway/.claude/keys`), never in the project.
- `*.key.txt` is the first line of `.gitignore`. Never commit a key. Never write a verbatim personal
  key path into project docs (SR-01).

---

## Code Quality Standards

Follow `templates/code-standards/python.md` (the pipeline, parser, gates, and exporters are Python 3),
and `templates/code-standards/powershell.md` for the hunt-guide examples.

### Project-Specific Standards

- **Verified, not derived.** No indicator ships without a real fetch against a real authoritative
  source (SUCCESS_CRITERIA load-bearing clause). No guessed file/registry/service/DLL names.
- **Recognition-grade altitude.** No file hashes, no version-pinned values as indicators or in any
  export (DR-09/DR-10). Hashes used in verification live only in the verification log. Normalize
  version-specific source outputs to the stable form before they become indicators.
- **Designation is not malware.** 1260H is corporate affiliation, not a malware finding. Never emit
  the STIX `malware` SDO or `malicious-activity` type. Every external artifact carries the
  designation-not-malware and report-don't-block caveats and the AI-assisted/best-effort label.
- **Claim-typed evidence.** Each source is credited only for the claim it proves (DR-02a); a
  host-presence indicator cannot reach VERIFIED on attribution evidence alone (ARCHITECTURE §4a).
- **Never ingest the quarantine.** `background/_quarantine_untrusted_copilot/` is UNTRUSTED; anything
  traceable to it starts as CANDIDATE with no inherited provenance.
- **Read-only, no-install.** Never install or execute any designated-vendor software (SR-02). The
  Playwright tier executes untrusted vendor JS — sandbox it; do not pipe rendered content into the
  master unsanitized.

---

## Branding and Website

Cutaway Security branding is the default. No website component in scope for this project.

---

## Project Content Lives in the Planning Docs

This file holds operating rules. Project-specific content lives in `claude-dev/`:

| Content | Home |
|---------|------|
| Technical constraints (protocols, platform, dependencies) | claude-dev/ARCHITECTURE.md (§13) + claude-dev/REQUIREMENTS.md (IR/AR) |
| Project scope (in / out) | claude-dev/VISION.md (§6) + claude-dev/REQUIREMENTS.md (§0, §11) |
| Testing criteria and environment | claude-dev/REQUIREMENTS.md (§10) + claude-dev/SUCCESS_CRITERIA.md + claude-dev/TEST_ENVIRONMENT.md |
| Document trust levels | claude-dev/AUTHORITY_MAP.md |

---

## Communication Style

- Focus on substance, skip unnecessary praise
- Be direct about problems -- identify specific issues with line numbers
- Question assumptions and challenge problematic approaches
- Ground claims in evidence, not reflexive validation
- For human-facing deliverables (README, the guide, the ETAC PDF), avoid AI writing tells; the
  `humanizer` skill covers this

---

## Documentation Updates Required

| Change Type | Update |
|-------------|--------|
| Architecture or constraint change | claude-dev/ARCHITECTURE.md |
| Phase completion | claude-dev/PLAN.md |
| Session activity / status | claude-dev/RESUME.md + claude-dev/PLAN.md |
| Problem encountered / blocker | claude-dev/PLAN.md (Current Phase: Blockers) |
| Durable decision or lesson | claude-dev/VIBE_HISTORY.md |
| Usage change | README.md |

---

## Session Workflow

Start: read CLAUDE.md, ARCHITECTURE.md, PLAN.md, VIBE_HISTORY.md; state understanding; wait for
confirmation. During: one task at a time, test each change, document blockers in PLAN.md, stop and ask
on persistent issues. End: update PLAN.md and RESUME.md, add lessons to VIBE_HISTORY.md, list blockers,
summarize.
