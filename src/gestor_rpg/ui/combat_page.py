from __future__ import annotations

import uuid

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gestor_rpg.core.models import (
    ENCOUNTER_STATUSES,
    Campaign,
    Character,
    Combatant,
    Encounter,
    encounter_status_label,
)
from gestor_rpg.core.plugin import read_pool
from gestor_rpg.core.registry import PluginRegistry
from gestor_rpg.db import queries
from gestor_rpg.db.connection import Database
from gestor_rpg.modules.combat_grid import clamp_cell, next_free_cell
from gestor_rpg.modules.dice.parser import roll
from gestor_rpg.ui.combat_grid import CombatGridView
from gestor_rpg.ui.styles import (
    EMPTY_NO_CAMPAIGN,
    INK,
    MUTED,
    SAGE_SOFT,
    make_empty_hint,
    set_empty_state,
    set_role,
    fit_button,
)


def _clamp_pool(current: int, amount: int, maximum: int) -> int:
    value = current + amount
    if amount < 0:
        return max(0, value)
    cap = maximum if maximum else value
    return min(cap, value)


def _initiative_expr(bonus: int) -> str:
    if bonus > 0:
        return f"1d20+{bonus}"
    if bonus < 0:
        return f"1d20{bonus}"
    return "1d20"


def _pool_row(current: QSpinBox, maximum: QSpinBox) -> QWidget:
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    layout.addWidget(current, 1)
    slash = QLabel("/")
    slash.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(slash)
    layout.addWidget(maximum, 1)
    return row


