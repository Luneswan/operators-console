#!/bin/sh
# Installs or updates Operator's Console on macOS or Linux.
#
#   curl -fsSL https://raw.githubusercontent.com/Luneswan/operators-console/main/install.sh | sh
#
# Downloads the latest release from GitHub, checks it against the SHA256SUMS
# published with that release, and puts the app where your desktop expects it.
# Nothing is installed system-wide and nothing needs sudo.
#
# Running it again on a machine that already has the app is an in-place
# update. Your progress is never touched: it lives in
#   macOS  ~/Library/Application Support/Operator's Console
#   Linux  ${XDG_DATA_HOME:-~/.local/share}/operators-console
# and the application itself is installed somewhere else entirely.
#
# Trust root: this script trusts GitHub and the owner of the repository. The
# checksum proves the bytes match what that release published; it does not
# prove who published it. Set OPCON_SKIP_VERIFY=1 only to install a release
# published before checksums existed.
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

# Refuse anything but plain HTTPS, on the first request and on every redirect.
CURL="curl --proto =https --proto-redir =https -fL"

https_only() {
    case "$1" in
        https://*) printf '%s' "$1" ;;
        *) die "Refusing to fetch over an insecure connection: $1" ;;
    esac
}

sha256_of() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | cut -d' ' -f1
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$1" | cut -d' ' -f1
    else
        die "Neither sha256sum nor shasum is available, so the download cannot be verified."
    fi
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
RELEASE="$($CURL -sS -H 'User-Agent: operators-console-installer' "$API")" \
    || die "Could not reach GitHub. Download it by hand from https://github.com/$REPO/releases"

# Pick the asset whose URL matches $1, without needing jq.
asset_url() {
    printf '%s' "$RELEASE" \
        | tr ',' '\n' \
        | grep '"browser_download_url"' \
        | sed 's/.*"browser_download_url": *"//; s/".*//' \
        | grep -- "$1" \
        | head -n 1
}

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT INT TERM

# --------------------------------------------------------------- checksums --
# Fetched before the asset, so a release with no checksums stops the install
# before anything large is downloaded.
SUMS_URL="$(asset_url '/SHA256SUMS$')" || SUMS_URL=""
EXPECTED=""
if [ -n "$SUMS_URL" ]; then
    $CURL -sS "$(https_only "$SUMS_URL")" -o "$TMP/SHA256SUMS" \
        || die "Could not download the checksum file for this release."
elif [ "${OPCON_SKIP_VERIFY:-0}" != "1" ]; then
    # Here, not in verify(): the comment above promises nothing large is
    # fetched first, and the AppImage is the large thing.
    die "This release does not publish a SHA256SUMS file, so the download cannot be verified. Refusing to install it. Set OPCON_SKIP_VERIFY=1 to install it anyway."
fi

# verify <file> <basename>
verify() {
    _file="$1"; _name="$2"
    EXPECTED=""
    if [ -f "$TMP/SHA256SUMS" ]; then
        EXPECTED="$(sed 's/\*//' "$TMP/SHA256SUMS" \
            | awk -v n="$_name" '$2 == n { print $1; exit }')"
    fi
    if [ -z "$EXPECTED" ]; then
        if [ "${OPCON_SKIP_VERIFY:-0}" = "1" ]; then
            warn "Installing without verification because OPCON_SKIP_VERIFY=1."
            return 0
        fi
        die "This release does not publish a SHA256SUMS file, so the download cannot be verified. Refusing to install it. Set OPCON_SKIP_VERIFY=1 to install it anyway."
    fi
    _actual="$(sha256_of "$_file")"
    if [ "$_actual" != "$EXPECTED" ]; then
        rm -f "$_file"
        die "The download does not match the checksum published with the release. It has been discarded and nothing was installed."
    fi
    say "Checksum verified"
}

# Ask a running copy to quit, so files are not replaced underneath it.
stop_running() {
    if command -v pkill >/dev/null 2>&1 && pkill -f "$1" >/dev/null 2>&1; then
        say "Asked the running copy to close"
        _n=0
        while [ "$_n" -lt 40 ] && pgrep -f "$1" >/dev/null 2>&1; do
            _n=$((_n + 1))
            sleep 0.25
        done
        pgrep -f "$1" >/dev/null 2>&1 && pkill -KILL -f "$1" >/dev/null 2>&1 || true
    fi
}

