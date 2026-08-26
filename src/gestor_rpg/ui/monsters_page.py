from __future__ import annotations

import uuid

from PySide6.QtCore import Qt
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
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from gestor_rpg.core.models import Campaign, Character
from gestor_rpg.core.registry import PluginRegistry
from gestor_rpg.db import queries
from gestor_rpg.db.connection import Database
from gestor_rpg.modules.monsters.generator import generate_monster
from gestor_rpg.plugins._ddt_bestiary import POWER_LABELS
from gestor_rpg.ui.styles import EMPTY_NO_CAMPAIGN, make_empty_hint, set_empty_state, set_role


class MonstersPage(QWidget):
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
        self._payload: dict | None = None
        self._monsters: list[Character] = []
        self._catalog: list[dict] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        title = QLabel("Monstros")
        title.setObjectName("pageTitle")
        root.addWidget(title)
        self.hint = QLabel("Abra uma campanha para gerar monstros do sistema ativo.")
        self.hint.setObjectName("pageSubtitle")
        root.addWidget(self.hint)

        splitter = QSplitter()
        left = QWidget()
        left.setObjectName("sidePanel")
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(12, 12, 12, 12)
        left_l.setSpacing(10)
        section = QLabel("MONSTROS DA CAMPANHA")
        section.setObjectName("sectionTitle")
        left_l.addWidget(section)
        self.list = QListWidget()
        self.list_empty = make_empty_hint(EMPTY_NO_CAMPAIGN)
        left_l.addWidget(self.list, 1)
        left_l.addWidget(self.list_empty, 1)
        self.list.hide()
        self.btn_delete = QPushButton("Excluir selecionado")
        self.btn_delete.clicked.connect(self._delete)
        left_l.addWidget(self.btn_delete)
        splitter.addWidget(left)

        self.catalog_panel = QWidget()
        self.catalog_panel.setObjectName("sidePanel")
        cat_l = QVBoxLayout(self.catalog_panel)
        cat_l.setContentsMargins(12, 12, 12, 12)
        cat_title = QLabel("CATÁLOGO")
        cat_title.setObjectName("sectionTitle")
        cat_l.addWidget(cat_title)
        self.catalog_count = QLabel("")
        cat_l.addWidget(self.catalog_count)

        filters = QFormLayout()
        filters.setHorizontalSpacing(12)
        filters.setVerticalSpacing(10)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar nome, origem, poder…")
        self.search.textChanged.connect(self._refresh_catalog)
        self.origin = QComboBox()
        self.origin.currentIndexChanged.connect(self._refresh_catalog)
        self.scale = QComboBox()
        self.scale.currentIndexChanged.connect(self._refresh_catalog)
        filters.addRow("Busca", self.search)
        self.origin_label = QLabel("Origem")
        self.scale_label = QLabel("Escala")
        filters.addRow(self.origin_label, self.origin)
        filters.addRow(self.scale_label, self.scale)
        cat_l.addLayout(filters)

        self.catalog_list = QListWidget()
        self.catalog_list.currentRowChanged.connect(self._preview_catalog_row)
        self.catalog_list.itemDoubleClicked.connect(self._use_selected)
        self.catalog_empty = make_empty_hint("Nenhuma ficha neste filtro")
        cat_l.addWidget(self.catalog_list, 1)
        cat_l.addWidget(self.catalog_empty, 1)
        self.catalog_empty.hide()
        splitter.addWidget(self.catalog_panel)

        editor = QWidget()
        form_host = QVBoxLayout(editor)
        form_host.setContentsMargins(12, 0, 0, 0)
        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        self.system_label = QLabel("—")
        self.power = QComboBox()
        self.power.currentIndexChanged.connect(self._refresh_catalog)
        self.level = QSpinBox()
        self.level.setRange(0, 20)
        self.level.setValue(0)
        self.level.setSpecialValueText("Usar poder")
        form.addRow("Sistema", self.system_label)
        form.addRow("Poder", self.power)
        form.addRow("Nível / desafio", self.level)
        form_host.addLayout(form)

        extra = QFormLayout()
        extra.setHorizontalSpacing(12)
        extra.setVerticalSpacing(10)
        self.name = QLineEdit()
        self.challenge = QLineEdit()
        extra.addRow("Nome", self.name)
        extra.addRow("Desafio", self.challenge)
        form_host.addLayout(extra)

        form_host.addWidget(QLabel("Notas"))
        self.notes = QPlainTextEdit()
        self.notes.setMaximumHeight(80)
        form_host.addWidget(self.notes)

        form_host.addWidget(QLabel("Ficha"))
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        form_host.addWidget(self.preview, 1)

        buttons = QGridLayout()
        buttons.setHorizontalSpacing(8)
        buttons.setVerticalSpacing(8)
        gen = QPushButton("Gerar aleatório")
        use = QPushButton("Usar ficha do catálogo")
        save = QPushButton("Salvar na campanha")
        set_role(gen, "primary")
        gen.clicked.connect(self._generate)
        use.clicked.connect(self._use_selected)
        save.clicked.connect(self._save)
        self.btn_generate = gen
        self.btn_use = use
        self.btn_save = save
        buttons.addWidget(gen, 0, 0)
        buttons.addWidget(use, 0, 1)
        buttons.addWidget(save, 1, 0, 1, 2)
        form_host.addLayout(buttons)
        splitter.addWidget(editor)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 2)
        root.addWidget(splitter, 1)
        self._fill_power_options(catalog=False)
        self.catalog_panel.setVisible(False)
        self.btn_use.setVisible(False)
        self._set_enabled(False)

    def set_campaign(self, campaign: Campaign | None) -> None:
        self.campaign = campaign
        if campaign is None:
            self.hint.setText("Abra uma campanha para gerar monstros do sistema ativo.")
            self.system_label.setText("—")
            self._catalog = []
            self._fill_power_options(catalog=False)
            self._set_enabled(False)
            self.list.clear()
            self.catalog_list.clear()
            self._monsters = []
            self._payload = None
            self.catalog_panel.setVisible(False)
            self.btn_use.setVisible(False)
            self.list_empty.setText(EMPTY_NO_CAMPAIGN)
            set_empty_state(self.list, self.list_empty, True)
            set_empty_state(self.catalog_list, self.catalog_empty, True)
            return
        plugin = self.registry.get(campaign.system_slug)
        self._catalog = list(plugin.monster_catalog())
        has_catalog = bool(self._catalog)
        uses_cr = any(item.get("cr") is not None for item in self._catalog)
        self.origin_label.setText("Tipo" if uses_cr else "Origem")
        self.scale_label.setText("Habitat" if uses_cr else "Escala")
        self.search.setPlaceholderText(
            "Buscar nome, tipo, habitat…" if uses_cr else "Buscar nome, origem, poder…"
        )
        self._fill_power_options(catalog=has_catalog)
        self._fill_catalog_filters()
        extra = f"  ·  {len(self._catalog)} fichas no catálogo" if has_catalog else ""
        self.hint.setText(f"{campaign.name}  ·  {campaign.system_name}{extra}")
        self.system_label.setText(campaign.system_name)
        self.catalog_panel.setVisible(has_catalog)
        self.btn_use.setVisible(has_catalog)
        self.level.setVisible(not has_catalog)
        self._set_enabled(True)
        self.reload()
        self._refresh_catalog()

    def reload(self) -> None:
        if self.campaign is None:
            return
        self._monsters = queries.list_characters(
            self.db.conn, self.campaign.id, kind="monster"
        )
        self.list.clear()
        for monster in self._monsters:
            self.list.addItem(QListWidgetItem(monster.name))
        self.list_empty.setText("Nenhum monstro na campanha")
        set_empty_state(self.list, self.list_empty, not self._monsters)

    def _fill_power_options(self, *, catalog: bool) -> None:
        self.power.blockSignals(True)
        self.power.clear()
        if catalog:
            self.power.addItem("Todos", "todos")
            for key, label in POWER_LABELS.items():
                self.power.addItem(label, key)
        else:
            self.power.addItem("Fraco", "fraco")
            self.power.addItem("Médio", "medio")
            self.power.addItem("Forte", "forte")
            self.power.setCurrentIndex(1)
        self.power.blockSignals(False)

    def _fill_catalog_filters(self) -> None:
        self.origin.blockSignals(True)
        self.scale.blockSignals(True)
        self.origin.clear()
        self.scale.clear()
        self.origin.addItem("Todas", "todos")
        seen_categories: list[str] = []
        for item in self._catalog:
            slug = str(item.get("category") or "")
            label = str(item.get("category_label") or slug)
            if slug and slug not in seen_categories:
                seen_categories.append(slug)
                self.origin.addItem(label, slug)
        self.scale.addItem("Todas", "todas")
        seen_scales: list[str] = []
        for item in self._catalog:
            values = list(item.get("habitats") or [])
            if not values and item.get("escala"):
                values = [item.get("escala")]
            for value in values:
                if value and value not in seen_scales:
                    seen_scales.append(str(value))
                    self.scale.addItem(str(value), value)
        self.origin.blockSignals(False)
        self.scale.blockSignals(False)

    def _filtered_catalog(self) -> list[dict]:
        if not self._catalog:
            return []
        power = self.power.currentData()
        category = self.origin.currentData()
        escala = self.scale.currentData()
        needle = self.search.text().strip().lower()
        out: list[dict] = []
        for entry in self._catalog:
            if power and power not in {"", "todos"} and entry.get("power") != power:
                continue
            if category and category not in {"", "todos"} and entry.get("category") != category:
                continue
            habitats = entry.get("habitats") or [entry.get("escala")]
            if escala and escala not in {"", "todas"} and escala not in habitats:
                continue
            if needle:
                blob = " ".join(
                    [
                        str(entry.get("name") or ""),
                        str(entry.get("origem") or ""),
                        str(entry.get("category_label") or ""),
                        str(entry.get("escala") or ""),
                        str(entry.get("cr") or ""),
                        " ".join(str(item) for item in habitats if item),
                        " ".join(entry.get("pericias") or []),
                        " ".join(entry.get("poderes") or []),
                    ]
                ).lower()
                if needle not in blob:
                    continue
            out.append(entry)
        return out

    def _refresh_catalog(self) -> None:
        if not self.catalog_panel.isVisible():
            return
        rows = self._filtered_catalog()
        current_slug = None
        current = self.catalog_list.currentItem()
        if current is not None:
            current_slug = current.data(Qt.ItemDataRole.UserRole)
        self.catalog_list.blockSignals(True)
        self.catalog_list.clear()
        restore = 0
        for index, entry in enumerate(rows):
            points = entry.get("points")
            if entry.get("cr") is not None:
                pts = f"ND {entry['cr']}"
            else:
                pts = f"{points} pt" if points is not None else "Lendário"
            label = (
                f"{entry['name']}  ·  {pts}  ·  {entry.get('escala')}  ·  "
                f"{entry.get('category_label')}"
            )
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, entry.get("slug"))
            self.catalog_list.addItem(item)
            if entry.get("slug") == current_slug:
                restore = index
        self.catalog_list.blockSignals(False)
        self.catalog_count.setText(f"{len(rows)} de {len(self._catalog)} fichas")
        set_empty_state(self.catalog_list, self.catalog_empty, not rows)
        if rows:
            self.catalog_list.setCurrentRow(restore)

    def _set_enabled(self, enabled: bool) -> None:
        for widget in (
            self.list,
            self.btn_delete,
            self.power,
            self.level,
            self.name,
            self.challenge,
            self.notes,
            self.preview,
            self.search,
            self.origin,
            self.scale,
            self.catalog_list,
            self.btn_generate,
            self.btn_use,
            self.btn_save,
        ):
            widget.setEnabled(enabled)

    def _catalog_kwargs(self) -> dict:
        kwargs: dict = {}
        if not self._catalog:
            return kwargs
        power = self.power.currentData()
        if power:
            kwargs["power"] = power
        category = self.origin.currentData()
        if category and category not in {"", "todos"}:
            kwargs["category"] = category
        escala = self.scale.currentData()
        if escala and escala not in {"", "todas"}:
            kwargs["escala"] = escala
        query = self.search.text().strip()
        if query:
            kwargs["query"] = query
        return kwargs

    def _apply_payload(self, payload: dict) -> None:
        self._payload = payload
        self.name.setText(payload["name"])
        self.challenge.setText(str(payload.get("challenge", "")))
        self.notes.setPlainText(str(payload.get("notes") or ""))
        plugin = (
            self.registry.get(self.campaign.system_slug) if self.campaign else None
        )
        preview = (
            plugin.format_monster_preview(payload)
            if plugin is not None
            else str(payload.get("notes") or "")
        )
        self.preview.setPlainText(preview)

    def _generate(self) -> None:
        if self.campaign is None:
            return
        plugin = self.registry.get(self.campaign.system_slug)
        level = None if self._catalog else (self.level.value() or None)
        extra = self._catalog_kwargs()
        power = extra.pop("power", None) or self.power.currentData() or "medio"
        payload = generate_monster(plugin, power=power, level=level, **extra)
        self._apply_payload(payload)

    def _use_selected(self) -> None:
        if self.campaign is None or not self._catalog:
            return
        item = self.catalog_list.currentItem()
        if item is None:
            QMessageBox.warning(self, "Monstros", "Selecione uma ficha no catálogo.")
            return
        slug = item.data(Qt.ItemDataRole.UserRole)
        plugin = self.registry.get(self.campaign.system_slug)
        payload = generate_monster(plugin, name=slug)
        self._apply_payload(payload)

    def _preview_catalog_row(self, row: int) -> None:
        if row < 0 or self.campaign is None or not self._catalog:
            return
        item = self.catalog_list.item(row)
        if item is None:
            return
        slug = item.data(Qt.ItemDataRole.UserRole)
        plugin = self.registry.get(self.campaign.system_slug)
        payload = generate_monster(plugin, name=slug)
        self._apply_payload(payload)

    def _save(self) -> None:
        if self.campaign is None:
            QMessageBox.warning(self, "Monstros", "Abra uma campanha antes de salvar.")
            return
        if self._payload is None:
            QMessageBox.warning(self, "Monstros", "Gere ou escolha um monstro antes de salvar.")
            return
        character = Character(
            id=None,
            uuid=str(uuid.uuid4()),
            campaign_id=self.campaign.id,
            system_id=self.campaign.system_id,
            kind="monster",
            name=self.name.text().strip() or self._payload["name"],
            notes=self.notes.toPlainText().strip(),
            story_hook=f"Desafio {self.challenge.text().strip()}".strip(),
            attributes=self._payload["attributes"],
        )
        queries.create_character(self.db.conn, character)
        self.reload()
        QMessageBox.information(self, "Monstros", "Monstro salvo na campanha.")

    def _delete(self) -> None:
        row = self.list.currentRow()
        if not (0 <= row < len(self._monsters)):
            return
        monster = self._monsters[row]
        if monster.id is None:
            return
        if (
            QMessageBox.question(self, "Excluir", f"Excluir «{monster.name}»?")
            != QMessageBox.StandardButton.Yes
        ):
            return
        queries.delete_character(self.db.conn, monster.id)
        self.reload()

