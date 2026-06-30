# Section 1260H Software Catalog (Layer 2)

AI-assisted, best-effort. Source: DoD Section 1260H list dated 2026-06-08. This is **exposure/inventory** analysis, not malware detection — a 1260H designation is a corporate-affiliation flag, not a finding that the software is malicious. **Report, do not auto-block.** Generated from the dataset; do not hand-edit.

## Coverage (all 80 designated parent entities assessed)

| Disposition | Count |
|---|---|
| No installable Windows software found | 26 |
| Publishes installable Windows software | 19 |
| Hardware / firmware only | 19 |
| Candidate — software likely, not yet confirmed | 12 |
| Server / Linux platforms only | 3 |
| indicators_identified | 1 |
| **Total** | **80** |

**Software products catalogued:** 59 (40 verified vendor-official, 11 reported third-party, 8 candidate). Verified/reported are usable now; candidates need confirmation.

## Vendors with confirmed installable Windows software

These vendors publish Windows software (vendor-official = verified; third-party = reported). Host-artifact detectors (exact installed file/registry/service names) are Layer 3 and are not yet attached.

| Vendor (1260H entity) | Software product | Type | Status | Source |
|---|---|---|---|---|
| Qihoo 360 | 360 Total Security | Antivirus / endpoint security suite | verified | <https://www.360totalsecurity.com/> |
| Alibaba | DingTalk | Enterprise collaboration desktop client | reported | <https://www.wingetgui.com/apps/Alibaba-DingTalk> |
| Autel Technology | Maxi PC Suite | Diagnostic device update/management utility | verified | <https://autel.us/software-downloads/> |
| Autel Technology | MaxiLinkII | Code-reader desktop tool | verified | <https://autel.us/software-downloads/> |
| Autel Technology | MaxiScope | PC oscilloscope software | verified | <https://autel.us/software-downloads/> |
| Autel Technology | DS708 PC Suite | MaxiDAS DS708 update suite | verified | <https://autel.us/software-downloads/> |
| Baidu | Baidu Netdisk | Cloud-storage desktop client | reported | <https://wingetgui.com/apps/Baidu-BaiduNetdisk> |
| Knownsec | ZoomEye-python | cross-platform Python CLI/SDK via pip (runs on Windows; NOT a standalone Windows installer) | verified | <https://github.com/knownsec/ZoomEye-python> |
| China Telecom | Cloud 189 PC client | Cloud-storage desktop client | verified | <https://cloud.189.cn/web/static/download-client/index.html> |
| China Telecom | eCloud Computer | Cloud-desktop client | reported | <https://apps.microsoft.com/detail/xpdnk2982gqmxt> |
| GTCOM | YeeKit Word Translation Plug-in | MS Word translation client (C/S) | verified | <https://www.gtcom.com.cn/en/index.php?c=products&a=sanlist&id=25> |
| GTCOM | YeeCaption | Audio/video translation desktop software | verified | <https://www.gtcom.com.cn/en/index.php?c=products&a=sanlist&id=25> |
| Hikvision | iVMS-4200 | Video-management client (VMS) | verified | <https://www.hikvision.com/us-en/support/download/software/ivms4200-series/> |
| Hikvision | HikCentral Professional | Video surveillance management software (Windows) | verified | <https://www.hikvision.com/us-en/support/download/software/> |
| Hikvision | SADP Tool | Device search/activation utility | verified | <https://www.hikvision.com/us-en/support/download/software/> |
| Hikvision | Batch Configuration Tool | Device batch-configuration utility | verified | <https://www.hikvision.com/us-en/support/download/software/> |
| Unitree | Unilidar 2 | 4D LiDAR point-cloud visualization desktop app (Win64; OS per vendor manual, corroborated via search) | verified | <https://oss-global-cdn.unitree.com/static/Unitree%204D%20LiDAR%20L2%20User%20Manual.pdf> |
| Hesai Group (also known as Hesai Technology Co., Ltd.) | PandarView 2 | Point-cloud visualization desktop app | verified | <https://www.hesaitech.com/product_downloads/pandarview-2/> |
| Hesai Group (also known as Hesai Technology Co., Ltd.) | LidarUtilities | Device configuration utilities (Win64) | verified | <https://www.hesaitech.com/downloads/> |
| Huawei Holding | HUAWEI PC Manager | PC management / device-collaboration app | verified | <https://consumer.huawei.com/en/support/pc-manager/> |
| Huawei Holding | HUAWEI HiSuite | Phone/PC suite (backup, data management) | verified | <https://consumer.huawei.com/en/support/hisuite/> |
| Huawei Holding | eNSP / eNSP Pro | Enterprise network simulation platform | verified | <https://info.support.huawei.com/info-finder/encyclopedia/en/eNSP+Pro.html> |
| Quectel Wireless Solutions Co., Ltd. | Quectel Windows USB Driver | Windows USB device driver (NDIS/ECM/RNDIS) | verified | <https://www.quectel.com/download/quectel_windows_usb_driverq_ndis_v2-8_en/> |
| Quectel Wireless Solutions Co., Ltd. | QNavigator | Module test / AT-command GUI tool | verified | <https://www.quectel.com/download/qnavigator_v1-5/> |
| Quectel Wireless Solutions Co., Ltd. | QCOM | Serial / AT-command terminal tool | verified | <https://www.quectel.com/download/qcom_v1-6/> |
| Quectel Wireless Solutions Co., Ltd. | QFlash | Firmware flashing utility | reported | <https://techship.com/downloads/quectel-qflash-flash-tool-for-windows/> |
| Robosense Technology Co., Ltd. | RSView | LiDAR point-cloud visualization / config app | verified | <https://store.robosense.ai/pages/faq-software-rsview> |
| SDIC Intelligence (Xiamen) Information Co., Ltd. | Forensics Master | Digital forensic analysis software | verified | <https://www.meiyapico.com/forensics-master_p18.html> |
| DJI | DJI Assistant 2 | Drone firmware / calibration tool | verified | <https://www.dji.com/downloads/softwares/assistant-dji-2> |
| DJI | DJI Terra | Photogrammetry / mapping app (Windows-only) | verified | <https://www.dji.com/downloads/products/dji-terra> |
| DJI | DJI Thermal Analysis Tool 3 | Thermal image analysis tool | verified | <https://www.dji.com/downloads/softwares/dji-dtat3> |
| TP-Link | Omada Software Controller | On-prem network management console | verified | <https://support.omadanetworks.com/us/download/software/omada-controller/> |
| TP-Link | Pharos Control | Centralized network management software | verified | <https://www.tp-link.com/us/support/download/pharos-control/> |
| Geosun | GNSS Explorer | GNSS post-processing (desktop; Windows implied, OS not stated on vendor page) | verified | <https://en.geosuntech.com/> |
| Geosun | Shuttle | GNSS/INS trajectory post-processing (desktop; Windows implied, OS not stated) | verified | <https://en.geosuntech.com/> |
| Geosun | PointCloudCreater | Point-cloud preprocessing (desktop; Windows implied, OS not stated) | verified | <https://en.geosuntech.com/> |
| Geosun | WaypointMaster | UAV flight planning (desktop; Windows implied, OS not stated) | verified | <https://en.geosuntech.com/> |
| YMTC | ZHITAI UNIMASTER SSD | SSD management/monitoring utility | verified | <https://www.ymtc.com/cn/techsupport.html> |
| YMTC | ZHITAI UNIMASTER PSSD | Portable SSD management utility | verified | <https://www.ymtc.com/cn/techsupport.html> |
| YMTC | PSSD AESTool | Portable SSD encryption utility | verified | <https://www.ymtc.com/cn/techsupport.html> |
| Dahua | SmartPSS | Video management client (Win64) | reported | <https://www.dahuawiki.com/Software> |
| Dahua | SmartPSS Lite | Video management client | reported | <https://www.dahuawiki.com/Software> |
| Dahua | DSS Express | Video management server software | reported | <https://www.dahuawiki.com/Software> |
| Dahua | ConfigTool | Device discovery/configuration tool | reported | <https://www.dahuawiki.com/Software> |
| Dahua | Smart Player | Playback/conversion tool | reported | <https://www.dahuawiki.com/Software> |
| Dahua | Dahua Toolbox | Maintenance/utility suite | reported | <https://www.dahuawiki.com/Software> |

