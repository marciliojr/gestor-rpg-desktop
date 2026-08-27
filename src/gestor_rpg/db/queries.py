from __future__ import annotations

import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone

from gestor_rpg.core.models import (
    ENCOUNTER_STATUSES,
    LOCATION_KINDS,
    PEOPLE_ATTITUDES,
    Campaign,
    Character,
    CharacterHit,
    Combatant,
    DiceRecord,
    DocumentHit,
    Encounter,
    ImportedDocument,
    Location,
    Person,
    SessionEntry,
)
from gestor_rpg.core.plugin import write_pool


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def list_systems(conn: sqlite3.Connection) -> list[tuple[int, str, str]]:
    rows = conn.execute("SELECT id, slug, name FROM rpg_systems ORDER BY id").fetchall()
    return [(int(r["id"]), str(r["slug"]), str(r["name"])) for r in rows]


def system_by_slug(conn: sqlite3.Connection, slug: str) -> tuple[int, str, str] | None:
    row = conn.execute(
        "SELECT id, slug, name FROM rpg_systems WHERE slug = ?", (slug,)
    ).fetchone()
    if not row:
        return None
    return int(row["id"]), str(row["slug"]), str(row["name"])


def system_by_id(conn: sqlite3.Connection, system_id: int) -> tuple[int, str, str] | None:
    row = conn.execute(
        "SELECT id, slug, name FROM rpg_systems WHERE id = ?", (system_id,)
    ).fetchone()
    if not row:
        return None
    return int(row["id"]), str(row["slug"]), str(row["name"])


