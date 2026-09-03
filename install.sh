#!/bin/sh
# Installs Operator's Console on macOS or Linux.
#
#   curl -fsSL https://raw.githubusercontent.com/Luneswan/operators-console/main/install.sh | sh
#
# Downloads the latest release from GitHub and puts the app where your desktop
# expects it. Nothing is installed system-wide and nothing needs sudo, except
# the optional .deb path which asks for it explicitly.
set -eu

REPO="${OPCON_REPO:-Luneswan/operators-console}"
VERSION="${OPCON_VERSION:-latest}"
APP_ID="operators-console"

say()  { printf '==> %s\n' "$1"; }
warn() { printf 'warning: %s\n' "$1" >&2; }
die()  { printf 'error: %s\n' "$1" >&2; exit 1; }

need() {
    command -v "$1" >/dev/null 2>&1 || die "$1 is required but not installed."
}

need curl

OS="$(uname -s)"
ARCH="$(uname -m)"

case "$ARCH" in
    x86_64|amd64) ;;
    arm64|aarch64)
        if [ "$OS" != "Darwin" ]; then
            die "No prebuilt Linux build for $ARCH yet. Install from source instead:
    pip install operators-console"
        fi
        ;;
    *) die "Unsupported architecture: $ARCH" ;;
esac

if [ "$VERSION" = "latest" ]; then
    API="https://api.github.com/repos/$REPO/releases/latest"
else
    API="https://api.github.com/repos/$REPO/releases/tags/$VERSION"
fi

say "Looking up the latest release of $REPO"
RELEASE="$(curl -fsSL -H 'User-Agent: operators-console-installer' "$API")" \
    || die "Could not reach GitHub. Download it by hand from https://github.com/$REPO/releases"

# Pick the asset whose name contains $1, without needing jq.
asset_url() {
    printf '%s' "$RELEASE" \
        | tr ',' '\n' \
        | grep '"browser_download_url"' \
        | grep "$1" \
        | head -n 1 \
        | sed 's/.*"browser_download_url": *"//; s/".*//'
}

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT INT TERM

if [ "$OS" = "Darwin" ]; then
    # There is one disk image per architecture. Matching only on ".dmg" would
    # hand an Apple silicon build to an Intel Mac, where it will not launch.
    case "$ARCH" in
        arm64)  DMG_ARCH="arm64" ;;
        x86_64) DMG_ARCH="x86_64" ;;
        *)      die "Unsupported macOS architecture: $ARCH" ;;
    esac

    URL="$(asset_url "${DMG_ARCH}\.dmg")"
    [ -n "$URL" ] || die "This release has no macOS build for $ARCH. See https://github.com/$REPO/releases"

    say "Downloading $(basename "$URL")"
    curl -fL --progress-bar "$URL" -o "$TMP/app.dmg"

    say "Mounting the disk image"
    MOUNT="$TMP/mnt"
    mkdir -p "$MOUNT"
    hdiutil attach "$TMP/app.dmg" -nobrowse -quiet -mountpoint "$MOUNT"

    APP="$(find "$MOUNT" -maxdepth 1 -name '*.app' -print -quit)"
    [ -n "$APP" ] || { hdiutil detach "$MOUNT" -quiet; die "No .app inside the disk image."; }

    TARGET="$HOME/Applications"
    mkdir -p "$TARGET"
    say "Copying to $TARGET"
    rm -rf "$TARGET/$(basename "$APP")"
    cp -R "$APP" "$TARGET/"
    hdiutil detach "$MOUNT" -quiet

    # The build is unsigned, so clear the quarantine flag the download added.
    # Without this macOS refuses to open it at all on first launch.
    xattr -dr com.apple.quarantine "$TARGET/$(basename "$APP")" 2>/dev/null || true

    say "Done."
    printf '    Installed to %s\n' "$TARGET/$(basename "$APP")"
    printf '    Open it from Launchpad, or run: open "%s"\n' "$TARGET/$(basename "$APP")"
    printf '    Progress lives in ~/Library/Application Support/Operator'"'"'s Console\n'
    exit 0
fi

# ---------------------------------------------------------------- Linux ----
URL="$(asset_url 'AppImage')"
[ -n "$URL" ] || die "This release has no Linux build. See https://github.com/$REPO/releases"

BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
APP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/$APP_ID"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICON_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/256x256/apps"
mkdir -p "$BIN_DIR" "$APP_DIR" "$DESKTOP_DIR" "$ICON_DIR"

say "Downloading $(basename "$URL")"
curl -fL --progress-bar "$URL" -o "$APP_DIR/$APP_ID.AppImage"
chmod +x "$APP_DIR/$APP_ID.AppImage"

ln -sf "$APP_DIR/$APP_ID.AppImage" "$BIN_DIR/$APP_ID"

# Extract the icon out of the AppImage so the launcher entry is not blank.
( cd "$TMP" && "$APP_DIR/$APP_ID.AppImage" --appimage-extract "$APP_ID.png" >/dev/null 2>&1 ) || true
if [ -f "$TMP/squashfs-root/$APP_ID.png" ]; then
    cp "$TMP/squashfs-root/$APP_ID.png" "$ICON_DIR/$APP_ID.png"
fi

cat > "$DESKTOP_DIR/$APP_ID.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Operator's Console
GenericName=Python Curriculum
Comment=Learn Python step by step, with graded exercises and spaced review
Exec=$APP_DIR/$APP_ID.AppImage
Icon=$APP_ID
Terminal=false
Categories=Education;Development;ComputerScience;
StartupNotify=true
StartupWMClass=$APP_ID
DESKTOP
chmod +x "$DESKTOP_DIR/$APP_ID.desktop"

command -v update-desktop-database >/dev/null 2>&1 \
    && update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true

say "Done."
printf '    Installed to %s\n' "$APP_DIR/$APP_ID.AppImage"
case ":$PATH:" in
    *":$BIN_DIR:"*) printf '    Run it with: %s\n' "$APP_ID" ;;
    *) warn "$BIN_DIR is not on your PATH. Add it, or launch the app from your desktop menu." ;;
esac
printf '    Progress lives in %s\n' "${XDG_DATA_HOME:-$HOME/.local/share}/$APP_ID"

if ! ldconfig -p 2>/dev/null | grep -q libxkbcommon; then
    warn "Qt needs a few system libraries. On Debian or Ubuntu:
    sudo apt install libegl1 libgl1 libxkbcommon-x11-0 libxcb-cursor0 libfontconfig1"
fi
