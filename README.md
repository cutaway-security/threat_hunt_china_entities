# Section 1260H Designated-Vendor Software — Company & Software List

**Cutaway Security · AI-assisted, best-effort.** A list of the companies on the U.S. DoD **Section
1260H** "Chinese military companies" list and the software they produce that can be installed on
computers. A 1260H designation is a **corporate-affiliation flag — not a finding that the software is
malicious.** This is exposure/inventory analysis to help administrators recognize and find this
software. **Report findings for human review; do not auto-block.**

## Findings

Of the **79 designated parent entities** (plus 108 named subsidiaries and 11 delisted entities; WuXi AppTec
was removed by a Federal Register notice on 2026-11-10):

- **20 publish installable Windows software** (surveillance, consumer, networking, device-management,
  security, and engineering tools).
- **3** deliver primarily **server / Linux** platforms.
- **19** are **device / firmware** vendors (chips, displays, batteries, optics, sensors).
- **25** produce **no installable software** (aerospace, shipping, nuclear, chemical, construction,
  logistics, services).
- **12** are **candidates** — likely to publish software but not yet confirmed for Windows.

The Windows-software vendors include the surveillance majors (**Hikvision, Dahua**), networking
(**Huawei, TP-Link**), consumer/communications (**Tencent, Qihoo 360, Alibaba, Baidu**), devices
(**DJI, Autel, Quectel**), and several sensor/LiDAR, storage, and security vendors. The full list with
products, descriptions, sources, and confidence is in **[CATALOG.md](CATALOG.md)**.

## What's here

| File | For | What it is |
|---|---|---|
| **CATALOG.md** | Admins / analysts (reading) | The readable company → software list, by category, with sources and confidence tiers. |
| **data/master/entities.master.json** | Tools | The full dataset (entities, software, sources, dispositions) for ingestion. |
| **companies_software.csv** | Spreadsheets / simple tools | A flat company + software list. |
| **Find-DesignatedVendorSoftware.ps1** | Hunters / admins | A PowerShell sweep of installed software for these vendors (see below). |
| **METHODOLOGY.md** | Reviewers | How it was built, the discipline, and the limitations. |
| **Compare-1260HList.ps1** | Maintainers | Checks the dataset against the current 1260H list (see below). |

## Finding it on your endpoints

`Find-DesignatedVendorSoftware.ps1` enumerates installed software from the Windows uninstall registry
and flags entries whose **Publisher or product name** matches a designated vendor. Run it on a host (or
push via your management tooling):

```powershell
powershell -ExecutionPolicy Bypass -File .\Find-DesignatedVendorSoftware.ps1
```

**Output — it goes to standard output, not a file (unless you ask).**
- A one-line **status/summary** prints to the console (e.g. "4 designated-vendor software item(s) found. REVIEW…").
- Each match is emitted to **stdout as an object** (`Host, DisplayName, DisplayVersion, Publisher, InstallLocation, InstallDate`). Run interactively you'll see them listed; the status line is kept on a separate stream so it does **not** pollute piped or redirected output.
- It creates **no file by itself.** To save results, choose one:
  - `-OutputCsv C:\Temp\found.csv` — built-in CSV file output.
  - `... | Export-Csv -NoTypeInformation found.csv` — pipe the objects into your own CSV / EDR collection tooling.
  - `... > found.txt` — redirect the readable output to a text file.

Validated on Windows 10 Pro (PowerShell 5.1): the no-match path, the registry/Publisher match path, and all three save options work as described.

**Reduce false negatives — read this.** This method only sees software registered in Add/Remove
Programs with a recognizable vendor string. It **will miss**: portable/unregistered apps, embedded SDK
components (DLLs inside other software), renamed binaries, and software whose Publisher is a localized
or unexpected name not in the vendor list. **Treat "no match" as "not found by this method," not "the
software is absent."** Pair it with the catalog for manual review and conversations with system owners.

## Keeping the list current

DoD adds and removes 1260H entities between annual lists with Federal Register notices.
`Compare-1260HList.ps1` downloads the current list from a pinned release of
[us-restricted-parties](https://github.com/Mattbusel/us-restricted-parties) (a daily build from the
Federal Register), checks the file's SHA-256 against that release's `manifest.json`, and prints each
parent entity that is in `entities.master.json` but no longer listed (with the removal notice), or
listed but missing here. It is read-only and needs only Windows PowerShell 5.1 or later.

```powershell
.\Compare-1260HList.ps1                  # pinned release
.\Compare-1260HList.ps1 -Release latest  # newest daily build
```

No output objects means the dataset matches the list. `tests/Test-Compare1260HList.ps1` runs it
against local test files (no network).

## Limitations

Best-effort and built from public sources only — the 1260H notice plus vendor pages, winget, NIST NVD,
and VirusTotal — **without installing any of the software.** The **company/software list is the
high-confidence deliverable.** Exact install-time artifacts (installed exe names, install paths,
services, SDK DLLs) are **not** comprehensively included; they require verification and enrichment.
Windows first; OT/ICS hunting should be passive. No file hashes, no version-pinned values. See
`METHODOLOGY.md`.

## License

MIT (see `LICENSE`). This is a Cutaway Security research effort; attribution appreciated.
