# STIX 2.1 Modeling Notes (for Architecture — Phase 7)

Source: research vector 3, verified against OASIS STIX 2.1 OS [3], the OASIS identity JSON
schema [3a], and TAXII 2.1 [3b]. See `20260630_1260h_software_threat_hunt_RESEARCH.md` §5.

## Decisions to carry into ARCHITECTURE.md
- Model designated-vendor software presence as: `identity` (vendor) + `software` SCO + `indicator`
  (file/registry pattern) + `relationship` (`related-to`), wrapped in a `bundle`.
- Software SCO required: `type`/`id`/`name`; embed `vendor`, `swid`, and `cpe` **with the version
  field WILDCARDED** (`cpe:2.3:a:vendor:product:*:*:*:*:*:*:*:*`). **Do NOT** emit the SCO `version`
  property and do NOT emit a version-pinned `cpe` — that would put a version-pinned value in an export,
  violating the no-version-pin altitude rule (DR-09/DR-10). Normalize NVD CPEs to wildcard-version at
  the export boundary. <!-- AI review 20260630-085540 (anthropic CRITICAL): the prior skeleton embedded
  version 4.2.1 + a version-pinned cpe, contradicting DR-09/DR-10. -->
- Identity SDO: only `name` required in 2.1; set `identity_class:organization`.
- Indicator: `pattern_type:stix`; non-malware semantics (NOT `malicious-activity`, NOT the `malware`
  SDO). `indicator_types` value (`anomalous-activity` vs `benign`) is **pending ETAC confirmation**
  before the v0.3 freeze (FR-08, open question §16.1).
- Distribution: signed bundle FILES for ETAC; TAXII 2.1 server NOT required for v1 (TAXII wraps
  content in an *envelope* in 2.1).
- Embed SBOM-grade identifiers (CPE/SWID/PURL) for SBOM interoperability.

## Verified illustrative bundle skeleton (verified properties only)
```json
{
  "type": "bundle",
  "id": "bundle--a1b2c3d4-0000-4000-8000-000000000001",
  "objects": [
    {
      "type": "identity",
      "spec_version": "2.1",
      "id": "identity--11111111-0000-4000-8000-000000000001",
      "created": "2026-06-30T00:00:00.000Z",
      "modified": "2026-06-30T00:00:00.000Z",
      "name": "Designated Vendor Y, LLC",
      "identity_class": "organization"
    },
    {
      "type": "software",
      "id": "software--22222222-0000-5000-8000-000000000002",
      "name": "ProductX",
      "vendor": "Designated Vendor Y, LLC",
      "cpe": "cpe:2.3:a:vendory:productx:*:*:*:*:*:*:*:*"
    },
    {
      "type": "indicator",
      "spec_version": "2.1",
      "id": "indicator--33333333-0000-4000-8000-000000000003",
      "created": "2026-06-30T00:00:00.000Z",
      "modified": "2026-06-30T00:00:00.000Z",
      "name": "Designated-vendor software file present",
      "indicator_types": ["anomalous-activity"],
      "pattern": "[file:name = 'productx.exe']",
      "pattern_type": "stix",
      "valid_from": "2026-06-30T00:00:00.000Z"
    },
    {
      "type": "relationship",
      "spec_version": "2.1",
      "id": "relationship--44444444-0000-4000-8000-000000000004",
      "created": "2026-06-30T00:00:00.000Z",
      "modified": "2026-06-30T00:00:00.000Z",
      "relationship_type": "related-to",
      "source_ref": "identity--11111111-0000-4000-8000-000000000001",
      "target_ref": "software--22222222-0000-5000-8000-000000000002"
    }
  ]
}
```
Note: Software SCO has no `created`/`modified`/`spec_version` (it is an SCO). Registry-pattern
form: `[windows-registry-key:key = 'HKEY_LOCAL_MACHINE\\SOFTWARE\\VendorY']`.
