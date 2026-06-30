"""Source adapters. Each returns raw facts + the source URL; claim-typing happens in verify.py.

Read-only HTTP against public sources (SR-02). No target software is installed or executed.
"""
import json, os, time, urllib.parse, urllib.request

UA = "threat_hunt_china_entities/0.2 (Cutaway Security; defensive research)"
WINGET_API = "https://api.github.com/repos/microsoft/winget-pkgs/contents/manifests"
WINGET_RAW = "https://raw.githubusercontent.com/microsoft/winget-pkgs/master/manifests"
NVD_CPE = "https://services.nvd.nist.gov/rest/json/cpes/2.0"
VT_FILE = "https://www.virustotal.com/api/v3/files/"


class SourceError(Exception):
    pass


def _get(url, headers=None, timeout=30, retries=2, backoff=2.0):
    last = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < retries:   # rate limit / throttle -> back off
                time.sleep(backoff * (attempt + 1)); last = e; continue
            return e.code, e.read().decode("utf-8", "replace") if e.fp else ""
        except Exception as e:  # noqa: BLE001 - network is best-effort here
            last = e
            if attempt < retries:
                time.sleep(backoff * (attempt + 1)); continue
            raise SourceError(f"GET {url} failed: {e}") from e
    raise SourceError(f"GET {url} failed after retries: {last}")


def resolve_keys_dir():
    return os.environ.get("KEYS_DIR") or os.path.expanduser("~/.claude/keys")


def vt_api_key():
    p = os.path.join(resolve_keys_dir(), "virustotal.key.txt")
    if not os.path.isfile(p):
        raise SourceError(f"VirusTotal key not found at {p} (set KEYS_DIR)")
    return open(p, encoding="utf-8").read().strip().splitlines()[0].strip()


# ---- winget-pkgs ---------------------------------------------------------------------------------

def _winget_folder(identifier):
    """A PackageIdentifier like 'DJI.DJIAssistant2.ConsumerDronesSeries' maps to nested folders
    manifests/d/DJI/DJIAssistant2/ConsumerDronesSeries; the manifest file uses the full dotted id."""
    first = identifier[0].lower()
    return f"{first}/" + "/".join(identifier.split("."))


def url_head(url, timeout=20):
    """Read-only liveness check (HEAD; falls back to a 1-byte ranged GET). Confirms a vendor CDN
    serves a file without downloading or executing it (SR-02). Returns HTTP status int or None."""
    for method, hdr in (("HEAD", {}), ("GET", {"Range": "bytes=0-0"})):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, **hdr})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if e.code in (405, 501) and method == "HEAD":
                continue
            return e.code
        except Exception:
            return None
    return None


def winget_versions(identifier):
    """List committed version directories for a PackageIdentifier."""
    status, body = _get(f"{WINGET_API}/{_winget_folder(identifier)}",
                        headers={"Accept": "application/vnd.github+json"})
    if status != 200:
        raise SourceError(f"winget {identifier}: HTTP {status}")
    names = [e["name"] for e in json.loads(body) if e.get("type") == "dir"]
    # version dirs start with a digit (optionally a leading v/V); non-version subdirs are ignored
    import re
    return sorted([n for n in names if re.match(r"[vV]?\d", n)], key=_verkey)


def _verkey(v):
    out = []
    for part in v.lstrip("vV").replace("-", ".").split("."):
        out.append((0, int(part)) if part.isdigit() else (1, part))
    return out


def winget_installer(identifier, version):
    """Return the parsed installer manifest dict for a specific version (YAML)."""
    import yaml
    url = f"{WINGET_RAW}/{_winget_folder(identifier)}/{version}/{identifier}.installer.yaml"
    status, body = _get(url)
    if status != 200:
        raise SourceError(f"winget installer manifest {identifier}/{version}: HTTP {status}")
    data = yaml.safe_load(body)
    data["_source_url"] = url
    return data


def winget_latest(identifier):
    versions = winget_versions(identifier)
    if not versions:
        raise SourceError(f"winget {identifier}: no versions")
    return winget_installer(identifier, versions[-1])


# ---- NIST NVD CPE --------------------------------------------------------------------------------

def nvd_cpe(keyword, limit=5):
    q = urllib.parse.urlencode({"keywordSearch": keyword, "resultsPerPage": limit})
    status, body = _get(f"{NVD_CPE}?{q}", timeout=40)
    if status != 200:
        raise SourceError(f"NVD CPE '{keyword}': HTTP {status}")
    prods = json.loads(body).get("products", [])
    return [p["cpe"]["cpeName"] for p in prods if "cpe" in p and "cpeName" in p["cpe"]]


# ---- VirusTotal ----------------------------------------------------------------------------------

def cpe_wildcard(cpe_name):
    """Canonicalize an NVD CPE 2.3 name to vendor:product with EVERYTHING after wildcarded
    (no version pin; DR-10). 'cpe:2.3:a:tencent:wechat:6.3.18:*:*:*:*:android:*:*' ->
    'cpe:2.3:a:tencent:wechat:*:*:*:*:*:*:*:*'."""
    parts = cpe_name.split(":")
    if len(parts) < 6 or parts[0] != "cpe" or parts[1] != "2.3":
        return None
    part, vendor, product = parts[2], parts[3], parts[4]
    return f"cpe:2.3:{part}:{vendor}:{product}:" + ":".join(["*"] * 7)


def vt_file(sha256, key=None):
    key = key or vt_api_key()
    # VT public API is ~4 lookups/min. Fail FAST on 429 (one short retry) and let the caller degrade
    # the tier rather than hang the whole run; a later pass can re-fetch when quota resets.
    status, body = _get(VT_FILE + sha256, headers={"x-apikey": key}, timeout=40,
                        retries=1, backoff=8.0)
    if status == 404:
        return {"found": False, "_source_url": VT_FILE + sha256}
    if status == 429:
        return {"found": False, "rate_limited": True, "_source_url": VT_FILE + sha256}
    if status != 200:
        raise SourceError(f"VT {sha256[:12]}: HTTP {status}")
    a = json.loads(body).get("data", {}).get("attributes", {})
    sig = a.get("signature_info", {}) or {}
    return {
        "found": True,
        "meaningful_name": a.get("meaningful_name"),
        "names": a.get("names", [])[:12],
        "type_description": a.get("type_description"),
        "signers": sig.get("signers"),
        "verified": sig.get("verified"),
        "product": sig.get("product"),
        "_source_url": VT_FILE + sha256,
    }
