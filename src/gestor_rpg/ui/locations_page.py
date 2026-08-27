from __future__ import annotations

import uuid

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gestor_rpg.core.models import LOCATION_KINDS, Campaign, Location, location_kind_label
from gestor_rpg.db import queries
from gestor_rpg.db.connection import Database
from gestor_rpg.ui.styles import EMPTY_NO_CAMPAIGN, make_empty_hint, set_empty_state, set_role


class LocationsPage(QWidget):
    def __init__(self, db: Database, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self.campaign: Campaign | None = None
        self._items: list[Location] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        title = QLabel("Locais")
        title.setObjectName("pageTitle")
        root.addWidget(title)
        self.hint = QLabel("Abra uma campanha para cadastrar cidades e outros lugares.")
        self.hint.setObjectName("pageSubtitle")
        root.addWidget(self.hint)

        splitter = QSplitter()
        left = QWidget()
        left.setObjectName("sidePanel")
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(12, 12, 12, 12)
        left_l.setSpacing(10)
        section = QLabel("MUNDO")
        section.setObjectName("sectionTitle")
        left_l.addWidget(section)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar…")
        self.search.textChanged.connect(self._rebuild_list)
        left_l.addWidget(self.search)
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._on_row)
        self.list_empty = make_empty_hint(EMPTY_NO_CAMPAIGN)
        left_l.addWidget(self.list, 1)
        left_l.addWidget(self.list_empty, 1)
        self.list.hide()
        btns = QHBoxLayout()
        btns.setSpacing(8)
        self.btn_new = QPushButton("Novo")
        self.btn_save = QPushButton("Salvar")
        self.btn_delete = QPushButton("Excluir")
        set_role(self.btn_save, "primary")
        self.btn_new.clicked.connect(self._new)
        self.btn_save.clicked.connect(self._save)
        self.btn_delete.clicked.connect(self._delete)
        btns.addWidget(self.btn_new)
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_delete)
        left_l.addLayout(btns)
        splitter.addWidget(left)

        form_box = QWidget()
        form_l = QVBoxLayout(form_box)
        form_l.setContentsMargins(12, 0, 0, 0)
        detail = QLabel("LOCAL")
        detail.setObjectName("sectionTitle")
        form_l.addWidget(detail)
        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        self.name = QLineEdit()
        self.kind = QComboBox()
        for key, label in LOCATION_KINDS:
            self.kind.addItem(label, key)
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("O que o grupo vê e ouve neste lugar…")
        self.secrets = QTextEdit()
        self.secrets.setPlaceholderText("O que só o mestre sabe…")
        form.addRow("Nome", self.name)
        form.addRow("Tipo", self.kind)
        form.addRow("Descrição", self.notes)
        form.addRow("Segredos", self.secrets)
        form_l.addLayout(form, 1)
        splitter.addWidget(form_box)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        root.addWidget(splitter, 1)
        self._set_enabled(False)

    def set_campaign(self, campaign: Campaign | None) -> None:
        self.campaign = campaign
        if campaign is None:
            self.hint.setText("Abra uma campanha para cadastrar cidades e outros lugares.")
            self._set_enabled(False)
            self._items = []
            self.search.clear()
            self._clear_form()
            self.list_empty.setText(EMPTY_NO_CAMPAIGN)
            set_empty_state(self.list, self.list_empty, True)
            return
        self.hint.setText(f"{campaign.name}  ·  {campaign.system_name}")
        self._set_enabled(True)
        self.reload()

    def reload(self, select_id: int | None = None) -> None:
        if self.campaign is None:
            return
        self._items = queries.list_locations(self.db.conn, self.campaign.id)
        self._rebuild_list(select_id=select_id)

    def _visible(self) -> list[Location]:
        needle = self.search.text().strip().lower()
        if not needle:
            return list(self._items)
        return [
            item
            for item in self._items
            if needle in item.name.lower()
            or needle in item.kind.lower()
            or needle in location_kind_label(item.kind).lower()
            or needle in item.notes.lower()
        ]

    def _rebuild_list(self, _text: str = "", *, select_id: int | None = None) -> None:
        visible = self._visible()
        current_id = select_id
        if current_id is None:
            current = self.current()
            current_id = current.id if current else None
        self.list.blockSignals(True)
        self.list.clear()
        selected = 0
        for i, item in enumerate(visible):
            kind = location_kind_label(item.kind)
            self.list.addItem(QListWidgetItem(f"{item.name}\n{kind}"))
            if current_id is not None and item.id == current_id:
                selected = i
        self.list.blockSignals(False)
        empty = "Nenhum local ainda" if not self._items else "Nada corresponde à busca"
        self.list_empty.setText(empty)
        set_empty_state(self.list, self.list_empty, not visible)
        if visible:
            self.list.setCurrentRow(selected)
        else:
            self._clear_form()

    def _set_enabled(self, enabled: bool) -> None:
        for widget in (
            self.list,
            self.search,
            self.btn_new,
            self.btn_save,
            self.btn_delete,
            self.name,
            self.kind,
            self.notes,
            self.secrets,
        ):
            widget.setEnabled(enabled)

    def current(self) -> Location | None:
        visible = self._visible()
        row = self.list.currentRow()
        if 0 <= row < len(visible):
            return visible[row]
        return None

    def _on_row(self, row: int) -> None:
        visible = self._visible()
        if not (0 <= row < len(visible)):
            self._clear_form()
            return
        item = visible[row]
        self.name.setText(item.name)
        index = self.kind.findData(item.kind)
        self.kind.setCurrentIndex(index if index >= 0 else 0)
        self.notes.setPlainText(item.notes)
        self.secrets.setPlainText(item.secrets)

    def _clear_form(self) -> None:
        self.name.clear()
        self.kind.setCurrentIndex(0)
        self.notes.clear()
        self.secrets.clear()

    def _new(self) -> None:
        if self.campaign is None:
            return
        self.list.blockSignals(True)
        self.list.clearSelection()
        self.list.setCurrentRow(-1)
        self.list.blockSignals(False)
        self._clear_form()
        self.name.setFocus()

    def _save(self) -> None:
        if self.campaign is None:
            return
        name = self.name.text().strip()
        if not name:
            QMessageBox.warning(self, "Locais", "Informe o nome do lugar.")
            return
        current = self.current()
        kind = str(self.kind.currentData() or "cidade")
        notes = self.notes.toPlainText()
        secrets = self.secrets.toPlainText()
        if current is None:
            created = queries.create_location(
                self.db.conn,
                Location(
                    id=None,
                    uuid=str(uuid.uuid4()),
                    campaign_id=self.campaign.id,
                    name=name,
                    kind=kind,
                    notes=notes,
                    secrets=secrets,
                ),
            )
            self.reload(created.id)
        else:
            current.name = name
            current.kind = kind
            current.notes = notes
            current.secrets = secrets
            queries.update_location(self.db.conn, current)
            self.reload(current.id)

    def _delete(self) -> None:
        current = self.current()
        if current is None or current.id is None:
            return
        if (
            QMessageBox.question(self, "Excluir", f"Excluir «{current.name}»?")
            != QMessageBox.StandardButton.Yes
        ):
            return
        queries.delete_location(self.db.conn, current.id)
        self.reload()
