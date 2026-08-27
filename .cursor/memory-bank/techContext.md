# Tech context

- Python ≥ 3.12, PySide6 ≥ 6.7, pymupdf, pytesseract, Pillow
- SQLite schema v7 em `gestor.db` (`GESTOR_RPG_DATA` ou AppData / XDG)
- Pacote: `src/gestor_rpg`; entrada `python3 -m gestor_rpg`
- Versão: `src/gestor_rpg/__init__.py` (`__version__`), `pyproject.toml`, spec RPM
- Testes: pytest, `pythonpath = src`
- Empacote: PyInstaller `packaging/pyinstaller.spec` (`console=False`; pasta `GestorRPG` no Windows, `Gestor RPG.app` no macOS); AppImage via `appimagetool`; RPM Fedora; `packaging/package-release.py` para zip/tar.gz/AppImage
- CI: GitHub Actions `.github/workflows/ci.yml` (pytest offscreen) e `release.yml` (binários na tag `v*`)
- Recursos: `src/gestor_rpg/resources/` (SVG, setas de combo PNG — gitignore de `*.png` com exceção desta pasta)
