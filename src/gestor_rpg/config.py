from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "Gestor RPG"
ORG_NAME = "GestorRPG"
APP_SLUG = "gestor-rpg"


def data_dir() -> Path:
    override = os.environ.get("GESTOR_RPG_DATA")
    if override:
        return Path(override)
    try:
        from PySide6.QtCore import QStandardPaths

        loc = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        )
        if loc:
            return Path(loc)
    except Exception:
        pass
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / APP_SLUG
    return Path.home() / ".local" / "share" / APP_SLUG


def db_path() -> Path:
    return data_dir() / "gestor.db"


def ensure_app_dirs() -> Path:
    path = data_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path
