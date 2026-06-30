# Architecture Decision Records — threat_hunt_china_entities

Irreversible or load-bearing decisions, each with context, decision, and consequences. Referenced
from ARCHITECTURE.md. Newest considerations appended; do not silently reverse an ADR.

## ADR-001 — Nested JSON master over relational/CSV
- **Context:** the prior CoPilot run used separate CSVs and produced an attribution file mapping every
  indicator to `UNKNOWN/UNKNOWN`.
- **Decision:** one nested JSON document, entity → software → indicator; delisted + backlog alongside.
- **Consequences:** orphaned attribution is structurally impossible; one schema, one diffable source,
  one export source. Cost: large single file, mitigated by tool-only edits and schema validation.

## ADR-002 — Master-and-exports (generated projections)
- **Context:** hand-authored summaries drifted and burned the prior run.
- **Decision:** Markdown/STIX/CSV/YAML are generated from the master; none hand-maintained.
- **Consequences:** provenance/tier filtering enforced once in the exporter; a generator bug is caught
  by round-trip/validation gates rather than silently shipping.

## ADR-003 — Shipped/backlog structural separation
- **Context:** policy alone cannot guarantee CANDIDATE values never ship.
- **Decision:** REPORTED/CANDIDATE live in a separate namespace; a tier-leak gate plus the namespace
  split (defense in depth) keep them out of every export.
- **Consequences:** an export bug cannot leak low-tier values; quarantine-traceable values start CANDIDATE.

## ADR-004 — Non-malware STIX semantics
- **Context:** a 1260H designation is corporate affiliation, not a malware finding (*DJI v. DoD*);
  mislabeling lawful software could trigger downstream auto-blocking.
- **Decision:** STIX `software`+`identity`+`indicator`+`relationship`, never `malware`/`malicious-activity`;
  CPE version wildcarded, SCO `version` omitted; `indicator_types` confirmed with ETAC before v0.3.
- **Consequences:** safe for consumers to ingest; no version-pin enters the export.

## ADR-005 — No-install verification policy
- **Context:** notice-only research; running PRC surveillance/endpoint software in the environment is
  unacceptable.
- **Decision:** the pipeline is read-only against external sources and never installs/executes target
  software. A lab-VM ground-truth install is a future, user/ETAC-led option only.
- **Consequences:** some host artifacts (service names, uninstall keys) may stay unverifiable from
  public sources; those remain CANDIDATE rather than being guessed.

## ADR-006 — Atomic claim-typed evidence model
- **Context:** DR-02a ("each source proves only its claim type") is only as strong as its enforcement;
  a flat record lets attribution be promoted to host-presence.
- **Decision:** indicators are assembled from typed claim objects (binary_signer, installer_filename,
  arp_publisher, sdk_dll_name, service_name, install_path, registry_key, product_naming), each bound to
  its source class; assembly rules forbid unsupported promotions; the schema enforces it.
- **Consequences:** a host-presence indicator cannot reach VERIFIED on attribution alone; the
  verification log is self-describing for ETAC. Cost: more schema complexity (accepted).

## ADR-007 — Recognition-grade altitude (no hashes, no version pins)
- **Context:** hashes/version strings are point-in-time and unstable (Pyramid of Pain); they identify
  one instance and miss the rest.
- **Decision:** indicators are named, version-independent artifacts; no hashes or version-pinned values
  as indicators or in exports; a verification hash lives only in the log; normalize version-specific
  source outputs to the stable form.
- **Consequences:** durable across vendor/list updates; higher false-positive rate by design (mitigated
  by two-class corroboration and report-don't-block). A forensic IOC effort is explicitly out of scope.
