# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

root = Path(SPECPATH).resolve().parent
src = root / "src"

hidden = collect_submodules("gestor_rpg")
datas = collect_data_files("gestor_rpg")
exe_name = "GestorRPG" if sys.platform == "win32" else "gestor-rpg"
coll_name = "GestorRPG" if sys.platform == "win32" else "gestor-rpg"

a = Analysis(
    [str(src / "gestor_rpg" / "__main__.py")],
    pathex=[str(src)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden
    + [
        "PySide6.QtPrintSupport",
        "PySide6.QtSvg",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtCore",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name=coll_name,
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Gestor RPG.app",
        icon=None,
        bundle_identifier="com.marciliojr.gestor-rpg",
        info_plist={
            "CFBundleName": "Gestor RPG",
            "CFBundleDisplayName": "Gestor RPG",
            "CFBundleShortVersionString": "1.1.0",
            "CFBundleVersion": "1.1.0",
            "NSHighResolutionCapable": True,
        },
    )
