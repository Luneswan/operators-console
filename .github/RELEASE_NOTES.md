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
| Windows | `...windows-setup.exe`, or `...windows-portable.zip` to run without installing |
| macOS, Apple silicon | `...macos-arm64.dmg` |
| macOS, Intel | `...macos-x86_64.dmg` |
| Linux | `...x86_64.AppImage`, or the `.deb` |

Nothing here is code-signed, so the first launch needs one extra step:
Windows shows a SmartScreen warning — click **More info**, then **Run anyway**.
macOS refuses a double-click — **right-click the app, then Open**. The one-line
installers above handle the macOS case for you.

Your progress is a single file on your own machine. There is no account, no
sign-in, and the app makes no network calls.
