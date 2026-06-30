# Deep Research Survey — Threat Hunting for Section 1260H Designated-Vendor Software

Project: threat_hunt_china_entities
Date: 2026-06-30
Status: Phase 2 deliverable. Methodology + state-of-the-art survey. NOT the indicator dataset
(that is a later verification slice). Best-effort, AI-assisted; citation-audited (see §1.3).

---

## §1 Scope and Methodology

### 1.1 Question
What is the defensible state of the art for (a) the meaning and limits of a DoD Section 1260H
designation, (b) hunting the *presence* of specific vendor software on enterprise Windows hosts,
(c) representing "designated-vendor software is present" in shareable CTI formats without
mislabeling it as malware, and (d) the feasibility of sourcing *verified* host artifacts for the
high-signal vendors? These four vectors shape the project's requirements and architecture.

### 1.2 Method
Four parallel research vectors, each executed under a strict no-fabrication contract: every
factual claim requires a fetched-and-cited URL; uncitable claims are marked "do not use";
no invented file/registry/service names. Government primary sources preferred for policy;
Microsoft Learn for Windows mechanisms; OASIS for STIX; vendor portals for artifact feasibility.

### 1.3 Citation audit
Five load-bearing citations were independently re-fetched by the lead author. Four verified
verbatim (MS Uninstall-key values; MoFo "not sanctions" sentence; Huawei HiSuite V14.0.0.370;
STIX software SCO + indicator-type-ov). **One correction:** the "65 new entities" count and the
"June 30 2027" procurement date are **not** in the Morrison Foerster source — MoFo supports
"over twenty new parent-level designations" and only the June 30 2026 §805 date. The 65 count is
attributed to WilmerHale [1]; the 2027 date requires WilmerHale/primary, not MoFo [2]. The list's
**date (June 8 2026)** and **codification (10 U.S.C. § 113, note)** are confirmed directly from
the primary PDF held locally in `background/`.

### 1.4 Prior-art / duplication check (project gate)
No existing publication maps the 1260H list to host-based software-presence hunting indicators.
The nearest government work — CISA AA25-239a, "Countering Chinese State-Sponsored Actors" [13] —
addresses PRC **APT compromise TTPs**, a different question from *presence/exposure of
designated-vendor commercial software*. The Energy Threat Analysis Center (ETAC) is a DOE/CESER
public-private body [14]; no equivalent 1260H software-hunt product was found. **Conclusion: the
niche is unfilled and complementary, not duplicative — the project proceeds.**

---

## §2 Definitions and Prior Art

- **Section 1260H list** — DoD's at-least-annual identification of "Chinese military companies"
  operating in the U.S. (see §3). An **affiliation/provenance flag**, not a malware list.
- **Software-presence hunting** — inventory-discovery: proving a named product is installed on a
  host via authoritative, version-stable artifacts (see §4). Distinct from compromise hunting.
- **Designated-vendor software exposure indicator** — our coined term: an artifact (file, path,
  registry key, service, DLL) whose presence shows a designated vendor's commercial software is
  installed/running. Policy/supply-chain relevant; not inherently malicious.
- Prior art: CISA China advisories [13] (APT TTPs); STIX 2.1 [3] / SBOM standards [11] (software
  identity); the (now-quarantined) prior CoPilot run, whose failure modes — uncited indicators
  and all-`UNKNOWN` attribution — directly motivate this project's data model.

---

## §3 §1260H Context and What a Designation Means

### 3.1 Statutory basis and legal effect
Section 1260H was enacted in the William M. (Mac) Thornberry NDAA FY2021 (Pub. L. 116-283;
codified at 10 U.S.C. § 113, note — confirmed from the primary PDF). It directs the Secretary of
Defense to identify and publish, at least annually, entities that are "Chinese military
companies" operating directly or indirectly in the U.S. [1][2]. An entity qualifies if it engages
in U.S. commercial activity **and** is either owned/controlled by or acting on behalf of China's
military (PLA/CMC) **or** is a "military-civil fusion (MCF) contributor" to China's defense
industrial base [1][3].

