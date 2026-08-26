from __future__ import annotations

import sqlite3
from pathlib import Path

from gestor_rpg.db.migrations import apply_migrations


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")
        apply_migrations(self.conn)

    def close(self) -> None:
        self.conn.close()
