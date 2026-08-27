from __future__ import annotations

import uuid

from gestor_rpg.core.models import Character, Combatant, ImportedDocument, Location, Person, SessionEntry
from gestor_rpg.db.connection import Database
from gestor_rpg.db import queries


def test_schema_and_character_roundtrip(tmp_path):
    db = Database(tmp_path / "test.db")
    systems = queries.list_systems(db.conn)
    assert [s[1] for s in systems] == ["ddt_victory", "dnd5e"]

    campaign = queries.create_campaign(db.conn, "Mesa Teste", systems[0][0], "notas")
    loaded = queries.get_campaign(db.conn, campaign.id)
    assert loaded is not None
    assert loaded.system_slug == "ddt_victory"

    character = queries.create_character(
        db.conn,
        Character(
            id=None,
            uuid=str(uuid.uuid4()),
            campaign_id=campaign.id,
            system_id=campaign.system_id,
            kind="pc",
            name="Aldric",
            attributes={"forca": 2, "habilidade": 1},
        ),
    )
    again = queries.get_character(db.conn, character.id)
    assert again is not None
    assert again.name == "Aldric"
    assert again.attributes["forca"] == 2

    again.name = "Aldric II"
    again.attributes["forca"] = 3
    queries.update_character(db.conn, again)
    updated = queries.get_character(db.conn, character.id)
    assert updated is not None
    assert updated.name == "Aldric II"
    assert updated.attributes["forca"] == 3

    doc = queries.insert_document(
        db.conn,
        ImportedDocument(
            id=None,
            uuid=str(uuid.uuid4()),
            title="Manual",
            source_path="/tmp/x.pdf",
            doc_type="manual",
            system_id=campaign.system_id,
            character_id=None,
            extracted_text="texto extraído",
        ),
    )
    assert doc.id is not None
    listed = queries.list_documents(db.conn, campaign.system_id)
    assert listed[0].title == "Manual"

    queries.delete_character(db.conn, character.id)
    assert queries.get_character(db.conn, character.id) is None
    db.close()


def test_fts_search_and_monster_kind(tmp_path):
    db = Database(tmp_path / "fts.db")
    version = db.conn.execute("SELECT version FROM schema_version").fetchone()
    assert int(version[0]) == 7
    fts = db.conn.execute(
        "SELECT name FROM sqlite_master WHERE name = 'documents_fts'"
    ).fetchone()
    assert fts is not None
    chars_fts = db.conn.execute(
        "SELECT name FROM sqlite_master WHERE name = 'characters_fts'"
    ).fetchone()
    assert chars_fts is not None

    systems = queries.list_systems(db.conn)
    campaign = queries.create_campaign(db.conn, "Mesa FTS", systems[0][0])
    monster = queries.create_character(
        db.conn,
        Character(
            id=None,
            uuid=str(uuid.uuid4()),
            campaign_id=campaign.id,
            system_id=campaign.system_id,
            kind="monster",
            name="Lobo da Serra",
            attributes={"pv_atual": 10, "pv_max": 10, "pm_atual": 4, "pm_max": 4},
        ),
    )
    assert monster.kind == "monster"

    queries.insert_document(
        db.conn,
        ImportedDocument(
            id=None,
            uuid=str(uuid.uuid4()),
            title="Manual da Bruma",
            source_path="/tmp/bruma.pdf",
            doc_type="manual",
            system_id=campaign.system_id,
            character_id=None,
            extracted_text="O dragão de bruma habita as cavernas geladas da serra.",
        ),
    )
    hits = queries.search_documents(db.conn, "bruma")
    assert hits
    assert hits[0].title == "Manual da Bruma"
    assert "bruma" in hits[0].extracted_text.lower()
    ranked = queries.search_documents(db.conn, "dragão", campaign.system_id)
    assert ranked
    db.close()