## Candidate vendors (software named but not yet confirmed Windows)

Leads only — product names appear on vendor or third-party pages but a Windows build/distribution was not confirmed. Do not treat as confirmed until verified.

| Vendor (1260H entity) | Software product | Type | Status | Source |
|---|---|---|---|---|
| CETC Cyberspace Security Technology Co., Ltd. (formerly Chen Du Westone Information Industry Co., Ltd.) | Endpoint Security Management System | Endpoint security client | candidate | <https://en.cetccst.com.cn/about/173.html> |
| CETC Cyberspace Security Technology Co., Ltd. (formerly Chen Du Westone Information Industry Co., Ltd.) | File Encryption and Access Control | Endpoint encryption client | candidate | <https://en.cetccst.com.cn/about/173.html> |
| CETC Cyberspace Security Technology Co., Ltd. (formerly Chen Du Westone Information Industry Co., Ltd.) | OrangeMessage | Secure messaging client | candidate | <https://en.cetccst.com.cn/about/173.html> |
| JOUAV | Eagle Map | Drone GCS / mission-planning software | candidate | <https://www.jouav.com/products/eagle-map.html> |
| JOUAV | FlightSurv | Drone mapping / flight-planning | candidate | <https://www.jouav.com/products/software/> |
| Inspur | InspurDiagLogCollect-Win | Server diagnostic/log-collection client tool | candidate | <https://www.scribd.com/presentation/458371263/3-Knowdge-base-and-tools> |
| Phenix Optical Company Limited (formerly Phoenix Optics Company Limited) | Phenix microscope imaging software | Microscope imaging/measurement (bundled) | candidate | <https://www.medicalexpo.com/prod/phenix-optics-co-ltd/product-301427-1015838.html> |
| Phenix Optical Company Limited (formerly Phoenix Optics Company Limited) | Phenix ME200 digital-microscope driver | Windows device driver | candidate | <https://phenix-digital-microscope-me200-vu-drvie.software.informer.com/> |

