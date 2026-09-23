<#
.SYNOPSIS
    Installs or updates Operator's Console on Windows.

.DESCRIPTION
    Downloads the latest release from GitHub, checks it against the SHA256SUMS
    published with that release, and installs it for the current user only, so
    no administrator prompt appears.

    Run it with:
        irm https://raw.githubusercontent.com/Luneswan/operators-console/main/install.ps1 | iex

    Running it again on a machine that already has the app is an in-place
    update. Your progress lives in %APPDATA%\Operator's Console and is never
    touched, whichever way you install.

    Add -Portable to unpack it into your user folder instead of installing.
    Add -SkipVerify only to install a release published before checksums
    existed; it turns off the one check that would catch a swapped download.

.NOTES
    Trust root: this script trusts GitHub and the owner of the repository. The
    checksum proves the bytes match what that release published; it does not
    prove who published it. Code signing would be the next step.
#>
[CmdletBinding()]
param(
    [string] $Repo = 'Luneswan/operators-console',
    [string] $Version = 'latest',
    [switch] $Portable,
    [switch] $SkipVerify
)

$ErrorActionPreference = 'Stop'

function Write-Step([string] $Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Assert-Https([string] $Url, [string] $What) {
    if ($Url -notmatch '^https://') {
        throw "Refusing to fetch $What over an insecure connection: $Url"
    }
    return $Url
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

# The portable zip is "...-windows-x64-portable.zip" from 1.1.0; the looser
# pattern also finds the "...-windows-portable.zip" of older releases.
$pattern = if ($Portable) { '*windows*portable.zip' } else { '*windows-setup.exe' }
$asset = $release.assets | Where-Object { $_.name -like $pattern } | Select-Object -First 1
if (-not $asset) {
    throw "Release $($release.tag_name) has no asset matching $pattern. See https://github.com/$Repo/releases"
}

$temp = Join-Path $env:TEMP ("operators-console-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $temp -Force | Out-Null
$download = Join-Path $temp $asset.name

# ---------------------------------------------------------------- checksum --
# Fetched from the same release as the asset, before the asset itself, so a
# release that publishes no checksums stops the install before anything is
# downloaded rather than after.
$expected = $null
$sumsAsset = $release.assets | Where-Object { $_.name -eq 'SHA256SUMS' } | Select-Object -First 1
if ($sumsAsset) {
    $sumsUrl = Assert-Https $sumsAsset.browser_download_url 'the checksum file'
    $sums = (Invoke-WebRequest -Uri $sumsUrl -UseBasicParsing).Content
    foreach ($line in ($sums -split "`n")) {
        $parts = ($line.Trim() -split '\s+', 2)
        if ($parts.Count -eq 2 -and $parts[1].TrimStart('*') -eq $asset.name) {
            $expected = $parts[0].ToLower()
            break
        }
    }
}

if (-not $expected) {
    if (-not $SkipVerify) {
        Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue
        throw "This release does not publish a SHA256SUMS file, so the download cannot be verified. Refusing to install it. Re-run with -SkipVerify to install it anyway."
    }
    Write-Warning "Installing without verification because -SkipVerify was given."
}

# ---------------------------------------------------------------- download --
$assetUrl = Assert-Https $asset.browser_download_url 'the application'
$sizeMb = [math]::Round($asset.size / 1MB, 1)
Write-Step "Downloading $($asset.name) ($sizeMb MB)"
$before = $ProgressPreference
$ProgressPreference = 'SilentlyContinue'
try {
    Invoke-WebRequest -Uri $assetUrl -OutFile $download -UseBasicParsing
} finally {
    $ProgressPreference = $before
}

if ($expected) {
    Write-Step 'Checking the download against the release checksum'
    $actual = (Get-FileHash -Path $download -Algorithm SHA256).Hash.ToLower()
    if ($actual -ne $expected) {
        Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue
        throw "The download does not match the checksum published with the release. It has been discarded and nothing was installed."
    }
}

# --------------------------------------------------------- running instance --
# Replacing files under a running executable fails on Windows, so ask the app
# to close first and only force it if it will not.
$running = Get-Process -Name 'operators-console' -ErrorAction SilentlyContinue
if ($running) {
    Write-Step 'Closing the running copy of Operator''s Console'
    foreach ($proc in $running) {
        try { $null = $proc.CloseMainWindow() } catch { }
    }
    $deadline = (Get-Date).AddSeconds(20)
    while ((Get-Date) -lt $deadline -and (Get-Process -Name 'operators-console' -ErrorAction SilentlyContinue)) {
        Start-Sleep -Milliseconds 300
    }
    $stubborn = Get-Process -Name 'operators-console' -ErrorAction SilentlyContinue
    if ($stubborn) {
        Write-Warning 'It did not close on its own; stopping it.'
        $stubborn | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
}

if ($Portable) {
    # %LOCALAPPDATA%\Programs is the program directory. The learner's progress
    # lives under %APPDATA%, a different root, so nothing here can reach it.
    $target = Join-Path $env:LOCALAPPDATA 'Programs\Operators Console'
    Write-Step "Unpacking to $target"

    # Unpack into a staging folder first: a failed or partial extraction then
    # leaves the working installation alone, and -Force never expands over a
    # directory that holds anything but the previous build.
    $staging = Join-Path $temp 'unpacked'
    New-Item -ItemType Directory -Path $staging -Force | Out-Null
    Expand-Archive -Path $download -DestinationPath $staging -Force

    $newExe = Get-ChildItem -Path $staging -Filter 'operators-console.exe' -Recurse |
        Select-Object -First 1
    if (-not $newExe) { throw "The archive did not contain operators-console.exe" }

    $previous = "$target.previous"
    if (Test-Path $previous) { Remove-Item $previous -Recurse -Force }
    if (Test-Path $target) { Move-Item $target $previous }
    New-Item -ItemType Directory -Path (Split-Path $target) -Force | Out-Null
    try {
        Move-Item $staging $target
    } catch {
        if (Test-Path $previous) { Move-Item $previous $target }
        throw "The install failed and the previous version was put back: $_"
    }
    if (Test-Path $previous) {
        # Anything the learner kept beside the app is part of neither build:
        # it moves back, rather than being deleted along with the old build.
        Get-ChildItem -LiteralPath $previous -Force |
            Where-Object { -not (Test-Path -LiteralPath (Join-Path $target $_.Name)) } |
            ForEach-Object { Move-Item -LiteralPath $_.FullName -Destination $target }
        Remove-Item $previous -Recurse -Force -ErrorAction SilentlyContinue
    }

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
    # Inno Setup upgrades an existing installation in place and leaves the
    # Start menu entry and the desktop shortcut where they were. A silent run
    # opens the app when it finishes (installer.iss, RelaunchAfterUpdate),
    # which is what someone who has just run this wants; /NORELAUNCH would
    # turn that off, and the closing message below would then be wrong.
    $arguments = @('/SILENT', '/SUPPRESSMSGBOXES', '/NORESTART')
    $process = Start-Process -FilePath $download -ArgumentList $arguments -Wait -PassThru
    if ($process.ExitCode -ne 0) {
        throw "The installer exited with code $($process.ExitCode)."
    }
    Write-Step 'Done. Operator''s Console is opening now; it is also in your Start menu.'
}

Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue
Write-Host ''
Write-Host "Your progress lives in $env:APPDATA\Operator's Console" -ForegroundColor DarkGray
Write-Host 'Installing, updating and uninstalling never touch it.' -ForegroundColor DarkGray
