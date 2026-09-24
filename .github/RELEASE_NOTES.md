**1.3.0**: a study timer, time-left estimates from your real pace, and a study guide for every checklist line.

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

- **Study timer**: Start studying in the top bar (Ctrl+T), Pause, Stop. It
  keeps running if you close the app. Stop shows what you finished while it
  ran and saves the session to your log.
- **Time left from your real pace**: each phase's hours are split over its
  steps, gate checks, exercises, quiz and project. Your timed sessions set
  your pace; your study hours set the finish date. Shown on Today, the
  Roadmap, Progress, each phase and Settings.
- **Study guides**: every one of the 633 checklist lines has how to do it,
  where to learn it and how to tell it is done. The next line opens with
  its guide. Every section says how to work through it.
- **Roadmap detail**: dates and hours left per phase, what is left by kind,
  and where each career level is reached.
- Fixed: a focus ring showed on "Today" after typing in a dialog.

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