if [ "$OS" = "Darwin" ]; then
    # There is one disk image per architecture. Matching only on ".dmg" would
    # hand an Apple silicon build to an Intel Mac, where it will not launch.
    case "$ARCH" in
        arm64)  DMG_ARCH="arm64" ;;
        x86_64) DMG_ARCH="x86_64" ;;
        *)      die "Unsupported macOS architecture: $ARCH" ;;
    esac

    URL="$(asset_url "${DMG_ARCH}\.dmg\$")"
    [ -n "$URL" ] || die "This release has no macOS build for $ARCH. See https://github.com/$REPO/releases"
    NAME="$(basename "$URL")"

    say "Downloading $NAME"
    $CURL --progress-bar "$(https_only "$URL")" -o "$TMP/$NAME"
    verify "$TMP/$NAME" "$NAME"

    say "Mounting the disk image"
    MOUNT="$TMP/mnt"
    mkdir -p "$MOUNT"
    hdiutil attach "$TMP/$NAME" -nobrowse -quiet -mountpoint "$MOUNT"

    APP="$(find "$MOUNT" -maxdepth 1 -name '*.app' -print -quit)"
    [ -n "$APP" ] || { hdiutil detach "$MOUNT" -quiet; die "No .app inside the disk image."; }

    # ~/Applications holds the program; ~/Library/Application Support holds the
    # progress. Different roots, so replacing one cannot reach the other.
    TARGET="$HOME/Applications"
    BASE="$(basename "$APP")"
    mkdir -p "$TARGET"
    stop_running "$TARGET/$BASE"

    say "Copying to $TARGET"
    # Stage the copy, then swap, so an interrupted install leaves the working
    # version in place rather than half a bundle.
    rm -rf "$TARGET/$BASE.new" "$TARGET/$BASE.previous"
    cp -R "$APP" "$TARGET/$BASE.new"
    hdiutil detach "$MOUNT" -quiet
    if [ -d "$TARGET/$BASE" ]; then
        mv "$TARGET/$BASE" "$TARGET/$BASE.previous"
    fi
    if mv "$TARGET/$BASE.new" "$TARGET/$BASE"; then
        rm -rf "$TARGET/$BASE.previous"
    else
        [ -d "$TARGET/$BASE.previous" ] && mv "$TARGET/$BASE.previous" "$TARGET/$BASE"
        die "The install failed and the previous version was put back."
    fi

    # The build is unsigned, so clear the quarantine flag the download added.
    # Without this macOS refuses to open it at all on first launch.
    xattr -dr com.apple.quarantine "$TARGET/$BASE" 2>/dev/null || true

    say "Done."
    printf '    Installed to %s\n' "$TARGET/$BASE"
    printf '    Open it from Launchpad, or run: open "%s"\n' "$TARGET/$BASE"
    printf '    Progress lives in ~/Library/Application Support/Operator'"'"'s Console\n'
    exit 0
fi

# ---------------------------------------------------------------- Linux ----
URL="$(asset_url 'AppImage$')"
[ -n "$URL" ] || die "This release has no Linux build. See https://github.com/$REPO/releases"
NAME="$(basename "$URL")"

BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
DATA_ROOT="${XDG_DATA_HOME:-$HOME/.local/share}"
# The program goes under ~/.local/opt, NOT under $XDG_DATA_HOME/operators-console:
# that directory is where core/paths.py keeps progress.db, and an installer
# that writes the application into the same folder as the learner's database
# is one `rm -rf` away from destroying it.
APP_DIR="${OPCON_APP_DIR:-$HOME/.local/opt/$APP_ID}"
STORE_DIR="$DATA_ROOT/$APP_ID"
DESKTOP_DIR="$DATA_ROOT/applications"
ICON_DIR="$DATA_ROOT/icons/hicolor/256x256/apps"
mkdir -p "$BIN_DIR" "$APP_DIR" "$DESKTOP_DIR" "$ICON_DIR"

case "$APP_DIR" in
    "$STORE_DIR"|"$STORE_DIR"/*)
        die "The application directory ($APP_DIR) is inside the progress directory ($STORE_DIR). Set OPCON_APP_DIR somewhere else." ;;
esac

stop_running "$APP_ID.AppImage"

say "Downloading $NAME"
$CURL --progress-bar "$(https_only "$URL")" -o "$TMP/$NAME"
verify "$TMP/$NAME" "$NAME"

# Swap the image only once it is known good, keeping the old one until the new
# one is in place.
TARGET_IMAGE="$APP_DIR/$APP_ID.AppImage"
chmod +x "$TMP/$NAME"
[ -f "$TARGET_IMAGE" ] && mv "$TARGET_IMAGE" "$TARGET_IMAGE.previous"
if mv "$TMP/$NAME" "$TARGET_IMAGE"; then
    rm -f "$TARGET_IMAGE.previous"
else
    [ -f "$TARGET_IMAGE.previous" ] && mv "$TARGET_IMAGE.previous" "$TARGET_IMAGE"
    die "The install failed and the previous version was put back."
fi
chmod +x "$TARGET_IMAGE"

# Earlier versions of this script installed the AppImage into the same folder
# as the database. Remove that copy, and nothing else in there.
OLD_IMAGE="$STORE_DIR/$APP_ID.AppImage"
if [ -f "$OLD_IMAGE" ] && [ "$OLD_IMAGE" != "$TARGET_IMAGE" ]; then
    say "Moving the application out of your progress folder"
    rm -f "$OLD_IMAGE"
fi

ln -sf "$TARGET_IMAGE" "$BIN_DIR/$APP_ID"

# Extract the icon out of the AppImage so the launcher entry is not blank.
( cd "$TMP" && "$TARGET_IMAGE" --appimage-extract "$APP_ID.png" >/dev/null 2>&1 ) || true
if [ -f "$TMP/squashfs-root/$APP_ID.png" ]; then
    cp "$TMP/squashfs-root/$APP_ID.png" "$ICON_DIR/$APP_ID.png"
fi

cat > "$DESKTOP_DIR/$APP_ID.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Operator's Console
GenericName=Python Curriculum
Comment=Learn Python step by step, with graded exercises and spaced review
Exec=$TARGET_IMAGE
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
printf '    Installed to %s\n' "$TARGET_IMAGE"
case ":$PATH:" in
    *":$BIN_DIR:"*) printf '    Run it with: %s\n' "$APP_ID" ;;
    *) warn "$BIN_DIR is not on your PATH. Add it, or launch the app from your desktop menu." ;;
esac
printf '    Progress lives in %s and is never touched by an install.\n' "$STORE_DIR"

if ! ldconfig -p 2>/dev/null | grep -q libxkbcommon; then
    warn "Qt needs a few system libraries. On Debian or Ubuntu:
    sudo apt install libegl1 libgl1 libxkbcommon-x11-0 libxcb-cursor0 libfontconfig1"
fi
