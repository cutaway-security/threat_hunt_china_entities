"""Ship gates. Run before any export. A failing gate fails the build (exit non-zero)."""
import datetime, json, os, re

FILE_TYPES = {"FILE_NAME", "DLL_NAME"}
PATHISH = {"FILE_NAME", "DLL_NAME", "PROCESS_NAME", "FILE_PATH", "FOLDER_PATH"}

SHIPPABLE = {"VERIFIED", "CORROBORATED"}


def _iter_indicators(master):
    for e in master.get("entities", []):
        for sw in e.get("software", []):
            for ind in sw.get("indicators", []):
                yield e, sw, ind


def validate_schema(master, schema_path):
    from jsonschema import Draft202012Validator
    schema = json.load(open(schema_path, encoding="utf-8"))
    return [f"{list(e.path)}: {e.message}" for e in
            sorted(Draft202012Validator(schema).iter_errors(master), key=lambda e: list(e.path))]


def tier_leak(master):
    """TSC-03: no REPORTED/CANDIDATE may be nested under shipped software (must live in backlog)."""
    leaks = []
    for e, sw, ind in _iter_indicators(master):
        if ind["confidence_tier"] not in SHIPPABLE:
            leaks.append(f"{e['name']} / {sw['name']} / {ind['value']} is {ind['confidence_tier']} but nested as shipped")
    return leaks


def staleness(master, window_days=180):
    """TSC-04: every shipped indicator must have a date_verified within the window."""
    today = datetime.date.today()
    stale = []
    for e, sw, ind in _iter_indicators(master):
        dv = ind.get("date_verified")
        try:
            age = (today - datetime.date.fromisoformat(dv)).days
        except Exception:
            stale.append(f"{sw['name']} / {ind['value']}: missing/invalid date_verified")
            continue
        if age > window_days:
            stale.append(f"{sw['name']} / {ind['value']}: {age}d old (> {window_days})")
    return stale


def provenance(master):
    """TSC-02: every shipped indicator has >=1 claim, each with a source_url."""
    bad = []
    for e, sw, ind in _iter_indicators(master):
        if not ind.get("claims"):
            bad.append(f"{sw['name']} / {ind['value']}: no claims")
        for c in ind.get("claims", []):
            if not c.get("source_url"):
                bad.append(f"{sw['name']} / {ind['value']}: claim {c.get('claim_type')} missing source_url")
    return bad


def value_sanity(master):
    """DR-10: no shipped indicator value may carry a version-like substring; FILE_NAME/DLL_NAME must
    be clean filenames. Defense in depth behind the normalizer."""
    bad = []
    for e, sw, ind in _iter_indicators(master):
        v, t = ind["value"], ind["indicator_type"]
        if t in PATHISH and re.search(r"\d+\.\d+", v):
            bad.append(f"{sw['name']} / {v}: version-like value (DR-10)")
        if t in FILE_TYPES and not re.match(r"^[A-Za-z0-9 ._+\-]+\.[A-Za-z0-9]{2,4}$", v):
            bad.append(f"{sw['name']} / {v}: not a clean filename")
    return bad


def run_all(master, schema_path, window_days=180):
    results = {
        "schema": validate_schema(master, schema_path),
        "provenance_TSC-02": provenance(master),
        "tier_leak_TSC-03": tier_leak(master),
        "staleness_TSC-04": staleness(master, window_days),
        "value_sanity_DR-10": value_sanity(master),
    }
    ok = all(not v for v in results.values())
    return ok, results