Crucially, a 1260H designation is **not a sanctions action and does not, by itself, prohibit
transactions**. Morrison Foerster, verbatim: *"A designation on the 1260H List does not, by
itself, impose sanctions or prohibit commercial transactions with the designated entity"* [2].
The list began as a "name and shame" tool [1]; its enforcement teeth come from a **separate**
statute — **FY2024 NDAA Section 805** — which bars the **Department of Defense** (not the private
sector at large) from contracting with listed entities effective **June 30 2026**, with a further
procurement restriction reported as effective **June 30 2027** [1] (the 2027 date per WilmerHale;
MoFo's footnote states only the 2026 date [2]). The direct legal consequence is therefore a
**federal-procurement restriction on DoD**, plus secondary effects — not an OFAC blocking action,
import ban, or prohibition on U.S. persons doing business with the company.

### 3.2 Update history
Initial list (~47 entities; secondary sources split on a 2021 vs October 2022 inaugural
publication — **unresolved**) [4][5]; 2022 (+13); January 2024 (+16, −3); January 2025 → ~76 total
(added Tencent, CATL, SenseTime, Autel) [5]; a near-identical February 2026 update reportedly
published then withdrawn [1]. The **current version is dated June 8 2026** (confirmed from the
primary PDF), described by WilmerHale as adding **65 entities (17 new parent-level + 48
subsidiaries)** [1] and by MoFo as "over twenty new parent-level designations" [2] — a minor
secondary-source discrepancy worth noting. This project's own verified parse of the June 8 2026
PDF yields **80 designated parents + 108 subsidiaries + 10 delisted** (see `data/source_extraction/`).

### 3.3 Designation ≠ compromised software
A listing speaks to **corporate affiliation with the MCF apparatus, not to whether a vendor's
commercial software is malware** [3]. The litigation record makes this concrete: in *DJI v. DoD*,
the court upheld DJI's listing on **affiliation grounds** (MCF contributor; a civilian
"National Enterprise Technology Center" designation tied to military-industrial planning), not on
any finding that DJI products are compromised [8]. Coverage of the 2026 additions (e.g., Alibaba,
Baidu) likewise frames inclusion around MCF ties, not product-security findings [9]. **Defensible
framing for this project: presence on 1260H flags vendor provenance and a policy/procurement
risk — it is not a technical determination that the software is malicious.**

### 3.4 Overlapping regimes that DO restrict equipment/software
Unlike 1260H, several regimes directly restrict some of these vendors, which is why cataloging
their software footprint is operationally relevant:
- **NDAA Section 889 / FCC Covered List** — names Huawei, ZTE, Hytera, **Hikvision, Dahua** [10][11];
  FCC bars new equipment authorizations and §889 bars federal agencies/contractors from using the
  gear. DJI reportedly added to the Covered List Dec 2025 via FY2025 NDAA §1709 — *flag: snippet
  only* [10].
- **Treasury NS-CMIC (EO 14032)** — bars U.S. persons trading listed firms' securities; Huawei,
  Hikvision, Dahua reported listed — *flag: snippet only* [12].
- **Commerce Entity List** — export-licensing restrictions; Huawei, Hikvision/Dahua reported
  listed — *flag: snippet only* [12].

So Hikvision, Dahua, Huawei, and ZTE sit on multiple equipment/software-restricting lists, and
DJI faces procurement and (reported) Covered-List restrictions.

---

## §4 Hunting Software Presence on Windows: Methods and Reliability

Proving a vendor's software is *installed* is an inventory problem, not compromise hunting. High
confidence comes from artifacts that are **authoritative** (the OS/installer wrote them) and
**stable** (they do not churn across versions).

### 4.1 Host-based artifact classes (ranked by reliability)
- **(a) Uninstall registry keys — gold standard.** Windows Installer writes the Add/Remove
  Programs record under `HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall` (subkey =
  product-code GUID), with documented values `DisplayName`, `DisplayVersion`, `Publisher`,
  `InstallLocation`, `InstallDate`, `UninstallString` [15] (re-verified). 32-bit apps on 64-bit
  Windows are redirected to `…\WOW6432Node\…\Uninstall` [16]; per-user installs to
  `HKCU\…\Uninstall`. Enumerate all three. Stability high; FP risk low (leftover keys aside).
  `DisplayName`/`Publisher` are the most reliable presence signal.
- **(b) Install folders** under `%ProgramFiles%` / `%ProgramFiles(x86)%` (from `InstallLocation`
  [15]). Stable across minor versions; moderate FP risk (relocatable).
- **(c) Windows services** — vendor-unique short/display names. High stability, low FP.
- **(d) Embedded/loaded DLLs** — vendor SDK shipped inside a third-party app; detects components
  with no Uninstall entry, but higher FP (same DLL ships in unrelated products).
- **(e) Running process names** — proves *running now*, not installed; transient and renameable.
  Lowest confidence; corroborate with disk/registry evidence.
- **(f) App Paths / Run keys** [17][18] — useful secondary corroboration; optional for vendors,
  so absence does not disprove installation.

