#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist/gestor-rpg"
APPDIR="$ROOT/dist/GestorRPG.AppDir"
SPEC="$ROOT/packaging/pyinstaller.spec"

cd "$ROOT"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
python3 -m PyInstaller --noconfirm --clean --distpath "$ROOT/dist" --workpath "$ROOT/build/pyinstaller" "$SPEC"

rm -rf "$APPDIR"
mkdir -p "$APPDIR/opt" "$APPDIR/usr/share/applications" "$APPDIR/usr/share/icons/hicolor/scalable/apps"
cp -a "$DIST" "$APPDIR/opt/gestor-rpg"
install -m 0755 "$ROOT/packaging/AppRun" "$APPDIR/AppRun"
install -m 0644 "$ROOT/packaging/gestor-rpg.desktop" "$APPDIR/gestor-rpg.desktop"
install -m 0644 "$ROOT/packaging/gestor-rpg.desktop" "$APPDIR/usr/share/applications/gestor-rpg.desktop"
install -m 0644 "$ROOT/src/gestor_rpg/resources/gestor-rpg.svg" "$APPDIR/gestor-rpg.svg"
install -m 0644 "$ROOT/src/gestor_rpg/resources/gestor-rpg.svg" "$APPDIR/usr/share/icons/hicolor/scalable/apps/gestor-rpg.svg"

if command -v appimagetool >/dev/null 2>&1; then
  appimagetool "$APPDIR" "$ROOT/dist/GestorRPG.AppImage"
  echo "AppImage em dist/GestorRPG.AppImage"
else
  echo "AppDir pronto em dist/GestorRPG.AppDir"
  echo "Para gerar o .AppImage: instale appimagetool e rode de novo, ou:"
  echo "  appimagetool dist/GestorRPG.AppDir dist/GestorRPG.AppImage"
fi
