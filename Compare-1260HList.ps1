<#
.SYNOPSIS
    Check data/master/entities.master.json against the current Section 1260H list (Cutaway Security).

.DESCRIPTION
    The master dataset was extracted from the DoD notice dated 2026-06-08. DoD changes the list
    between annual notices with Federal Register notices of designation and removal. This script
    downloads the 1260H list from a pinned release of the us-restricted-parties feed
    (https://github.com/Mattbusel/us-restricted-parties, a daily build from the Federal Register),
    checks the file's SHA-256 against the release's manifest.json, and compares the listed parent
    entities with the entities in the master dataset.

    Names are compared after dropping case, punctuation, parentheses and corporate suffixes, and
    each side's aliases are used (e.g. "Chengdu M&S Electronics Technology Co., Ltd." here and
    "Chengdu Mengsheng Electronic Technology Co., Ltd." in the Federal Register text both carry the
    alias "M&S Electronics"). Only parent entities are compared; subsidiaries are not.

    Read-only: nothing in the repository is changed. Uses only Invoke-WebRequest, Get-FileHash and
    ConvertFrom-Json (Windows PowerShell 5.1 or PowerShell 7).

.PARAMETER Release
    Release tag of the feed to read. Defaults to a pinned tag; pass 'latest' for the newest build.

.PARAMETER FeedPath
    Folder that already holds manifest.json and us_dod_1260h.jsonl (offline use). Skips the download.
    The SHA-256 check still runs.

.PARAMETER MasterPath
    The master dataset. Defaults to data/master/entities.master.json next to this script.

.OUTPUTS
    One PSCustomObject per difference (Change, Name, CompanyId, Date, Source) to STANDARD OUTPUT:
      NoLongerListed - in the master dataset, not on the current list (Source is the removal notice
                       when the feed has one).
      NotInMaster    - on the current list, not in the master dataset.
    A status line goes to the console (host) stream. No output objects means the master dataset
    matches the current list.

.EXAMPLE
    .\Compare-1260HList.ps1

.EXAMPLE
    .\Compare-1260HList.ps1 -Release latest | Format-Table -AutoSize
#>

[CmdletBinding()]
param(
    [string] $Release = 'data-2026-11-18',
    [string] $FeedPath,
    [string] $MasterPath = (Join-Path $PSScriptRoot 'data\master\entities.master.json')
)

$ErrorActionPreference = 'Stop'
$FeedRepo = 'https://github.com/Mattbusel/us-restricted-parties'
$ListFile = 'us_dod_1260h.jsonl'

function Get-NameKey([string] $Name) {
    if (-not $Name) { return $null }
    $s = $Name.ToLowerInvariant() -replace '\([^)]*\)', ' ' -replace '[^a-z0-9]+', ' '
    $s = $s -replace '\b(co|ltd|inc|corp|corporation|company|limited|group|the|llc|plc)\b', ' '
    $s = ($s -split '\s+' | Where-Object { $_ }) -join ' '
    if ($s) { $s } else { $null }
}

# 1. Get the release files.
if ($FeedPath) {
    $dir = $FeedPath
} else {
    $dir = Join-Path ([IO.Path]::GetTempPath()) ('us-restricted-parties-' + [guid]::NewGuid())
    New-Item -ItemType Directory -Path $dir | Out-Null
    $base = if ($Release -eq 'latest') { "$FeedRepo/releases/latest/download" } else { "$FeedRepo/releases/download/$Release" }
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    foreach ($f in 'manifest.json', $ListFile) {
        Invoke-WebRequest -UseBasicParsing -Uri "$base/$f" -OutFile (Join-Path $dir $f)
    }
}

try {
    # 2. Verify the list file against the manifest before using it.
    $manifest = Get-Content -Raw -Encoding UTF8 -Path (Join-Path $dir 'manifest.json') | ConvertFrom-Json
    $listInfo = $manifest.lists.us_dod_1260h
    $listPath = Join-Path $dir $ListFile
    $actual = (Get-FileHash -Algorithm SHA256 -Path $listPath).Hash.ToLowerInvariant()
    if (-not $listInfo -or $actual -ne ([string]$listInfo.sha256).ToLowerInvariant()) {
        throw "SHA-256 of $ListFile ($actual) does not match manifest.json ($($listInfo.sha256)). Not using it."
    }

    # 3. Parent entities on the current list, with all their names.
    $parents = @(Get-Content -Encoding UTF8 -Path $listPath |
        Where-Object { $_.Trim() } |
        ForEach-Object { $_ | ConvertFrom-Json } |
        Where-Object { -not $_.PARENT_NAME })
    $feedKeys = @{}
    foreach ($p in $parents) {
        foreach ($n in $p.NAMES) {
            $k = Get-NameKey $n.NAME_ORG
            if ($k) { $feedKeys[$k] = $p }
        }
    }
    $removals = @{}
    foreach ($r in @($listInfo.notes.later_notices)) {
        if ($r -and $r.action -eq 'removed') { $removals[(Get-NameKey $r.name)] = $r }
    }
} finally {
    if (-not $FeedPath) { Remove-Item -Recurse -Force -Path $dir -ErrorAction SilentlyContinue }
}

# 4. Compare.
$master = Get-Content -Raw -Encoding UTF8 -Path $MasterPath | ConvertFrom-Json
$matched = @{}
$diffs = @(foreach ($e in $master.entities) {
    $keys = @((Get-NameKey $e.name), (Get-NameKey $e.short_alias)) | Where-Object { $_ }
    $hit = $null
    foreach ($k in $keys) { if ($feedKeys.ContainsKey($k)) { $hit = $feedKeys[$k]; break } }
    if ($hit) {
        $matched[$hit.RECORD_ID] = $true
        continue
    }
    $notice = $null
    foreach ($k in $keys) { if ($removals.ContainsKey($k)) { $notice = $removals[$k]; break } }
    [pscustomobject]@{
        Change    = 'NoLongerListed'
        Name      = $e.name
        CompanyId = $e.company_id
        Date      = if ($notice) { $notice.date } else { $null }
        Source    = if ($notice) { "FR Doc. $($notice.doc) $($notice.url)" } else { $null }
    }
}
foreach ($p in $parents) {
    if ($matched.ContainsKey($p.RECORD_ID)) { continue }
    [pscustomobject]@{
        Change    = 'NotInMaster'
        Name      = $p.NAME_ORG
        CompanyId = $null
        Date      = $p.LISTED_ON
        Source    = $p.SOURCE_URL
    }
})

$label = if ($FeedPath) { $FeedPath } else { "$FeedRepo release $Release" }
$summary = "{0} entities in the master dataset, {1} listed parent entities in {2} (SHA-256 verified)." -f @($master.entities).Count, $parents.Count, $label
if ($diffs.Count) {
    Write-Host ("$summary {0} difference(s); update the master dataset." -f $diffs.Count) -ForegroundColor Yellow
} else {
    Write-Host "$summary The master dataset matches the current list." -ForegroundColor Green
}
$diffs
