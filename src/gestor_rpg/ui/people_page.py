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

from gestor_rpg.core.models import (
    PEOPLE_ATTITUDES,
    Campaign,
    Person,
    person_attitude_label,
)
from gestor_rpg.db import queries
from gestor_rpg.db.connection import Database
from gestor_rpg.ui.styles import EMPTY_NO_CAMPAIGN, make_empty_hint, set_empty_state, set_role


class PeoplePage(QWidget):
    def __init__(self, db: Database, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self.campaign: Campaign | None = None
        self._items: list[Person] = []
        self._location_names: dict[int, str] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        title = QLabel("Pessoas")
        title.setObjectName("pageTitle")
        root.addWidget(title)
        self.hint = QLabel("Abra uma campanha para cadastrar NPCs do mundo.")
        self.hint.setObjectName("pageSubtitle")
        root.addWidget(self.hint)

        splitter = QSplitter()
        left = QWidget()
        left.setObjectName("sidePanel")
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(12, 12, 12, 12)
        left_l.setSpacing(10)
        section = QLabel("ELENCO")
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
        self.btn_new = QPushButton("Nova")
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
        detail = QLabel("PESSOA")
        detail.setObjectName("sectionTitle")
        form_l.addWidget(detail)
        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        self.name = QLineEdit()
        self.role = QLineEdit()
        self.role.setPlaceholderText("Estalajadeira, guarda, vilão…")
        self.location = QComboBox()
        self.attitude = QComboBox()
        for key, label in PEOPLE_ATTITUDES:
            self.attitude.addItem(label, key)
        self.character = QComboBox()
        self.appearance = QTextEdit()
        self.appearance.setPlaceholderText("Como reconhecê-la na mesa…")
        self.appearance.setMaximumHeight(90)
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("O que o grupo já sabe…")
        self.secrets = QTextEdit()
        self.secrets.setPlaceholderText("Segredos, alianças, o que esconde…")
        form.addRow("Nome", self.name)
        form.addRow("Papel", self.role)
        form.addRow("Local", self.location)
        form.addRow("Atitude", self.attitude)
        form.addRow("Ficha", self.character)
        form.addRow("Aparência", self.appearance)
        form.addRow("Notas", self.notes)
        form.addRow("Segredos", self.secrets)
        form_l.addLayout(form, 1)
        splitter.addWidget(form_box)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        root.addWidget(splitter, 1)
        self.character.currentIndexChanged.connect(self._maybe_fill_name)
        self._set_enabled(False)

    def set_campaign(self, campaign: Campaign | None) -> None:
        self.campaign = campaign
        if campaign is None:
            self.hint.setText("Abra uma campanha para cadastrar NPCs do mundo.")
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
        locations = queries.list_locations(self.db.conn, self.campaign.id)
        self._location_names = {item.id: item.name for item in locations if item.id is not None}
        self._fill_locations()
        self._fill_characters()
        self._items = queries.list_people(self.db.conn, self.campaign.id)
        self._rebuild_list(select_id=select_id)

    def _fill_locations(self, selected_id: int | None = None) -> None:
        current = selected_id
        self.location.blockSignals(True)
        self.location.clear()
        self.location.addItem("Nenhum", None)
        if self.campaign is not None:
            for item in queries.list_locations(self.db.conn, self.campaign.id):
                self.location.addItem(item.name, item.id)
        if current is not None:
            index = self.location.findData(current)
            self.location.setCurrentIndex(index if index >= 0 else 0)
        else:
            self.location.setCurrentIndex(0)
        self.location.blockSignals(False)

    def _fill_characters(self, selected_id: int | None = None) -> None:
        current = selected_id
        self.character.blockSignals(True)
        self.character.clear()
        self.character.addItem("Sem ficha", None)
        if self.campaign is not None:
            for item in queries.list_characters(self.db.conn, self.campaign.id):
                self.character.addItem(f"[{item.kind.upper()}] {item.name}", item.id)
        if current is not None:
            index = self.character.findData(current)
            self.character.setCurrentIndex(index if index >= 0 else 0)
        else:
            self.character.setCurrentIndex(0)
        self.character.blockSignals(False)

    def _maybe_fill_name(self, _index: int) -> None:
        if self.name.text().strip():
            return
        character_id = self.character.currentData()
        if character_id is None or self.campaign is None:
            return
        character = queries.get_character(self.db.conn, int(character_id))
        if character is not None:
            self.name.setText(character.name)

    def _visible(self) -> list[Person]:
        needle = self.search.text().strip().lower()
        if not needle:
            return list(self._items)
        hits: list[Person] = []
        for item in self._items:
            place = self._location_names.get(item.location_id or -1, "")
            blob = " ".join(
                (
                    item.name,
                    item.role,
                    item.attitude,
                    person_attitude_label(item.attitude),
                    place,
                    item.notes,
                )
            ).lower()
            if needle in blob:
                hits.append(item)
        return hits

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
            role = item.role.strip() or "sem papel"
            place = self._location_names.get(item.location_id or -1, "sem local")
            attitude = person_attitude_label(item.attitude)
            self.list.addItem(QListWidgetItem(f"{item.name}, {role}\n{place} · {attitude}"))
            if current_id is not None and item.id == current_id:
                selected = i
        self.list.blockSignals(False)
        empty = "Nenhuma pessoa ainda" if not self._items else "Nada corresponde à busca"
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
            self.role,
            self.location,
            self.attitude,
            self.character,
            self.appearance,
            self.notes,
            self.secrets,
        ):
            widget.setEnabled(enabled)

    def current(self) -> Person | None:
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
        self.role.setText(item.role)
        self._fill_locations(item.location_id)
        index = self.attitude.findData(item.attitude)
        self.attitude.setCurrentIndex(index if index >= 0 else 1)
        self._fill_characters(item.character_id)
        self.appearance.setPlainText(item.appearance)
        self.notes.setPlainText(item.notes)
        self.secrets.setPlainText(item.secrets)

    def _clear_form(self) -> None:
        self.name.clear()
        self.role.clear()
        self._fill_locations()
        self.attitude.setCurrentIndex(1)
        self._fill_characters()
        self.appearance.clear()
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
            QMessageBox.warning(self, "Pessoas", "Informe o nome.")
            return
        current = self.current()
        payload = Person(
            id=None if current is None else current.id,
            uuid=str(uuid.uuid4()) if current is None else current.uuid,
            campaign_id=self.campaign.id,
            location_id=self.location.currentData(),
            character_id=self.character.currentData(),
            name=name,
            role=self.role.text().strip(),
            appearance=self.appearance.toPlainText(),
            notes=self.notes.toPlainText(),
            secrets=self.secrets.toPlainText(),
            attitude=str(self.attitude.currentData() or "neutro"),
        )
        if current is None:
            created = queries.create_person(self.db.conn, payload)
            self.reload(created.id)
        else:
            queries.update_person(self.db.conn, payload)
            self.reload(payload.id)

    def _delete(self) -> None:
        current = self.current()
        if current is None or current.id is None:
            return
        if (
            QMessageBox.question(self, "Excluir", f"Excluir «{current.name}»?")
            != QMessageBox.StandardButton.Yes
        ):
            return
        queries.delete_person(self.db.conn, current.id)
        self.reload()
