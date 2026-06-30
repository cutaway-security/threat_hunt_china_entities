#!/usr/bin/env python3
"""v0.2 seed runner: verify the easy-vendor seed against live sources, write VERIFIED/CORROBORATED
indicators into the master (REPORTED/CANDIDATE go to the backlog namespace), append a verification
log, and run the ship gates.

Real external calls (winget, NVD, VirusTotal) — this is the "real fetch" the load-bearing clause
requires. VirusTotal public API is rate-limited, so VT calls are paced.

Run:  KEYS_DIR=~/.claude/keys .venv/bin/python pipeline/build_seed.py
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from pipeline import verify, gates  # noqa: E402

MASTER = os.path.join(ROOT, "data", "master", "entities.master.json")
SCHEMA = os.path.join(ROOT, "data", "schema", "master.schema.json")
LOG = os.path.join(ROOT, "data", "logs", "verification_log.jsonl")

SEED = [
    {"match": "Tencent Holdings", "software": "WeChat for Windows", "category": "messaging client",
     "winget": "Tencent.WeChat", "nvd_keyword": "tencent wechat",
     "vendor_tokens": ["Tencent"], "exe_hint": "wechat"},
    {"match": "Tencent Holdings", "software": "QQ for Windows", "category": "messaging client",
     "winget": "Tencent.QQ", "nvd_keyword": "tencent qq",
     "vendor_tokens": ["Tencent"], "exe_hint": "qq"},
    {"match": "Huawei", "software": "HiSuite", "category": "device management tool",
     "winget": "Huawei.HiSuite", "nvd_keyword": "huawei hisuite",
     "vendor_tokens": ["Huawei"], "exe_hint": "hisuite"},
    {"match": "DJI", "software": "DJI Assistant 2 (Consumer Drones)", "category": "UAV configuration tool",
     "winget": "DJI.DJIAssistant2.ConsumerDronesSeries", "nvd_keyword": "dji assistant",
     "vendor_tokens": ["DJI", "Da-Jiang", "SZ DJI"], "exe_hint": "assistant"},
    {"match": "360 Security Technology", "software": "360 Total Security", "category": "endpoint security",
     "winget": "360.360TotalSecurity", "nvd_keyword": "360 total security",
     "vendor_tokens": ["360", "Qihoo"], "exe_hint": "360"},
]


def find_entity(master, match):
    for e in master["entities"]:
        if match.lower() in e["name"].lower():
            return e
    return None


def main():
    master = json.load(open(MASTER, encoding="utf-8"))
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    logf = open(LOG, "w", encoding="utf-8")

    sw_n = ind_n = 0
    summary = []
    vt_calls = 0
    # Clear the VirusTotal per-minute rate window before the first lookup.
    print("cooling down 60s to clear the VirusTotal rate-limit window...", flush=True)
    time.sleep(60)
    for item in SEED:
        ent = find_entity(master, item["match"])
        if not ent:
            summary.append((item["software"], "ENTITY NOT FOUND", 0)); continue

        # pace VT (public API ~4/min): we make at most one VT call per item
        if vt_calls > 0:
            time.sleep(20)
        claims, facts, flog = verify.gather_claims(item)
        vt_calls += 1
        for rec in flog:
            logf.write(json.dumps({"software": item["software"], **rec}, ensure_ascii=False) + "\n")

        inds = verify.assemble_indicators(item, claims, facts, item["vendor_tokens"])
        shippable = [i for i in inds if i["confidence_tier"] in gates.SHIPPABLE]
        backlog = [i for i in inds if i["confidence_tier"] not in gates.SHIPPABLE]

        if shippable:
            sw_n += 1
            sid = f"S{sw_n:04d}"
            for i in shippable:
                ind_n += 1
                i["indicator_id"] = f"I{ind_n:04d}"
            software = {"software_id": sid, "name": item["software"],
                        "vendor_company_id": ent["company_id"], "category": item["category"],
                        "indicators": shippable}
            if facts.get("cpe"):
                software["cpe"] = facts["cpe"]
            ent["software"].append(software)
            ent["disposition"] = "indicators_identified"
            ent["disposition_justification"] = f"{item['software']} verified present via winget/NVD/VirusTotal (see verification log)."
        for b in backlog:
            ind_n += 1
            b["indicator_id"] = f"I{ind_n:04d}"
            b.setdefault("notes", "")
            b["notes"] = (b["notes"] + f" | {ent['name']} / {item['software']}").strip(" |")
            master["backlog"].append(b)

        tiers = ", ".join(sorted({i["confidence_tier"] for i in inds})) or "none"
        summary.append((item["software"], f"{len(shippable)} shipped ({tiers}), {len(backlog)} backlog", len(shippable)))

    logf.close()
    json.dump(master, open(MASTER, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("=== seed results ===")
    for name, status, _ in summary:
        print(f"  {name:24} {status}")

    ok, results = gates.run_all(master, SCHEMA)
    print("\n=== ship gates ===")
    for gate, issues in results.items():
        print(f"  {gate:20} {'PASS' if not issues else 'FAIL'}")
        for x in issues[:5]:
            print("      -", x)
    print(f"\nverification log: {LOG}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
