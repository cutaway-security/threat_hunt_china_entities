# Consolidated Architecture Review (Pass 2) — threat_hunt_china_entities

- Synthesizer: Claude (orchestrator)
- Date: 2026-06-30
- Panel: anthropic (claude-opus-4-8), mistral (mistral-medium-latest), openai (gpt-5.4) — all `ok`
- Scope: ARCHITECTURE.md (primary) + the full planning set + parser as grounding

## Verdict

Unanimous: architecture is **sound and the phasing is now right** (the first-pass over-scope was
fixed). The panel converged on a different, deeper risk than last time: **semantic overclaim** — the
system is "one enthusiastic implementation away from promoting attribution evidence into host-presence
evidence" (openai). The fixes are mostly doc-level reconciliations plus making v0.1 actually real.

## Consensus findings (2+ reviewers)

1. **[ALL] Count gate ≠ fidelity gate.** The parser checks only the 80/108/10 totals; TSC-01/MR-01
   require an automated **full name diff** of all parents + all subsidiaries (+ delisted). A
   mis-merge/mis-split/mis-attribution that preserves totals passes silently. → TSC-01 is **not yet
   met**; "trusted foundation" / "reproducible from parser" is overstated until the name-diff +
   committed expected-name lists + a golden-output regression test exist. *(v0.1 slice — to PLAN.)*
2. **[anthropic CRITICAL] STIX skeleton embeds version-pinned data** (`version: "4.2.1"`,
   `cpe:...:4.2.1:...`) — violates the no-version-pin rule (DR-09/DR-10) in an export. → Wildcard the
   CPE version field, drop the SCO `version`, normalize at the export boundary. ADR it. *Applied.*
3. **[openai CRITICAL] VERIFIED wording is looser than DR-02a.** `verification_pipeline_notes.md`
   reads "VT signer OR official-domain installer = VERIFIED," which would let a host-presence
   indicator (registry key / service / path) be marked VERIFIED on attribution evidence alone. →
   Rewrite so a host-presence claim needs vendor-official support **for that specific indicator
   type**. *Applied.* Deeper fix (adopted): model evidence as **atomic typed claims** (binary-signer,
   installer-filename, ARP-publisher, SDK-DLL-name), each binding a source class to what it proves,
   and assemble indicators from claims — enforces DR-02a in the schema, not just policy.
4. **[anthropic+openai HIGH] "Structurally impossible" describes a future state.** Schema, master,
   gates are all `[planned]`; only the parser exists. → Soften to "designed so that … once schema +
   gates land," and mark planned-vs-implemented in the architecture tables. *Applied.*
5. **[ALL] Secret-path drift.** `verification_pipeline_notes.md` still contains the literal
   `~/.claude/keys/virustotal.key.txt`; ARCH §11 says "user's Claude keys dir." SR-01 forbids verbatim
   personal paths in docs. → Scrub to the `KEYS_DIR` contract. *Applied.*
6. **[openai HIGH + others] STIX indicator_type over-committed.** FR-08 says MUST `anomalous-activity`,
   but ARCH §16 + research call it open pending ETAC. → Soften FR-08 to "non-malware semantics; exact
   `indicator_types` confirmed with ETAC before v0.3 freeze." *Applied.*
7. **[ALL] Playwright executes untrusted vendor/WAF JavaScript** — a trust boundary the docs don't
   name. → Sandbox, pin Chromium (149), never let rendered content flow unsanitized into the master;
   model source **deception** (SEO poisoning, changed manifests), not just outage. *Applied (ARCH §9).*
8. **[ALL] Authority map + consistency matrix + ADRs + single status source** — repeatedly requested.
   → Carried to Phase 9/10 deliverables (MR-04 already requires them).
9. **[openai] TSC-06 test-plan row is stale** ("manual review" vs the criterion's "executed against a
   fixture"). *Applied.* **[openai]** Split internal-readiness from external ETAC acceptance (Gate D /
   BSC-01). *Applied.* **[openai]** TSC-09 could reward shallow wins → add a qualitative constraint.
   *Applied.*
10. **[anthropic LOW]** "65 entities" still appears unqualified in VIBE_HISTORY/reference → label as
    unreconciled secondary count. *Applied.*

## Referee notes (panel wrong/imprecise)

- **mistral CRITICAL #1 (short_alias still extracts "Xiamen") is FALSE.** The trailing-paren fix is in;
  the committed JSON shows `"short_alias": null` for SDIC (anthropic independently verified). mistral
  used stale line numbers and reasoned about the pre-fix code. **Rejected.**
- mistral's "drift or manual edit" inference follows from the same misread. Rejected.
- All three again note "pipeline not implemented" — expected for a pre-implementation init; the valid
  core (count-vs-name gate, overclaim language, claim-typing, STIX contradiction) is adopted; pipeline
  *code* stays the v0.2 slice.

## Applied this pass (doc-level)

STIX version-pin fix (notes + ARCH §8 + ADR note); strict VERIFIED wording + atomic claim-typed
evidence model (new ARCH decision); FR-08 softened; key-path scrubbed; overclaim language honest +
planned-vs-implemented marked; Playwright trust boundary + source-deception threat (ARCH §9); TSC-06
row reconciled, TSC-09 qualitative constraint, internal/external gate split; "65 entities" qualified.

## Carried to PLAN (v0.1/v0.2 implementation — NOT built during init)

- v0.1: committed JSON schema (with claim-typed evidence model); committed expected parent/subsidiary/
  delisted name lists; **name-diff gate** + **golden-output regression test**; parser hardening
  (UTF-8, subsidiary-merge robustness); entities-only master stub with dispositions; authority map +
  ADRs. **TSC-01 / Gate A do not pass until the name-diff exists.**
- v0.2: verification pipeline as code with the atomic-claim evidence layer; tier-leak/re-fetch gates;
  immutable verification log; sandboxed Playwright; per-source integrity cross-checks; seed must
  include ≥1 host-presence indicator stronger than executable-name attribution (TSC-09 qualitative).

## Bottom line

No re-scope needed; the phasing holds. The pass's real value: the **claim-typed evidence model**
(operationalizing DR-02a so attribution can't be promoted to host-presence) and catching the **STIX
version-pin self-contradiction**. v0.1 is honestly *in progress*, not landed — the name-diff gate is
what makes the foundation "trusted." Proceed to Phases 9–11 with these carried into PLAN.
