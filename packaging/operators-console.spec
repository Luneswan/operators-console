# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller recipe. One spec, three platforms.

The application re-launches itself with --exercise-runner to grade code, so the
bundle must be able to start itself. That works in both onefile and onedir
builds because sys.executable points at the bundle.
"""
import sys
from pathlib import Path

HERE = Path(SPECPATH).resolve()
ROOT = HERE.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))
from operators_console.version import APP_NAME, __version__  # noqa: E402

DATA = [
    (str(SRC / "operators_console" / "data"), "operators_console/data"),
]

# Qt modules the app never touches. Dropping them roughly halves the bundle.
EXCLUDES = [
    "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets",
    "PySide6.QtWebEngineQuick", "PySide6.QtQuick", "PySide6.QtQuick3D",
    "PySide6.QtQml", "PySide6.Qt3DCore", "PySide6.Qt3DRender",
    "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets",
    "PySide6.QtCharts", "PySide6.QtDataVisualization", "PySide6.QtBluetooth",
    "PySide6.QtNfc", "PySide6.QtPositioning", "PySide6.QtSerialPort",
    "PySide6.QtDesigner", "PySide6.QtHelp", "PySide6.QtTest",
    "PySide6.QtOpenGL", "PySide6.QtOpenGLWidgets", "PySide6.QtSql",
    "PySide6.QtNetworkAuth", "PySide6.QtRemoteObjects", "PySide6.QtScxml",
    "PySide6.QtSensors", "PySide6.QtSpatialAudio", "PySide6.QtTextToSpeech",
    "PySide6.QtWebChannel", "PySide6.QtWebSockets", "PySide6.QtPdf",
    "PySide6.QtPdfWidgets", "PySide6.QtUiTools",
    "tkinter", "matplotlib", "numpy", "pandas", "scipy", "PIL", "pytest",
]

# PyInstaller still collects some Qt libraries as transitive dependencies even
# when the Python module is excluded. The app is pure QtWidgets with the Fusion
# style, so the QML runtime, the PDF engine, the software OpenGL rasteriser and
# the bundled translations are all dead weight.
DROP_BINARY_PREFIXES = (
    "opengl32sw",
    "Qt6Quick", "Qt6Qml", "Qt6Pdf", "Qt63D", "Qt6Charts",
    "Qt6DataVisualization", "Qt6Multimedia", "Qt6Sensors", "Qt6WebEngine",
    "Qt6Designer", "Qt6Sql", "Qt6Test", "Qt6Bluetooth", "Qt6Nfc",
    "Qt6SerialPort", "Qt6Scxml", "Qt6RemoteObjects", "Qt6SpatialAudio",
    "Qt6TextToSpeech", "Qt6WebChannel", "Qt6WebSockets", "Qt6Positioning",
)
DROP_PATH_PARTS = (
    "PySide6/translations", "PySide6\translations",
    "PySide6/qml", "PySide6\qml",
    "plugins/sqldrivers", "plugins\sqldrivers",
    "plugins/multimedia", "plugins\multimedia",
    "plugins/designer", "plugins\designer",
    "plugins/webview", "plugins\webview",
    "plugins/assetimporters", "plugins\assetimporters",
    "plugins/renderers", "plugins\renderers",
    "plugins/sceneparsers", "plugins\sceneparsers",
    "plugins/geometryloaders", "plugins\geometryloaders",
    "plugins/texttospeech", "plugins\texttospeech",
    "plugins/position", "plugins\position",
)


def _keep(entry):
    name = Path(entry[0]).name
    if name.startswith(DROP_BINARY_PREFIXES):
        return False
    normalised = entry[0].replace("\\", "/")
    return not any(part.replace("\\", "/") in normalised
                   for part in DROP_PATH_PARTS)


block_cipher = None

a = Analysis(
    [str(SRC / "operators_console" / "__main__.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=DATA,
    hiddenimports=["operators_console"],
    hookspath=[],
    runtime_hooks=[],
    excludes=EXCLUDES,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
a.binaries = TOC([entry for entry in a.binaries if _keep(entry)])
a.datas = TOC([entry for entry in a.datas if _keep(entry)])

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if sys.platform == "win32":
    icon = str(HERE / "icons" / "operators-console.ico")
elif sys.platform == "darwin":
    icon = str(HERE / "icons" / "operators-console.icns")
else:
    icon = str(HERE / "icons" / "operators-console-256.png")

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="operators-console",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon if Path(icon).exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="operators-console",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Operator's Console.app",
        icon=icon if Path(icon).exists() else None,
        bundle_identifier="dev.operatorsconsole.app",
        version=__version__,
        info_plist={
            "CFBundleName": APP_NAME,
            "CFBundleDisplayName": APP_NAME,
            "CFBundleShortVersionString": __version__,
            "CFBundleVersion": __version__,
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "11.0",
            "LSApplicationCategoryType": "public.app-category.education",
            "NSHumanReadableCopyright": "MIT licensed.",
        },
    )
