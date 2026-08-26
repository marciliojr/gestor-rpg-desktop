from __future__ import annotations

import random

from gestor_rpg.core.models import PdfExtract
from gestor_rpg.core.registry import PluginRegistry


def test_all_plugins_defaults_and_npc():
    registry = PluginRegistry()
    assert registry.slugs() == ["ddt_victory", "dnd5e"]
    for plugin in registry.all():
        defaults = plugin.default_attributes()
        assert plugin.validate_attributes(defaults) == []
        npc = plugin.generate_npc({"power": "medio", "rng": random.Random(1)})
        assert "attributes" in npc
        assert npc["motivation"]
        assert npc["story_hook"]
        errors = plugin.validate_attributes(npc["attributes"])
        assert errors == [], errors


def test_victory_monster_catalog():
    plugin = PluginRegistry().get("ddt_victory")
    catalog = plugin.monster_catalog()
    assert len(catalog) == 47
    slugs = {item["slug"] for item in catalog}
    names = {item["name"] for item in catalog}
    assert "grunk-guerreiro-perpetuo-grunt" in slugs
    assert "Grunk (Guerreiro Perpétuo / Grunt)" in names
    assert "orochi" in slugs
    categories = {item["category"] for item in catalog}
    assert categories == {
        "masmorras",
        "sombria",
        "mitica",
        "epica",
        "ajudantes",
        "ferozes",
    }
    grunk = plugin.generate_monster({"name": "grunk-guerreiro-perpetuo-grunt"})
    assert grunk["name"].startswith("Grunk")
    assert grunk["attributes"]["pv_max"] == 5
    assert grunk["attributes"]["poder"] == 1
    assert grunk["attributes"]["habilidade"] == 1
    assert grunk["attributes"]["resistencia"] == 1
    assert "armadura" not in grunk["attributes"]
    assert "poder_de_fogo" not in grunk["attributes"]
    assert grunk["attributes"]["pm_max"] == 0
    assert grunk["attributes"]["pa_max"] == 0
    assert plugin.validate_attributes(grunk["attributes"]) == []
    random_one = plugin.generate_monster({"power": "fraco", "rng": random.Random(3)})
    assert random_one["attributes"]["pv_max"] >= 1
    assert plugin.validate_attributes(random_one["attributes"]) == []


def test_dnd_monster_catalog():
    plugin = PluginRegistry().get("dnd5e")
    catalog = plugin.monster_catalog()
    assert len(catalog) == 109
    slugs = {item["slug"] for item in catalog}
    names = {item["name"] for item in catalog}
    assert "goblin" in slugs
    assert "Goblin" in names
    assert "veterano" in slugs
    assert "aarakocra" in slugs
    types = {item["category_label"] for item in catalog}
    assert "Humanoide" in types
    assert "Besta" in types
    assert "Dragão" in types
    veteran = plugin.generate_monster({"name": "veterano"})
    assert veteran["name"] == "Veterano"
    assert veteran["attributes"]["ca"] == 17
    assert veteran["attributes"]["hp_max"] == 58
    assert veteran["attributes"]["abilities"]["str"] == 16
    assert plugin.validate_attributes(veteran["attributes"]) == []
    goblin = plugin.generate_monster({"name": "goblin"})
    assert goblin["challenge"] == "1/4"
    assert goblin["attributes"]["classe"] == "Humanoide"
    random_one = plugin.generate_monster({"power": "fraco", "rng": random.Random(3)})
    assert random_one["attributes"]["hp_max"] >= 1
    assert plugin.validate_attributes(random_one["attributes"]) == []


def test_all_plugins_generate_monster():
    registry = PluginRegistry()
    for plugin in registry.all():
        monster = plugin.generate_monster({"power": "medio", "rng": random.Random(1)})
        assert monster["name"]
        assert "attributes" in monster
        assert "challenge" in monster
        assert "notes" in monster
        errors = plugin.validate_attributes(monster["attributes"])
        assert errors == [], errors
        paths = plugin.hp_paths()
        assert "hp" in paths
        again = plugin.generate_monster({"level": 5, "rng": random.Random(2)})
        assert plugin.validate_attributes(again["attributes"]) == []


def test_parse_ddt_victory_sheet():
    plugin = PluginRegistry().get("ddt_victory")
    text = """
    Nome: Kael
    Poder: 2
    Habilidade: 1
    Resistência: 2
    PV: 10
    PM: 5
    PA: 1
    Arquétipo: Guerreiro
    """
    parsed = plugin.try_parse_sheet(
        PdfExtract(path="x.pdf", full_text=text, page_texts=[text], used_ocr=False)
    )
    assert parsed is not None
    assert parsed.name == "Kael"
    assert parsed.attributes["poder"] == 2
    assert parsed.attributes["resistencia"] == 2
    assert "armadura" not in parsed.attributes
    assert "poder_de_fogo" not in parsed.attributes


def test_parse_dnd_requires_enough_fields():
    plugin = PluginRegistry().get("dnd5e")
    weak = PdfExtract(path="x.pdf", full_text="olá mundo", page_texts=["olá mundo"], used_ocr=False)
    assert plugin.try_parse_sheet(weak) is None
    text = "Name: Mira\nStrength: 16\nDexterity: 14\nConstitution: 13\nHP: 12\nAC: 16\nLevel: 3"
    parsed = plugin.try_parse_sheet(
        PdfExtract(path="x.pdf", full_text=text, page_texts=[text], used_ocr=False)
    )
    assert parsed is not None
    assert parsed.attributes["abilities"]["str"] == 16
    assert parsed.attributes["ca"] == 16