### 4.2 Enumeration method and the key pitfall
**Do not use `Win32_Product` (WMI/CIM):** querying it forces the MSI provider to run a
consistency check that **verifies/repairs every installed package**, is slow, and emits
MsiInstaller "reconfigured the product" events for each app; Microsoft recommends avoiding it [19].
Preferred: read the Uninstall keys directly with `Get-ItemProperty`/`Get-ChildItem` [20];
`Get-Package` (provider-dependent) [21]; `Get-Service`, `Get-Process`, `Get-ChildItem` for
service/process/file evidence.

**Verified PowerShell — enumerate installed software from the Uninstall keys** (seeds the hunt
guide; syntax per [20], value names per [15]):
```powershell
$paths = @(
  'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
  'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
  'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*'
)
Get-ItemProperty -Path $paths -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName } |
    Select-Object DisplayName, DisplayVersion, Publisher, InstallLocation, InstallDate |
    Sort-Object DisplayName
```

### 4.3 Low-false-positive indicator engineering
Per Bianco's Pyramid of Pain, file **hashes** are trivially changed (any recompile/version bump
invalidates them) — avoid as a primary presence signal [22]; same for version-specific strings.
Avoid **generic** names (`setup.exe`, `service.exe`, common SDK DLLs) — they collide across
unrelated software. The durable signal is the **vendor-unique identifier**: `Publisher`/
`DisplayName`, a vendor-specific service short name, a distinctive install folder, or a uniquely
named proprietary DLL. Match on those and **corroborate across two artifact classes**; treat
single-class hits as lower confidence. This directly motivates the project's confidence rubric.

### 4.4 Operational caveat — report, don't auto-block
This is exposure/inventory discovery. Much target software (WeChat, Qihoo 360, DJI tools) is
legitimate, user-installed software flagged for **policy/supply-chain** reasons, not because it is
malicious. Detections must **report and route for human review, not auto-block/auto-remediate.**
Surface full provenance (host, artifact class, exact path/key) and let a human adjudicate.

---

## §5 Representing Designated-Vendor Software Presence in STIX 2.1 (Not Malware)

The modeling problem is attribution without mislabeling. STIX 2.1 [3] handles it with a Software
SCO + Identity SDO + optional Indicator SDOs + Relationship SROs in a Bundle.

- **Software (SCO, §6.14)** — required `type`/`id`/`name`; optional `cpe`, `swid`, `vendor`,
  `version` (re-verified). Records the observed presence and self-attributes via `vendor`. No
  malware semantics.
- **Identity (SDO, §4.5)** — only `name` required in 2.1 (`identity_class` is **optional** in 2.1,
  contrary to 2.0; confirmed against the OASIS JSON schema [3a]); use `identity_class:organization`
  for the vendor.
- **Indicator (SDO, §4.7) + patterning (§9)** — `pattern_type:stix`; patterns like
  `[file:name = 'product.exe']` or `[windows-registry-key:key = 'HKEY_LOCAL_MACHINE\\SOFTWARE\\VendorY']`.
  Carries the *detection logic*, separate from the Software SCO's *observed fact*.
- **Relationship (SRO, §5.1.2)** — in 2.1 refs may point at SDOs or SCOs; link vendor Identity to
  Software SCO with the generic `related-to` (no predefined identity→software term).

**Avoid the `malware` SDO and the `malicious-activity` indicator type** — misclassifying lawful
commercial software could trigger automated blocking downstream. The `indicator-type-ov` (§10.10)
values are `anomalous-activity, anonymization, attribution, benign, compromised,
malicious-activity, unknown` (both `malicious-activity` and `anomalous-activity` confirmed present
[3]). Defensible choice: **`anomalous-activity`** (policy-relevant, not malicious) or
`benign`/`unknown`, plus a clear `description`.

**Distribution:** a `bundle` (§8) of Identity + Software + Indicator(s) + Relationship(s) is a
complete exchange artifact; a **TAXII 2.1 server is not required** for ETAC — a signed bundle file
suffices (TAXII 2.1 wraps content in an *envelope*, a change from 2.0 [3b]). **Adjacent
standards:** SBOM formats (SPDX [11], CycloneDX) model software identity well; embed **CPE/SWID/
PURL** identifiers inside the STIX Software SCO so the assertion is unambiguous and
SBOM-interoperable. Recommendation: STIX as the sharing wrapper (native Identity attribution +
Relationships + Indicators), with SBOM-grade identifiers embedded.

Illustrative verified-properties-only bundle skeleton (Identity + Software SCO + file-name
Indicator + Relationship) is retained in the project's STIX design notes for the architecture phase.

---

