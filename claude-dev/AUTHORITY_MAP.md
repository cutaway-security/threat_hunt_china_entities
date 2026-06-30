# AUTHORITY MAP — threat_hunt_china_entities

Which artifacts are authoritative, which are historical, which are untrusted, and which are generated.
Prevents scripts or humans from blurring trust levels (e.g., ingesting quarantined "leads" as data).

| Path | Role | Trust | Hand-authored / generated | Ingest as data? | Export source? |
|---|---|---|---|---|---|
| `background/ENTITIES-...-SECTION-1260H.PDF` | Authoritative entity source | TRUSTED (primary) | source | yes (via parser) | n/a |
| `background/original_report_url.txt` | Source provenance | TRUSTED | source | reference only | no |
| `data/source_extraction/1260h_pdftotext_layout.txt` | Parser input | TRUSTED (derived from PDF) | generated (`pdftotext -layout`) | yes (parser only) | no |
| `data/source_extraction/parse_1260h.py` | Entity extractor | TRUSTED (code) | hand-authored | n/a | n/a |
| `data/source_extraction/entities_1260h.json` | Entity correlation | COUNT-VERIFIED (name-diff pending) | generated (parser) | yes | feeds master |
| `data/schema/` `data/master/` `data/backlog/` `data/logs/` | Schema, master, backlog, verification log | TRUSTED once built | generated/code | master only | master is the only export source |
| `claude-dev/*.md` (VISION, REQUIREMENTS, SUCCESS_CRITERIA, ARCHITECTURE, DISCOVERY_NOTES, PLAN, RESUME, VIBE_HISTORY, TEST_ENVIRONMENT, AUTHORITY_MAP, ADRS, verification/STIX notes) | Canonical planning docs | TRUSTED (planning) | hand-authored | no (not data) | no |
| `claude-dev/<date>_..._RESEARCH.md` | Research survey | TRUSTED (cited) | hand-authored | no | no |
| `claude-dev/.ai-reviews/**` | Multi-AI review record | HISTORICAL | generated | no | no |
| `background/_quarantine_untrusted_copilot/**` | Prior corrupted run | **UNTRUSTED** | historical | **NO — leads only; anything traced here starts CANDIDATE with no inherited provenance** | no |

Rules:
- The **JSON master is the only export source**. Markdown/STIX/CSV/YAML are generated from it.
- The verification pipeline MUST NOT recursively discover/ingest `background/` or the quarantine; it
  reads only explicit, trusted inputs.
- Anything traceable to the quarantine enters as CANDIDATE in the backlog namespace, never shipped.