def _campaign_from_row(row: sqlite3.Row) -> Campaign:
    return Campaign(
        id=int(row["id"]),
        name=str(row["name"]),
        system_id=int(row["system_id"]),
        system_slug=str(row["system_slug"]),
        system_name=str(row["system_name"]),
        notes=str(row["notes"] or ""),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


_CAMPAIGN_SELECT = """
SELECT c.id, c.name, c.system_id, s.slug AS system_slug, s.name AS system_name,
       c.notes, c.created_at, c.updated_at
FROM campaigns c
JOIN rpg_systems s ON s.id = c.system_id
"""


def list_campaigns(conn: sqlite3.Connection) -> list[Campaign]:
    rows = conn.execute(_CAMPAIGN_SELECT + " ORDER BY c.updated_at DESC").fetchall()
    return [_campaign_from_row(r) for r in rows]


def get_campaign(conn: sqlite3.Connection, campaign_id: int) -> Campaign | None:
    row = conn.execute(_CAMPAIGN_SELECT + " WHERE c.id = ?", (campaign_id,)).fetchone()
    return _campaign_from_row(row) if row else None


def create_campaign(conn: sqlite3.Connection, name: str, system_id: int, notes: str = "") -> Campaign:
    now = _now()
    cur = conn.execute(
        """
        INSERT INTO campaigns (name, system_id, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, system_id, notes, now, now),
    )
    conn.commit()
    campaign = get_campaign(conn, int(cur.lastrowid))
    assert campaign is not None
    return campaign


def update_campaign(conn: sqlite3.Connection, campaign: Campaign) -> None:
    conn.execute(
        """
        UPDATE campaigns SET name = ?, notes = ?, updated_at = ?
        WHERE id = ?
        """,
        (campaign.name, campaign.notes, _now(), campaign.id),
    )
    conn.commit()


def delete_campaign(conn: sqlite3.Connection, campaign_id: int) -> None:
    conn.execute("DELETE FROM campaigns WHERE id = ?", (campaign_id,))
    conn.commit()


def _character_from_row(row: sqlite3.Row) -> Character:
    raw = row["attributes_json"] or "{}"
    try:
        attributes = json.loads(raw)
    except json.JSONDecodeError:
        attributes = {}
    if not isinstance(attributes, dict):
        attributes = {}
    return Character(
        id=int(row["id"]),
        uuid=str(row["uuid"]),
        campaign_id=int(row["campaign_id"]) if row["campaign_id"] is not None else None,
        system_id=int(row["system_id"]),
        kind=str(row["kind"]),
        name=str(row["name"]),
        notes=str(row["notes"] or ""),
        motivation=str(row["motivation"] or ""),
        story_hook=str(row["story_hook"] or ""),
        attributes=attributes,
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def list_characters(
    conn: sqlite3.Connection,
    campaign_id: int | None = None,
    kind: str | None = None,
) -> list[Character]:
    sql = "SELECT * FROM characters WHERE 1=1"
    params: list[object] = []
    if campaign_id is not None:
        sql += " AND campaign_id = ?"
        params.append(campaign_id)
    if kind is not None:
        sql += " AND kind = ?"
        params.append(kind)
    sql += " ORDER BY name COLLATE NOCASE"
    rows = conn.execute(sql, params).fetchall()
    return [_character_from_row(r) for r in rows]


def get_character(conn: sqlite3.Connection, character_id: int) -> Character | None:
    row = conn.execute("SELECT * FROM characters WHERE id = ?", (character_id,)).fetchone()
    return _character_from_row(row) if row else None


def create_character(conn: sqlite3.Connection, character: Character) -> Character:
    now = _now()
    uid = character.uuid or str(uuid.uuid4())
    cur = conn.execute(
        """
        INSERT INTO characters (
            uuid, campaign_id, system_id, kind, name, notes,
            motivation, story_hook, attributes_json, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            uid,
            character.campaign_id,
            character.system_id,
            character.kind,
            character.name,
            character.notes,
            character.motivation,
            character.story_hook,
            json.dumps(character.attributes, ensure_ascii=False),
            now,
            now,
        ),
    )
    conn.commit()
    created = get_character(conn, int(cur.lastrowid))
    assert created is not None
    return created


def update_character(conn: sqlite3.Connection, character: Character) -> None:
    conn.execute(
        """
        UPDATE characters SET
            name = ?, notes = ?, motivation = ?, story_hook = ?,
            attributes_json = ?, kind = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            character.name,
            character.notes,
            character.motivation,
            character.story_hook,
            json.dumps(character.attributes, ensure_ascii=False),
            character.kind,
            _now(),
            character.id,
        ),
    )
    conn.commit()


def delete_character(conn: sqlite3.Connection, character_id: int) -> None:
    conn.execute("DELETE FROM characters WHERE id = ?", (character_id,))
    conn.commit()


def insert_document(conn: sqlite3.Connection, doc: ImportedDocument) -> ImportedDocument:
    now = _now()
    uid = doc.uuid or str(uuid.uuid4())
    cur = conn.execute(
        """
        INSERT INTO imported_documents (
            uuid, title, source_path, doc_type, system_id, character_id,
            extracted_text, metadata_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            uid,
            doc.title,
            doc.source_path,
            doc.doc_type,
            doc.system_id,
            doc.character_id,
            doc.extracted_text,
            json.dumps(doc.metadata, ensure_ascii=False),
            now,
        ),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM imported_documents WHERE id = ?", (int(cur.lastrowid),)
    ).fetchone()
    return _document_from_row(row)


def _document_from_row(row: sqlite3.Row) -> ImportedDocument:
    raw = row["metadata_json"] or "{}"
    try:
        metadata = json.loads(raw)
    except json.JSONDecodeError:
        metadata = {}
    if not isinstance(metadata, dict):
        metadata = {}
    return ImportedDocument(
        id=int(row["id"]),
        uuid=str(row["uuid"]),
        title=str(row["title"]),
        source_path=str(row["source_path"] or ""),
        doc_type=str(row["doc_type"]),
        system_id=int(row["system_id"]) if row["system_id"] is not None else None,
        character_id=int(row["character_id"]) if row["character_id"] is not None else None,
        extracted_text=str(row["extracted_text"] or ""),
        metadata=metadata,
        created_at=str(row["created_at"]),
    )


def list_documents(conn: sqlite3.Connection, system_id: int | None = None) -> list[ImportedDocument]:
    if system_id is None:
        rows = conn.execute(
            "SELECT * FROM imported_documents ORDER BY created_at DESC"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM imported_documents WHERE system_id = ? ORDER BY created_at DESC",
            (system_id,),
        ).fetchall()
    return [_document_from_row(r) for r in rows]


def insert_dice_roll(
    conn: sqlite3.Connection, expression: str, total: int, detail: list
) -> DiceRecord:
    now = _now()
    cur = conn.execute(
        """
        INSERT INTO dice_history (expression, total, detail_json, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (expression, total, json.dumps(detail, ensure_ascii=False), now),
    )
    conn.commit()
    return DiceRecord(
        id=int(cur.lastrowid),
        expression=expression,
        total=total,
        detail=detail,
        created_at=now,
    )


def list_dice_history(conn: sqlite3.Connection, limit: int = 40) -> list[DiceRecord]:
    rows = conn.execute(
        "SELECT * FROM dice_history ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    records: list[DiceRecord] = []
    for row in rows:
        try:
            detail = json.loads(row["detail_json"])
        except json.JSONDecodeError:
            detail = []
        records.append(
            DiceRecord(
                id=int(row["id"]),
                expression=str(row["expression"]),
                total=int(row["total"]),
                detail=detail if isinstance(detail, list) else [],
                created_at=str(row["created_at"]),
            )
        )
    return records


def clear_dice_history(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM dice_history")
    conn.commit()


def get_setting(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
    return str(row["value"]) if row else None


def set_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO app_settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    conn.commit()


def get_document(conn: sqlite3.Connection, document_id: int) -> ImportedDocument | None:
    row = conn.execute(
        "SELECT * FROM imported_documents WHERE id = ?", (document_id,)
    ).fetchone()
    return _document_from_row(row) if row else None


def _fts_match_query(raw: str) -> str:
    tokens = re.findall(r"[A-Za-zÀ-ÿ0-9]+", raw)
    return " AND ".join(f"{token}*" for token in tokens)


def search_documents(
    conn: sqlite3.Connection,
    query: str,
    system_id: int | None = None,
) -> list[DocumentHit]:
    match = _fts_match_query(query)
    if not match:
        return []
    sql = """
        SELECT d.*, snippet(documents_fts, 1, '[[', ']]', '…', 24) AS snippet,
               bm25(documents_fts) AS rank
        FROM documents_fts
        JOIN imported_documents d ON d.id = documents_fts.rowid
        WHERE documents_fts MATCH ?
    """
    params: list[object] = [match]
    if system_id is not None:
        sql += " AND d.system_id = ?"
        params.append(system_id)
    sql += " ORDER BY rank ASC, d.id DESC"
    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError:
        return []
    hits: list[DocumentHit] = []
    for row in rows:
        hits.append(
            DocumentHit(
                id=int(row["id"]),
                title=str(row["title"]),
                source_path=str(row["source_path"] or ""),
                doc_type=str(row["doc_type"]),
                system_id=int(row["system_id"]) if row["system_id"] is not None else None,
                snippet=str(row["snippet"] or ""),
                rank=float(row["rank"] or 0),
                extracted_text=str(row["extracted_text"] or ""),
            )
        )
    return hits


def _pick_fts_snippet(*snippets: str) -> str:
    marked = [text for text in snippets if "[[" in text]
    if marked:
        return marked[0].replace("\n", " ").strip()
    for text in snippets:
        cleaned = text.replace("\n", " ").strip()
        if cleaned:
            return cleaned
    return ""


def search_characters(
    conn: sqlite3.Connection,
    query: str,
    campaign_id: int,
) -> list[CharacterHit]:
    match = _fts_match_query(query)
    if not match:
        return []
    sql = """
        SELECT c.id, c.name, c.kind,
               snippet(characters_fts, 0, '[[', ']]', '…', 16) AS sn_name,
               snippet(characters_fts, 1, '[[', ']]', '…', 16) AS sn_notes,
               snippet(characters_fts, 2, '[[', ']]', '…', 16) AS sn_mot,
               snippet(characters_fts, 3, '[[', ']]', '…', 16) AS sn_hook,
               snippet(characters_fts, 4, '[[', ']]', '…', 24) AS sn_attrs,
               bm25(characters_fts) AS rank
        FROM characters_fts
        JOIN characters c ON c.id = characters_fts.rowid
        WHERE characters_fts MATCH ?
          AND c.campaign_id = ?
        ORDER BY rank ASC, c.name COLLATE NOCASE
    """
    try:
        rows = conn.execute(sql, (match, campaign_id)).fetchall()
    except sqlite3.OperationalError:
        return []
    hits: list[CharacterHit] = []
    for row in rows:
        hits.append(
            CharacterHit(
                id=int(row["id"]),
                name=str(row["name"]),
                kind=str(row["kind"]),
                snippet=_pick_fts_snippet(
                    str(row["sn_attrs"] or ""),
                    str(row["sn_notes"] or ""),
                    str(row["sn_mot"] or ""),
                    str(row["sn_hook"] or ""),
                    str(row["sn_name"] or ""),
                ),
                rank=float(row["rank"] or 0),
            )
        )
    return hits


def _row_int(row: sqlite3.Row, key: str, default: int = 0) -> int:
    if key not in row.keys() or row[key] is None:
        return default
    return int(row[key])


def _row_optional_int(row: sqlite3.Row, key: str) -> int | None:
    if key not in row.keys() or row[key] is None:
        return None
    return int(row[key])


def _row_text(row: sqlite3.Row, key: str, default: str = "") -> str:
    if key not in row.keys() or row[key] is None:
        return default
    return str(row[key])


_LOCATION_KIND_KEYS = {key for key, _label in LOCATION_KINDS}
_PEOPLE_ATTITUDE_KEYS = {key for key, _label in PEOPLE_ATTITUDES}
_ENCOUNTER_STATUS_KEYS = {key for key, _label in ENCOUNTER_STATUSES}


def _norm_location_kind(kind: str) -> str:
    return kind if kind in _LOCATION_KIND_KEYS else "outro"


def _norm_attitude(attitude: str) -> str:
    return attitude if attitude in _PEOPLE_ATTITUDE_KEYS else "neutro"


def _norm_encounter_status(status: str) -> str:
    return status if status in _ENCOUNTER_STATUS_KEYS else "preparado"


def _location_from_row(row: sqlite3.Row) -> Location:
    return Location(
        id=int(row["id"]),
        uuid=str(row["uuid"]),
        campaign_id=int(row["campaign_id"]),
        name=str(row["name"]),
        kind=_norm_location_kind(str(row["kind"] or "cidade")),
        notes=str(row["notes"] or ""),
        secrets=str(row["secrets"] or ""),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def list_locations(conn: sqlite3.Connection, campaign_id: int) -> list[Location]:
    rows = conn.execute(
        """
        SELECT * FROM locations
        WHERE campaign_id = ?
        ORDER BY name COLLATE NOCASE, id
        """,
        (campaign_id,),
    ).fetchall()
    return [_location_from_row(r) for r in rows]


def get_location(conn: sqlite3.Connection, location_id: int) -> Location | None:
    row = conn.execute("SELECT * FROM locations WHERE id = ?", (location_id,)).fetchone()
    return _location_from_row(row) if row else None


def create_location(conn: sqlite3.Connection, location: Location) -> Location:
    now = _now()
    uid = location.uuid or str(uuid.uuid4())
    cur = conn.execute(
        """
        INSERT INTO locations (
            uuid, campaign_id, name, kind, notes, secrets, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            uid,
            location.campaign_id,
            location.name,
            _norm_location_kind(location.kind),
            location.notes,
            location.secrets,
            now,
            now,
        ),
    )
    conn.commit()
    created = get_location(conn, int(cur.lastrowid))
    assert created is not None
    return created


def update_location(conn: sqlite3.Connection, location: Location) -> None:
    conn.execute(
        """
        UPDATE locations SET
            name = ?, kind = ?, notes = ?, secrets = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            location.name,
            _norm_location_kind(location.kind),
            location.notes,
            location.secrets,
            _now(),
            location.id,
        ),
    )
    conn.commit()


def delete_location(conn: sqlite3.Connection, location_id: int) -> None:
    conn.execute("DELETE FROM locations WHERE id = ?", (location_id,))
    conn.commit()


def _person_from_row(row: sqlite3.Row) -> Person:
    return Person(
        id=int(row["id"]),
        uuid=str(row["uuid"]),
        campaign_id=int(row["campaign_id"]),
        location_id=_row_optional_int(row, "location_id"),
        character_id=_row_optional_int(row, "character_id"),
        name=str(row["name"] or ""),
        role=str(row["role"] or ""),
        appearance=str(row["appearance"] or ""),
        notes=str(row["notes"] or ""),
        secrets=str(row["secrets"] or ""),
        attitude=_norm_attitude(str(row["attitude"] or "neutro")),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def list_people(conn: sqlite3.Connection, campaign_id: int) -> list[Person]:
    rows = conn.execute(
        """
        SELECT * FROM people
        WHERE campaign_id = ?
        ORDER BY name COLLATE NOCASE, id
        """,
        (campaign_id,),
    ).fetchall()
    return [_person_from_row(r) for r in rows]


def get_person(conn: sqlite3.Connection, person_id: int) -> Person | None:
    row = conn.execute("SELECT * FROM people WHERE id = ?", (person_id,)).fetchone()
    return _person_from_row(row) if row else None


def create_person(conn: sqlite3.Connection, person: Person) -> Person:
    now = _now()
    uid = person.uuid or str(uuid.uuid4())
    cur = conn.execute(
        """
        INSERT INTO people (
            uuid, campaign_id, location_id, character_id, name, role, appearance,
            notes, secrets, attitude, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            uid,
            person.campaign_id,
            person.location_id,
            person.character_id,
            person.name,
            person.role,
            person.appearance,
            person.notes,
            person.secrets,
            _norm_attitude(person.attitude),
            now,
            now,
        ),
    )
    conn.commit()
    created = get_person(conn, int(cur.lastrowid))
    assert created is not None
    return created


def update_person(conn: sqlite3.Connection, person: Person) -> None:
    conn.execute(
        """
        UPDATE people SET
            location_id = ?, character_id = ?, name = ?, role = ?, appearance = ?,
            notes = ?, secrets = ?, attitude = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            person.location_id,
            person.character_id,
            person.name,
            person.role,
            person.appearance,
            person.notes,
            person.secrets,
            _norm_attitude(person.attitude),
            _now(),
            person.id,
        ),
    )
    conn.commit()


def delete_person(conn: sqlite3.Connection, person_id: int) -> None:
    conn.execute("DELETE FROM people WHERE id = ?", (person_id,))
    conn.commit()


def _encounter_from_row(row: sqlite3.Row) -> Encounter:
    return Encounter(
        id=int(row["id"]),
        campaign_id=int(row["campaign_id"]),
        name=str(row["name"]),
        round=int(row["round"] or 1),
        grid_cols=max(4, _row_int(row, "grid_cols", 12)),
        grid_rows=max(4, _row_int(row, "grid_rows", 8)),
        location_id=_row_optional_int(row, "location_id"),
        notes=_row_text(row, "notes"),
        status=_norm_encounter_status(_row_text(row, "status", "preparado")),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def list_encounters(conn: sqlite3.Connection, campaign_id: int) -> list[Encounter]:
    rows = conn.execute(
        "SELECT * FROM encounters WHERE campaign_id = ? ORDER BY updated_at DESC, id DESC",
        (campaign_id,),
    ).fetchall()
    return [_encounter_from_row(r) for r in rows]


def get_encounter(conn: sqlite3.Connection, encounter_id: int) -> Encounter | None:
    row = conn.execute("SELECT * FROM encounters WHERE id = ?", (encounter_id,)).fetchone()
    return _encounter_from_row(row) if row else None


def get_latest_encounter(conn: sqlite3.Connection, campaign_id: int) -> Encounter | None:
    row = conn.execute(
        """
        SELECT * FROM encounters
        WHERE campaign_id = ?
        ORDER BY updated_at DESC, id DESC
        LIMIT 1
        """,
        (campaign_id,),
    ).fetchone()
    return _encounter_from_row(row) if row else None


def create_encounter(
    conn: sqlite3.Connection,
    campaign_id: int,
    name: str = "Combate atual",
    location_id: int | None = None,
    notes: str = "",
    status: str = "preparado",
) -> Encounter:
    now = _now()
    cur = conn.execute(
        """
        INSERT INTO encounters (
            campaign_id, name, round, grid_cols, grid_rows,
            location_id, notes, status, created_at, updated_at
        )
        VALUES (?, ?, 1, 12, 8, ?, ?, ?, ?, ?)
        """,
        (
            campaign_id,
            name,
            location_id,
            notes,
            _norm_encounter_status(status),
            now,
            now,
        ),
    )
    conn.commit()
    encounter = get_encounter(conn, int(cur.lastrowid))
    assert encounter is not None
    return encounter


def pick_play_encounter(conn: sqlite3.Connection, campaign_id: int) -> Encounter | None:
    encounters = list_encounters(conn, campaign_id)
    for wanted in ("em_andamento", "preparado"):
        for item in encounters:
            if item.status == wanted:
                return item
    return encounters[0] if encounters else None


def get_or_create_encounter(conn: sqlite3.Connection, campaign_id: int) -> Encounter:
    existing = pick_play_encounter(conn, campaign_id)
    if existing is not None:
        return existing
    return create_encounter(conn, campaign_id, status="em_andamento")


def update_encounter(conn: sqlite3.Connection, encounter: Encounter) -> None:
    conn.execute(
        """
        UPDATE encounters SET
            name = ?, round = ?, grid_cols = ?, grid_rows = ?,
            location_id = ?, notes = ?, status = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            encounter.name,
            encounter.round,
            max(4, int(encounter.grid_cols or 12)),
            max(4, int(encounter.grid_rows or 8)),
            encounter.location_id,
            encounter.notes or "",
            _norm_encounter_status(encounter.status),
            _now(),
            encounter.id,
        ),
    )
    conn.commit()


