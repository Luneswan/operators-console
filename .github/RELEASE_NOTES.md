**1.1.1** — checklist stretch goals are now folded and optional, new releases
show up in the app within minutes, and checklist lines no longer shift under the
mouse. Details in the changelog below.

**On 1.0.1 or newer (installed)?** The update button appears on its own. If a
1.0.x version ever reopens after updating, close it and run the
`...-windows-setup.exe` below once.
**On 1.0.0, or a 1.0.x portable build?** Those cannot update themselves. Run the
installer command below once; it keeps all your progress, and every later
version then updates in-app. For a portable build on Windows use:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Luneswan/operators-console/main/install.ps1))) -Portable
```

What changed in this version is in [CHANGELOG.md](https://github.com/Luneswan/operators-console/blob/main/CHANGELOG.md).

## Install

**Windows** — paste into PowerShell:

```powershell
irm https://raw.githubusercontent.com/Luneswan/operators-console/main/install.ps1 | iex
```

**macOS or Linux** — paste into a terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/Luneswan/operators-console/main/install.sh | sh
```

Or download a file below and open it.

| You are on | Download |
|---|---|
| Windows | `...-windows-setup.exe`, or `...-windows-x64-portable.zip` to run without installing |
| macOS, Apple silicon | `...-macos-arm64.dmg` |
| macOS, Intel | `...-macos-x86_64.dmg` |
| Linux | `...-x86_64.AppImage`, the `.deb`, or the `.tar.gz` |

Every file below is listed in `SHA256SUMS`, published with this release. The
one-line installers and the in-app update check each download against it and
refuse anything that does not match. To check a file by hand, run
`sha256sum -c SHA256SUMS --ignore-missing` (Linux), `shasum -a 256 -c SHA256SUMS --ignore-missing`
(macOS) or `Get-FileHash <file>` (PowerShell) and compare.

Nothing here is code-signed, so the first launch needs one extra step:
Windows shows a SmartScreen warning — click **More info**, then **Run anyway**.
macOS refuses a double-click — **right-click the app, then Open**. The one-line
installers above handle the macOS case for you.

## Your data and the network

Your progress is a single file on your own machine. There is no account and no
sign-in. The app makes one kind of network request and no other: it asks
GitHub whether a newer version exists (the latest release's details and its
`SHA256SUMS` list, nothing about you), shortly after it starts and every 30
minutes while it is open, so it can offer an update. It downloads nothing until
you press the button, and you can turn the check off in Settings. Links in the
Library open in your own browser.
