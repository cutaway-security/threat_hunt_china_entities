# Verification Pipeline Notes (for Requirements §Data/§AR and Architecture — Phases 4 & 7)

The data model's integrity depends on grounding every artifact in an authoritative, citable
source. This is the "verified, not derived" rule made operational. Established and proven live on
2026-06-30; feeds REQUIREMENTS (DR/AR/SR) and ARCHITECTURE (a first-class "Verification Pipeline"
component).

## The problem this solves
A plain HTTP GET / markdown fetch cannot read several vendor download portals: they are
JavaScript-rendered SPAs *and* WAF/bot-blocked (e.g., Hikvision returns HTTP 403 to both `curl`
and the markdown fetcher). The quarantined CoPilot run asserted artifacts (e.g. `HCNetSDK.dll`,
`iVMS-4200.exe`) with no real citation. The pipeline below replaces assertion with grounded
verification, and routes around the blocked portals.

## Tool inventory (this environment)
- `curl`, `jq`, `pdftotext`, `wget` — preinstalled; **bash has direct network egress** (verified:
  GitHub raw 200, NVD API 200).
- VirusTotal API key — resolved via the `KEYS_DIR` contract (`${KEYS_DIR}/virustotal.key.txt`;
  default keys-dir), never committed, never a verbatim personal path in docs (SR-01). Verified working.
- Playwright + Chromium — installed into project `.venv/` (Tier-2 headless rendering for
  JS/WAF-blocked portals). Invoke via `.venv/bin/python` scripts.

## Source stack (tiered) and what each yields

| Tier | Source | Yields | Tool | Provenance strength |
|---|---|---|---|---|
| 1 | **winget-pkgs** (github raw/API, plain text) | official InstallerUrl + filename, InstallerType, ProductCode, SHA256, AppsAndFeaturesEntries (DisplayName/Publisher/UpgradeCode → Uninstall key) | curl+jq | HIGH when InstallerUrl is an official vendor domain |
| 1 | **NVD CPE dictionary** (services.nvd.nist.gov, JSON) | canonical `cpe:2.3:a:vendor:product:version` naming; confirms product/vendor exist; OS marker (e.g. `:windows:`) | curl+jq | HIGH for naming/canonicalization |
| 1 | **Vendor SDK / user-manual PDFs** (direct URL) | DLL names (HCNetSDK, dhnetsdk), service names, install paths from official docs | curl + pdftotext | HIGH (vendor-official) when URL is obtainable |
| 2 | **Vendor SPA portals** (Hikvision/DJI/Dahua) | installer/version strings + direct PDF URLs hidden behind JS | Playwright/Chromium | HIGH if render succeeds; may be WAF/geo-blocked |
| 3 | **VirusTotal** (api/v3/files/{sha256}) | meaningful_name, observed names (incl. installed exe), code-signer (signature_info.signers), signature_verified, signature_product | curl+jq + VT key | VERY HIGH — code-signing cert ties binary to vendor |
| 3 | Reputable third-party (e.g., software catalogs, well-known wikis) | corroboration only | curl | MEDIUM → REPORTED tier |

## Source → confidence-tier mapping (feeds the rubric, decision D2)
- **VERIFIED** — requires **≥2 independent artifact classes with at least one vendor-official source
  for that specific indicator type** (DR-02). A source is credited only for the claim it proves
  (DR-02a): VT signer and an official-domain installer establish *binary provenance and naming* — they
  do **NOT** by themselves verify a registry key, service name, or install path. So a host-presence
  indicator (REGISTRY_KEY/SERVICE_NAME/FILE_PATH/DLL_NAME) reaches VERIFIED only with vendor-official
  support for *that* artifact (SDK/user-manual PDF, ARP entry, etc.), never on attribution alone.
  <!-- AI review 20260630-085540 (openai CRITICAL): prior wording let attribution be promoted to
  host-presence; tightened to per-indicator-type vendor-official support. -->
- **CORROBORATED** — multiple reputable sources agree (e.g., winget + NVD CPE) but no single
  vendor-official confirmation of the exact artifact.
- **REPORTED** — single reputable third-party; needs confirmation. Not shipped to ETAC set.
- **CANDIDATE** — plausible/unsourced (e.g., the quarantined CoPilot values). Backlog only.