## §6 Source Availability for Verified Vendor Artifacts (Feasibility)

Assessment of whether authoritative citable sources exist for Windows host artifacts per
high-signal vendor. **Only two artifact facts are verified so far**; the rest have a confirmed
authoritative source but require the dedicated verification slice (several vendor pages are
JavaScript-rendered and need headless rendering or SDK-manual/winget fallbacks).

| Vendor | Official Windows software? | Source quality | Easy/Hard |
|---|---|---|---|
| Qihoo 360 | Yes (360totalsecurity.com) | MEDIUM | Moderate |
| Hikvision | Yes (support portal + SDK) | HIGH | Easy |
| Dahua | Yes (support + DEPP SDK, gated) | MEDIUM-HIGH | Moderate |
| Tencent | Yes (Meeting/WeChat/QQ) | MEDIUM-HIGH | Easy (Store/winget) |
| Huawei | Yes (HiSuite, verified) | HIGH | Easy |
| TP-Link | Yes (Omada) | HIGH (Omada)/LOW (Tapo) | Easy |
| DJI | Yes (Assistant 2) | HIGH | Easy-Moderate |

- **Verified now (HIGH):** Huawei **HiSuite V14.0.0.370**, EXE, 62.3M, Win 7/8.1/10/11 (re-verified
  by lead author) [S-Huawei]; 360 ships online + offline installers [S-360].
- **Source-exists but artifacts NOT yet verified** (need slice; many JS-rendered): all Hikvision
  (incl. the claimed `HCNetSDK.dll`); all Dahua (incl. NetSDK / `dhnetsdk`); Tencent installer
  filenames; DJI Assistant 2 filename/version; Omada installer/service name. **None of these
  should be treated as confirmed** — notably, this is the same set the quarantined CoPilot bundle
  asserted without proof.
- **Best source classes, ranked:** (1) vendor SDK developer docs/manuals (DLL/API names);
  (2) official user-manual PDFs (install paths, service names); (3) vendor download portals
  (installer + version; many JS-rendered); (4) winget / Microsoft Store manifests (consumer apps).

---

## §7 Implications for This Project

1. **Framing (from §3):** every artifact and the guide must state designation = affiliation flag,
   NOT malware; cite the "not sanctions" point and *DJI v. DoD*; date-stamp to the June 8 2026
   list. The overlapping 889/FCC/NS-CMIC regimes justify prioritizing Hikvision, Dahua, Huawei,
   DJI, TP-Link.
2. **Data model (from §4.3):** the confidence rubric must encode artifact-class reliability
   (Uninstall key > install folder/service > DLL > process) and require corroboration across two
   classes for the top tier. Hashes and version strings are excluded by design.
3. **Hunt guidance (from §4.2/4.4):** PowerShell examples build on direct Uninstall-key reads
   (never `Win32_Product`); every example carries the report-don't-block caveat.
4. **Distribution (from §5):** STIX 2.1 as wrapper with `anomalous-activity` indicators + embedded
   CPE/SWID; bundle files for ETAC (no TAXII server needed for v1).
5. **Sequencing (from §6):** per-vendor artifact verification is a real, non-trivial slice needing
   headless rendering / SDK manuals / winget — confirming the decision NOT to fold it into this
   survey. Start with the Easy/HIGH vendors (Hikvision, Huawei, TP-Link, DJI, Tencent).

---

## §8 Open Questions the Literature Does Not Resolve