def delete_encounter(conn: sqlite3.Connection, encounter_id: int) -> None:
    conn.execute("DELETE FROM encounters WHERE id = ?", (encounter_id,))
    conn.commit()


def _combatant_from_row(row: sqlite3.Row) -> Combatant:
    raw = row["snapshot_json"] or "{}"
    try:
        snapshot = json.loads(raw)
    except json.JSONDecodeError:
        snapshot = {}
    if not isinstance(snapshot, dict):
        snapshot = {}
    return Combatant(
        id=int(row["id"]),
        encounter_id=int(row["encounter_id"]),
        character_id=int(row["character_id"]) if row["character_id"] is not None else None,
        name=str(row["name"]),
        initiative=int(row["initiative"] or 0),
        hp_current=int(row["hp_current"] or 0),
        hp_max=int(row["hp_max"] or 0),
        resource_current=int(row["resource_current"] or 0),
        resource_max=int(row["resource_max"] or 0),
        action_current=int(row["action_current"] or 0) if "action_current" in row.keys() else 0,
        action_max=int(row["action_max"] or 0) if "action_max" in row.keys() else 0,
        is_active=bool(row["is_active"]),
        sort_order=int(row["sort_order"] or 0),
        notes=str(row["notes"] or ""),
        snapshot=snapshot,
        grid_x=_row_int(row, "grid_x", -1),
        grid_y=_row_int(row, "grid_y", -1),
    )