### Candidate vendors with no named product yet

- **BGI Group** — Genomics; sequencer/bioinformatics software exists in the BGI/MGI ecosystem but verified Windows downloads belong to affiliate MGI; needs per-product verification.
- **CEC** — State electronics/IT holding; subsidiaries publish software (some Linux/Kylin), but no Windows product confirmed under the named parent.
- **CETC** — Defense-electronics conglomerate; some subsidiaries make software, none confirmed Windows under the named umbrella.
- **CloudWalk** — Facial-recognition AI; publishes a detection SDK but verified platforms are mobile/embedded/cloud, no Windows build confirmed.
- **Sugon** — Server/HPC/storage and cloud vendor (server/Linux-oriented); a Windows mgmt/driver tool is plausible but unconfirmed.
- **MGI** — Gene-sequencing instruments; verified software (ZLIMS/MegaBOLT/ZTRON) is server/Linux; instrument-control Windows distribution unconfirmed.
- **NetPosa** — VMS/video-cloud provider; a Windows operator client is likely (largest China VMS) but no named installer confirmed (site fetch refused).
- **SenseTime** — Computer-vision AI; verified offerings are cloud/web and mobile/embedded SDKs; no Windows desktop app/SDK confirmed.

## Host-artifact detectors (best-effort — PARTIAL, requires verification)

> **Read this before using the detectors.** This section is a *best-effort starting point*, **not a complete or authoritative detection set.** Only host artifacts we could verify from public sources (without installing the software) are listed, each with a confidence tier. **The absence of a detector does NOT mean the software is absent** — it means we have not yet verified a stable host artifact for it. Most install-time artifacts (installed exe names, install paths, service names, SDK DLLs) require enrichment — vendor SDK manuals, VirusTotal code-signer lookups, or controlled lab observation — and MUST be confirmed before operational use. The **software catalog above is the high-confidence deliverable**; these detectors are supplementary.

Confidence tiers: **VERIFIED** = vendor-official + a second independent source for this exact artifact; **CORROBORATED** = multiple reputable sources, none vendor-official. Lower tiers are not shown here (they stay in the backlog).

| Vendor | Software | Detector type | Value | Confidence |
|---|---|---|---|---|
| Tencent | WeChat for Windows | FILE_NAME | `WeChatSetup.exe` | VERIFIED |
| Tencent | QQ for Windows | REGISTRY_KEY | `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{052CFB79-9D62-42E3-8A15-DE66C2C97C3E}` | CORROBORATED |

**2 verified/corroborated detector(s)** attached so far, across 59 catalogued products. Coverage is deliberately not claimed.

## Vendors assessed as producing no installable Windows software

**No installable Windows software found (26):** AVIC; Aerosun; CASIC; CCA; CCCG; CCTC; CGN; CH UAV; CNCEC; CNNC; CNOOC; COMAC; COMEC; COSCO SHIPPING; CRRC; CSCEC; CSSC; CTG; ChemChina; China Mobile Comm; China SpaceSat; China Unicom; Novogene; SinoTrans; Trina Solar; WuXi AppTec

**Hardware / firmware only (19):** Autel Robotics; BOE; BYD; CALB; CATL; CETC Potevio Science & Technology Co., Ltd (formerly Guangzhou GCI Science & Technology Co., Ltd.); CIMC; CSGC; CXMT; EVE Energy Co., Ltd.; Guizhou Aviation Tech; Innolight; JA Solar; M&S Electronics; NIO, Inc.; Norinco Group; Origincell; SMIC; Tianma

**Server / Linux platforms only (3):** Baicells; CETC Digital Technology Co., Ltd. (formerly Shanghai East China Computer Co., Ltd.); Yitu

