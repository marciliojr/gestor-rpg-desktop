from __future__ import annotations

import uuid

from gestor_rpg.core.models import Character, Combatant
from gestor_rpg.core.registry import PluginRegistry
from gestor_rpg.db import queries
from gestor_rpg.db.connection import Database


def test_encounter_initiative_and_damage_persists_json(tmp_path):
    db = Database(tmp_path / "combat.db")
    plugin = PluginRegistry().get("ddt_victory")
    systems = queries.list_systems(db.conn)
    ddt_id = next(item[0] for item in systems if item[1] == "ddt_victory")
    campaign = queries.create_campaign(db.conn, "Combate", ddt_id)
    attrs = plugin.default_attributes()
    attrs["pv_atual"] = 20
    attrs["pv_max"] = 20
    attrs["pm_atual"] = 10
    attrs["pm_max"] = 10
    attrs["pa_atual"] = 3
    attrs["pa_max"] = 3
    character = queries.create_character(
        db.conn,
        Character(
            id=None,
            uuid=str(uuid.uuid4()),
            campaign_id=campaign.id,
            system_id=campaign.system_id,
            kind="pc",
            name="Kael",
            attributes=attrs,
        ),
    )
    encounter = queries.create_encounter(db.conn, campaign.id, "Emboscada")
    first = queries.create_combatant(
        db.conn,
        Combatant(
            id=None,
            encounter_id=encounter.id,
            character_id=character.id,
            name=character.name,
            initiative=14,
            hp_current=20,
            hp_max=20,
            resource_current=10,
            resource_max=10,
            action_current=3,
            action_max=3,
            is_active=True,
            sort_order=0,
            snapshot=dict(attrs),
        ),
    )
    second = queries.create_combatant(
        db.conn,
        Combatant(
            id=None,
            encounter_id=encounter.id,
            character_id=None,
            name="Ratão",
            initiative=8,
            hp_current=6,
            hp_max=6,
            is_active=False,
            sort_order=1,
        ),
    )
    queries.apply_combatant_hp(
        db.conn,
        first.id,
        hp_current=12,
        hp_paths=plugin.hp_paths(),
    )
    loaded = queries.get_character(db.conn, character.id)
    assert loaded is not None
    assert loaded.attributes["pv_atual"] == 12
    assert loaded.attributes["pv_max"] == 20

    queries.apply_combatant_hp(
        db.conn,
        first.id,
        action_current=1,
        hp_paths=plugin.hp_paths(),
    )
    loaded = queries.get_character(db.conn, character.id)
    assert loaded is not None
    assert loaded.attributes["pa_atual"] == 1
    assert loaded.attributes["pa_max"] == 3
    assert "action" in plugin.hp_paths()

    extra = queries.create_encounter(db.conn, campaign.id, "Segundo")
    listed = queries.list_encounters(db.conn, campaign.id)
    assert {item.name for item in listed} >= {"Emboscada", "Segundo"}
    assert extra.id != encounter.id

    advanced = queries.advance_turn(db.conn, encounter.id)
    assert advanced.round == 1
    combatants = queries.list_combatants(db.conn, encounter.id)
    active = [item for item in combatants if item.is_active]
    assert len(active) == 1
    assert active[0].id == second.id

    wrapped = queries.advance_turn(db.conn, encounter.id)
    assert wrapped.round == 2
    db.close()


def test_grid_placement_helpers_and_persistence(tmp_path):
    from gestor_rpg.modules.combat_grid import next_free_cell, token_label

    assert next_free_cell(2, 2, {(0, 0)}) == (1, 0)
    assert token_label("Kael Bravo") == "KB"
    db = Database(tmp_path / "grid.db")
    systems = queries.list_systems(db.conn)
    campaign = queries.create_campaign(db.conn, "Grid", systems[0][0])
    encounter = queries.create_encounter(db.conn, campaign.id, "Arena")
    assert encounter.grid_cols == 12
    assert encounter.grid_rows == 8
    first = queries.create_combatant(
        db.conn,
        Combatant(
            id=None,
            encounter_id=encounter.id,
            character_id=None,
            name="Kael",
            grid_x=2,
            grid_y=3,
        ),
    )
    loaded = queries.get_combatant(db.conn, first.id or 0)
    assert loaded is not None
    assert loaded.grid_x == 2
    assert loaded.grid_y == 3
    encounter.grid_cols = 10
    queries.update_encounter(db.conn, encounter)
    again = queries.get_encounter(db.conn, encounter.id or 0)
    assert again is not None
    assert again.grid_cols == 10
    db.close()