def list_combatants(conn: sqlite3.Connection, encounter_id: int) -> list[Combatant]:
    rows = conn.execute(
        """
        SELECT * FROM combatants
        WHERE encounter_id = ?
        ORDER BY sort_order ASC, initiative DESC, id ASC
        """,
        (encounter_id,),
    ).fetchall()
    return [_combatant_from_row(r) for r in rows]


def get_combatant(conn: sqlite3.Connection, combatant_id: int) -> Combatant | None:
    row = conn.execute("SELECT * FROM combatants WHERE id = ?", (combatant_id,)).fetchone()
    return _combatant_from_row(row) if row else None


def create_combatant(conn: sqlite3.Connection, combatant: Combatant) -> Combatant:
    cur = conn.execute(
        """
        INSERT INTO combatants (
            encounter_id, character_id, name, initiative, hp_current, hp_max,
            resource_current, resource_max, action_current, action_max,
            is_active, sort_order, notes, snapshot_json, grid_x, grid_y
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            combatant.encounter_id,
            combatant.character_id,
            combatant.name,
            combatant.initiative,
            combatant.hp_current,
            combatant.hp_max,
            combatant.resource_current,
            combatant.resource_max,
            combatant.action_current,
            combatant.action_max,
            1 if combatant.is_active else 0,
            combatant.sort_order,
            combatant.notes,
            json.dumps(combatant.snapshot, ensure_ascii=False),
            combatant.grid_x,
            combatant.grid_y,
        ),
    )
    conn.execute(
        "UPDATE encounters SET updated_at = ? WHERE id = ?",
        (_now(), combatant.encounter_id),
    )
    conn.commit()
    created = get_combatant(conn, int(cur.lastrowid))
    assert created is not None
    return created


def update_combatant(conn: sqlite3.Connection, combatant: Combatant) -> None:
    conn.execute(
        """
        UPDATE combatants SET
            character_id = ?, name = ?, initiative = ?, hp_current = ?, hp_max = ?,
            resource_current = ?, resource_max = ?, action_current = ?, action_max = ?,
            is_active = ?, sort_order = ?,
            notes = ?, snapshot_json = ?, grid_x = ?, grid_y = ?
        WHERE id = ?
        """,
        (
            combatant.character_id,
            combatant.name,
            combatant.initiative,
            combatant.hp_current,
            combatant.hp_max,
            combatant.resource_current,
            combatant.resource_max,
            combatant.action_current,
            combatant.action_max,
            1 if combatant.is_active else 0,
            combatant.sort_order,
            combatant.notes,
            json.dumps(combatant.snapshot, ensure_ascii=False),
            combatant.grid_x,
            combatant.grid_y,
            combatant.id,
        ),
    )
    conn.execute(
        "UPDATE encounters SET updated_at = ? WHERE id = ?",
        (_now(), combatant.encounter_id),
    )
    conn.commit()


def delete_combatant(conn: sqlite3.Connection, combatant_id: int) -> None:
    conn.execute("DELETE FROM combatants WHERE id = ?", (combatant_id,))
    conn.commit()


def apply_combatant_hp(
    conn: sqlite3.Connection,
    combatant_id: int,
    *,
    hp_current: int | None = None,
    hp_max: int | None = None,
    resource_current: int | None = None,
    resource_max: int | None = None,
    action_current: int | None = None,
    action_max: int | None = None,
    hp_paths: dict[str, tuple[str, str]] | None = None,
) -> Combatant:
    combatant = get_combatant(conn, combatant_id)
    if combatant is None:
        raise ValueError("Combatente não encontrado")
    if hp_current is not None:
        combatant.hp_current = int(hp_current)
    if hp_max is not None:
        combatant.hp_max = int(hp_max)
    if resource_current is not None:
        combatant.resource_current = int(resource_current)
    if resource_max is not None:
        combatant.resource_max = int(resource_max)
    if action_current is not None:
        combatant.action_current = int(action_current)
    if action_max is not None:
        combatant.action_max = int(action_max)
    update_combatant(conn, combatant)
    if combatant.character_id is not None and hp_paths:
        character = get_character(conn, combatant.character_id)
        if character is not None:
            write_pool(
                character.attributes,
                hp_paths,
                hp_current=combatant.hp_current,
                hp_max=combatant.hp_max,
                resource_current=combatant.resource_current,
                resource_max=combatant.resource_max,
                action_current=combatant.action_current,
                action_max=combatant.action_max,
            )
            update_character(conn, character)
    refreshed = get_combatant(conn, combatant_id)
    assert refreshed is not None
    return refreshed


def set_active_combatant(conn: sqlite3.Connection, encounter_id: int, combatant_id: int) -> None:
    conn.execute(
        "UPDATE combatants SET is_active = 0 WHERE encounter_id = ?",
        (encounter_id,),
    )
    conn.execute(
        "UPDATE combatants SET is_active = 1 WHERE id = ? AND encounter_id = ?",
        (combatant_id, encounter_id),
    )
    conn.execute(
        "UPDATE encounters SET updated_at = ? WHERE id = ?",
        (_now(), encounter_id),
    )
    conn.commit()


def advance_turn(conn: sqlite3.Connection, encounter_id: int) -> Encounter:
    encounter = get_encounter(conn, encounter_id)
    if encounter is None:
        raise ValueError("Combate não encontrado")
    combatants = list_combatants(conn, encounter_id)
    if not combatants:
        return encounter
    active_index = next((i for i, item in enumerate(combatants) if item.is_active), -1)
    next_index = 0 if active_index < 0 else (active_index + 1) % len(combatants)
    if active_index >= 0 and next_index == 0:
        encounter.round += 1
        update_encounter(conn, encounter)
    nxt = combatants[next_index]
    assert nxt.id is not None
    set_active_combatant(conn, encounter_id, nxt.id)
    refreshed = get_encounter(conn, encounter_id)
    assert refreshed is not None
    return refreshed


def get_document(conn: sqlite3.Connection, document_id: int) -> ImportedDocument | None:
    row = conn.execute(
        "SELECT * FROM imported_documents WHERE id = ?", (document_id,)
    ).fetchone()
    return _document_from_row(row) if row else None


def delete_document(conn: sqlite3.Connection, document_id: int) -> None:
    conn.execute("DELETE FROM imported_documents WHERE id = ?", (document_id,))
    conn.commit()


def _session_from_row(row: sqlite3.Row) -> SessionEntry:
    return SessionEntry(
        id=int(row["id"]),
        uuid=str(row["uuid"]),
        campaign_id=int(row["campaign_id"]),
        encounter_id=int(row["encounter_id"]) if row["encounter_id"] is not None else None,
        title=str(row["title"] or ""),
        body=str(row["body"] or ""),
        xp=str(row["xp"] or ""),
        treasure=str(row["treasure"] or ""),
        hooks=_row_text(row, "hooks"),
        created_at=str(row["created_at"] or ""),
        updated_at=str(row["updated_at"] or ""),
    )


def list_session_entries(conn: sqlite3.Connection, campaign_id: int) -> list[SessionEntry]:
    rows = conn.execute(
        """
        SELECT * FROM session_entries
        WHERE campaign_id = ?
        ORDER BY updated_at DESC, id DESC
        """,
        (campaign_id,),
    ).fetchall()
    return [_session_from_row(r) for r in rows]


def get_session_entry(conn: sqlite3.Connection, entry_id: int) -> SessionEntry | None:
    row = conn.execute(
        "SELECT * FROM session_entries WHERE id = ?", (entry_id,)
    ).fetchone()
    return _session_from_row(row) if row else None


def create_session_entry(conn: sqlite3.Connection, entry: SessionEntry) -> SessionEntry:
    now = _now()
    uid = entry.uuid or str(uuid.uuid4())
    cur = conn.execute(
        """
        INSERT INTO session_entries (
            uuid, campaign_id, encounter_id, title, body, xp, treasure, hooks,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            uid,
            entry.campaign_id,
            entry.encounter_id,
            entry.title,
            entry.body,
            entry.xp,
            entry.treasure,
            entry.hooks,
            now,
            now,
        ),
    )
    conn.commit()
    created = get_session_entry(conn, int(cur.lastrowid))
    assert created is not None
    return created


