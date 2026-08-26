from __future__ import annotations

import json
import re
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
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

from gestor_rpg.core.models import Campaign
from gestor_rpg.core.registry import registry
from gestor_rpg.db import queries
from gestor_rpg.db.connection import Database
from gestor_rpg.ui.styles import make_empty_hint, set_empty_state, set_role


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", name).strip(" .")
    return (cleaned or "campanha")[:80]


class CampaignsPage(QWidget):
    campaign_selected = Signal(object)

    def __init__(self, db: Database, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self._campaigns: list[Campaign] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        title = QLabel("Campanhas")
        title.setObjectName("pageTitle")
        root.addWidget(title)
        hint = QLabel("Crie ou abra uma mesa.")
        hint.setObjectName("pageSubtitle")
        root.addWidget(hint)

        splitter = QSplitter()
        left = QWidget()
        left.setObjectName("sidePanel")
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(12, 12, 12, 12)
        left_l.setSpacing(10)
        section = QLabel("MESAS")
        section.setObjectName("sectionTitle")
        left_l.addWidget(section)
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._on_row)
        self.list_empty = make_empty_hint("Nenhuma mesa ainda")
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
        extra = QVBoxLayout()
        extra.setSpacing(8)
        self.btn_export = QPushButton("Exportar JSON…")
        self.btn_export_pdf = QPushButton("Exportar PDF…")
        self.btn_import = QPushButton("Importar JSON…")
        self.btn_export.clicked.connect(self._export)
        self.btn_export_pdf.clicked.connect(self._export_pdf)
        self.btn_import.clicked.connect(self._import)
        extra.addWidget(self.btn_export)
        extra.addWidget(self.btn_export_pdf)
        extra.addWidget(self.btn_import)
        left_l.addLayout(btns)
        left_l.addLayout(extra)
        splitter.addWidget(left)

        form_box = QWidget()
        form_l = QVBoxLayout(form_box)
        form_l.setContentsMargins(12, 0, 0, 0)
        detail = QLabel("DETALHES")
        detail.setObjectName("sectionTitle")
        form_l.addWidget(detail)
        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        self.name = QLineEdit()
        self.system = QComboBox()
        for system_id, slug, name in queries.list_systems(self.db.conn):
            self.system.addItem(name, (system_id, slug))
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Anotações da mesa…")
        self.btn_open = QPushButton("Abrir campanha")
        set_role(self.btn_open, "primary")
        self.btn_open.clicked.connect(self._open)
        form.addRow("Nome", self.name)
        form.addRow("Sistema", self.system)
        form.addRow("Notas", self.notes)
        form_l.addLayout(form, 1)
        form_l.addWidget(self.btn_open)
        splitter.addWidget(form_box)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        root.addWidget(splitter, 1)

        self.reload()

    def reload(self, select_id: int | None = None) -> None:
        self._campaigns = queries.list_campaigns(self.db.conn)
        self.list.blockSignals(True)
        self.list.clear()
        selected_row = 0
        for i, campaign in enumerate(self._campaigns):
            item = QListWidgetItem(f"{campaign.name}  ·  {campaign.system_name}")
            item.setData(256, campaign.id)
            self.list.addItem(item)
            if select_id is not None and campaign.id == select_id:
                selected_row = i
        self.list.blockSignals(False)
        set_empty_state(self.list, self.list_empty, not self._campaigns)
        if self._campaigns:
            self.list.setCurrentRow(selected_row)
        else:
            self._clear_form()

    def current(self) -> Campaign | None:
        row = self.list.currentRow()
        if 0 <= row < len(self._campaigns):
            return self._campaigns[row]
        return None

    def _on_row(self, row: int) -> None:
        if not (0 <= row < len(self._campaigns)):
            self._clear_form()
            return
        campaign = self._campaigns[row]
        self.name.setText(campaign.name)
        self.notes.setPlainText(campaign.notes)
        for i in range(self.system.count()):
            system_id, _slug = self.system.itemData(i)
            if system_id == campaign.system_id:
                self.system.setCurrentIndex(i)
                break
        self.system.setEnabled(False)

    def _clear_form(self) -> None:
        self.name.clear()
        self.notes.clear()
        self.system.setCurrentIndex(0)
        self.system.setEnabled(True)

    def _new(self) -> None:
        self.list.clearSelection()
        self.list.setCurrentRow(-1)
        self._clear_form()
        self.name.setFocus()

    def _save(self) -> None:
        name = self.name.text().strip()
        if not name:
            QMessageBox.warning(self, "Campanha", "Informe um nome.")
            return
        current = self.current()
        if current is None:
            system_id, _slug = self.system.currentData()
            created = queries.create_campaign(self.db.conn, name, system_id, self.notes.toPlainText())
            self.reload(created.id)
        else:
            current.name = name
            current.notes = self.notes.toPlainText()
            queries.update_campaign(self.db.conn, current)
            self.reload(current.id)

    def _delete(self) -> None:
        current = self.current()
        if current is None:
            return
        if QMessageBox.question(self, "Excluir", f"Excluir a campanha «{current.name}»?") != QMessageBox.StandardButton.Yes:
            return
        queries.delete_campaign(self.db.conn, current.id)
        self.reload()
        self.campaign_selected.emit(None)

    def _open(self) -> None:
        current = self.current()
        if current is None:
            QMessageBox.information(self, "Campanha", "Selecione ou salve uma campanha primeiro.")
            return
        self.campaign_selected.emit(current)

    def _export(self) -> None:
        current = self.current()
        if current is None:
            QMessageBox.information(self, "Campanha", "Selecione uma campanha para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar campanha",
            f"{_safe_filename(current.name)}.json",
            "Campanha JSON (*.json)",
        )
        if not path:
            return
        payload = queries.export_campaign(self.db.conn, current.id)
        target = Path(path)
        if target.suffix.lower() != ".json":
            target = target.with_suffix(".json")
        Path(target).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        QMessageBox.information(self, "Campanha", "Campanha exportada em JSON.")

    def _export_pdf(self) -> None:
        from gestor_rpg.modules.sheet_export.html import format_campaign_html
        from gestor_rpg.modules.sheet_export.pdf import write_sheet_pdf

        current = self.current()
        if current is None:
            QMessageBox.information(self, "Campanha", "Selecione uma campanha para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar campanha em PDF",
            f"{_safe_filename(current.name)}.pdf",
            "PDF (*.pdf)",
        )
        if not path:
            return
        payload = queries.export_campaign(self.db.conn, current.id)
        plugin = registry().get(current.system_slug)
        html = format_campaign_html(payload, plugin)
        target = Path(path)
        if target.suffix.lower() != ".pdf":
            target = target.with_suffix(".pdf")
        try:
            write_sheet_pdf(html, target, title=current.name)
        except OSError as exc:
            QMessageBox.warning(self, "Campanha", f"Não foi possível exportar: {exc}")
            return
        QMessageBox.information(self, "Campanha", "Campanha exportada em PDF.")

    def _import(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar campanha",
            "",
            "Campanha JSON (*.json)",
        )
        if not path:
            return
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            created = queries.import_campaign(self.db.conn, payload)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            QMessageBox.warning(self, "Campanha", f"Não foi possível importar: {exc}")
            return
        self.reload(created.id)
        self.campaign_selected.emit(created)