## Per-artifact verification workflow
1. Identify product from the 1260H entity (entity → software).
2. NVD CPE: confirm canonical vendor/product naming → seeds STIX `cpe` **with the version field
   wildcarded** (`...:product:*:*:...`); the version-pinned NVD value stays in the verification log only.
3. winget: get official InstallerUrl/filename, ProductCode, AppsAndFeaturesEntries (→ Uninstall
   DisplayName/Publisher), SHA256.
4. VT (on the SHA256): confirm code-signer = designated vendor; capture installed exe name(s).
5. For SDK DLLs / services / install paths not in winget: fetch the vendor SDK/user-manual PDF
   (direct URL; use Playwright to locate it if the portal is JS/WAF-blocked) → pdftotext → extract.
6. Record EVERY artifact with: value, indicator_type, source_url, source_tier, date_verified,
   confidence. No artifact without a citation. Corroborate across ≥2 classes for VERIFIED.

## Proven examples (live, 2026-06-30)
- **Tencent WeChat** — winget InstallerUrl `https://dldir1v6.qq.com/weixin/Windows/WeChatSetup.exe`
  (official Tencent CDN); VT: signed by **Tencent Technology (Shenzhen) Company Limited**,
  signature_product 微信电脑版, observed installed name `wechat.exe`. → VERIFIED candidate set.
- **NVD CPE** confirmed: `cpe:2.3:a:hikvision:ivms-4200:2.6.2.6`, `cpe:2.3:a:tp-link:
  omada_software_controller:4.4.4:*:*:*:*:windows`, `cpe:2.3:a:huawei:hisuite:*`,
  `cpe:2.3:o:dahuasecurity:smartpss_firmware:1.16.1`.
- **winget coverage**: Tencent (WeChat/QQ/TencentMeeting/VooVMeeting/WeCom…), DJI (DJIAssistant2,
  DJITerra), Huawei (HiSuite, Welink…), 360 (360SE/360Zip/360Ent…), Dahua (SmartPSSLite).

## Known gaps (route to Tier 2/3 + SDK PDFs)
- **Hikvision** — absent from winget; portal WAF-blocked to curl BUT **now reachable via Playwright**
  (proven 2026-06-30: iVMS-4200 software page rendered HTTP 200, vendor version `V3.14.0.6_E`).
  Client-tool artifacts (iVMS-4200, SADP) are now sourceable from the rendered portal; the SDK DLL
  `HCNetSDK.dll` still needs the Device Network SDK manual PDF (locate its direct URL via Playwright)
  and/or VT lookups of known Hikvision-signed binaries.
- **Dahua NetSDK** (`dhnetsdk`) — DEPP SDK portal is partner-gated; rely on the NetSDK programmer
  manual PDF if a direct URL is obtainable, else CANDIDATE.
- **SDK DLLs generally** — highest-effort class; VT (signer) + SDK PDF are the verification path.

## Altitude & VirusTotal bounds (anti-creep, Don 2026-06-30)
- This is recognition-grade analysis: indicators are **named, version-independent** artifacts
  (executable/DLL/folder/service/registry-key names). **No hashes, no version-pinned values** as
  indicators or in exports (DR-09); a hash used for a VT lookup stays in the verification log only.
- Normalize version-specific source outputs to the stable form before they become indicators
  (`WeChatSetup_3.9.12.57_x64.exe` → `wechat.exe`; `iVMS-4200 V3.14.0.6_E` → `iVMS-4200.exe`) (DR-10).
- **VirusTotal is point-in-time, not an enumerator.** Use it to (a) confirm product naming,
  (b) attribute a binary to its vendor via code-signer, and (c) detect vendor SDK/libraries embedded
  in other products. A VT hit is one instance; its absence proves nothing — so VT supports
  CORROBORATED/attribution, never coverage, and never a build-specific or hash indicator.

## Implication for ETAC deliverable
The first ETAC hand-off is METHOD + a small VERIFIED seed (consumer apps verifiable via
winget+VT+NVD now), growing as the SDK/portal-blocked vendors are worked through. This is honest
expectation-setting, not a limitation of rigor.