def test_character_fts_and_session_entries(tmp_path):
    db = Database(tmp_path / "session.db")
    systems = queries.list_systems(db.conn)
    campaign = queries.create_campaign(db.conn, "Mesa Sessão", systems[1][0])
    character = queries.create_character(
        db.conn,
        Character(
            id=None,
            uuid=str(uuid.uuid4()),
            campaign_id=campaign.id,
            system_id=campaign.system_id,
            kind="pc",
            name="Lyra",
            notes="gosta de sombras",
            attributes={"classe": "Feiticeiro", "pericias": ["Acrobacia", "Arcanismo"]},
        ),
    )
    other = queries.create_character(
        db.conn,
        Character(
            id=None,
            uuid=str(uuid.uuid4()),
            campaign_id=campaign.id,
            system_id=campaign.system_id,
            kind="npc",
            name="Guarda",
            attributes={"classe": "Guerreiro"},
        ),
    )
    by_skill = queries.search_characters(db.conn, "Acrobacia", campaign.id)
    assert any(hit.id == character.id for hit in by_skill)
    assert all(hit.id != other.id for hit in by_skill)
    by_class = queries.search_characters(db.conn, "Feiticeiro", campaign.id)
    assert by_class and by_class[0].id == character.id
    encounter = queries.create_encounter(db.conn, campaign.id, "Emboscada")
    entry = queries.create_session_entry(
        db.conn,
        SessionEntry(
            id=None,
            uuid=str(uuid.uuid4()),
            campaign_id=campaign.id,
            encounter_id=encounter.id,
            title="Noite na serra",
            body="O grupo fugiu do lobo.",
            xp="300 cada",
            treasure="2 PO, poção",
        ),
    )
    listed = queries.list_session_entries(db.conn, campaign.id)
    assert listed[0].id == entry.id
    assert listed[0].xp == "300 cada"
    entry.body = "O grupo derrotou o lobo."
    queries.update_session_entry(db.conn, entry)
    loaded = queries.get_session_entry(db.conn, entry.id or 0)
    assert loaded is not None
    assert "derrotou" in loaded.body
    payload = queries.export_campaign(db.conn, campaign.id)
    assert payload["session_entries"]
    assert payload["session_entries"][0]["encounter_name"] == "Emboscada"
    imported = queries.import_campaign(db.conn, payload)
    imported_entries = queries.list_session_entries(db.conn, imported.id)
    assert any(item.title == "Noite na serra" for item in imported_entries)
    imported_encounters = queries.list_encounters(db.conn, imported.id)
    enc_ids = {item.id: item.name for item in imported_encounters}
    linked = next(item for item in imported_entries if item.title == "Noite na serra")
    assert enc_ids.get(linked.encounter_id) == "Emboscada"
    queries.delete_session_entry(db.conn, entry.id or 0)
    assert queries.get_session_entry(db.conn, entry.id or 0) is None
    db.close()


def test_delete_document_and_campaign_export_roundtrip(tmp_path):
    db = Database(tmp_path / "backup.db")
    systems = queries.list_systems(db.conn)
    campaign = queries.create_campaign(db.conn, "Mesa Backup", systems[0][0], "notas da mesa")
    character = queries.create_character(
        db.conn,
        Character(
            id=None,
            uuid=str(uuid.uuid4()),
            campaign_id=campaign.id,
            system_id=campaign.system_id,
            kind="pc",
            name="Kael",
            attributes={"forca": 2, "pv_atual": 10, "pv_max": 10},
        ),
    )
    doc = queries.insert_document(
        db.conn,
        ImportedDocument(
            id=None,
            uuid=str(uuid.uuid4()),
            title="Manual",
            source_path="/tmp/x.pdf",
            doc_type="manual",
            system_id=campaign.system_id,
            character_id=character.id,
            extracted_text="texto extraído da mesa",
        ),
    )
    encounter = queries.create_encounter(db.conn, campaign.id, "Emboscada")
    queries.create_combatant(
        db.conn,
        Combatant(
            id=None,
            encounter_id=encounter.id,
            character_id=character.id,
            name=character.name,
            hp_current=10,
            hp_max=10,
            action_current=1,
            action_max=1,
            grid_x=3,
            grid_y=1,
        ),
    )
    payload = queries.export_campaign(db.conn, campaign.id)
    assert payload["format"] == "gestor-rpg-campaign-v1"
    assert payload["encounters"][0]["grid_cols"] == 12
    assert payload["encounters"][0]["combatants"][0]["grid_x"] == 3
    assert payload["campaign"]["name"] == "Mesa Backup"
    imported = queries.import_campaign(db.conn, payload)
    assert imported.id != campaign.id
    chars = queries.list_characters(db.conn, imported.id)
    assert any(item.name == "Kael" for item in chars)
    encounters = queries.list_encounters(db.conn, imported.id)
    assert any(item.name == "Emboscada" for item in encounters)
    imported_enc = next(item for item in encounters if item.name == "Emboscada")
    imported_combatants = queries.list_combatants(db.conn, imported_enc.id or 0)
    assert imported_combatants[0].grid_x == 3
    assert imported_combatants[0].grid_y == 1
    queries.delete_document(db.conn, doc.id)
    assert queries.get_document(db.conn, doc.id) is None
    hits = queries.search_documents(db.conn, "texto extraído da mesa")
    titles = [hit.title for hit in hits]
    assert "Manual" in titles
    db.close()


