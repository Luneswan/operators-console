<#
.SYNOPSIS
    Installs Operator's Console on Windows.

.DESCRIPTION
    Downloads the latest release from GitHub and runs the installer. It installs
    for the current user only, so no administrator prompt appears.

    Run it with:
        irm https://raw.githubusercontent.com/Luneswan/operators-console/main/install.ps1 | iex

    Add -Portable to unpack it into your user folder instead of installing.
#>
[CmdletBinding()]
param(
    [string] $Repo = 'Luneswan/operators-console',
    [string] $Version = 'latest',
    [switch] $Portable
)

$ErrorActionPreference = 'Stop'

function Write-Step([string] $Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

if ($PSVersionTable.PSVersion.Major -lt 5) {
    throw "Windows PowerShell 5 or newer is required."
}
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

Write-Step "Looking up the latest release of $Repo"
$api = if ($Version -eq 'latest') {
    "https://api.github.com/repos/$Repo/releases/latest"
} else {
    "https://api.github.com/repos/$Repo/releases/tags/$Version"
}

try {
    $release = Invoke-RestMethod -Uri $api -Headers @{ 'User-Agent' = 'operators-console-installer' }
} catch {
    throw "Could not reach GitHub. Check your connection, or download the installer by hand from https://github.com/$Repo/releases"
}

$pattern = if ($Portable) { '*windows-portable.zip' } else { '*windows-setup.exe' }
$asset = $release.assets | Where-Object { $_.name -like $pattern } | Select-Object -First 1
if (-not $asset) {
    throw "Release $($release.tag_name) has no asset matching $pattern. See https://github.com/$Repo/releases"
}

$temp = Join-Path $env:TEMP ("operators-console-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $temp -Force | Out-Null
$download = Join-Path $temp $asset.name

$sizeMb = [math]::Round($asset.size / 1MB, 1)
Write-Step "Downloading $($asset.name) ($sizeMb MB)"
$before = $ProgressPreference
$ProgressPreference = 'SilentlyContinue'
try {
    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $download -UseBasicParsing
} finally {
    $ProgressPreference = $before
}

if ($Portable) {
    $target = Join-Path $env:LOCALAPPDATA 'Programs\Operators Console'
    Write-Step "Unpacking to $target"
    if (Test-Path $target) { Remove-Item $target -Recurse -Force }
    New-Item -ItemType Directory -Path $target -Force | Out-Null
    Expand-Archive -Path $download -DestinationPath $target -Force

    $exe = Get-ChildItem -Path $target -Filter 'operators-console.exe' -Recurse |
        Select-Object -First 1
    if (-not $exe) { throw "The archive did not contain operators-console.exe" }

    $shortcut = Join-Path ([Environment]::GetFolderPath('Desktop')) "Operator's Console.lnk"
    $shell = New-Object -ComObject WScript.Shell
    $link = $shell.CreateShortcut($shortcut)
    $link.TargetPath = $exe.FullName
    $link.WorkingDirectory = $exe.DirectoryName
    $link.Description = 'A guided Python curriculum'
    $link.Save()

    Write-Step 'Done. There is a shortcut on your desktop.'
    Write-Host "    Installed to $($exe.DirectoryName)" -ForegroundColor DarkGray
} else {
    Write-Step 'Running the installer'
    $arguments = @('/SILENT', '/SUPPRESSMSGBOXES', '/NORESTART')
    $process = Start-Process -FilePath $download -ArgumentList $arguments -Wait -PassThru
    if ($process.ExitCode -ne 0) {
        throw "The installer exited with code $($process.ExitCode)."
    }
    Write-Step 'Done. Look for Operator''s Console in your Start menu.'
}

Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue
Write-Host ''
Write-Host "Your progress lives in $env:APPDATA\Operator's Console" -ForegroundColor DarkGray
Write-Host 'Uninstalling never touches it.' -ForegroundColor DarkGray
