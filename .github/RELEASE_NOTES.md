**1.2.0**: career pathways, a career ladder, user profiles and a report form.

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

- **14 specializations**, one per career path: data and charts, desktop and
  mobile apps, command-line tools, games, science, finance, computer vision,
  NLP, testing, network automation, embedded and IoT, security, bots, and
  blockchain. Each has a checklist, gate, reading list, quiz, graded
  exercises and a project. 21 goals and 16 tracks; the roadmap orders phases
  by what each one needs first and adds missing prerequisites for your goals.
- **Career ladder**: Starting out, Beginner, Junior, Mid-level, Senior,
  Senior+. Levels come from proven phases, not ticked lines.
- **Profiles**: several people on one computer, each with their own
  progress, settings, review deck and snapshots. File -> Switch profile or
  Settings -> Profiles. Your existing progress stays where it is.
- **Report or request**: Settings and Help open a form that fills in a
  GitHub issue for you to submit. The app sends nothing.

The course is now 35 phases, 161 exercises, 354 quiz questions and 36
projects. Your progress carries over; question and checklist ids are
unchanged.

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