1. Inaugural 1260H date (2021 vs Oct 2022) and exact running totals — reconcile against primary
   DoD releases (which 403'd the fetcher; re-verify before publication).
2. Exact current membership on NS-CMIC / Entity List / FCC Covered List for each vendor — snippet
   level only; verify against OFAC/BIS/FCC primaries before relying on it.
3. Whether ETAC has unpublished/internal 1260H work — the dedup check covers public sources only;
   confirm with the ETAC contact.
4. The right STIX `indicator_types` value (`anomalous-activity` vs `benign`) — finalize in
   architecture; may warrant a short note to ETAC on their ingestion preference.
5. For JS-rendered vendor portals, the sanctioned method to capture artifact strings
   (headless browser vs SDK-manual PDFs vs winget manifests) — resolve in the verification slice.

---

## References

1. WilmerHale, "Pentagon Adds 65 New Entities to the 1260H List" (fetched) — https://www.wilmerhale.com/en/insights/client-alerts/20260611-pentagon-adds-65-new-entities-to-the-1260h-list-of-chinese-military-companies
2. Morrison Foerster, "DoD Expands the Section 1260H List" (fetched, re-verified) — https://www.mofo.com/resources/insights/260626-dod-expands-the-section-1260h-chinese-military-companies-list
3. STIX 2.1, OASIS Standard (re-verified) — https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html
3a. OASIS cti-stix2 JSON schema, identity (required: name) — https://github.com/oasis-open/cti-stix2-json-schemas/blob/master/schemas/sdos/identity.json
3b. TAXII 2.1, OASIS Standard — https://docs.oasis-open.org/cti/taxii/v2.1/os/taxii-v2.1-os.html
4. Akin Gump, "DoD Updates Section 1260H List" (403 to fetcher) — https://www.akingump.com/en/insights/alerts/dod-updates-section-1260h-list-of-chinese-military-companies-operating-directly-or-indirectly-in-the-united-states
5. Dechert, "DoD's List of 'Chinese Military Companies'" — https://www.dechert.com/knowledge/onpoint/2024/2/dod-s-list-of--chinese-military-companies---what-s-new-and-what-.html
6. DoD official list PDF, June 8 2026 (primary; 403 to fetcher; held locally) — https://media.defense.gov/2026/Jun/08/2003945537/-1/-1/1/ENTITIES-IDENTIFIED-AS-CHINESE-MILITARY-COMPANIES-OPERATING-IN-THE-UNITED-STATES-IN-ACCORDANCE-WITH-SECTION-1260H.PDF
7. DoD/War Department release (primary; 403) — https://www.war.gov/News/Releases/Release/Article/4511232/
8. DroneXL, DJI v. DoD ruling (secondary) — https://dronexl.co/2025/09/26/dji-loses-pentagon-lawsuit/
9. Foreign Policy, Alibaba/Baidu on 1260H (secondary) — https://foreignpolicy.com/2026/06/22/china-military-civil-fusion-pentagon-blacklist-alibaba-baidu/
10. CRS LSB10895, FCC rules (403) — https://www.congress.gov/crs-product/LSB10895
11. O'Melveny, FCC bans new licenses (fetched) — https://www.omm.com/insights/alerts-publications/fcc-bans-new-licenses-for-the-import-and-use-of-certain-chinese-telecommunications-and-video-surveillance-equipment/
12. OFAC NS-CMIC / EO 14032 overview (secondary) — https://modeldiplomat.com/learn/glossary/ns-cmic-list
13. CISA AA25-239a, Countering Chinese State-Sponsored Actors — https://www.cisa.gov/news-events/cybersecurity-advisories/aa25-239a
14. DOE CESER, Energy Threat Analysis Center — https://www.energy.gov/ceser/energy-threat-analysis-center-0
15. MS Learn, Uninstall Registry Key properties (re-verified) — https://learn.microsoft.com/en-us/windows/win32/msi/uninstall-registry-key
16. MS Learn, WOW6432Node registry redirection — https://learn.microsoft.com/en-us/troubleshoot/windows-client/application-management/wow6432node-registry-key-present-32-bit-machine
17. MS Learn, Application Registration / App Paths — https://learn.microsoft.com/en-us/windows/win32/shell/app-registration
18. MS Learn, Run and RunOnce Registry Keys — https://learn.microsoft.com/en-us/windows/win32/setupapi/run-and-runonce-registry-keys
19. MS Learn, Win32_Product reconfiguration (KB974524) — https://learn.microsoft.com/en-us/troubleshoot/windows-server/admin-development/windows-installer-reconfigured-all-applications
20. MS Learn, Get-ItemProperty — https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-itemproperty
21. MS Learn, Get-Package — https://learn.microsoft.com/en-us/powershell/module/packagemanagement/get-package
22. David J. Bianco, "The Pyramid of Pain" — http://detect-respond.blogspot.com/2013/03/the-pyramid-of-pain.html
S-Huawei. Huawei HiSuite support page (re-verified V14.0.0.370) — https://consumer.huawei.com/en/support/hisuite/
S-360. 360 Total Security download (installer existence) — https://www.360totalsecurity.com/en/download-free-antivirus/

### Source-availability endpoints for the verification slice (not yet artifact-verified)
- Hikvision SDK portal — https://www.hikvision.com/en/support/download/sdk/
- Dahua download center — https://www.dahuasecurity.com/support/downloadCenter ; DEPP SDK — https://depp.dahuasecurity.com/integration/guide/download/sdk
- DJI Assistant 2 hub — https://www.dji.com/downloads/softwares/assistant-dji-2
- Tencent Meeting — https://meeting.tencent.com/download-center.html ; WeChat — https://www.wechat.com/en
- TP-Link Omada — https://support.omadanetworks.com/us/product/omada-software-controller/
