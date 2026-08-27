#!/usr/bin/env python3
"""Gera o artefato de release (zip / tar.gz / AppImage) para o SO atual."""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
UPLOAD = DIST / "upload"
SPEC = ROOT / "packaging" / "pyinstaller.spec"
VERSION = (os.environ.get("GESTOR_RPG_VERSION") or "1.1.0").lstrip("v")


def _arch() -> str:
    machine = platform.machine().lower()
    if machine in {"amd64", "x86_64"}:
        return "x64"
    if machine in {"arm64", "aarch64"}:
        return "arm64"
    return machine or "unknown"


def _run(cmd: list[str]) -> None:
    subprocess.check_call(cmd, cwd=ROOT)


def _pyinstaller() -> None:
    _run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--distpath",
            str(DIST),
            "--workpath",
            str(ROOT / "build" / "pyinstaller"),
            str(SPEC),
        ]
    )


def _zip_tree(src: Path, dest: Path, arc_root: str | None = None) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    root_name = arc_root if arc_root is not None else src.name
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as archive:
        if src.is_file():
            archive.write(src, f"{root_name}/{src.name}" if root_name else src.name)
            return
        for path in src.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(src)
            archive.write(path, f"{root_name}/{relative}" if root_name else str(relative))


def _tar_tree(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(dest, "w:gz") as archive:
        archive.add(src, arcname=src.name)


def _linux_appimage() -> Path | None:
    script = ROOT / "packaging" / "build-appimage.sh"
    env = os.environ.copy()
    env["APPIMAGE_EXTRACT_AND_RUN"] = "1"
    subprocess.check_call(["bash", str(script)], cwd=ROOT, env=env)
    image = DIST / "GestorRPG.AppImage"
    return image if image.exists() else None


def main() -> None:
    UPLOAD.mkdir(parents=True, exist_ok=True)
    system = platform.system().lower()
    arch = _arch()
    if system == "linux":
        image = _linux_appimage()
        folder = DIST / "gestor-rpg"
        tarball = UPLOAD / f"GestorRPG-{VERSION}-linux-{arch}.tar.gz"
        _tar_tree(folder, tarball)
        print(tarball)
        if image is not None:
            target = UPLOAD / f"GestorRPG-{VERSION}-linux-{arch}.AppImage"
            shutil.copy2(image, target)
            target.chmod(0o755)
            print(target)
        return
    _pyinstaller()
    if system == "windows":
        folder = DIST / "GestorRPG"
        dest = UPLOAD / f"GestorRPG-{VERSION}-windows-{arch}.zip"
        _zip_tree(folder, dest)
        print(dest)
        return
    if system == "darwin":
        dest = UPLOAD / f"GestorRPG-{VERSION}-macos-{arch}.zip"
        app = DIST / "Gestor RPG.app"
        folder = DIST / "gestor-rpg"
        if app.exists():
            _zip_tree(app, dest, arc_root="Gestor RPG.app")
        elif folder.exists():
            _zip_tree(folder, dest)
        else:
            raise SystemExit("Pacote macOS não encontrado")
        print(dest)
        return
    raise SystemExit(f"SO não suportado: {system}")


if __name__ == "__main__":
    main()
