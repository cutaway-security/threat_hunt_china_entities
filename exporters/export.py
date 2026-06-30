#!/usr/bin/env python3
"""Generate shareable exports from the master (single source of truth): STIX 2.1, YAML, CSV.

Non-malware semantics (designation is corporate affiliation, NOT a malware finding): the STIX bundle
uses `software` + `identity` + `indicator(anomalous-activity)`, never the `malware` SDO. CPE version
fields are wildcarded and no version-pinned value is emitted (DR-09/DR-10). Every export carries the
best-effort / not-malware / report-don't-block caveats.

Run:  .venv/bin/python exporters/export.py
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MASTER = os.path.join(ROOT, "data", "master", "entities.master.json")
DIST = os.path.join(ROOT, "dist")

CAVEAT = ("AI-assisted, best-effort. A DoD Section 1260H designation is a corporate-affiliation flag, "
          "NOT a finding that the software is malicious. Exposure/inventory analysis only. "
          "Report and route for human review; do NOT auto-block. Detectors are partial and require "
          "verification before operational use.")


def load():
    return json.load(open(MASTER, encoding="utf-8"))


def export_csv(m):
    d = os.path.join(DIST, "csv")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "entities.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["# " + CAVEAT])
        w.writerow(["company_id", "name", "short_alias", "disposition", "disposition_justification", "subsidiary_count"])
        for e in m["entities"]:
            w.writerow([e["company_id"], e["name"], e.get("short_alias") or "", e["disposition"],
                        e["disposition_justification"], len(e.get("subsidiaries", []))])
    with open(os.path.join(d, "software.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["# " + CAVEAT])
        w.writerow(["software_id", "vendor_company_id", "vendor_name", "software", "category",
                    "catalog_status", "windows_installable", "source_url"])
        for e in m["entities"]:
            for s in e["software"]:
                w.writerow([s["software_id"], e["company_id"], e.get("short_alias") or e["name"], s["name"],
                            s.get("category", ""), s["catalog_status"], s.get("windows_installable", ""), s.get("source_url", "")])
    with open(os.path.join(d, "detectors.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["# " + CAVEAT + " Coverage is NOT claimed; absence of a detector != software absent."])
        w.writerow(["indicator_id", "software_id", "vendor_name", "software", "indicator_type", "value",
                    "presence_class", "confidence_tier", "date_verified"])
        for e in m["entities"]:
            for s in e["software"]:
                for i in s["indicators"]:
                    w.writerow([i["indicator_id"], s["software_id"], e.get("short_alias") or e["name"], s["name"],
                                i["indicator_type"], i["value"], i["presence_class"], i["confidence_tier"], i.get("date_verified", "")])
    return ["csv/entities.csv", "csv/software.csv", "csv/detectors.csv"]


def export_yaml(m):
    import yaml
    d = os.path.join(DIST, "yaml")
    os.makedirs(d, exist_ok=True)
    out = {"_caveat": CAVEAT, "meta": m["meta"],
           "entities": [{"company_id": e["company_id"], "name": e["name"], "short_alias": e.get("short_alias"),
                         "disposition": e["disposition"], "disposition_justification": e["disposition_justification"],
                         "software": [{"name": s["name"], "category": s.get("category"), "catalog_status": s["catalog_status"],
                                       "source_url": s.get("source_url"),
                                       "detectors": [{"type": i["indicator_type"], "value": i["value"],
                                                      "confidence": i["confidence_tier"]} for i in s["indicators"]]}
                                      for s in e["software"]]} for e in m["entities"]],
           "delisted": m["delisted"]}
    with open(os.path.join(d, "catalog.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(out, f, allow_unicode=True, sort_keys=False, width=100)
    return ["yaml/catalog.yaml"]


def _stix_pattern(itype, value):
    if itype in ("FILE_NAME", "DLL_NAME"):
        return f"[file:name = '{value}']"
    if itype in ("FILE_PATH", "FOLDER_PATH"):
        return f"[file:parent_directory_ref.path = '{value}']"
    if itype == "PROCESS_NAME":
        return f"[process:name = '{value}']"
    if itype == "REGISTRY_KEY":
        key = value.replace("HKLM\\", "HKEY_LOCAL_MACHINE\\").replace("HKCU\\", "HKEY_CURRENT_USER\\")
        return "[windows-registry-key:key = '" + key.replace("\\", "\\\\") + "']"
    return None


def export_stix(m):
    import stix2
    d = os.path.join(DIST, "stix")
    os.makedirs(d, exist_ok=True)
    # Build identities for vendors that have software; software SCOs; indicators; relationships.
    objs = []
    ident_by_cid = {}
    for e in m["entities"]:
        if not e["software"]:
            continue
        ident = stix2.Identity(name=e["name"], identity_class="organization",
                               description=f"DoD Section 1260H-designated entity ({e['company_id']}). Affiliation flag, not a malware finding.")
        ident_by_cid[e["company_id"]] = ident
        objs.append(ident)
        for s in e["software"]:
            sw = stix2.Software(name=s["name"], vendor=(e.get("short_alias") or e["name"]))
            objs.append(sw)
            objs.append(stix2.Relationship(relationship_type="related-to", source_ref=sw.id, target_ref=ident.id,
                                           description="software produced by designated vendor"))
            for i in s["indicators"]:
                pat = _stix_pattern(i["indicator_type"], i["value"])
                if not pat:
                    continue
                ind = stix2.Indicator(name=f"{s['name']} present ({i['indicator_type']})", pattern=pat,
                                      pattern_type="stix", indicator_types=["anomalous-activity"],
                                      description=f"{i['confidence_tier']} host-artifact for {s['name']} ({e.get('short_alias') or e['name']}). {CAVEAT}")
                objs.append(ind)
                objs.append(stix2.Relationship(relationship_type="related-to", source_ref=ind.id, target_ref=sw.id,
                                               description=f"detector for {s['name']}"))
    # A note carrying the caveat, referencing all identities.
    if ident_by_cid:
        objs.insert(0, stix2.Note(abstract="Usage and limitations",
                                  content=CAVEAT, object_refs=[i.id for i in ident_by_cid.values()]))
    bundle = stix2.Bundle(objs, allow_custom=False)
    with open(os.path.join(d, "1260h_software_bundle.json"), "w", encoding="utf-8") as f:
        f.write(bundle.serialize(pretty=True))
    n_ind = sum(1 for o in objs if getattr(o, "type", "") == "indicator")
    return [f"stix/1260h_software_bundle.json ({len(objs)} objects, {n_ind} indicators)"]


def main():
    m = load()
    os.makedirs(DIST, exist_ok=True)
    produced = []
    produced += export_csv(m)
    produced += export_yaml(m)
    produced += export_stix(m)
    open(os.path.join(DIST, "README.md"), "w", encoding="utf-8").write(
        "# Generated exports\n\n" + CAVEAT + "\n\nGenerated from the dataset master; do not hand-edit.\n\n- "
        + "\n- ".join(produced) + "\n")
    print("exports written to dist/:")
    for p in produced:
        print("  ", p)


if __name__ == "__main__":
    main()