class CombatPage(QWidget):
    def __init__(
        self,
        db: Database,
        registry: PluginRegistry,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.db = db
        self.registry = registry
        self.campaign: Campaign | None = None
        self.encounter: Encounter | None = None
        self._roster: list[Character] = []
        self._combatants: list[Combatant] = []
        self._current: Combatant | None = None
        self._filling = False

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        title = QLabel("Combate")
        title.setObjectName("pageTitle")
        root.addWidget(title)
        self.hint = QLabel("Abra uma campanha para preparar e rodar as lutas.")
        self.hint.setObjectName("pageSubtitle")
        root.addWidget(self.hint)

        top = QHBoxLayout()
        top.setSpacing(10)
        self.round_label = QLabel("Rodada —")
        self.round_label.setObjectName("roundBadge")
        self.round_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.encounter_box = QComboBox()
        self.encounter_box.currentIndexChanged.connect(self._on_encounter_chosen)
        self.btn_next = QPushButton("Próximo turno")
        self.btn_init = QPushButton("Rolar iniciativa")
        self.btn_new = QPushButton("Nova luta")
        self.btn_delete_encounter = QPushButton("Excluir luta")
        set_role(self.btn_next, "primary")
        set_role(self.btn_delete_encounter, "quiet")
        self.btn_next.clicked.connect(self._next_turn)
        self.btn_init.clicked.connect(self._roll_initiative)
        self.btn_new.clicked.connect(self._new_encounter)
        self.btn_delete_encounter.clicked.connect(self._delete_encounter)
        top.addWidget(self.round_label)
        top.addWidget(QLabel("Luta"))
        top.addWidget(self.encounter_box, 1)
        root.addLayout(top)
        meta = QGridLayout()
        meta.setHorizontalSpacing(8)
        meta.setVerticalSpacing(8)
        self.fight_name = QLineEdit()
        self.fight_name.setPlaceholderText("Nome da luta")
        self.fight_name.editingFinished.connect(self._persist_fight_meta)
        self.fight_location = QComboBox()
        self.fight_location.currentIndexChanged.connect(self._persist_fight_meta)
        self.fight_status = QComboBox()
        for key, label in ENCOUNTER_STATUSES:
            self.fight_status.addItem(label, key)
        self.fight_status.currentIndexChanged.connect(self._persist_fight_meta)
        meta.addWidget(QLabel("Nome"), 0, 0)
        meta.addWidget(self.fight_name, 0, 1)
        meta.addWidget(QLabel("Local"), 0, 2)
        meta.addWidget(self.fight_location, 0, 3)
        meta.addWidget(QLabel("Situação"), 1, 0)
        meta.addWidget(self.fight_status, 1, 1)
        self.fight_notes = QTextEdit()
        self.fight_notes.setPlaceholderText("Terreno, gatilho, o que o grupo não viu ainda…")
        self.fight_notes.setMaximumHeight(72)
        self.fight_notes.setTabChangesFocus(True)
        meta.addWidget(QLabel("Notas"), 1, 2)
        meta.addWidget(self.fight_notes, 1, 3)
        meta.setColumnStretch(1, 1)
        meta.setColumnStretch(3, 2)
        root.addLayout(meta)
        actions = QGridLayout()
        actions.setHorizontalSpacing(8)
        actions.setVerticalSpacing(8)
        actions.addWidget(self.btn_next, 0, 0)
        actions.addWidget(self.btn_init, 0, 1)
        actions.addWidget(self.btn_new, 1, 0)
        actions.addWidget(self.btn_delete_encounter, 1, 1)
        root.addLayout(actions)

        splitter = QSplitter()
        roster_box = QWidget()
        roster_box.setObjectName("sidePanel")
        roster_l = QVBoxLayout(roster_box)
        roster_l.setContentsMargins(12, 12, 12, 12)
        roster_l.setSpacing(10)
        roster_title = QLabel("PERSONAGENS")
        roster_title.setObjectName("sectionTitle")
        roster_l.addWidget(roster_title)
        self.roster = QListWidget()
        self.roster_empty = make_empty_hint(EMPTY_NO_CAMPAIGN)
        roster_l.addWidget(self.roster, 1)
        roster_l.addWidget(self.roster_empty, 1)
        self.roster.hide()
        self.btn_add = QPushButton("Adicionar ao combate")
        self.btn_add.clicked.connect(self._add_from_roster)
        roster_l.addWidget(self.btn_add)
        adhoc = QHBoxLayout()
        adhoc.setSpacing(8)
        self.adhoc_name = QLineEdit()
        self.adhoc_name.setPlaceholderText("Combatente avulso")
        self.btn_adhoc = QPushButton("Adicionar")
        self.btn_adhoc.clicked.connect(self._add_adhoc)
        adhoc.addWidget(self.adhoc_name, 1)
        adhoc.addWidget(self.btn_adhoc)
        roster_l.addLayout(adhoc)
        splitter.addWidget(roster_box)

        order_box = QWidget()
        order_box.setObjectName("sidePanel")
        order_box.setProperty("tone", "paper")
        order_l = QVBoxLayout(order_box)
        order_l.setContentsMargins(12, 12, 12, 12)
        order_l.setSpacing(10)
        order_title = QLabel("INICIATIVA")
        order_title.setObjectName("sectionTitle")
        order_l.addWidget(order_title)
        self.order = QListWidget()
        self.order.currentRowChanged.connect(self._on_combatant)
        self.order_empty = make_empty_hint(EMPTY_NO_CAMPAIGN)
        order_l.addWidget(self.order, 1)
        order_l.addWidget(self.order_empty, 1)
        self.order.hide()
        self.btn_remove = QPushButton("Remover do combate")
        self.btn_remove.clicked.connect(self._remove)
        order_l.addWidget(self.btn_remove)
        splitter.addWidget(order_box)
        style = order_box.style()
        style.unpolish(order_box)
        style.polish(order_box)

        detail = QWidget()
        detail_l = QVBoxLayout(detail)
        detail_l.setContentsMargins(4, 0, 0, 0)
        detail_l.setSpacing(10)
        detail_title = QLabel("COMBATENTE")
        detail_title.setObjectName("sectionTitle")
        detail_l.addWidget(detail_title)
        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        self.detail_name = QLabel("—")
        self.initiative = QSpinBox()
        self.initiative.setRange(-20, 40)
        self.hp_current = QSpinBox()
        self.hp_current.setRange(0, 9999)
        self.hp_max = QSpinBox()
        self.hp_max.setRange(0, 9999)
        self.resource_current = QSpinBox()
        self.resource_current.setRange(0, 9999)
        self.resource_max = QSpinBox()
        self.resource_max.setRange(0, 9999)
        self.action_current = QSpinBox()
        self.action_current.setRange(0, 9999)
        self.action_max = QSpinBox()
        self.action_max.setRange(0, 9999)
        self.hp_label = QLabel("PV")
        self.res_label = QLabel("PM")
        self.action_label = QLabel("PA")
        self.hp_row = _pool_row(self.hp_current, self.hp_max)
        self.resource_row = _pool_row(self.resource_current, self.resource_max)
        self.action_row = _pool_row(self.action_current, self.action_max)
        form.addRow("Nome", self.detail_name)
        form.addRow("Iniciativa", self.initiative)
        form.addRow(self.hp_label, self.hp_row)
        form.addRow(self.res_label, self.resource_row)
        form.addRow(self.action_label, self.action_row)
        for spin in (
            self.initiative,
            self.hp_current,
            self.hp_max,
            self.resource_current,
            self.resource_max,
            self.action_current,
            self.action_max,
        ):
            spin.editingFinished.connect(self._persist_fields)

        apply = QVBoxLayout()
        apply.setContentsMargins(0, 8, 0, 0)
        apply.setSpacing(8)
        self.amount = QSpinBox()
        self.amount.setRange(1, 999)
        self.amount.setValue(1)
        self.btn_damage = QPushButton("Dano")
        self.btn_heal = QPushButton("Cura")
        self.btn_spend = QPushButton("Gastar PM")
        self.btn_restore = QPushButton("Recuperar PM")
        self.btn_spend_action = QPushButton("Gastar PA")
        self.btn_restore_action = QPushButton("Recuperar PA")
        set_role(self.btn_damage, "foe")
        self.btn_damage.clicked.connect(lambda: self._apply_delta(-self.amount.value(), "hp"))
        self.btn_heal.clicked.connect(lambda: self._apply_delta(self.amount.value(), "hp"))
        self.btn_spend.clicked.connect(lambda: self._apply_delta(-self.amount.value(), "resource"))
        self.btn_restore.clicked.connect(lambda: self._apply_delta(self.amount.value(), "resource"))
        self.btn_spend_action.clicked.connect(lambda: self._apply_delta(-self.amount.value(), "action"))
        self.btn_restore_action.clicked.connect(lambda: self._apply_delta(self.amount.value(), "action"))
        hp_btns = QHBoxLayout()
        hp_btns.setSpacing(8)
        hp_btns.addWidget(QLabel("Dano / cura"))
        hp_btns.addWidget(self.amount, 1)
        hp_btns.addWidget(self.btn_damage)
        hp_btns.addWidget(self.btn_heal)
        apply.addLayout(hp_btns)
        self.resource_btns = QWidget()
        res_btns = QHBoxLayout(self.resource_btns)
        res_btns.setContentsMargins(0, 0, 0, 0)
        res_btns.setSpacing(8)
        res_btns.addWidget(self.btn_spend, 1)
        res_btns.addWidget(self.btn_restore, 1)
        apply.addWidget(self.resource_btns)
        self.action_btns = QWidget()
        act_btns = QHBoxLayout(self.action_btns)
        act_btns.setContentsMargins(0, 0, 0, 0)
        act_btns.setSpacing(8)
        act_btns.addWidget(self.btn_spend_action, 1)
        act_btns.addWidget(self.btn_restore_action, 1)
        apply.addWidget(self.action_btns)
        apply_host = QWidget()
        apply_host.setLayout(apply)
        form.addRow(apply_host)
        detail_l.addLayout(form, 1)
        splitter.addWidget(detail)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 3)
        root.addWidget(splitter, 1)

        self.map_panel = QWidget(self)
        self.map_panel.setObjectName("mapPanel")
        map_l = QVBoxLayout(self.map_panel)
        map_l.setContentsMargins(12, 16, 12, 12)
        map_l.setSpacing(10)
        map_title = QLabel("MAPA")
        map_title.setObjectName("sectionTitle")
        map_l.addWidget(map_title)
        map_size = QHBoxLayout()
        map_size.setSpacing(8)
        self.grid_cols = QSpinBox()
        self.grid_cols.setRange(4, 24)
        self.grid_cols.setValue(12)
        self.grid_rows = QSpinBox()
        self.grid_rows.setRange(4, 16)
        self.grid_rows.setValue(8)
        self.grid_cols.editingFinished.connect(self._resize_grid)
        self.grid_rows.editingFinished.connect(self._resize_grid)
        map_size.addWidget(QLabel("Colunas"))
        map_size.addWidget(self.grid_cols, 1)
        map_size.addWidget(QLabel("Linhas"))
        map_size.addWidget(self.grid_rows, 1)
        map_l.addLayout(map_size)
        map_card = QWidget()
        map_card.setObjectName("mapCard")
        card_l = QVBoxLayout(map_card)
        card_l.setContentsMargins(8, 8, 8, 8)
        card_l.setSpacing(0)
        self.grid = CombatGridView()
        self.grid.token_selected.connect(self._on_token_selected)
        self.grid.token_moved.connect(self._on_token_moved)
        card_l.addWidget(self.grid, 1)
        map_l.addWidget(map_card, 1)
        zoom_row = QHBoxLayout()
        zoom_row.setSpacing(8)
        self.btn_zoom = QPushButton("Ajustar zoom")
        self.btn_zoom.clicked.connect(self.grid.refit)
        zoom_row.addWidget(self.btn_zoom)
        zoom_row.addStretch(1)
        map_l.addLayout(zoom_row)
        hint_map = QLabel("Casas A1… · roda do mouse para zoom")
        hint_map.setObjectName("mutedHint")
        hint_map.setWordWrap(True)
        map_l.addWidget(hint_map)
        self._relabel_pools()
        self._set_enabled(False)

    def set_campaign(self, campaign: Campaign | None) -> None:
        self.campaign = campaign
        self.encounter = None
        if campaign is None:
            self.hint.setText("Abra uma campanha para preparar e rodar as lutas.")
            self._set_enabled(False)
            self.roster.clear()
            self.order.clear()
            self._roster = []
            self._combatants = []
            self.round_label.setText("Rodada —")
            self.encounter_box.blockSignals(True)
            self.encounter_box.clear()
            self.encounter_box.blockSignals(False)
            self._fill_fight_form(None)
            self.grid.set_board(12, 8, [])
            self.roster_empty.setText(EMPTY_NO_CAMPAIGN)
            self.order_empty.setText(EMPTY_NO_CAMPAIGN)
            set_empty_state(self.roster, self.roster_empty, True)
            set_empty_state(self.order, self.order_empty, True)
            return
        self.hint.setText(f"{campaign.name}  ·  {campaign.system_name}")
        self._set_enabled(True)
        self._relabel_pools()
        self.reload()

    def reload(self) -> None:
        if self.campaign is None:
            return
        self._roster = queries.list_characters(self.db.conn, self.campaign.id)
        self.roster.clear()
        for character in self._roster:
            self.roster.addItem(
                QListWidgetItem(f"[{character.kind.upper()}] {character.name}")
            )
        self.roster_empty.setText("Nenhum personagem na campanha")
        set_empty_state(self.roster, self.roster_empty, not self._roster)
        if self.encounter is None or self.encounter.id is None:
            self.encounter = queries.get_or_create_encounter(self.db.conn, self.campaign.id)
        else:
            loaded = queries.get_encounter(self.db.conn, self.encounter.id)
            self.encounter = loaded or queries.get_or_create_encounter(
                self.db.conn, self.campaign.id
            )
        self._fill_encounters()
        self._reload_combatants()

    def _fill_encounters(self) -> None:
        if self.campaign is None:
            return
        current_id = self.encounter.id if self.encounter else None
        encounters = queries.list_encounters(self.db.conn, self.campaign.id)
        self.encounter_box.blockSignals(True)
        self.encounter_box.clear()
        selected = 0
        for index, encounter in enumerate(encounters):
            self.encounter_box.addItem(self._encounter_label(encounter), encounter.id)
            if encounter.id == current_id:
                selected = index
        self.encounter_box.setCurrentIndex(selected)
        self.encounter_box.blockSignals(False)
        if encounters:
            chosen = encounters[selected]
            self.encounter = queries.get_encounter(self.db.conn, chosen.id or 0) or chosen
        self._fill_fight_form(self.encounter)

    def _encounter_label(self, encounter: Encounter) -> str:
        status = encounter_status_label(encounter.status)
        return f"{encounter.name}  ·  {status}  ·  rodada {encounter.round}"

    def _fill_locations(self, selected_id: int | None = None) -> None:
        self.fight_location.blockSignals(True)
        self.fight_location.clear()
        self.fight_location.addItem("Nenhum", None)
        if self.campaign is not None:
            for item in queries.list_locations(self.db.conn, self.campaign.id):
                self.fight_location.addItem(item.name, item.id)
        if selected_id is not None:
            index = self.fight_location.findData(selected_id)
            self.fight_location.setCurrentIndex(index if index >= 0 else 0)
        else:
            self.fight_location.setCurrentIndex(0)
        self.fight_location.blockSignals(False)

    def _fill_fight_form(self, encounter: Encounter | None) -> None:
        self._filling = True
        if encounter is None:
            self.fight_name.clear()
            self._fill_locations()
            self.fight_status.setCurrentIndex(0)
            self.fight_notes.clear()
            self._filling = False
            return
        self.fight_name.setText(encounter.name)
        self._fill_locations(encounter.location_id)
        index = self.fight_status.findData(encounter.status)
        self.fight_status.setCurrentIndex(index if index >= 0 else 0)
        self.fight_notes.setPlainText(encounter.notes)
        self._filling = False

    def _persist_fight_meta(self) -> None:
        if self._filling or self.encounter is None or self.encounter.id is None:
            return
        name = self.fight_name.text().strip() or self.encounter.name
        self.encounter.name = name
        self.encounter.location_id = self.fight_location.currentData()
        self.encounter.status = str(self.fight_status.currentData() or "preparado")
        self.encounter.notes = self.fight_notes.toPlainText()
        queries.update_encounter(self.db.conn, self.encounter)
        index = self.encounter_box.currentIndex()
        if index >= 0:
            self.encounter_box.setItemText(index, self._encounter_label(self.encounter))

    def _on_encounter_chosen(self, index: int) -> None:
        if self._filling:
            return
        self._persist_fight_meta()
        encounter_id = self.encounter_box.itemData(index)
        if encounter_id is None:
            return
        encounter = queries.get_encounter(self.db.conn, int(encounter_id))
        if encounter is None:
            return
        self.encounter = encounter
        self._fill_fight_form(encounter)
        self._reload_combatants()

    def _relabel_pools(self) -> None:
        plugin = self._plugin()
        paths = plugin.hp_paths() if plugin else {}
        labels = self._pool_labels()
        self.hp_label.setText(labels["hp"])
        self.res_label.setText(labels["resource"])
        self.action_label.setText(labels["action"])
        resource = labels["resource"]
        action = labels["action"]
        self.btn_spend.setText(
            "Gastar recurso" if resource == "Recurso" else f"Gastar {resource}"
        )
        self.btn_restore.setText(
            "Recuperar recurso" if resource == "Recurso" else f"Recuperar {resource}"
        )
        self.btn_spend_action.setText(f"Gastar {action}")
        self.btn_restore_action.setText(f"Recuperar {action}")
        for button in (
            self.btn_spend,
            self.btn_restore,
            self.btn_spend_action,
            self.btn_restore_action,
        ):
            fit_button(button)
        has_resource = bool(paths.get("resource"))
        self.res_label.setVisible(has_resource)
        self.resource_row.setVisible(has_resource)
        self.resource_btns.setVisible(has_resource)
        has_action = bool(paths.get("action"))
        self.action_label.setVisible(has_action)
        self.action_row.setVisible(has_action)
        self.action_btns.setVisible(has_action)

    def _pool_labels(self) -> dict[str, str]:
        plugin = self._plugin()
        if plugin and plugin.slug == "dnd5e":
            return {"hp": "HP", "resource": "Recurso", "action": "Ação"}
        return {"hp": "PV", "resource": "PM", "action": "PA"}

    def _plugin(self):
        if self.campaign is None:
            return None
        return self.registry.get(self.campaign.system_slug)

    def _set_enabled(self, enabled: bool) -> None:
        for widget in (
            self.roster,
            self.order,
            self.btn_add,
            self.btn_adhoc,
            self.btn_remove,
            self.btn_next,
            self.btn_init,
            self.btn_new,
            self.btn_delete_encounter,
            self.encounter_box,
            self.fight_name,
            self.fight_location,
            self.fight_status,
            self.fight_notes,
            self.adhoc_name,
            self.grid,
            self.grid_cols,
            self.grid_rows,
            self.btn_zoom,
        ):
            widget.setEnabled(enabled)

    def _reload_combatants(self, select_id: int | None = None) -> None:
        if self.encounter is None or self.encounter.id is None:
            return
        self._combatants = queries.list_combatants(self.db.conn, self.encounter.id)
        self._ensure_positions()
        self.round_label.setText(f"Rodada {self.encounter.round}")
        index = self.encounter_box.currentIndex()
        if index >= 0:
            self.encounter_box.setItemText(index, self._encounter_label(self.encounter))
        self.order.blockSignals(True)
        self.order.clear()
        selected = 0
        for i, combatant in enumerate(self._combatants):
            self.order.addItem(self._order_item(combatant))
            if (select_id is not None and combatant.id == select_id) or (
                select_id is None and combatant.is_active
            ):
                selected = i
        self.order.blockSignals(False)
        self.order_empty.setText("Nenhum combate ainda")
        set_empty_state(self.order, self.order_empty, not self._combatants)
        if self._combatants:
            self.order.setCurrentRow(selected)
        else:
            self._current = None
        self._sync_grid()

    def _order_item(self, combatant: Combatant) -> QListWidgetItem:
        labels = self._pool_labels()
        plugin = self._plugin()
        paths = plugin.hp_paths() if plugin else {}
        marker = "▶ " if combatant.is_active else ""
        extra = ""
        if paths.get("resource") and combatant.resource_max:
            extra += (
                f"  {labels['resource']} "
                f"{combatant.resource_current}/{combatant.resource_max}"
            )
        if paths.get("action") and combatant.action_max:
            extra += (
                f"  {labels['action']} "
                f"{combatant.action_current}/{combatant.action_max}"
            )
        hp = f"{combatant.hp_current}/{combatant.hp_max}"
        item = QListWidgetItem(
            f"{marker}{combatant.initiative:02d}  {combatant.name}  [{hp}]{extra}"
        )
        font = QFont(item.font())
        if combatant.hp_current <= 0:
            font.setStrikeOut(True)
            item.setForeground(QBrush(QColor(MUTED)))
        if combatant.is_active:
            item.setData(Qt.ItemDataRole.UserRole, "active")
            item.setBackground(QBrush(QColor(SAGE_SOFT)))
            if combatant.hp_current > 0:
                item.setForeground(QBrush(QColor(INK)))
            font.setBold(True)
        item.setFont(font)
        return item

    def _add_from_roster(self) -> None:
        if self.campaign is None or self.encounter is None or self.encounter.id is None:
            return
        row = self.roster.currentRow()
        if not (0 <= row < len(self._roster)):
            QMessageBox.warning(self, "Combate", "Selecione um personagem na lista.")
            return
        character = self._roster[row]
        plugin = self._plugin()
        paths = plugin.hp_paths() if plugin else {"hp": ("hp_atual", "hp_max")}
        pool = read_pool(character.attributes, paths)
        cell = self._next_cell()
        combatant = Combatant(
            id=None,
            encounter_id=self.encounter.id,
            character_id=character.id,
            name=character.name,
            hp_current=pool["hp_current"],
            hp_max=pool["hp_max"],
            resource_current=pool["resource_current"],
            resource_max=pool["resource_max"],
            action_current=pool["action_current"],
            action_max=pool["action_max"],
            sort_order=len(self._combatants),
            snapshot=dict(character.attributes),
            grid_x=cell[0],
            grid_y=cell[1],
        )
        created = queries.create_combatant(self.db.conn, combatant)
        self._reload_combatants(created.id)

    def _add_adhoc(self) -> None:
        if self.encounter is None or self.encounter.id is None:
            return
        name = self.adhoc_name.text().strip() or "Combatente"
        cell = self._next_cell()
        combatant = Combatant(
            id=None,
            encounter_id=self.encounter.id,
            character_id=None,
            name=name,
            hp_current=10,
            hp_max=10,
            sort_order=len(self._combatants),
            grid_x=cell[0],
            grid_y=cell[1],
        )
        created = queries.create_combatant(self.db.conn, combatant)
        self.adhoc_name.clear()
        self._reload_combatants(created.id)

    def _remove(self) -> None:
        current = self._current
        if current is None or current.id is None:
            return
        queries.delete_combatant(self.db.conn, current.id)
        self._current = None
        self._reload_combatants()

    def _on_combatant(self, row: int) -> None:
        if not (0 <= row < len(self._combatants)):
            self._current = None
            return
        self._current = self._combatants[row]
        self._fill_detail(self._current)
        if self._current.id is not None:
            self.grid.highlight(self._current.id)

    def _next_cell(self) -> tuple[int, int]:
        cols = self.encounter.grid_cols if self.encounter else 12
        rows = self.encounter.grid_rows if self.encounter else 8
        occupied = {
            (item.grid_x, item.grid_y)
            for item in self._combatants
            if item.grid_x >= 0 and item.grid_y >= 0
        }
        return next_free_cell(cols, rows, occupied)

    def _ensure_positions(self) -> None:
        if self.encounter is None:
            return
        occupied = {
            (item.grid_x, item.grid_y)
            for item in self._combatants
            if item.grid_x >= 0 and item.grid_y >= 0
        }
        changed = False
        for combatant in self._combatants:
            if combatant.grid_x >= 0 and combatant.grid_y >= 0:
                continue
            x, y = next_free_cell(self.encounter.grid_cols, self.encounter.grid_rows, occupied)
            combatant.grid_x, combatant.grid_y = x, y
            occupied.add((x, y))
            queries.update_combatant(self.db.conn, combatant)
            changed = True
        if changed:
            self._combatants = queries.list_combatants(self.db.conn, self.encounter.id or 0)

    def _sync_grid(self) -> None:
        if self.encounter is None:
            self.grid.set_board(12, 8, [])
            return
        self.grid_cols.blockSignals(True)
        self.grid_rows.blockSignals(True)
        self.grid_cols.setValue(self.encounter.grid_cols)
        self.grid_rows.setValue(self.encounter.grid_rows)
        self.grid_cols.blockSignals(False)
        self.grid_rows.blockSignals(False)
        self.grid.set_board(self.encounter.grid_cols, self.encounter.grid_rows, self._combatants)
        current_id = self._current.id if self._current else None
        self.grid.highlight(current_id)

    def _on_token_selected(self, combatant_id: int) -> None:
        for index, combatant in enumerate(self._combatants):
            if combatant.id != combatant_id:
                continue
            self.order.blockSignals(True)
            self.order.setCurrentRow(index)
            self.order.blockSignals(False)
            self._current = combatant
            self._fill_detail(combatant)
            self.grid.highlight(combatant_id)
            return

    def _on_token_moved(self, combatant_id: int, col: int, row: int) -> None:
        target_id = combatant_id
        if target_id < 0:
            if self._current is None or self._current.id is None:
                return
            target_id = self._current.id
        combatant = next((item for item in self._combatants if item.id == target_id), None)
        if combatant is None or combatant.id is None:
            return
        occupied = {
            (item.grid_x, item.grid_y)
            for item in self._combatants
            if item.id != combatant.id and item.grid_x >= 0
        }
        if (col, row) in occupied:
            self._sync_grid()
            return
        if combatant.grid_x == col and combatant.grid_y == row:
            self._sync_grid()
            return
        combatant.grid_x, combatant.grid_y = col, row
        queries.update_combatant(self.db.conn, combatant)
        self._reload_combatants(combatant.id)

    def _resize_grid(self) -> None:
        if self.encounter is None or self.encounter.id is None:
            return
        cols = self.grid_cols.value()
        rows = self.grid_rows.value()
        if cols == self.encounter.grid_cols and rows == self.encounter.grid_rows:
            return
        self.encounter.grid_cols = cols
        self.encounter.grid_rows = rows
        queries.update_encounter(self.db.conn, self.encounter)
        for combatant in self._combatants:
            if combatant.grid_x < 0:
                continue
            combatant.grid_x, combatant.grid_y = clamp_cell(
                combatant.grid_x, combatant.grid_y, cols, rows
            )
            queries.update_combatant(self.db.conn, combatant)
        self._reload_combatants(self._current.id if self._current else None)

    def _fill_detail(self, combatant: Combatant) -> None:
        self.detail_name.setText(combatant.name)
        for spin in (
            self.initiative,
            self.hp_current,
            self.hp_max,
            self.resource_current,
            self.resource_max,
            self.action_current,
            self.action_max,
        ):
            spin.blockSignals(True)
        self.initiative.setValue(combatant.initiative)
        self.hp_current.setValue(combatant.hp_current)
        self.hp_max.setValue(combatant.hp_max)
        self.resource_current.setValue(combatant.resource_current)
        self.resource_max.setValue(combatant.resource_max)
        self.action_current.setValue(combatant.action_current)
        self.action_max.setValue(combatant.action_max)
        for spin in (
            self.initiative,
            self.hp_current,
            self.hp_max,
            self.resource_current,
            self.resource_max,
            self.action_current,
            self.action_max,
        ):
            spin.blockSignals(False)

    def _persist_fields(self) -> None:
        current = self._current
        if current is None or current.id is None:
            return
        current.initiative = self.initiative.value()
        plugin = self._plugin()
        queries.apply_combatant_hp(
            self.db.conn,
            current.id,
            hp_current=self.hp_current.value(),
            hp_max=self.hp_max.value(),
            resource_current=self.resource_current.value(),
            resource_max=self.resource_max.value(),
            action_current=self.action_current.value(),
            action_max=self.action_max.value(),
            hp_paths=plugin.hp_paths() if plugin else None,
        )
        current.hp_current = self.hp_current.value()
        current.hp_max = self.hp_max.value()
        current.resource_current = self.resource_current.value()
        current.resource_max = self.resource_max.value()
        current.action_current = self.action_current.value()
        current.action_max = self.action_max.value()
        queries.update_combatant(self.db.conn, current)
        self._reload_combatants(current.id)

    def _apply_delta(self, amount: int, pool: str) -> None:
        current = self._current
        if current is None or current.id is None:
            return
        plugin = self._plugin()
        paths = plugin.hp_paths() if plugin else None
        if pool == "hp":
            queries.apply_combatant_hp(
                self.db.conn,
                current.id,
                hp_current=_clamp_pool(current.hp_current, amount, current.hp_max),
                hp_paths=paths,
            )
        elif pool == "action":
            queries.apply_combatant_hp(
                self.db.conn,
                current.id,
                action_current=_clamp_pool(
                    current.action_current, amount, current.action_max
                ),
                hp_paths=paths,
            )
        else:
            queries.apply_combatant_hp(
                self.db.conn,
                current.id,
                resource_current=_clamp_pool(
                    current.resource_current, amount, current.resource_max
                ),
                hp_paths=paths,
            )
        self._reload_combatants(current.id)

    def _roll_initiative(self) -> None:
        if self.encounter is None or self.encounter.id is None:
            return
        self._persist_fight_meta()
        plugin = self._plugin()
        rolled: list[Combatant] = []
        for combatant in self._combatants:
            bonus = 0
            if plugin is not None:
                attrs = combatant.snapshot
                if combatant.character_id:
                    character = queries.get_character(self.db.conn, combatant.character_id)
                    if character is not None:
                        attrs = character.attributes
                bonus = plugin.initiative_bonus(attrs)
            result = roll(_initiative_expr(bonus))
            combatant.initiative = result.total
            rolled.append(combatant)
        rolled.sort(key=lambda item: (-item.initiative, item.name))
        for index, combatant in enumerate(rolled):
            combatant.sort_order = index
            combatant.is_active = index == 0
            queries.update_combatant(self.db.conn, combatant)
        if self.encounter:
            self.encounter.round = 1
            if self.encounter.status == "preparado":
                self.encounter.status = "em_andamento"
                self._fill_fight_form(self.encounter)
            queries.update_encounter(self.db.conn, self.encounter)
        self._reload_combatants()

    def _next_turn(self) -> None:
        if self.encounter is None or self.encounter.id is None:
            return
        self._persist_fight_meta()
        if self.encounter.status == "preparado":
            self.encounter.status = "em_andamento"
            queries.update_encounter(self.db.conn, self.encounter)
            self._fill_fight_form(self.encounter)
        self.encounter = queries.advance_turn(self.db.conn, self.encounter.id)
        self._reload_combatants()

    def _new_encounter(self) -> None:
        if self.campaign is None:
            return
        if self._combatants and (
            QMessageBox.question(
                self,
                "Nova luta",
                "Criar uma luta nova? A atual permanece no histórico.",
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        self._persist_fight_meta()
        self.encounter = queries.create_encounter(
            self.db.conn, self.campaign.id, f"Luta {uuid.uuid4().hex[:6]}"
        )
        self._fill_encounters()
        self._reload_combatants()

    def _delete_encounter(self) -> None:
        if self.campaign is None or self.encounter is None or self.encounter.id is None:
            return
        if (
            QMessageBox.question(
                self,
                "Excluir luta",
                f"Excluir «{self.encounter.name}» e todos os combatentes?",
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        queries.delete_encounter(self.db.conn, self.encounter.id)
        self.encounter = queries.get_or_create_encounter(self.db.conn, self.campaign.id)
        self._fill_encounters()
        self._reload_combatants()
