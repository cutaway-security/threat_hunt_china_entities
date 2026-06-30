<#
.SYNOPSIS
    Sweep installed software for vendors on the U.S. DoD Section 1260H list (Cutaway Security).

.DESCRIPTION
    Reads the Windows "uninstall" registry keys (Add/Remove Programs records) for the local machine
    and current user, and flags entries whose Publisher or DisplayName matches a 1260H entity that is
    known to publish installable Windows software (see CATALOG.md).

    A Section 1260H designation is a CORPORATE-AFFILIATION flag, NOT a malware finding. This is
    exposure/inventory discovery. REPORT matches for human review; do NOT auto-block — much of this
    software (e.g. WeChat, 360, DJI tools) may be legitimately user-installed.

    Deliberately does NOT use Win32_Product (WMI), which triggers an MSI reconfiguration of every
    installed package and is slow; it reads the registry directly.

.NOTES
    REDUCING FALSE NEGATIVES — this method only sees software that:
      * is registered in Add/Remove Programs (so it MISSES portable / unregistered apps), and
      * carries a recognizable vendor string in Publisher or DisplayName.
    It will MISS: embedded SDK components (DLLs shipped inside other software), renamed binaries, and
    software whose Publisher is a localized/unexpected name not in the $Vendors list below.
    Treat "no match" as "not found by this method", NOT "the software is absent". Extend $Vendors for
    your environment, and corroborate with the catalog and on-host file/folder review.
#>

[CmdletBinding()]
param(
    # Publisher / DisplayName patterns for 1260H vendors that publish Windows software (from CATALOG.md).
    [string[]] $Vendors = @(
        'Tencent', 'WeChat', 'Weixin', '腾讯',
        'Hikvision', '海康',
        'Dahua', '大华',
        'Huawei', '华为',
        'DJI', 'Da-?Jiang', 'SZ DJI', '大疆',
        'TP-?Link', 'Omada', 'Pharos',
        'Qihoo', '360 ?Total ?Security', '奇虎', '360安全',
        'Autel', 'Maxi',
        'Quectel',
        'Baidu', '百度',
        'Alibaba', 'DingTalk', '钉钉', '阿里',
        'Hesai', 'RoboSense', 'Unitree',
        'Yangtze Memory', 'YMTC', 'ZHITAI', '致铛',
        'Geosun',
        'GTCOM', 'Global Tone',
        'Inspur', '浪潮',
        'Meiya', 'SDIC',
        'China Telecom', 'Tianyi', '天翼', '中国电信',
        'Knownsec', 'ZoomEye'
    )
)

$pattern = ($Vendors -join '|')

$paths = @(
    'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*'
)

$hits = Get-ItemProperty -Path $paths -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -and ($_.Publisher -match $pattern -or $_.DisplayName -match $pattern) } |
    Select-Object @{N = 'Host'; E = { $env:COMPUTERNAME } },
                  DisplayName, DisplayVersion, Publisher, InstallLocation, InstallDate |
    Sort-Object Publisher, DisplayName

if ($hits) {
    $hits | Format-Table -AutoSize
    Write-Host ""
    Write-Host ("[{0}] {1} designated-vendor software item(s) found. REVIEW (do not auto-block); confirm against CATALOG.md." -f $env:COMPUTERNAME, @($hits).Count) -ForegroundColor Yellow
} else {
    Write-Host ("[{0}] No designated-vendor software found by this method. NOTE: absence here is not proof of absence (see false-negative note in this script's header)." -f $env:COMPUTERNAME) -ForegroundColor Green
}

# Emit objects too, so this can pipe into Export-Csv / your collection tooling.
$hits
