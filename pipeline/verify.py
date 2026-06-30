"""Assemble indicators from typed claims, with tiering rules that enforce DR-02a.

Key rule: a source is credited only for the claim it proves. Attribution evidence (a VirusTotal
code-signer match, an NVD canonical name) can never by itself promote a HOST-PRESENCE indicator
(REGISTRY_KEY / SERVICE_NAME / FILE_PATH / DLL_NAME) to VERIFIED. Those need a vendor-official source
for that specific artifact.
"""
import datetime, os, re, urllib.parse

from . import sources as S

OFFICIAL_DOMAIN_HINTS = ("qq.com", "huawei.com", "hihonor.com", "dji.com", "djicdn.com",
                         "360totalsecurity.com", "360.cn", "360safe.com", "tp-link.com",
                         "omadanetworks.com", "tencent.com", "weixin.qq.com")

HOST_PRESENCE_TYPES = {"REGISTRY_KEY", "SERVICE_NAME", "FILE_PATH", "FOLDER_PATH", "DLL_NAME"}


def today():
    return datetime.date.today().isoformat()


def normalize_filename(name):
    """Strip version and architecture tokens to a stable, version-independent form (DR-10).
    'WeChatSetup_3.9.12.57_x64.exe' -> 'WeChatSetup.exe'."""
    base = os.path.basename(urllib.parse.urlparse(name).path) if "/" in name else name
    base = urllib.parse.unquote_plus(base)  # decode %20/+ etc. from CDN URLs
    stem, dot, ext = base.rpartition(".")
    stem = stem or base
    # drop version-like and arch tokens delimited by _ - or space
    toks = re.split(r"[ _\-]+", stem)
    keep = [t for t in toks if t and not re.fullmatch(r"[vV]?\d+(\.\d+)*", t)
            and t.lower() not in {"x64", "x86", "amd64", "arm64", "win64", "win32", "setup", "install", "installer"}]
    out = "".join(keep) if keep else (toks[0] if toks else stem)
    return f"{out}.{ext}" if dot else out


GENERIC_STEMS = {"public", "download", "index", "default", "get", "file", "setup", "install",
                 "installer", "update", "main", "online", "offline", "client", "app"}


def clean_installer_name(url):
    """Return a clean, version-free installer filename from a URL, or None if it cannot be trusted.
    Rejects servlet paths ('public'), version-stamped names ('QQ9.7.23.29392.exe'), date/build stamps,
    and generic names. Deriving a stable name from a versioned/garbage URL is exactly the
    'derived not verified' failure we forbid (DR-10)."""
    base = urllib.parse.unquote_plus(os.path.basename(urllib.parse.urlparse(url).path)).strip()
    m = re.match(r"^([A-Za-z0-9 ._+\-]+)\.(exe|msi)$", base, re.I)
    if not m:
        return None
    stem, ext = m.group(1).strip(), m.group(2).lower()
    if re.search(r"\d+\.\d+", base) or re.search(r"\d{5,}", base):  # version or build/date stamp
        return None
    if stem.lower() in GENERIC_STEMS or len(stem) < 3:
        return None
    return re.sub(r"\s+", " ", stem) + "." + ext


def _is_official_domain(url):
    host = urllib.parse.urlparse(url).netloc.lower()
    return any(h in host for h in OFFICIAL_DOMAIN_HINTS)


def gather_claims(software):
    """Run sources for one software product; return (claims, facts, fetch_log).
    `software` = dict with winget=(publisher,package), nvd_keyword, name."""
    claims, facts, log = [], {}, []

    # --- winget ---
    try:
        m = S.winget_latest(software["winget"])
        inst = (m.get("Installers") or [{}])[0]
        url = inst.get("InstallerUrl") or ""
        man_url = m.get("_source_url", "")
        facts["installer_url"] = url
        facts["installer_sha256"] = inst.get("InstallerSha256") or m.get("InstallerSha256")
        installer = clean_installer_name(url) if url else None
        if installer:
            facts["installer_filename"] = installer
            official = _is_official_domain(url)
            facts["installer_official_domain"] = official
            claims.append({"claim_type": "installer_filename", "source_class": "winget",
                           "source_url": man_url,
                           "proves": f"winget lists the official installer {installer} at {url}",
                           "date_verified": today(), "raw_value": os.path.basename(urllib.parse.urlparse(url).path)})
            # Vendor-official confirmation (VT-independent): does the vendor's own CDN serve it?
            if official:
                status = S.url_head(url)
                log.append({"source": "vendor_cdn_head", "url": url, "status": status})
                if status in (200, 206):
                    facts["installer_official_live"] = True
                    claims.append({"claim_type": "installer_filename", "source_class": "vendor_official",
                                   "source_url": url,
                                   "proves": f"vendor official CDN serves {installer} (HTTP {status}) — vendor-distributed installer",
                                   "date_verified": today()})
        afe = m.get("AppsAndFeaturesEntries") or inst.get("AppsAndFeaturesEntries")
        if afe and (afe[0].get("ProductCode") or afe[0].get("UpgradeCode")):
            e = afe[0]
            facts["arp"] = e
            claims.append({"claim_type": "arp_publisher", "source_class": "winget",
                           "source_url": man_url,
                           "proves": (f"Add/Remove Programs entry: ProductCode={e.get('ProductCode')} "
                                      f"DisplayName={e.get('DisplayName')!r} Publisher={e.get('Publisher')!r} "
                                      f"type={e.get('InstallerType')}"),
                           "date_verified": today()})
        log.append({"source": "winget", "url": man_url, "status": "ok", "version": m.get("PackageVersion")})
    except S.SourceError as ex:
        log.append({"source": "winget", "status": "error", "error": str(ex)})

    # --- NVD CPE ---
    try:
        names = S.nvd_cpe(software["nvd_keyword"])
        cpe = next((S.cpe_wildcard(n) for n in names if S.cpe_wildcard(n)), None)
        if cpe:
            facts["cpe"] = cpe
            claims.append({"claim_type": "product_naming", "source_class": "nvd_cpe",
                           "source_url": f"{S.NVD_CPE}?keywordSearch={urllib.parse.quote(software['nvd_keyword'])}",
                           "proves": f"canonical naming {cpe}", "date_verified": today(),
                           "raw_value": names[0] if names else None})
        log.append({"source": "nvd_cpe", "status": "ok", "cpe": cpe})
    except S.SourceError as ex:
        log.append({"source": "nvd_cpe", "status": "error", "error": str(ex)})

    # --- VirusTotal (on the installer hash) ---
    sha = facts.get("installer_sha256")
    if sha:
        try:
            vt = S.vt_file(sha)
            if vt.get("found"):
                facts["vt"] = vt
                if vt.get("signers"):
                    claims.append({"claim_type": "binary_signer", "source_class": "virustotal",
                                   "source_url": vt["_source_url"],
                                   "proves": f"installer binary is code-signed by: {vt['signers']} (verified={vt.get('verified')})",
                                   "date_verified": today(), "raw_value": vt.get("meaningful_name")})
                facts["vt_names"] = vt.get("names", [])
                log.append({"source": "virustotal", "status": "ok", "signer": vt.get("signers"), "verified": vt.get("verified")})
            elif vt.get("rate_limited"):
                log.append({"source": "virustotal", "status": "rate_limited"})
            else:
                log.append({"source": "virustotal", "status": "not_found"})
        except S.SourceError as ex:
            log.append({"source": "virustotal", "status": "error", "error": str(ex)})

    return claims, facts, log


