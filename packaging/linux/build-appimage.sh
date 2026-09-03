#!/usr/bin/env bash
# Wrap the frozen build into a portable AppImage.
#
#   python packaging/build.py            # freeze first
#   packaging/linux/build-appimage.sh
#
# Needs appimagetool on PATH: https://github.com/AppImage/AppImageKit/releases
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
DIST="$ROOT/dist"
APPDIR="$ROOT/build/AppDir"
APP_ID="operators-console"
VERSION="$(python3 -c "import re,pathlib;print(re.search(r'__version__ = \"([^\"]+)\"', pathlib.Path('$ROOT/src/operators_console/version.py').read_text()).group(1))")"

if [ ! -d "$DIST/$APP_ID" ]; then
  echo "Freeze the app first: python packaging/build.py" >&2
  exit 1
fi
if ! command -v appimagetool >/dev/null 2>&1; then
  echo "appimagetool not found on PATH." >&2
  exit 1
fi

rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/share/applications" \
         "$APPDIR/usr/share/icons/hicolor/256x256/apps"

cp -r "$DIST/$APP_ID/." "$APPDIR/usr/bin/"
cp "$HERE/$APP_ID.desktop" "$APPDIR/usr/share/applications/"
cp "$HERE/$APP_ID.desktop" "$APPDIR/"
cp "$HERE/../icons/operators-console-256.png" \
   "$APPDIR/usr/share/icons/hicolor/256x256/apps/$APP_ID.png"
cp "$HERE/../icons/operators-console-256.png" "$APPDIR/$APP_ID.png"

cat > "$APPDIR/AppRun" <<'LAUNCH'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/operators-console" "$@"
LAUNCH
chmod +x "$APPDIR/AppRun"

ARCH=x86_64 appimagetool "$APPDIR" \
  "$DIST/${APP_ID}-${VERSION}-x86_64.AppImage"
echo "built $DIST/${APP_ID}-${VERSION}-x86_64.AppImage"
