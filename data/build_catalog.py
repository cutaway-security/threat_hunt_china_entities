#!/usr/bin/env python3
"""Build the Layer-2 software catalog into the master: for ALL 80 entities, a justified disposition,
and for software-producing vendors, the named Windows software products with provenance.

Source data: five parallel research agents (2026-06-30), each under strict no-fabrication rules
(a product is named only with a fetched source URL). catalog_status reflects source quality:
  verified  = vendor-official source confirms the vendor publishes this Windows software
  reported  = reputable third-party (winget/Microsoft Store/vendor wiki/KB)
  candidate = lead only, named but Windows build/distribution not yet confirmed

NO host artifacts (file/registry/service names) are set here — that is Layer 3 (detectors), which
runs the verification pipeline against this catalog. Software entries carry empty indicators[].

Run:  .venv/bin/python data/build_catalog.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUB = os.path.join(HERE, "source_extraction", "entities_1260h.json")
SCHEMA = os.path.join(HERE, "schema", "master.schema.json")
OUT = os.path.join(HERE, "master", "entities.master.json")

# Per-entity disposition for all 80 (from the agent assessments).
DISPOSITION = {
    "C0001": "software_no_verified_indicators", "C0002": "no_windows_software_found",
    "C0003": "no_windows_software_found", "C0004": "software_no_verified_indicators",
    "C0005": "software_no_verified_indicators", "C0006": "hardware_or_firmware_only",
    "C0007": "no_windows_software_found", "C0008": "server_or_linux_only",
    "C0009": "software_no_verified_indicators", "C0010": "software_no_verified_indicators",
    "C0011": "candidate_pending_verification", "C0012": "hardware_or_firmware_only",
    "C0013": "hardware_or_firmware_only", "C0014": "hardware_or_firmware_only",
    "C0015": "candidate_pending_verification", "C0016": "server_or_linux_only",
    "C0017": "hardware_or_firmware_only", "C0018": "hardware_or_firmware_only",
    "C0019": "candidate_pending_verification", "C0020": "hardware_or_firmware_only",
    "C0021": "no_windows_software_found", "C0022": "no_windows_software_found",
    "C0023": "no_windows_software_found", "C0024": "no_windows_software_found",
    "C0025": "no_windows_software_found", "C0026": "candidate_pending_verification",
    "C0027": "candidate_pending_verification", "C0028": "no_windows_software_found",
    "C0029": "hardware_or_firmware_only", "C0030": "no_windows_software_found",
    "C0031": "no_windows_software_found", "C0032": "no_windows_software_found",
    "C0033": "no_windows_software_found", "C0034": "no_windows_software_found",
    "C0035": "hardware_or_firmware_only", "C0036": "hardware_or_firmware_only",
    "C0037": "no_windows_software_found", "C0038": "no_windows_software_found",
    "C0039": "no_windows_software_found", "C0040": "software_no_verified_indicators",
    "C0041": "no_windows_software_found", "C0042": "no_windows_software_found",
    "C0043": "candidate_pending_verification", "C0044": "no_windows_software_found",
    "C0045": "hardware_or_firmware_only", "C0046": "no_windows_software_found",
    "C0047": "no_windows_software_found", "C0048": "candidate_pending_verification",
    "C0049": "hardware_or_firmware_only", "C0050": "software_no_verified_indicators",
    "C0051": "hardware_or_firmware_only", "C0052": "software_no_verified_indicators",
    "C0053": "software_no_verified_indicators", "C0054": "software_no_verified_indicators",
    "C0055": "software_no_verified_indicators", "C0056": "candidate_pending_verification",
    "C0057": "hardware_or_firmware_only", "C0058": "candidate_pending_verification",
    "C0059": "candidate_pending_verification", "C0060": "hardware_or_firmware_only",
    "C0061": "no_windows_software_found", "C0062": "hardware_or_firmware_only",
    "C0063": "candidate_pending_verification", "C0064": "software_no_verified_indicators",
    "C0065": "software_no_verified_indicators", "C0066": "software_no_verified_indicators",
    "C0067": "hardware_or_firmware_only", "C0068": "candidate_pending_verification",
    "C0069": "server_or_linux_only", "C0070": "software_no_verified_indicators",
    "C0071": "no_windows_software_found", "C0072": "software_no_verified_indicators",
    "C0073": "hardware_or_firmware_only", "C0074": "software_no_verified_indicators",
    "C0075": "no_windows_software_found", "C0076": "software_no_verified_indicators",
    "C0077": "no_windows_software_found", "C0078": "software_no_verified_indicators",
    "C0079": "software_no_verified_indicators", "C0080": "hardware_or_firmware_only",
}

# One-line justifications for the non-software dispositions (software vendors get a generic one).
JUSTIFY = {
    "C0002": "Aerospace/UAV and films hardware maker; no installable Windows software.",
    "C0003": "Industrial hardware (special vehicles, piping, nuclear equipment); no Windows software.",
    "C0006": "Camera-drone hardware; downloads are the mobile app, firmware, and manuals only.",
    "C0007": "State aerospace/defense manufacturing conglomerate; no commercial Windows software.",
    "C0008": "Telecom RAN hardware; management is cloud/server-hosted (CloudCore), browser-accessed.",
    "C0012": "LCD/OLED display-panel and component hardware maker.",
    "C0013": "EV/battery/electronics hardware; customer software is mobile-only.",
    "C0014": "Lithium battery cell/pack hardware maker; downloads are datasheets only.",
    "C0016": "Computing hardware plus server-side data-center/cloud platforms.",
    "C0017": "Telecom/network communication and RF/PCB hardware.",
    "C0018": "DRAM semiconductor memory fabricator (chips, not software).",
    "C0020": "Satellite navigation/EW RF components and hardware.",
    "C0021": "Aerospace/defense conglomerate (missiles, space, defense electronics).",
    "C0022": "Air cargo/freight airline (logistics service).",
    "C0023": "Infrastructure/construction conglomerate.",
    "C0024": "Construction-sector technology and engineering services.",
    "C0025": "Shipping, ports, and marine logistics conglomerate.",
    "C0028": "Nuclear power generation/energy operator.",
    "C0029": "Container/vehicle/marine-equipment manufacturer (hardware).",
    "C0030": "Telecom carrier; offerings are network services plus mobile/web apps.",
    "C0031": "Chemical manufacturing and agrochemical/materials conglomerate.",
    "C0032": "Chemical-plant engineering and EPC construction.",
    "C0033": "State nuclear conglomerate (weapons, power, fuel cycle).",
    "C0034": "Offshore oil and gas energy operator.",
    "C0035": "Defense/industrial hardware (weapons, vehicles, munitions, radars).",
    "C0036": "Defense/automotive hardware manufacturer.",
    "C0037": "Aerospace; satellites, antennas, Beidou terminals, ground systems (hardware).",
    "C0038": "State construction/engineering conglomerate.",
    "C0039": "Shipbuilding and marine/defense equipment conglomerate.",
    "C0041": "Hydropower/clean-energy infrastructure operator and builder.",
    "C0042": "Telecom service operator; only verified client is the mobile app.",
    "C0044": "Civil aircraft manufacturer (hardware and services).",
    "C0045": "EV-battery and energy-storage hardware; BMS ships as embedded firmware.",
    "C0046": "Rail/rolling-stock manufacturer (trains, locomotives, metro).",
    "C0047": "Shipbuilding/marine-engineering enterprise (CSSC subsidiary).",
    "C0049": "Lithium battery/ESS hardware; BMS is embedded firmware.",
    "C0051": "Aero-engine forging/metallurgical materials manufacturer.",
    "C0057": "Solar PV cell/module (panel) hardware manufacturer.",
    "C0060": "EV maker; in-car software is embedded; companion app is mobile-only.",
    "C0061": "Genomics sequencing services; bioinformatics is a cloud/web platform.",
    "C0062": "Automated cryogenic biobank storage hardware (embedded control).",
    "C0067": "Pure-play semiconductor wafer foundry (chips, not software).",
    "C0069": "Enterprise AI delivered as server/cloud/edge platforms and AI chips.",
    "C0071": "State logistics/shipping/freight-forwarding conglomerate.",
    "C0073": "LCD/AMOLED display and touch-panel hardware manufacturer.",
    "C0075": "Solar PV module hardware; monitoring is the cloud-based Trina Smart Cloud.",
    "C0077": "Pharma/biotech CRDMO services; customer tooling is a web portal.",
    "C0080": "High-speed optical transceiver/optical-module hardware (firmware onboard).",
    # candidates without confirmed products:
    "C0011": "Genomics; sequencer/bioinformatics software exists in the BGI/MGI ecosystem but verified Windows downloads belong to affiliate MGI; needs per-product verification.",
    "C0026": "State electronics/IT holding; subsidiaries publish software (some Linux/Kylin), but no Windows product confirmed under the named parent.",
    "C0027": "Defense-electronics conglomerate; some subsidiaries make software, none confirmed Windows under the named umbrella.",
    "C0043": "Facial-recognition AI; publishes a detection SDK but verified platforms are mobile/embedded/cloud, no Windows build confirmed.",
    "C0048": "Server/HPC/storage and cloud vendor (server/Linux-oriented); a Windows mgmt/driver tool is plausible but unconfirmed.",
    "C0058": "Gene-sequencing instruments; verified software (ZLIMS/MegaBOLT/ZTRON) is server/Linux; instrument-control Windows distribution unconfirmed.",
    "C0059": "VMS/video-cloud provider; a Windows operator client is likely (largest China VMS) but no named installer confirmed (site fetch refused).",
    "C0068": "Computer-vision AI; verified offerings are cloud/web and mobile/embedded SDKs; no Windows desktop app/SDK confirmed.",
}

# vendor_company_id -> list of (name, category, source_url, catalog_status)
SOFTWARE = {
    "C0001": [("360 Total Security", "Antivirus / endpoint security suite", "https://www.360totalsecurity.com/", "verified")],
    "C0004": [("DingTalk", "Enterprise collaboration desktop client", "https://www.wingetgui.com/apps/Alibaba-DingTalk", "reported")],
    "C0005": [("Maxi PC Suite", "Diagnostic device update/management utility", "https://autel.us/software-downloads/", "verified"),
              ("MaxiLinkII", "Code-reader desktop tool", "https://autel.us/software-downloads/", "verified"),
              ("MaxiScope", "PC oscilloscope software", "https://autel.us/software-downloads/", "verified"),
              ("DS708 PC Suite", "MaxiDAS DS708 update suite", "https://autel.us/software-downloads/", "verified")],
    "C0009": [("Baidu Netdisk", "Cloud-storage desktop client", "https://wingetgui.com/apps/Baidu-BaiduNetdisk", "reported")],
    "C0010": [("ZoomEye-python", "CLI/SDK (pip; cross-platform incl. Windows)", "https://github.com/knownsec/ZoomEye-python", "verified")],
    "C0015": [("Endpoint Security Management System", "Endpoint security client", "https://en.cetccst.com.cn/about/173.html", "candidate"),
              ("File Encryption and Access Control", "Endpoint encryption client", "https://en.cetccst.com.cn/about/173.html", "candidate"),
              ("OrangeMessage", "Secure messaging client", "https://en.cetccst.com.cn/about/173.html", "candidate")],
    "C0019": [("Eagle Map", "Drone GCS / mission-planning software", "https://www.jouav.com/products/eagle-map.html", "candidate"),
              ("FlightSurv", "Drone mapping / flight-planning", "https://www.jouav.com/products/software/", "candidate")],
    "C0040": [("Cloud 189 PC client", "Cloud-storage desktop client", "https://cloud.189.cn/web/static/download-client/index.html", "verified"),
              ("eCloud Computer", "Cloud-desktop client", "https://apps.microsoft.com/detail/xpdnk2982gqmxt", "reported")],
    "C0050": [("YeeKit Word Translation Plug-in", "MS Word translation client (C/S)", "https://www.gtcom.com.cn/en/index.php?c=products&a=sanlist&id=25", "verified"),
              ("YeeCaption", "Audio/video translation desktop software", "https://www.gtcom.com.cn/en/index.php?c=products&a=sanlist&id=25", "verified")],
    "C0052": [("iVMS-4200", "Video-management client (VMS)", "https://www.hikvision.com/us-en/support/download/software/ivms4200-series/", "verified"),
              ("HikCentral Professional", "Video surveillance management software", "https://us.hikvision.com/en/products/software/ivms-4200-series/free-client-software-hikvision-devices-ivms-4200-windows", "verified"),
              ("SADP Tool", "Device search/activation utility", "https://www.hikvision.com/us-en/support/download/software/", "verified"),
              ("Batch Configuration Tool", "Device batch-configuration utility", "https://www.hikvision.com/us-en/support/download/software/", "verified")],
    "C0053": [("Unilidar 2", "4D LiDAR point-cloud visualization (Win64)", "https://oss-global-cdn.unitree.com/static/Unitree%204D%20LiDAR%20L2%20User%20Manual.pdf", "verified"),
              ("unilidar_sdk", "LiDAR SDK", "https://github.com/unitreerobotics/unilidar_sdk", "verified")],
    "C0054": [("PandarView 2", "Point-cloud visualization desktop app", "https://www.hesaitech.com/product_downloads/pandarview-2/", "verified"),
              ("LidarUtilities", "Device configuration utilities (Win64)", "https://www.hesaitech.com/downloads/", "verified")],
    "C0055": [("HUAWEI PC Manager", "PC management / device-collaboration app", "https://consumer.huawei.com/en/support/pc-manager/", "verified"),
              ("HUAWEI HiSuite", "Phone/PC suite (backup, data management)", "https://consumer.huawei.com/en/support/hisuite/", "verified"),
              ("eNSP / eNSP Pro", "Enterprise network simulation platform", "https://info.support.huawei.com/info-finder/encyclopedia/en/eNSP+Pro.html", "verified")],
    "C0056": [("InspurDiagLogCollect-Win", "Server diagnostic/log-collection client tool", "https://www.scribd.com/presentation/458371263/3-Knowdge-base-and-tools", "candidate")],
    "C0063": [("Phenix microscope imaging software", "Microscope imaging/measurement (bundled)", "https://www.medicalexpo.com/prod/phenix-optics-co-ltd/product-301427-1015838.html", "candidate"),
              ("Phenix ME200 digital-microscope driver", "Windows device driver", "https://phenix-digital-microscope-me200-vu-drvie.software.informer.com/", "candidate")],
    "C0064": [("Quectel Windows USB Driver", "Windows USB device driver (NDIS/ECM/RNDIS)", "https://www.quectel.com/download/quectel_windows_usb_driverq_ndis_v2-8_en/", "verified"),
              ("QNavigator", "Module test / AT-command GUI tool", "https://www.quectel.com/download/qnavigator_v1-5/", "verified"),
              ("QCOM", "Serial / AT-command terminal tool", "https://www.quectel.com/download/qcom_v1-6/", "verified"),
              ("QFlash", "Firmware flashing utility", "https://techship.com/downloads/quectel-qflash-flash-tool-for-windows/", "reported")],
    "C0065": [("RSView", "LiDAR point-cloud visualization / config app", "https://store.robosense.ai/pages/faq-software-rsview", "verified")],
    "C0066": [("Forensics Master", "Digital forensic analysis software", "https://www.meiyapico.com/forensics-master_p18.html", "verified")],
    "C0070": [("DJI Assistant 2", "Drone firmware / calibration tool", "https://www.dji.com/downloads/softwares/assistant-dji-2", "verified"),
              ("DJI Terra", "Photogrammetry / mapping app (Windows-only)", "https://www.dji.com/downloads/products/dji-terra", "verified"),
              ("DJI Thermal Analysis Tool 3", "Thermal image analysis tool", "https://www.dji.com/downloads/softwares/dji-dtat3", "verified")],
    "C0072": [("WeChat for Windows", "Messaging client", "https://www.wechat.com/en", "verified"),
              ("QQ for Windows", "Messaging client", "https://im.qq.com/", "verified"),
              ("Tencent Meeting (VooV)", "Video conferencing client", "https://voovmeeting.com/download-center.html", "verified"),
              ("WeCom (Enterprise WeChat)", "Enterprise messaging client", "https://wingetgui.com/apps/Tencent-WeCom", "reported"),
              ("Tencent Docs", "Document collaboration client", "https://docs.qq.com/desktop/", "verified")],
    "C0074": [("Omada Software Controller", "On-prem network management console", "https://support.omadanetworks.com/us/download/software/omada-controller/", "verified"),
              ("Pharos Control", "Centralized network management software", "https://www.tp-link.com/us/support/download/pharos-control/", "verified")],
    "C0076": [("GNSS Explorer", "GNSS post-processing software", "https://en.geosuntech.com/", "verified"),
              ("Shuttle", "GNSS/INS trajectory post-processing", "https://en.geosuntech.com/", "verified"),
              ("PointCloudCreater", "Point-cloud preprocessing", "https://en.geosuntech.com/", "verified"),
              ("WaypointMaster", "UAV flight planning", "https://en.geosuntech.com/", "verified")],
    "C0078": [("ZHITAI UNIMASTER SSD", "SSD management/monitoring utility", "https://www.ymtc.com/cn/techsupport.html", "verified"),
              ("ZHITAI UNIMASTER PSSD", "Portable SSD management utility", "https://www.ymtc.com/cn/techsupport.html", "verified"),
              ("PSSD AESTool", "Portable SSD encryption utility", "https://www.ymtc.com/cn/techsupport.html", "verified")],
    "C0079": [("SmartPSS", "Video management client (Win64)", "https://www.dahuawiki.com/Software", "reported"),
              ("SmartPSS Lite", "Video management client", "https://www.dahuawiki.com/Software", "reported"),
              ("DSS Express", "Video management server software", "https://www.dahuawiki.com/Software", "reported"),
              ("ConfigTool", "Device discovery/configuration tool", "https://www.dahuawiki.com/Software", "reported"),
              ("Smart Player", "Playback/conversion tool", "https://www.dahuawiki.com/Software", "reported"),
              ("Dahua Toolbox", "Maintenance/utility suite", "https://www.dahuawiki.com/Software", "reported")],
}


def main():
    ext = json.load(open(STUB, encoding="utf-8"))
    parents = ext["designated_parents"]
    sid = 0
    entities = []
    for i, p in enumerate(parents, 1):
        cid = f"C{i:04d}"
        subs = []
        import re
        for s in p["subsidiaries"]:
            alias = None
            sn = s.strip()
            if sn.endswith(")"):
                m = re.findall(r"\(([^()]*)\)$", sn)
                if m and not m[-1].lower().startswith(("formerly", "also known")):
                    alias = m[-1].strip()
            subs.append({"name": s, "short_alias": alias})
        software = []
        for (name, category, url, status) in SOFTWARE.get(cid, []):
            sid += 1
            software.append({"software_id": f"S{sid:04d}", "name": name,
                             "vendor_company_id": cid, "category": category,
                             "windows_installable": True, "catalog_status": status,
                             "source_url": url, "indicators": []})
        disp = DISPOSITION[cid]
        if disp == "software_no_verified_indicators":
            just = f"Publishes installable Windows software ({len(software)} product(s) catalogued); host-artifact detectors not yet built (Layer 3)."
        else:
            just = JUSTIFY.get(cid, "Assessed: no confirmed installable Windows software.")
        entities.append({"company_id": cid, "name": p["name"], "short_alias": p.get("short_alias"),
                         "affiliation_rationale": p.get("rationale", ""), "subsidiaries": subs,
                         "disposition": disp, "disposition_justification": just, "software": software})

    master = {
        "meta": {"source_pdf": "ENTITIES-IDENTIFIED-AS-CHINESE-MILITARY-COMPANIES-OPERATING-IN-THE-UNITED-STATES-IN-ACCORDANCE-WITH-SECTION-1260H.PDF",
                 "source_url": "https://media.defense.gov/2026/Jun/08/2003945537/-1/-1/1/ENTITIES-IDENTIFIED-AS-CHINESE-MILITARY-COMPANIES-OPERATING-IN-THE-UNITED-STATES-IN-ACCORDANCE-WITH-SECTION-1260H.PDF",
                 "source_date": "2026-06-08", "list_version": "2026-06-08", "best_effort": True},
        "entities": entities, "delisted": list(ext["delisted_entities"]), "backlog": []}

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(master, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    from jsonschema import Draft202012Validator
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    errs = sorted(Draft202012Validator(schema).iter_errors(master), key=lambda e: list(e.path))
    if errs:
        print("SCHEMA VALIDATION FAILED:")
        for e in errs[:10]:
            print("  ", list(e.path), e.message)
        sys.exit(1)

    from collections import Counter
    disp = Counter(e["disposition"] for e in entities)
    nsw = sum(len(e["software"]) for e in entities)
    print(f"OK: catalog written. {len(entities)} entities, {nsw} software products. validates.")
    for k, v in sorted(disp.items(), key=lambda x: -x[1]):
        print(f"   {k}: {v}")


if __name__ == "__main__":
    main()
