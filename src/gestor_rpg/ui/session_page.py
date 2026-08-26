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

from gestor_rpg.core.models import Campaign, SessionEntry
from gestor_rpg.db import queries
from gestor_rpg.db.connection import Database
from gestor_rpg.ui.styles import EMPTY_NO_CAMPAIGN, make_empty_hint, set_empty_state, set_role


def _date_label(iso: str) -> str:
    return iso[:10] if iso else ""


class SessionPage(QWidget):
    def __init__(self, db: Database, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self.campaign: Campaign | None = None
        self._entries: list[SessionEntry] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        title = QLabel("Sessão")
        title.setObjectName("pageTitle")
        root.addWidget(title)
        self.hint = QLabel("Abra uma campanha para registrar a sessão.")
        self.hint.setObjectName("pageSubtitle")
        root.addWidget(self.hint)

        splitter = QSplitter()
        left = QWidget()
        left.setObjectName("sidePanel")
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(12, 12, 12, 12)
        left_l.setSpacing(10)
        section = QLabel("LOG DA MESA")
        section.setObjectName("sectionTitle")
        left_l.addWidget(section)
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
        detail = QLabel("ENTRADA")
        detail.setObjectName("sectionTitle")
        form_l.addWidget(detail)
        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        self.title = QLineEdit()
        self.encounter = QComboBox()
        self.xp = QLineEdit()
        self.xp.setPlaceholderText("300 cada, 1 nível…")
        self.treasure = QLineEdit()
        self.treasure.setPlaceholderText("2 PO, poção de cura…")
        self.body = QTextEdit()
        self.body.setPlaceholderText("O que aconteceu na mesa…")
        form.addRow("Título", self.title)
        form.addRow("Encontro", self.encounter)
        form.addRow("XP", self.xp)
        form.addRow("Tesouro", self.treasure)
        form.addRow("O que aconteceu", self.body)
        form_l.addLayout(form, 1)
        splitter.addWidget(form_box)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        root.addWidget(splitter, 1)
        self._set_enabled(False)

    def set_campaign(self, campaign: Campaign | None) -> None:
        self.campaign = campaign
        if campaign is None:
            self.hint.setText("Abra uma campanha para registrar a sessão.")
            self._set_enabled(False)
            self.list.clear()
            self._entries = []
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
        self._fill_encounters()
        self._entries = queries.list_session_entries(self.db.conn, self.campaign.id)
        self.list.blockSignals(True)
        self.list.clear()
        selected = 0
        for i, entry in enumerate(self._entries):
            stamp = _date_label(entry.updated_at)
            label = f"{entry.title}" if not stamp else f"{entry.title}\n{stamp}"
            self.list.addItem(QListWidgetItem(label))
            if select_id is not None and entry.id == select_id:
                selected = i
        self.list.blockSignals(False)
        self.list_empty.setText("Nenhum registro ainda")
        set_empty_state(self.list, self.list_empty, not self._entries)
        if self._entries:
            self.list.setCurrentRow(selected)
        else:
            self._clear_form()

    def _fill_encounters(self, selected_id: int | None = None) -> None:
        current = selected_id
        self.encounter.blockSignals(True)
        self.encounter.clear()
        self.encounter.addItem("Nenhum", None)
        if self.campaign is not None:
            for item in queries.list_encounters(self.db.conn, self.campaign.id):
                self.encounter.addItem(item.name, item.id)
        if current is not None:
            index = self.encounter.findData(current)
            self.encounter.setCurrentIndex(index if index >= 0 else 0)
        else:
            self.encounter.setCurrentIndex(0)
        self.encounter.blockSignals(False)

    def _set_enabled(self, enabled: bool) -> None:
        for widget in (
            self.list,
            self.btn_new,
            self.btn_save,
            self.btn_delete,
            self.title,
            self.encounter,
            self.xp,
            self.treasure,
            self.body,
        ):
            widget.setEnabled(enabled)

    def current(self) -> SessionEntry | None:
        row = self.list.currentRow()
        if 0 <= row < len(self._entries):
            return self._entries[row]
        return None

    def _on_row(self, row: int) -> None:
        if not (0 <= row < len(self._entries)):
            self._clear_form()
            return
        entry = self._entries[row]
        self.title.setText(entry.title)
        self.body.setPlainText(entry.body)
        self.xp.setText(entry.xp)
        self.treasure.setText(entry.treasure)
        self._fill_encounters(entry.encounter_id)

    def _clear_form(self) -> None:
        self.title.clear()
        self.body.clear()
        self.xp.clear()
        self.treasure.clear()
        self._fill_encounters()

    def _new(self) -> None:
        if self.campaign is None:
            return
        self.list.blockSignals(True)
        self.list.clearSelection()
        self.list.setCurrentRow(-1)
        self.list.blockSignals(False)
        self._clear_form()
        self.title.setFocus()

    def _save(self) -> None:
        if self.campaign is None:
            return
        title = self.title.text().strip()
        if not title:
            QMessageBox.warning(self, "Sessão", "Informe um título.")
            return
        current = self.current()
        encounter_id = self.encounter.currentData()
        if current is None:
            created = queries.create_session_entry(
                self.db.conn,
                SessionEntry(
                    id=None,
                    uuid=str(uuid.uuid4()),
                    campaign_id=self.campaign.id,
                    encounter_id=encounter_id,
                    title=title,
                    body=self.body.toPlainText(),
                    xp=self.xp.text().strip(),
                    treasure=self.treasure.text().strip(),
                ),
            )
            self.reload(created.id)
        else:
            current.title = title
            current.body = self.body.toPlainText()
            current.xp = self.xp.text().strip()
            current.treasure = self.treasure.text().strip()
            current.encounter_id = encounter_id
            queries.update_session_entry(self.db.conn, current)
            self.reload(current.id)

    def _delete(self) -> None:
        current = self.current()
        if current is None or current.id is None:
            return
        if (
            QMessageBox.question(self, "Excluir", f"Excluir «{current.title}»?")
            != QMessageBox.StandardButton.Yes
        ):
            return
        queries.delete_session_entry(self.db.conn, current.id)
        self.reload()
