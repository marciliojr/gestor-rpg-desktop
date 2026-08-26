#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist/gestor-rpg"
SPEC="$ROOT/packaging/pyinstaller.spec"
RPMDIR="$ROOT/build/rpm"

cd "$ROOT"
if [ ! -x "$DIST/gestor-rpg" ]; then
  python3 -m PyInstaller --noconfirm --clean --distpath "$ROOT/dist" --workpath "$ROOT/build/pyinstaller" "$SPEC"
fi

rm -rf "$RPMDIR"
mkdir -p "$RPMDIR"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
cp "$ROOT/packaging/gestor-rpg.rpm.spec" "$RPMDIR/SPECS/gestor-rpg.spec"

rpmbuild \
  --define "_topdir $RPMDIR" \
  --define "_builddir $ROOT" \
  --define "_sourcedir $ROOT" \
  --define "_rpmdir $RPMDIR/RPMS" \
  --define "_srcrpmdir $RPMDIR/SRPMS" \
  --define "_buildrootdir $RPMDIR/BUILDROOT" \
  -bb "$RPMDIR/SPECS/gestor-rpg.spec"

find "$RPMDIR/RPMS" -name '*.rpm' -exec cp {} "$ROOT/dist/" \;
echo "RPM em dist/"
ls -1 "$ROOT/dist"/*.rpm 2>/dev/null || true
