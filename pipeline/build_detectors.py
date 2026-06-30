#!/usr/bin/env python3
"""Layer 3 (best-effort, partial): attach host-artifact detectors to priority-vendor software that
is already in the Layer-2 catalog. Every detector carries a confidence tier; only VERIFIED/
CORROBORATED attach to shipped software, REPORTED/CANDIDATE go to the backlog namespace.

This is explicitly NOT complete. Many install-time artifacts (installed exe names, install paths,
service names, SDK DLLs) cannot be verified from public sources without installing the software
(which we do not do, SR-02). Those remain absent and the vendor keeps its Layer-2 catalog entry —
we do not invent them. Confidence in what IS shown must be high; coverage is not claimed.

Run:  KEYS_DIR=~/.claude/keys .venv/bin/python pipeline/build_detectors.py
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from pipeline import verify, gates  # noqa: E402

MASTER = os.path.join(ROOT, "data", "master", "entities.master.json")
SCHEMA = os.path.join(ROOT, "data", "schema", "master.schema.json")
LOG = os.path.join(ROOT, "data", "logs", "verification_log.jsonl")

# Priority-vendor software with a winget identifier (the reliable Tier-1 detector path).
# (company_id, catalog software name, winget identifier, vendor_tokens, exe_hint)
TARGETS = [
    ("C0072", "WeChat for Windows", "Tencent.WeChat", ["Tencent"], "wechat"),
    ("C0072", "QQ for Windows", "Tencent.QQ", ["Tencent"], "qq"),
    ("C0072", "Tencent Meeting (VooV)", "Tencent.TencentMeeting", ["Tencent"], "wemeet"),
    ("C0072", "WeCom (Enterprise WeChat)", "Tencent.WeCom", ["Tencent"], "wxwork"),
    ("C0055", "HUAWEI HiSuite", "Huawei.HiSuite", ["Huawei"], "hisuite"),
    ("C0070", "DJI Assistant 2", "DJI.DJIAssistant2.ConsumerDronesSeries", ["DJI", "Da-Jiang", "SZ DJI"], "assistant"),
    ("C0070", "DJI Terra", "DJI.DJITerra", ["DJI", "Da-Jiang", "SZ DJI"], "terra"),
]


def find_software(master, cid, name):
    for e in master["entities"]:
        if e["company_id"] == cid:
            for sw in e["software"]:
                if sw["name"] == name:
                    return e, sw
    return None, None


def main():
    master = json.load(open(MASTER, encoding="utf-8"))
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    logf = open(LOG, "w", encoding="utf-8")
    ind_n = 0
    summary = []
    print("cooling down 60s to clear the VirusTotal rate-limit window...", flush=True)
    time.sleep(60)

    for i, (cid, name, ident, vtoks, hint) in enumerate(TARGETS):
        ent, sw = find_software(master, cid, name)
        if not sw:
            summary.append((name, "NOT IN CATALOG")); continue
        if i > 0:
            time.sleep(20)  # pace VT
        item = {"winget": ident, "nvd_keyword": name.split("(")[0].strip(), "vendor_tokens": vtoks, "exe_hint": hint}
        claims, facts, flog = verify.gather_claims(item)
        for rec in flog:
            logf.write(json.dumps({"software": name, **rec}, ensure_ascii=False) + "\n")
        inds = verify.assemble_indicators(item, claims, facts, vtoks)
        ship = [x for x in inds if x["confidence_tier"] in gates.SHIPPABLE]
        back = [x for x in inds if x["confidence_tier"] not in gates.SHIPPABLE]
        for x in ship:
            ind_n += 1
            x["indicator_id"] = f"I{ind_n:04d}"
        sw["indicators"].extend(ship)
        if ship:
            ent["disposition"] = "indicators_identified"
            ent["disposition_justification"] = f"At least one host-artifact detector verified for {ent['short_alias'] or ent['name']} software (see verification log)."
        for b in back:
            ind_n += 1
            b["indicator_id"] = f"I{ind_n:04d}"
            b["notes"] = (b.get("notes", "") + f" | {name}").strip(" |")
            master["backlog"].append(b)
        tiers = ", ".join(sorted({x["confidence_tier"] for x in inds})) or "no clean artifact"
        summary.append((name, f"{len(ship)} detector(s) [{tiers}]"))

    logf.close()
    json.dump(master, open(MASTER, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("\n=== Layer-3 detector run (best-effort, partial) ===")
    for n, s in summary:
        print(f"  {n:30} {s}")
    ok, results = gates.run_all(master, SCHEMA)
    print("\n=== ship gates ===")
    for g, issues in results.items():
        print(f"  {g:20} {'PASS' if not issues else 'FAIL'}")
        for x in issues[:4]:
            print("     -", x)
    # honest coverage note
    n_det = sum(len(s["indicators"]) for e in master["entities"] for s in e["software"])
    n_sw = sum(len(e["software"]) for e in master["entities"])
    print(f"\nDetectors attached: {n_det} across {n_sw} catalogued products (PARTIAL by design; "
          f"install-time artifacts needing the software installed are NOT included).")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
