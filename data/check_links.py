#!/usr/bin/env python3
"""Link-liveness sweep over every source URL in the master. Categorizes each as live / blocked
(WAF/auth, may still be valid) / DEAD (404/410) / unreachable, mapped back to the software it backs.
Read-only HEAD/ranged-GET (SR-02)."""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from pipeline import sources as S

m = json.load(open(os.path.join(HERE, "master", "entities.master.json"), encoding="utf-8"))

# url -> list of "vendor / software [tier]" that cite it
refs = {}
for e in m["entities"]:
    for s in e["software"]:
        u = s.get("source_url")
        if u:
            refs.setdefault(u, []).append(f"{e.get('short_alias') or e['name']} / {s['name']} [{s['catalog_status']}]")
if m["meta"].get("source_url"):
    refs.setdefault(m["meta"]["source_url"], []).append("meta / 1260H source PDF")

def probe(u):
    return u, S.url_head(u, timeout=12)

results = {}
with ThreadPoolExecutor(max_workers=10) as ex:
    for u, st in ex.map(probe, list(refs)):
        results[u] = st

def bucket(st):
    if st in (200, 206) or (isinstance(st, int) and 300 <= st < 400):
        return "live"
    if st in (401, 403, 405, 429):
        return "blocked"   # WAF/auth/method/rate -- may still be a valid page
    if st in (404, 410):
        return "DEAD"
    return "unreachable"   # None / timeout / 5xx

from collections import Counter
cats = Counter(bucket(results[u]) for u in refs)
print(f"Checked {len(refs)} unique source URLs: " +
      ", ".join(f"{k}={v}" for k, v in sorted(cats.items())))
print()
for cat in ("DEAD", "unreachable", "blocked", "live"):
    urls = [u for u in refs if bucket(results[u]) == cat]
    if not urls:
        continue
    print(f"=== {cat} ({len(urls)}) ===")
    for u in sorted(urls):
        st = results[u]
        print(f"  [{st}] {u}")
        if cat in ("DEAD", "unreachable"):
            for r in refs[u]:
                print(f"        backs: {r}")
    print()
# exit nonzero if anything is DEAD (actionable)
sys.exit(1 if cats.get("DEAD") else 0)
