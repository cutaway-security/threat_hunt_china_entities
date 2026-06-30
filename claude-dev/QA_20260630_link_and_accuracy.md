# QA pass — link liveness + accuracy (2026-06-30)

Pre-share quality gate on the Layer-2 catalog. Tools: `data/check_links.py` (automated liveness) and
three independent re-verification agents over all 52 verified/reported software entries.

## Link liveness

44 unique source URLs checked (read-only HEAD/ranged-GET): **41 live (200), 3 blocked (403), 0 dead.**
The earlier Robosense dead link (caught in an earlier spot-check) is fixed and now 200.

The 3 "blocked" are WAF/bot 403s, not dead pages, and none is load-bearing:
- `media.defense.gov` 1260H PDF — the authoritative source (held locally); 403s bots.
- `apps.microsoft.com` Store listing (China Telecom eCloud Computer, *reported* tier) — Store 403s HEAD.
- `software.informer` Phenix driver (*candidate* tier) — weak third-party aggregator; candidate only.

## Accuracy (independent re-verification of 52 verified/reported entries)

**Result: the catalog is accurate.** No fabricated vendors or products; tier assignments are correct
(verified = vendor-official source, reported = third-party). Corrections applied:

| Finding | Action |
|---|---|
| **Knownsec / ZoomEye-python** is a cross-platform **pip CLI**, not a standalone Windows installer | Category clarified ("runs on Windows; NOT a standalone Windows installer") |
| **Unitree / `unilidar_sdk`** GitHub repo is the **Linux/ROS** L1 SDK, not Windows | Entry **removed** (Unitree keeps the Windows viewer "Unilidar 2"); product count 60 -> 59 |
| **Hikvision / HikCentral Professional** cited URL pointed to an **iVMS-4200** page (wrong product) | Source URL corrected to the Hikvision software portal; product is genuine |
| **Geosun** (4 tools) — vendor confirms the products but pages don't *explicitly* state Windows | "Windows implied, OS not stated" caveat added to each |

Notes (not errors): several vendor pages are JavaScript-rendered (Hikvision, DJI, some Tencent,
Quectel, China Telecom) and were confirmed via search rather than direct fetch; the products are
well-documented and the claims hold. All third-party-sourced entries (DingTalk/Baidu/WeCom via
wingetgui, Dahua via DahuaWiki, QFlash via Techship, eCloud via MS Store) are correctly at the
**reported** tier.

## Bottom line

Catalog is share-ready from a sourcing standpoint: no dead links, no fabrications, tiers correct, and
the few content issues are fixed. Confidence in the software list is high; the detector layer remains
best-effort/partial as documented.
