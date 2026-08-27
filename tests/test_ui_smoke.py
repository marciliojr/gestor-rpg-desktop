from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QWidget

from gestor_rpg.core.registry import PluginRegistry
from gestor_rpg.db.connection import Database
from gestor_rpg.ui.main_window import MainWindow


def test_main_window_and_sheet_widgets(tmp_path):
    app = QApplication.instance() or QApplication([])
    db = Database(tmp_path / "smoke.db")
    window = MainWindow(db)
    window.show()
    assert window.nav_page_labels() == [
        "Campanhas",
        "Locais",
        "Pessoas",
        "Fichas",
        "Documentos",
        "Monstros",
        "Combate",
        "Sessão",
    ]
    nav_texts = [window.nav.item(i).text() for i in range(window.nav.count())]
    assert nav_texts[:2] == ["MESA", "Campanhas"]
    assert "MUNDO" in nav_texts
    assert "PREPARAR" in nav_texts
    assert "JOGAR" in nav_texts
    assert window.menuBar().isHidden()
    assert window.tools.objectName() == "toolsList"
    tool_labels = [window.tools.item(i).text() for i in range(window.tools.count())]
    assert tool_labels == ["NPC rápido…", "Gerador de nomes…", "Importar PDF…"]
    assert window.help_nav.item(0).text() == "Como usar"
    assert window.btn_quit.text() == "Sair"
    assert window.sheets_page.btn_export_pdf.text() == "Exportar PDF…"
    assert window.campaigns_page.btn_export.text() == "Exportar JSON…"
    assert window.campaigns_page.btn_export_pdf.text() == "Exportar PDF…"
    assert window.sheets_page.btn_print.text() == "Imprimir…"
    assert window.combat_page.grid.objectName() == "combatGrid"
    assert window.combat_page.map_panel.objectName() == "mapPanel"
    assert window.combat_page.map_panel.findChild(QWidget, "mapCard") is not None
    assert window.combat_page.round_label.objectName() == "roundBadge"
    assert window.combat_page.hint.objectName() == "pageSubtitle"
    assert window.sheets_page.hint.objectName() == "pageSubtitle"
    assert window.documents_page.hint.objectName() == "pageSubtitle"
    assert window.monsters_page.hint.objectName() == "pageSubtitle"
    assert window.session_page.hint.objectName() == "pageSubtitle"
    assert window.locations_page.hint.objectName() == "pageSubtitle"
    assert window.people_page.hint.objectName() == "pageSubtitle"
    title_texts = [
        next(label.text() for label in page.findChildren(QLabel) if label.objectName() == "pageTitle")
        for page in (
            window.campaigns_page,
            window.locations_page,
            window.people_page,
            window.sheets_page,
            window.documents_page,
            window.monsters_page,
            window.combat_page,
            window.session_page,
            window.help_page,
        )
    ]
    assert title_texts == [
        "Campanhas",
        "Locais",
        "Pessoas",
        "Fichas",
        "Documentos",
        "Monstros",
        "Combate",
        "Sessão",
        "Como usar",
    ]
    assert window.help_page.toc.count() == 14
    assert window.help_page.toc.item(0).text() == "Começar"
    assert window.help_page.toc.item(3).text() == "Locais"
    assert window.sheets_page.btn_save.property("role") == "primary"
    assert window.sheets_page.btn_search.property("role") != "primary"
    assert window.documents_page.btn_import.property("role") == "primary"
    assert window.documents_page.btn_search.property("role") != "primary"
    assert window.monsters_page.btn_generate.property("role") == "primary"
    assert window.monsters_page.btn_save.property("role") != "primary"
    assert window.combat_page.btn_damage.property("role") == "foe"
    assert window.combat_page.btn_zoom.text() == "Ajustar zoom"
    assert window.combat_page.btn_new.text() == "Nova luta"
    assert window.combat_page.fight_name.placeholderText() == "Nome da luta"
    assert window.session_page.hooks.placeholderText().startswith("Ganchos")
    assert window.combat_page.roster.isHidden()
    assert window.combat_page.order_empty.objectName() == "emptyHint"
    assert window.dice_panel.detail.objectName() == "diceDetail"
    assert window.dice_panel.history_empty.objectName() == "emptyHint"
    rail = window.findChild(QWidget, "appRail")
    assert rail.findChild(QWidget, "mapPanel") is window.combat_page.map_panel
    assert not window.combat_page.map_panel.isVisibleTo(window)
    window.select_page(6)
    app.processEvents()
    assert window.combat_page.map_panel.isVisibleTo(window)
    window.select_page(8)
    app.processEvents()
    assert window.stack.currentWidget() is window.help_page
    assert not window.combat_page.map_panel.isVisibleTo(window)
    window.select_page(0)
    app.processEvents()
    assert not window.combat_page.map_panel.isVisibleTo(window)
    assert window.statusBar().isHidden()
    assert window.findChild(QWidget, "appSidebar") is not None
    assert rail is not None
    assert window.dice_panel.objectName() == "dicePanel"
    assert window.dice_panel.btn_clear.text() == "Limpar histórico"
    side_panels = window.findChildren(QWidget, "sidePanel")
    assert len(side_panels) >= 8
    assert any(panel.property("tone") == "paper" for panel in side_panels)
    for plugin in PluginRegistry().all():
        widget = plugin.create_sheet_widget()
        defaults = plugin.default_attributes()
        widget.set_attributes(defaults)
        loaded = widget.get_attributes()
        assert loaded
        assert plugin.validate_attributes(loaded) == []
        widget.deleteLater()
    from gestor_rpg.ui.styles import APP_QSS

    assert "combo-arrow.png" in APP_QSS
    assert window.monsters_page.catalog_list.count() == 0
    victory = PluginRegistry().get("ddt_victory")
    assert len(victory.monster_catalog()) == 47
    window.close()
    db.close()
    app.processEvents()


def test_combat_dnd_labels_hide_pa_and_strike_downed(tmp_path):
    from gestor_rpg.core.models import Combatant
    from gestor_rpg.db import queries

    app = QApplication.instance() or QApplication([])
    db = Database(tmp_path / "combat-ui.db")
    window = MainWindow(db)
    systems = queries.list_systems(db.conn)
    dnd_id = next(item[0] for item in systems if item[1] == "dnd5e")
    campaign = queries.create_campaign(db.conn, "Faerûn", dnd_id)
    window.combat_page.set_campaign(campaign)
    assert window.combat_page.hp_label.text() == "HP"
    assert window.combat_page.res_label.text() == "Recurso"
    assert window.combat_page.action_row.isHidden()
    assert not window.combat_page.resource_row.isHidden()
    encounter = window.combat_page.encounter
    assert encounter is not None
    assert encounter.id is not None
    queries.create_combatant(
        db.conn,
        Combatant(
            id=None,
            encounter_id=encounter.id,
            character_id=None,
            name="Orc",
            initiative=12,
            hp_current=0,
            hp_max=15,
            resource_current=2,
            resource_max=4,
            action_current=1,
            action_max=2,
            is_active=True,
            sort_order=0,
        ),
    )
    window.combat_page._reload_combatants()
    item = window.combat_page.order.item(0)
    assert item is not None
    text = item.text()
    assert "PM" not in text
    assert "PA" not in text
    assert "Recurso" in text
    assert item.font().strikeOut()
    window.close()
    db.close()
    app.processEvents()
