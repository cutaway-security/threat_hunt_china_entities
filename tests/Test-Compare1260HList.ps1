<#
.SYNOPSIS
    Offline tests for Compare-1260HList.ps1. No network, no test framework needed.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\tests\Test-Compare1260HList.ps1
#>

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$script = Join-Path $root 'Compare-1260HList.ps1'
$master = Get-Content -Raw -Encoding UTF8 -Path (Join-Path $root 'data\master\entities.master.json') | ConvertFrom-Json
$utf8 = New-Object Text.UTF8Encoding($false)
$failed = 0

function Assert($Condition, [string] $Message) {
    if ($Condition) { Write-Host "ok   $Message" } else { Write-Host "FAIL $Message" -ForegroundColor Red; $script:failed++ }
}

function New-Record([string] $Name, [string[]] $Aliases = @(), [string] $Parent) {
    $names = @(@{ NAME_TYPE = 'PRIMARY'; NAME_ORG = $Name }) + @($Aliases | ForEach-Object { @{ NAME_TYPE = 'ALIAS'; NAME_ORG = $_ } })
    $r = [ordered]@{
        DATA_SOURCE = 'US_DOD_1260H'
        RECORD_ID   = 'us_dod_1260h-' + ($Name.ToLowerInvariant() -replace '[^a-z0-9]+', '-').Trim('-')
        NAME_ORG    = $Name
        NAMES       = $names
        LISTED_ON   = '2026-06-10'
        SOURCE_URL  = 'https://www.federalregister.gov/d/2026-11571'
    }
    if ($Parent) { $r.PARENT_NAME = $Parent }
    $r
}

# Writes manifest.json + us_dod_1260h.jsonl the way a feed release lays them out.
function New-Feed($Records, $LaterNotices = @(), [switch] $Tamper) {
    $dir = Join-Path ([IO.Path]::GetTempPath()) ('compare-1260h-test-' + [guid]::NewGuid())
    New-Item -ItemType Directory -Path $dir | Out-Null
    $list = Join-Path $dir 'us_dod_1260h.jsonl'
    $lines = @($Records | ForEach-Object { ConvertTo-Json -InputObject $_ -Depth 5 -Compress })
    [IO.File]::WriteAllLines($list, [string[]] $lines, $utf8)
    $hash = (Get-FileHash -Algorithm SHA256 -Path $list).Hash.ToLowerInvariant()
    $manifest = @{ lists = @{ us_dod_1260h = @{ file = 'us_dod_1260h.jsonl'; sha256 = $hash; notes = @{ later_notices = @($LaterNotices) } } } }
    [IO.File]::WriteAllText((Join-Path $dir 'manifest.json'), (ConvertTo-Json -InputObject $manifest -Depth 6), $utf8)
    if ($Tamper) { [IO.File]::AppendAllText($list, "`n", $utf8) }
    $dir
}

# The list as the Federal Register prints it: same entities, different spellings for some.
$frSpelling = @{ 'Chengdu M&S Electronics Technology Co., Ltd. (M&S Electronics)' = 'Chengdu Mengsheng Electronic Technology Co., Ltd.' }
function Get-ListedRecords($Skip = @()) {
    foreach ($e in $master.entities) {
        if ($Skip -contains $e.company_id) { continue }
        $name = if ($frSpelling.ContainsKey($e.name)) { $frSpelling[$e.name] } else { $e.name -replace '\s*\([^)]*\)\s*$', '' }
        $aliases = @($e.short_alias | Where-Object { $_ })
        New-Record $name $aliases
        foreach ($s in $e.subsidiaries) { New-Record $s.name @() $name }
    }
}

$dirs = @()
try {
    # 1. A list that matches the dataset (including the M&S Electronics spelling and subsidiaries) gives no output.
    $dirs += ($d = New-Feed @(Get-ListedRecords))
    $out = @(& $script -FeedPath $d 6>$null)
    Assert ($out.Count -eq 0) "matching list: no differences (got $($out.Count))"

    # 2. A removal notice and a new designation are both reported.
    $first = $master.entities[0]
    $notice = @{ action = 'removed'; name = $first.name; date = '2026-11-10'; doc = '2026-22840'; url = 'https://www.federalregister.gov/d/2026-22840' }
    $records = @(Get-ListedRecords -Skip @($first.company_id)) + @(New-Record 'Example Newly Designated Co., Ltd.')
    $dirs += ($d = New-Feed $records @($notice))
    $out = @(& $script -FeedPath $d 6>$null)
    $gone = @($out | Where-Object { $_.Change -eq 'NoLongerListed' })
    $new = @($out | Where-Object { $_.Change -eq 'NotInMaster' })
    Assert ($out.Count -eq 2) "removal + addition: two differences (got $($out.Count))"
    Assert ($gone.Count -eq 1 -and $gone[0].CompanyId -eq $first.company_id) 'removed entity reported as NoLongerListed'
    Assert ($gone[0].Date -eq '2026-11-10' -and $gone[0].Source -like 'FR Doc. 2026-22840 *') 'removal carries the notice date and document'
    Assert ($new.Count -eq 1 -and $new[0].Name -eq 'Example Newly Designated Co., Ltd.') 'new designation reported as NotInMaster'

    # 3. A file that does not match the manifest hash is refused.
    $dirs += ($d = New-Feed @(Get-ListedRecords) -Tamper)
    $threw = $false
    try { & $script -FeedPath $d 6>$null | Out-Null } catch { $threw = $_.Exception.Message -like '*does not match manifest.json*' }
    Assert $threw 'hash mismatch is refused'
} finally {
    $dirs | ForEach-Object { Remove-Item -Recurse -Force -Path $_ -ErrorAction SilentlyContinue }
}

if ($failed) { Write-Host "$failed test(s) failed" -ForegroundColor Red; exit 1 }
Write-Host 'All tests passed' -ForegroundColor Green