def test_schema_v6_removes_alpha_and_tormenta(tmp_path):
    db = Database(tmp_path / "purge.db")
    db.conn.execute(
        "INSERT INTO rpg_systems (slug, name) VALUES (?, ?)",
        ("ddt_alpha", "3D&T Alpha"),
    )
    alpha_id = int(
        db.conn.execute("SELECT id FROM rpg_systems WHERE slug = 'ddt_alpha'").fetchone()[0]
    )
    campaign = queries.create_campaign(db.conn, "Mesa Alpha", alpha_id)
    db.conn.execute("UPDATE schema_version SET version = 5")
    db.conn.commit()
    from gestor_rpg.db.migrations import apply_migrations

    apply_migrations(db.conn)
    systems = [item[1] for item in queries.list_systems(db.conn)]
    assert systems == ["ddt_victory", "dnd5e"]
    assert queries.get_campaign(db.conn, campaign.id) is None
    version = db.conn.execute("SELECT version FROM schema_version").fetchone()
    assert int(version[0]) == 7
    db.close()


def test_locations_people_and_encounter_status(tmp_path):
    db = Database(tmp_path / "world.db")
    systems = queries.list_systems(db.conn)
    campaign = queries.create_campaign(db.conn, "Reino do Vale", systems[0][0])
    city = queries.create_location(
        db.conn,
        Location(
            id=None,
            uuid=str(uuid.uuid4()),
            campaign_id=campaign.id,
            name="Porto Seguro",
            kind="cidade",
            notes="Porto comercial",
            secrets="O prefeito barganha com piratas",
        ),
    )
    character = queries.create_character(
        db.conn,
        Character(
            id=None,
            uuid=str(uuid.uuid4()),
            campaign_id=campaign.id,
            system_id=campaign.system_id,
            kind="npc",
            name="Mara",
            attributes={},
        ),
    )
    person = queries.create_person(
        db.conn,
        Person(
            id=None,
            uuid=str(uuid.uuid4()),
            campaign_id=campaign.id,
            location_id=city.id,
            character_id=character.id,
            name="Mara",
            role="Estalajadeira",
            attitude="aliado",
            notes="Conhece todos os marinheiros",
            secrets="Esconde um mapa no porão",
        ),
    )
    listed = queries.list_people(db.conn, campaign.id)
    assert listed[0].id == person.id
    assert listed[0].location_id == city.id
    encounter = queries.create_encounter(
        db.conn,
        campaign.id,
        "Emboscada no cais",
        location_id=city.id,
        notes="Maré baixa",
        status="preparado",
    )
    assert encounter.status == "preparado"
    encounter.status = "em_andamento"
    queries.update_encounter(db.conn, encounter)
    loaded = queries.get_encounter(db.conn, encounter.id or 0)
    assert loaded is not None
    assert loaded.status == "em_andamento"
    assert loaded.location_id == city.id
    play = queries.pick_play_encounter(db.conn, campaign.id)
    assert play is not None
    assert play.id == encounter.id
    entry = queries.create_session_entry(
        db.conn,
        SessionEntry(
            id=None,
            uuid=str(uuid.uuid4()),
            campaign_id=campaign.id,
            encounter_id=encounter.id,
            title="Noite no porto",
            body="O grupo chegou ao cais.",
            hooks="O mapa no porão da Mara",
        ),
    )
    payload = queries.export_campaign(db.conn, campaign.id)
    assert payload["locations"][0]["name"] == "Porto Seguro"
    assert payload["people"][0]["role"] == "Estalajadeira"
    assert payload["encounters"][0]["status"] == "em_andamento"
    assert payload["session_entries"][0]["hooks"] == "O mapa no porão da Mara"
    imported = queries.import_campaign(db.conn, payload)
    places = queries.list_locations(db.conn, imported.id)
    assert any(item.name == "Porto Seguro" for item in places)
    people = queries.list_people(db.conn, imported.id)
    assert any(item.name == "Mara" and item.role == "Estalajadeira" for item in people)
    imported_enc = next(
        item for item in queries.list_encounters(db.conn, imported.id)
        if item.name == "Emboscada no cais"
    )
    assert imported_enc.status == "em_andamento"
    assert imported_enc.location_id == places[0].id
    imported_notes = queries.list_session_entries(db.conn, imported.id)
    assert any("porão" in item.hooks for item in imported_notes)
    queries.delete_person(db.conn, person.id or 0)
    queries.delete_location(db.conn, city.id or 0)
    assert queries.get_location(db.conn, city.id or 0) is None
    db.close()
