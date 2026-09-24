**1.3.1**: repairs a damaged progress file from your newest good snapshot, checkpoints the database every five minutes, and explains every line of the phase snippets.

**Updating from 1.0.1 or later (installed):** use the Update button in the
sidebar. If a 1.0.x build reopens on the old version after updating, close it
and run `...-windows-setup.exe` once.

**Updating from 1.0.0, or a 1.0.x portable build:** these cannot update
in-app. Run the install command below once. It keeps your progress, and later
versions update in-app. For a Windows portable build:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Luneswan/operators-console/main/install.ps1))) -Portable
```

**What is new:**

- If a profile's progress file is damaged, the app now says so when it
  opens and offers a repair: your newest good snapshot comes back, your
  current settings and anything else that still reads are kept, and the
  damaged files move to a folder beside it. Nothing is deleted.
- The database is checkpointed every five minutes, so a crash or an update
  cannot leave hours of changes outside the main file.
- The time-left text shows how your weekly hours are worked out.
- Every snippet on a phase page explains what each line does and why.

Your progress carries over.

Changes per version: [CHANGELOG.md](https://github.com/Luneswan/operators-console/blob/main/CHANGELOG.md).

## Install

Windows (PowerShell):

```powershell
irm https://raw.githubusercontent.com/Luneswan/operators-console/main/install.ps1 | iex
```

macOS or Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/Luneswan/operators-console/main/install.sh | sh
```

Or download a file below:

| Platform | File |
|---|---|
| Windows | `...-windows-setup.exe`, or `...-windows-x64-portable.zip` without installing |
| macOS, Apple silicon | `...-macos-arm64.dmg` |
| macOS, Intel | `...-macos-x86_64.dmg` |
| Linux | `...-x86_64.AppImage`, the `.deb`, or the `.tar.gz` |

Every file is listed in `SHA256SUMS`. The install scripts and the in-app
updater verify downloads against it and reject mismatches. To check a file
manually: `sha256sum -c SHA256SUMS --ignore-missing` (Linux),
`shasum -a 256 -c SHA256SUMS --ignore-missing` (macOS), or `Get-FileHash <file>`
(PowerShell).

The builds are not code-signed. Windows: in the SmartScreen warning, click
**More info**, then **Run anyway**. macOS: right-click the app and choose
**Open**. The macOS install script removes the quarantine flag, so this step is
not needed after a scripted install.

## Data and network

Progress is stored in a local SQLite file. There is no account. The only
network request is the update check: the app fetches the latest release's
details and `SHA256SUMS` from GitHub at start, every five minutes while open,
and when the window regains focus. It sends nothing about you, downloads
nothing until you press Update, and can be turned off in Settings. Library
links open in your browser.
