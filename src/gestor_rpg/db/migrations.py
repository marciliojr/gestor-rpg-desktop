from __future__ import annotations

import sqlite3

MIGRATION_V1 = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS rpg_systems (
    id    INTEGER PRIMARY KEY,
    slug  TEXT NOT NULL UNIQUE,
    name  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS campaigns (
    id         INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    system_id  INTEGER NOT NULL REFERENCES rpg_systems(id),
    notes      TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS characters (
    id              INTEGER PRIMARY KEY,
    uuid            TEXT NOT NULL UNIQUE,
    campaign_id     INTEGER REFERENCES campaigns(id) ON DELETE SET NULL,
    system_id       INTEGER NOT NULL REFERENCES rpg_systems(id),
    kind            TEXT NOT NULL CHECK (kind IN ('pc','npc')),
    name            TEXT NOT NULL,
    notes           TEXT,
    motivation      TEXT,
    story_hook      TEXT,
    attributes_json TEXT NOT NULL DEFAULT '{}',
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_char_campaign ON characters(campaign_id);
CREATE INDEX IF NOT EXISTS idx_char_system   ON characters(system_id);
CREATE INDEX IF NOT EXISTS idx_char_kind     ON characters(kind);

CREATE TABLE IF NOT EXISTS imported_documents (
    id              INTEGER PRIMARY KEY,
    uuid            TEXT NOT NULL UNIQUE,
    title           TEXT NOT NULL,
    source_path     TEXT,
    doc_type        TEXT NOT NULL CHECK (doc_type IN ('manual','sheet','other')),
    system_id       INTEGER REFERENCES rpg_systems(id),
    character_id    INTEGER REFERENCES characters(id) ON DELETE SET NULL,
    extracted_text  TEXT,
    metadata_json   TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dice_history (
    id          INTEGER PRIMARY KEY,
    expression  TEXT NOT NULL,
    total       INTEGER NOT NULL,
    detail_json TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS app_settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

SYSTEMS = [
    ("ddt_victory", "3D&T Victory"),
    ("dnd5e", "D&D 5e"),
]

MIGRATION_V2 = """
CREATE TABLE characters_v2 (
    id              INTEGER PRIMARY KEY,
    uuid            TEXT NOT NULL UNIQUE,
    campaign_id     INTEGER REFERENCES campaigns(id) ON DELETE SET NULL,
    system_id       INTEGER NOT NULL REFERENCES rpg_systems(id),
    kind            TEXT NOT NULL CHECK (kind IN ('pc','npc','monster')),
    name            TEXT NOT NULL,
    notes           TEXT,
    motivation      TEXT,
    story_hook      TEXT,
    attributes_json TEXT NOT NULL DEFAULT '{}',
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

INSERT INTO characters_v2 (
    id, uuid, campaign_id, system_id, kind, name, notes,
    motivation, story_hook, attributes_json, created_at, updated_at
)
SELECT
    id, uuid, campaign_id, system_id, kind, name, notes,
    motivation, story_hook, attributes_json, created_at, updated_at
FROM characters;

DROP TABLE characters;
ALTER TABLE characters_v2 RENAME TO characters;

CREATE INDEX IF NOT EXISTS idx_char_campaign ON characters(campaign_id);
CREATE INDEX IF NOT EXISTS idx_char_system   ON characters(system_id);
CREATE INDEX IF NOT EXISTS idx_char_kind     ON characters(kind);

CREATE VIRTUAL TABLE documents_fts USING fts5(
    title,
    extracted_text,
    content='imported_documents',
    content_rowid='id',
    tokenize='unicode61 remove_diacritics 2'
);

CREATE TRIGGER documents_fts_ai AFTER INSERT ON imported_documents BEGIN
    INSERT INTO documents_fts(rowid, title, extracted_text)
    VALUES (new.id, new.title, new.extracted_text);
END;

CREATE TRIGGER documents_fts_ad AFTER DELETE ON imported_documents BEGIN
    INSERT INTO documents_fts(documents_fts, rowid, title, extracted_text)
    VALUES ('delete', old.id, old.title, old.extracted_text);
END;

CREATE TRIGGER documents_fts_au AFTER UPDATE ON imported_documents BEGIN
    INSERT INTO documents_fts(documents_fts, rowid, title, extracted_text)
    VALUES ('delete', old.id, old.title, old.extracted_text);
    INSERT INTO documents_fts(rowid, title, extracted_text)
    VALUES (new.id, new.title, new.extracted_text);
END;

INSERT INTO documents_fts(rowid, title, extracted_text)
SELECT id, title, COALESCE(extracted_text, '') FROM imported_documents;

CREATE TABLE IF NOT EXISTS encounters (
    id          INTEGER PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    round       INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_enc_campaign ON encounters(campaign_id);

CREATE TABLE IF NOT EXISTS combatants (
    id                INTEGER PRIMARY KEY,
    encounter_id      INTEGER NOT NULL REFERENCES encounters(id) ON DELETE CASCADE,
    character_id      INTEGER REFERENCES characters(id) ON DELETE SET NULL,
    name              TEXT NOT NULL,
    initiative        INTEGER NOT NULL DEFAULT 0,
    hp_current        INTEGER NOT NULL DEFAULT 0,
    hp_max            INTEGER NOT NULL DEFAULT 0,
    resource_current  INTEGER NOT NULL DEFAULT 0,
    resource_max      INTEGER NOT NULL DEFAULT 0,
    is_active         INTEGER NOT NULL DEFAULT 0,
    sort_order        INTEGER NOT NULL DEFAULT 0,
    notes             TEXT,
    snapshot_json     TEXT
);

CREATE INDEX IF NOT EXISTS idx_comb_encounter ON combatants(encounter_id);
CREATE INDEX IF NOT EXISTS idx_comb_character ON combatants(character_id);
"""

MIGRATION_V3 = """
ALTER TABLE combatants ADD COLUMN action_current INTEGER NOT NULL DEFAULT 0;
ALTER TABLE combatants ADD COLUMN action_max INTEGER NOT NULL DEFAULT 0;
"""

MIGRATION_V4 = """
CREATE TABLE IF NOT EXISTS session_entries (
    id            INTEGER PRIMARY KEY,
    uuid          TEXT NOT NULL UNIQUE,
    campaign_id   INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    encounter_id  INTEGER REFERENCES encounters(id) ON DELETE SET NULL,
    title         TEXT NOT NULL,
    body          TEXT NOT NULL DEFAULT '',
    xp            TEXT NOT NULL DEFAULT '',
    treasure      TEXT NOT NULL DEFAULT '',
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_session_campaign ON session_entries(campaign_id);

CREATE VIRTUAL TABLE characters_fts USING fts5(
    name,
    notes,
    motivation,
    story_hook,
    attributes_json,
    content='characters',
    content_rowid='id',
    tokenize='unicode61 remove_diacritics 2'
);

CREATE TRIGGER characters_fts_ai AFTER INSERT ON characters BEGIN
    INSERT INTO characters_fts(rowid, name, notes, motivation, story_hook, attributes_json)
    VALUES (new.id, new.name, new.notes, new.motivation, new.story_hook, new.attributes_json);
END;

CREATE TRIGGER characters_fts_ad AFTER DELETE ON characters BEGIN
    INSERT INTO characters_fts(characters_fts, rowid, name, notes, motivation, story_hook, attributes_json)
    VALUES ('delete', old.id, old.name, old.notes, old.motivation, old.story_hook, old.attributes_json);
END;

CREATE TRIGGER characters_fts_au AFTER UPDATE ON characters BEGIN
    INSERT INTO characters_fts(characters_fts, rowid, name, notes, motivation, story_hook, attributes_json)
    VALUES ('delete', old.id, old.name, old.notes, old.motivation, old.story_hook, old.attributes_json);
    INSERT INTO characters_fts(rowid, name, notes, motivation, story_hook, attributes_json)
    VALUES (new.id, new.name, new.notes, new.motivation, new.story_hook, new.attributes_json);
END;

INSERT INTO characters_fts(rowid, name, notes, motivation, story_hook, attributes_json)
SELECT id, name, COALESCE(notes, ''), COALESCE(motivation, ''),
       COALESCE(story_hook, ''), COALESCE(attributes_json, '{}')
FROM characters;
"""

MIGRATION_V5 = """
ALTER TABLE encounters ADD COLUMN grid_cols INTEGER NOT NULL DEFAULT 12;
ALTER TABLE encounters ADD COLUMN grid_rows INTEGER NOT NULL DEFAULT 8;
ALTER TABLE combatants ADD COLUMN grid_x INTEGER NOT NULL DEFAULT -1;
ALTER TABLE combatants ADD COLUMN grid_y INTEGER NOT NULL DEFAULT -1;
"""

REMOVED_SYSTEM_SLUGS = ("ddt_alpha", "tormenta20")


def _current_version(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
    ).fetchone()
    if not row:
        return 0
    ver = conn.execute("SELECT version FROM schema_version").fetchone()
    return int(ver[0]) if ver else 0


def _purge_removed_systems(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        f"SELECT id FROM rpg_systems WHERE slug IN ({','.join('?' * len(REMOVED_SYSTEM_SLUGS))})",
        REMOVED_SYSTEM_SLUGS,
    ).fetchall()
    ids = [int(row[0]) for row in rows]
    if not ids:
        return
    placeholders = ",".join("?" * len(ids))
    campaign_rows = conn.execute(
        f"SELECT id FROM campaigns WHERE system_id IN ({placeholders})",
        ids,
    ).fetchall()
    campaign_ids = [int(row[0]) for row in campaign_rows]
    conn.execute(
        f"UPDATE imported_documents SET system_id = NULL WHERE system_id IN ({placeholders})",
        ids,
    )
    conn.execute(
        f"DELETE FROM characters WHERE system_id IN ({placeholders})",
        ids,
    )
    if campaign_ids:
        camp_ph = ",".join("?" * len(campaign_ids))
        conn.execute(f"DELETE FROM campaigns WHERE id IN ({camp_ph})", campaign_ids)
        setting = conn.execute(
            "SELECT value FROM app_settings WHERE key = 'current_campaign_id'"
        ).fetchone()
        if setting and str(setting[0]) in {str(cid) for cid in campaign_ids}:
            conn.execute("DELETE FROM app_settings WHERE key = 'current_campaign_id'")
    conn.execute(f"DELETE FROM rpg_systems WHERE id IN ({placeholders})", ids)


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (name,),
    ).fetchone()
    return row is not None


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(str(row[1]) == column for row in rows)


def _apply_v7(conn: sqlite3.Connection) -> None:
    if not _table_exists(conn, "locations"):
        conn.executescript(
            """
            CREATE TABLE locations (
                id           INTEGER PRIMARY KEY,
                uuid         TEXT NOT NULL UNIQUE,
                campaign_id  INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
                name         TEXT NOT NULL,
                kind         TEXT NOT NULL DEFAULT 'cidade',
                notes        TEXT NOT NULL DEFAULT '',
                secrets      TEXT NOT NULL DEFAULT '',
                created_at   TEXT NOT NULL,
                updated_at   TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_loc_campaign ON locations(campaign_id);
            """
        )
    if not _table_exists(conn, "people"):
        conn.executescript(
            """
            CREATE TABLE people (
                id            INTEGER PRIMARY KEY,
                uuid          TEXT NOT NULL UNIQUE,
                campaign_id   INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
                location_id   INTEGER REFERENCES locations(id) ON DELETE SET NULL,
                character_id  INTEGER REFERENCES characters(id) ON DELETE SET NULL,
                name          TEXT NOT NULL,
                role          TEXT NOT NULL DEFAULT '',
                appearance    TEXT NOT NULL DEFAULT '',
                notes         TEXT NOT NULL DEFAULT '',
                secrets       TEXT NOT NULL DEFAULT '',
                attitude      TEXT NOT NULL DEFAULT 'neutro',
                created_at    TEXT NOT NULL,
                updated_at    TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_people_campaign ON people(campaign_id);
            CREATE INDEX IF NOT EXISTS idx_people_location ON people(location_id);
            """
        )
    if not _column_exists(conn, "encounters", "location_id"):
        conn.execute(
            "ALTER TABLE encounters ADD COLUMN location_id INTEGER "
            "REFERENCES locations(id) ON DELETE SET NULL"
        )
    if not _column_exists(conn, "encounters", "notes"):
        conn.execute("ALTER TABLE encounters ADD COLUMN notes TEXT NOT NULL DEFAULT ''")
    if not _column_exists(conn, "encounters", "status"):
        conn.execute(
            "ALTER TABLE encounters ADD COLUMN status TEXT NOT NULL DEFAULT 'preparado'"
        )
    if not _column_exists(conn, "session_entries", "hooks"):
        conn.execute(
            "ALTER TABLE session_entries ADD COLUMN hooks TEXT NOT NULL DEFAULT ''"
        )


def apply_migrations(conn: sqlite3.Connection) -> None:
    version = _current_version(conn)
    if version < 1:
        conn.executescript(MIGRATION_V1)
        conn.execute("DELETE FROM schema_version")
        conn.execute("INSERT INTO schema_version (version) VALUES (1)")
        conn.executemany(
            "INSERT OR IGNORE INTO rpg_systems (slug, name) VALUES (?, ?)",
            SYSTEMS,
        )
        conn.commit()
    if version < 2:
        conn.commit()
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.executescript(MIGRATION_V2)
        conn.execute("UPDATE schema_version SET version = 2")
        conn.commit()
        conn.execute("PRAGMA foreign_keys = ON")
    if version < 3:
        conn.executescript(MIGRATION_V3)
        conn.execute("UPDATE schema_version SET version = 3")
        conn.commit()
    if version < 4:
        conn.executescript(MIGRATION_V4)
        conn.execute("UPDATE schema_version SET version = 4")
        conn.commit()
    if version < 5:
        conn.executescript(MIGRATION_V5)
        conn.execute("UPDATE schema_version SET version = 5")
        conn.commit()
    if version < 6:
        _purge_removed_systems(conn)
        conn.execute("UPDATE schema_version SET version = 6")
        conn.commit()
    if version < 7:
        _apply_v7(conn)
        conn.execute("UPDATE schema_version SET version = 7")
        conn.commit()
