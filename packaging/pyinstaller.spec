# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

root = Path(SPECPATH).resolve().parent
src = root / "src"

hidden = collect_submodules("gestor_rpg")
datas = collect_data_files("gestor_rpg")

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
    name="gestor-rpg",
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
    name="gestor-rpg",
)