def _signer_matches_vendor(signers, vendor_tokens):
    if not signers:
        return False
    s = signers.lower()
    return any(t.lower() in s for t in vendor_tokens)


def assemble_indicators(software, claims, facts, vendor_tokens):
    """Build indicators from claims with tier rules. Returns list of indicator dicts (schema shape)."""
    inds = []
    vt_signed_vendor = "vt" in facts and _signer_matches_vendor(facts["vt"].get("signers"), vendor_tokens)

    # 1) Installer FILE_NAME. VERIFIED only if VT cryptographically ties THIS binary to the vendor AND
    #    the installer came from an official vendor domain; else CORROBORATED; else REPORTED.
    if facts.get("installer_filename"):
        c = [x for x in claims if x["claim_type"] in ("installer_filename", "binary_signer", "product_naming")]
        n_classes = len(set(x["source_class"] for x in c))
        # Vendor-official confirmation of THIS installer: either the vendor CDN serves it (live HEAD),
        # or VT cryptographically ties the binary to the vendor.
        vendor_official = facts.get("installer_official_live") or (vt_signed_vendor and facts.get("installer_official_domain"))
        if vendor_official and n_classes >= 2:
            tier = "VERIFIED"
        elif n_classes >= 2 and facts.get("installer_official_domain"):
            tier = "CORROBORATED"
        else:
            tier = "REPORTED"
        inds.append(_ind("FILE_NAME", facts["installer_filename"], "product_installed", tier, c))

    # 2) Installed executable name(s) from VT observed names -> CORROBORATED at best (observed, not vendor-doc'd).
    if vt_signed_vendor:
        exe = _pick_installed_exe(facts.get("vt_names", []), software.get("exe_hint"))
        if exe:
            c = [x for x in claims if x["claim_type"] in ("binary_signer", "product_naming")]
            inds.append(_ind("FILE_NAME", exe, "product_installed", "CORROBORATED", c,
                             note="installed executable observed by VirusTotal; not vendor-documented"))

    # 3) Uninstall REGISTRY_KEY from winget ARP -> host-presence; catalog-sourced => CORROBORATED
    #    (vendor-official would be needed for VERIFIED, DR-02a).
    if facts.get("arp"):
        e = facts["arp"]; pc = e.get("ProductCode") or e.get("UpgradeCode")
        if pc:
            val = f"HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{pc}"
            c = [x for x in claims if x["claim_type"] in ("arp_publisher", "binary_signer")]
            inds.append(_ind("REGISTRY_KEY", val, "product_installed", "CORROBORATED", c,
                             note=f"Uninstall key; DisplayName={e.get('DisplayName')!r} Publisher={e.get('Publisher')!r}"))
    return inds


def _pick_installed_exe(names, hint):
    def usable(n):
        if not n.lower().endswith(".exe") or any(x in n.lower() for x in ("setup", "install", "update")):
            return None
        return clean_installer_name(n)  # clean, version-free, non-generic
    for n in names:  # prefer the hinted product executable
        if hint and hint.lower() in n.lower():
            c = usable(n)
            if c:
                return c
    for n in names:
        c = usable(n)
        if c:
            return c
    return None


def _ind(itype, value, presence, tier, claims, note=None):
    d = {"indicator_type": itype, "value": value, "presence_class": presence,
         "confidence_tier": tier, "date_verified": today(), "claims": claims}
    if note:
        d["notes"] = note
    return d