def update_session_entry(conn: sqlite3.Connection, entry: SessionEntry) -> None:
    conn.execute(
        """
        UPDATE session_entries SET
            encounter_id = ?, title = ?, body = ?, xp = ?, treasure = ?,
            hooks = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            entry.encounter_id,
            entry.title,
            entry.body,
            entry.xp,
            entry.treasure,
            entry.hooks,
            _now(),
            entry.id,
        ),
    )
    conn.commit()


def delete_session_entry(conn: sqlite3.Connection, entry_id: int) -> None:
    conn.execute("DELETE FROM session_entries WHERE id = ?", (entry_id,))
    conn.commit()


CAMPAIGN_EXPORT_FORMAT = "gestor-rpg-campaign-v1"


def export_campaign(conn: sqlite3.Connection, campaign_id: int) -> dict:
    campaign = get_campaign(conn, campaign_id)
    if campaign is None:
        raise ValueError("Campanha não encontrada")
    characters = list_characters(conn, campaign_id)
    char_ids = {item.id for item in characters if item.id is not None}
    uuid_by_id = {item.id: item.uuid for item in characters if item.id is not None}
    locations = list_locations(conn, campaign_id)
    loc_uuid_by_id = {item.id: item.uuid for item in locations if item.id is not None}
    people = list_people(conn, campaign_id)
    encounters_payload = []
    for encounter in list_encounters(conn, campaign_id):
        if encounter.id is None:
            continue
        combatants = []
        for combatant in list_combatants(conn, encounter.id):
            combatants.append(
                {
                    "name": combatant.name,
                    "character_uuid": uuid_by_id.get(combatant.character_id),
                    "initiative": combatant.initiative,
                    "hp_current": combatant.hp_current,
                    "hp_max": combatant.hp_max,
                    "resource_current": combatant.resource_current,
                    "resource_max": combatant.resource_max,
                    "action_current": combatant.action_current,
                    "action_max": combatant.action_max,
                    "is_active": combatant.is_active,
                    "sort_order": combatant.sort_order,
                    "notes": combatant.notes,
                    "snapshot": combatant.snapshot,
                    "grid_x": combatant.grid_x,
                    "grid_y": combatant.grid_y,
                }
            )
        encounters_payload.append(
            {
                "name": encounter.name,
                "round": encounter.round,
                "grid_cols": encounter.grid_cols,
                "grid_rows": encounter.grid_rows,
                "location_uuid": loc_uuid_by_id.get(encounter.location_id),
                "notes": encounter.notes,
                "status": encounter.status,
                "combatants": combatants,
            }
        )
    documents_payload = []
    for doc in list_documents(conn, campaign.system_id):
        if doc.character_id is not None and doc.character_id not in char_ids:
            continue
        documents_payload.append(
            {
                "uuid": doc.uuid,
                "title": doc.title,
                "source_path": doc.source_path,
                "doc_type": doc.doc_type,
                "extracted_text": doc.extracted_text,
                "metadata": doc.metadata,
                "character_uuid": uuid_by_id.get(doc.character_id),
            }
        )
    encounter_name_by_id = {
        item.id: item.name for item in list_encounters(conn, campaign_id) if item.id is not None
    }
    session_payload = []
    for entry in list_session_entries(conn, campaign_id):
        session_payload.append(
            {
                "title": entry.title,
                "body": entry.body,
                "xp": entry.xp,
                "treasure": entry.treasure,
                "hooks": entry.hooks,
                "encounter_name": encounter_name_by_id.get(entry.encounter_id)
                if entry.encounter_id is not None
                else None,
            }
        )
    return {
        "format": CAMPAIGN_EXPORT_FORMAT,
        "campaign": {
            "name": campaign.name,
            "system_slug": campaign.system_slug,
            "notes": campaign.notes,
        },
        "characters": [
            {
                "uuid": item.uuid,
                "kind": item.kind,
                "name": item.name,
                "notes": item.notes,
                "motivation": item.motivation,
                "story_hook": item.story_hook,
                "attributes": item.attributes,
            }
            for item in characters
        ],
        "locations": [
            {
                "uuid": item.uuid,
                "name": item.name,
                "kind": item.kind,
                "notes": item.notes,
                "secrets": item.secrets,
            }
            for item in locations
        ],
        "people": [
            {
                "uuid": item.uuid,
                "name": item.name,
                "role": item.role,
                "appearance": item.appearance,
                "notes": item.notes,
                "secrets": item.secrets,
                "attitude": item.attitude,
                "location_uuid": loc_uuid_by_id.get(item.location_id),
                "character_uuid": uuid_by_id.get(item.character_id),
            }
            for item in people
        ],
        "encounters": encounters_payload,
        "documents": documents_payload,
        "session_entries": session_payload,
    }


def import_campaign(conn: sqlite3.Connection, payload: dict) -> Campaign:
    if not isinstance(payload, dict) or payload.get("format") != CAMPAIGN_EXPORT_FORMAT:
        raise ValueError("Arquivo de campanha inválido")
    info = payload.get("campaign") or {}
    slug = str(info.get("system_slug") or "")
    system = system_by_slug(conn, slug)
    if system is None:
        raise ValueError(f"Sistema desconhecido: {slug}")
    name = str(info.get("name") or "Campanha importada").strip() or "Campanha importada"
    campaign = create_campaign(conn, name, system[0], str(info.get("notes") or ""))
    uuid_map: dict[str, int] = {}
    for raw in payload.get("characters") or []:
        if not isinstance(raw, dict):
            continue
        old_uuid = str(raw.get("uuid") or "")
        kind = str(raw.get("kind") or "pc")
        if kind not in {"pc", "npc", "monster"}:
            kind = "pc"
        created = create_character(
            conn,
            Character(
                id=None,
                uuid=str(uuid.uuid4()),
                campaign_id=campaign.id,
                system_id=campaign.system_id,
                kind=kind,
                name=str(raw.get("name") or "Sem nome"),
                notes=str(raw.get("notes") or ""),
                motivation=str(raw.get("motivation") or ""),
                story_hook=str(raw.get("story_hook") or ""),
                attributes=raw.get("attributes") if isinstance(raw.get("attributes"), dict) else {},
            ),
        )
        if old_uuid and created.id is not None:
            uuid_map[old_uuid] = created.id
    loc_uuid_map: dict[str, int] = {}
    for raw in payload.get("locations") or []:
        if not isinstance(raw, dict):
            continue
        old_uuid = str(raw.get("uuid") or "")
        created = create_location(
            conn,
            Location(
                id=None,
                uuid=str(uuid.uuid4()),
                campaign_id=campaign.id,
                name=str(raw.get("name") or "Local"),
                kind=str(raw.get("kind") or "cidade"),
                notes=str(raw.get("notes") or ""),
                secrets=str(raw.get("secrets") or ""),
            ),
        )
        if old_uuid and created.id is not None:
            loc_uuid_map[old_uuid] = created.id
    for raw in payload.get("people") or []:
        if not isinstance(raw, dict):
            continue
        loc_uuid = raw.get("location_uuid")
        char_uuid = raw.get("character_uuid")
        create_person(
            conn,
            Person(
                id=None,
                uuid=str(uuid.uuid4()),
                campaign_id=campaign.id,
                location_id=loc_uuid_map.get(str(loc_uuid)) if loc_uuid else None,
                character_id=uuid_map.get(str(char_uuid)) if char_uuid else None,
                name=str(raw.get("name") or "Sem nome"),
                role=str(raw.get("role") or ""),
                appearance=str(raw.get("appearance") or ""),
                notes=str(raw.get("notes") or ""),
                secrets=str(raw.get("secrets") or ""),
                attitude=str(raw.get("attitude") or "neutro"),
            ),
        )
    for raw in payload.get("documents") or []:
        if not isinstance(raw, dict):
            continue
        char_uuid = raw.get("character_uuid")
        character_id = uuid_map.get(str(char_uuid)) if char_uuid else None
        doc_type = str(raw.get("doc_type") or "other")
        if doc_type not in {"manual", "sheet", "other"}:
            doc_type = "other"
        insert_document(
            conn,
            ImportedDocument(
                id=None,
                uuid=str(uuid.uuid4()),
                title=str(raw.get("title") or "Documento"),
                source_path=str(raw.get("source_path") or ""),
                doc_type=doc_type,
                system_id=campaign.system_id,
                character_id=character_id,
                extracted_text=str(raw.get("extracted_text") or ""),
                metadata=raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {},
            ),
        )
    for raw_enc in payload.get("encounters") or []:
        if not isinstance(raw_enc, dict):
            continue
        loc_uuid = raw_enc.get("location_uuid")
        encounter = create_encounter(
            conn,
            campaign.id,
            str(raw_enc.get("name") or "Combate"),
            location_id=loc_uuid_map.get(str(loc_uuid)) if loc_uuid else None,
            notes=str(raw_enc.get("notes") or ""),
            status=str(raw_enc.get("status") or "preparado"),
        )
        encounter.round = int(raw_enc.get("round") or 1)
        encounter.grid_cols = int(raw_enc.get("grid_cols") or 12)
        encounter.grid_rows = int(raw_enc.get("grid_rows") or 8)
        update_encounter(conn, encounter)
        assert encounter.id is not None
        for raw_c in raw_enc.get("combatants") or []:
            if not isinstance(raw_c, dict):
                continue
            char_uuid = raw_c.get("character_uuid")
            character_id = uuid_map.get(str(char_uuid)) if char_uuid else None
            create_combatant(
                conn,
                Combatant(
                    id=None,
                    encounter_id=encounter.id,
                    character_id=character_id,
                    name=str(raw_c.get("name") or "Combatente"),
                    initiative=int(raw_c.get("initiative") or 0),
                    hp_current=int(raw_c.get("hp_current") or 0),
                    hp_max=int(raw_c.get("hp_max") or 0),
                    resource_current=int(raw_c.get("resource_current") or 0),
                    resource_max=int(raw_c.get("resource_max") or 0),
                    action_current=int(raw_c.get("action_current") or 0),
                    action_max=int(raw_c.get("action_max") or 0),
                    is_active=bool(raw_c.get("is_active")),
                    sort_order=int(raw_c.get("sort_order") or 0),
                    notes=str(raw_c.get("notes") or ""),
                    snapshot=raw_c.get("snapshot") if isinstance(raw_c.get("snapshot"), dict) else {},
                    grid_x=int(raw_c.get("grid_x") if raw_c.get("grid_x") is not None else -1),
                    grid_y=int(raw_c.get("grid_y") if raw_c.get("grid_y") is not None else -1),
                ),
            )
    encounter_id_by_name = {
        item.name: item.id
        for item in list_encounters(conn, campaign.id)
        if item.id is not None
    }
    for raw_session in payload.get("session_entries") or []:
        if not isinstance(raw_session, dict):
            continue
        encounter_name = raw_session.get("encounter_name")
        encounter_id = None
        if encounter_name:
            encounter_id = encounter_id_by_name.get(str(encounter_name))
        create_session_entry(
            conn,
            SessionEntry(
                id=None,
                uuid=str(uuid.uuid4()),
                campaign_id=campaign.id,
                encounter_id=encounter_id,
                title=str(raw_session.get("title") or "Sessão"),
                body=str(raw_session.get("body") or ""),
                xp=str(raw_session.get("xp") or ""),
                treasure=str(raw_session.get("treasure") or ""),
                hooks=str(raw_session.get("hooks") or ""),
            ),
        )
    refreshed = get_campaign(conn, campaign.id)
    assert refreshed is not None
    return refreshed