def test_victory_and_dnd_sheet_fields_match_official():
    registry = PluginRegistry()
    victory = registry.get("ddt_victory")
    defaults = victory.default_attributes()
    for key in ("arquetipo", "pa_atual", "pa_max", "tecnicas", "xp", "inventario_comum", "poder"):
        assert key in defaults
    assert "armadura" not in defaults
    assert "poder_de_fogo" not in defaults
    assert "forca" not in defaults
    assert "magias" not in defaults
    npc = victory.generate_npc({"power": "medio", "rng": random.Random(1)})
    assert victory.validate_attributes(npc["attributes"]) == []

    dnd = registry.get("dnd5e")
    dnd_defaults = dnd.default_attributes()
    for key in (
        "alinhamento",
        "arquetipo",
        "hp_temp",
        "espacos_magia",
        "recurso_nome",
        "metamagia",
        "truques",
        "expertise",
        "armas",
    ):
        assert key in dnd_defaults
    assert dnd.validate_attributes(dnd_defaults) == []

    form_text = """
    Name: Kael
    Strength: 8
    Dexterity: 14
    Constitution: 16
    HP: 18
    AC: 13
    Level: 3
    Class: Feiticeiro
    Archetype: Dracônico
    Proficiency Athletics: yes
    Sorcery Points: 3
    """
    parsed = dnd.try_parse_sheet(
        PdfExtract(path="feiticeiro.pdf", full_text=form_text, page_texts=[form_text], used_ocr=False)
    )
    assert parsed is not None
    assert parsed.attributes["classe"] == "Feiticeiro"
    assert parsed.attributes["arquetipo"] == "Dracônico"
    assert parsed.attributes["recurso_max"] == 3
    assert "Atletismo" in parsed.attributes["pericias"]


def test_monster_preview_differs_by_system():
    registry = PluginRegistry()
    victory = registry.get("ddt_victory")
    dnd = registry.get("dnd5e")
    v_preview = victory.format_monster_preview(
        victory.generate_monster({"name": "grunk-guerreiro-perpetuo-grunt"})
    )
    d_preview = dnd.format_monster_preview(
        dnd.generate_monster({"power": "medio", "rng": random.Random(1)})
    )
    assert "P " in v_preview
    assert "PdF" not in v_preview
    assert "CA " in d_preview
    assert "PdF" not in d_preview
    assert "JSON" not in v_preview
    assert "JSON" not in d_preview
    assert "action" in victory.hp_paths()
    assert "action" not in dnd.hp_paths()


def test_sheet_html_labels_by_system():
    registry = PluginRegistry()
    victory = registry.get("ddt_victory")
    victory_html = victory.format_sheet_html(
        {
            "name": "Kael",
            "kind": "pc",
            "attributes": victory.default_attributes(),
            "system_name": victory.display_name,
        }
    )
    assert "Kael" in victory_html
    assert "PA" in victory_html
    assert "Arquétipo" in victory_html
    assert "PdF" not in victory_html
    assert "Armadura" not in victory_html

    dnd = registry.get("dnd5e")
    dnd_html = dnd.format_sheet_html(
        {
            "name": "Mira",
            "kind": "pc",
            "attributes": dnd.default_attributes(),
            "system_name": dnd.display_name,
        }
    )
    assert "CA" in dnd_html
    assert "Perícias" in dnd_html


def test_dnd_sheet_html_reads_like_character_sheet():
    plugin = PluginRegistry().get("dnd5e")
    attrs = plugin.default_attributes()
    attrs.update(
        {
            "nivel": 3,
            "classe": "Druida",
            "raca": "Anão",
            "abilities": {
                "str": 10,
                "dex": 13,
                "con": 11,
                "int": 14,
                "wis": 14,
                "cha": 11,
            },
            "hp_max": 8,
            "hp_atual": 8,
            "ca": 11,
            "iniciativa": 1,
            "deslocamento": 9,
            "dados_vida": "1d8",
            "pericias": ["Atuação", "Furtividade"],
            "salvaguardas": ["Sabedoria", "Carisma"],
        }
    )
    html = plugin.format_sheet_html(
        {
            "name": "Torin",
            "kind": "pc",
            "attributes": attrs,
            "system_name": plugin.display_name,
        }
    )
    assert "Torin" in html
    assert "Druida 3" in html
    assert "Anão" in html
    assert "Atuação" in html
    assert "Furtividade" in html
    assert "Sabedoria" in html
    assert "Pontos de Feitiçaria" not in html
    assert "Metamagia" not in html
    assert "espacos_magia" not in html
    assert '"hp_max"' not in html
    assert "JSON" not in html

    preview = plugin.format_monster_preview(
        {"name": "Torin", "kind": "pc", "attributes": attrs}
    )
    assert "CA 11" in preview
    assert "Druida 3" in preview
    assert "Atuação" in preview
    assert "JSON" not in preview
    assert '"str":' not in preview

