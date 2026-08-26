from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from gestor_rpg import __version__
from gestor_rpg.config import APP_NAME, ORG_NAME, db_path, ensure_app_dirs
from gestor_rpg.db.connection import Database
from gestor_rpg.ui.main_window import MainWindow
from gestor_rpg.ui.styles import apply_theme


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(__version__)
    app.setOrganizationName(ORG_NAME)
    apply_theme(app)
    ensure_app_dirs()
    database = Database(db_path())
    window = MainWindow(database)
    window.show()
    raise SystemExit(app.exec())
