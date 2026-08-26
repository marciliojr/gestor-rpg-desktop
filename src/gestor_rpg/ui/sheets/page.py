from __future__ import annotations

import re
import uuid
from pathlib import Path

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
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from gestor_rpg.core.models import Campaign, Character
from gestor_rpg.core.plugin import SheetWidget
from gestor_rpg.core.registry import PluginRegistry
from gestor_rpg.db import queries
from gestor_rpg.db.connection import Database
from gestor_rpg.modules.sheet_export import print_sheet, write_sheet_pdf
from gestor_rpg.ui.styles import (
    EMPTY_NO_CAMPAIGN,
    make_empty_hint,
    polish_placeholders,
    set_empty_state,
    set_role,
)


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", name).strip(" .")
    return (cleaned or "ficha")[:80]


class SheetsPage(QWidget):
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
        self._characters: list[Character] = []
        self._sheet: SheetWidget | None = None
        self._current: Character | None = None
        self._searching = False

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        title = QLabel("Fichas")
        title.setObjectName("pageTitle")
        root.addWidget(title)
        self.hint = QLabel("Abra uma campanha para gerenciar fichas.")
        self.hint.setObjectName("pageSubtitle")
        root.addWidget(self.hint)

        splitter = QSplitter()
        left = QWidget()
        left.setObjectName("sidePanel")
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(12, 12, 12, 12)
        left_l.setSpacing(10)
        section = QLabel("PERSONAGENS")
        section.setObjectName("sectionTitle")
        left_l.addWidget(section)
        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar nas fichas…")
        self.search.returnPressed.connect(lambda: self._run_search())
        self.btn_search = QPushButton("Buscar")
        self.btn_search.clicked.connect(lambda: self._run_search())
        self.btn_clear_search = QPushButton("Limpar")
        self.btn_clear_search.clicked.connect(self._clear_search)
        search_row.addWidget(self.search, 1)
        search_row.addWidget(self.btn_search)
        search_row.addWidget(self.btn_clear_search)
        left_l.addLayout(search_row)
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._on_row)
        self.list_empty = make_empty_hint(EMPTY_NO_CAMPAIGN)
        left_l.addWidget(self.list, 1)
        left_l.addWidget(self.list_empty, 1)
        self.list.hide()
        btns = QHBoxLayout()
        btns.setSpacing(8)
        self.btn_pc = QPushButton("Novo PC")
        self.btn_npc = QPushButton("Novo NPC")
        self.btn_delete = QPushButton("Excluir")
        self.btn_pc.clicked.connect(lambda: self._new("pc"))
        self.btn_npc.clicked.connect(lambda: self._new("npc"))
        self.btn_delete.clicked.connect(self._delete)
        btns.addWidget(self.btn_pc, 1)
        btns.addWidget(self.btn_npc, 1)
        left_l.addLayout(btns)
        left_l.addWidget(self.btn_delete)
        splitter.addWidget(left)

        editor = QWidget()
        self.editor_layout = QVBoxLayout(editor)
        self.editor_layout.setContentsMargins(12, 0, 0, 0)
        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        self.name = QLineEdit()
        self.kind = QComboBox()
        self.kind.addItem("Personagem (PC)", "pc")
        self.kind.addItem("NPC", "npc")
        self.kind.addItem("Monstro", "monster")
        self.motivation = QLineEdit()
        self.story_hook = QLineEdit()
        self.notes = QPlainTextEdit()
        self.notes.setMaximumHeight(80)
        form.addRow("Nome", self.name)
        form.addRow("Tipo", self.kind)
        form.addRow("Motivação", self.motivation)
        form.addRow("Gancho", self.story_hook)
        form.addRow("Notas", self.notes)
        self.editor_layout.addLayout(form)
        self.sheet_host = QVBoxLayout()
        self.editor_layout.addLayout(self.sheet_host, 1)
        save_row = QHBoxLayout()
        save_row.setSpacing(8)
        self.btn_save = QPushButton("Salvar ficha")
        self.btn_export_pdf = QPushButton("Exportar PDF…")
        self.btn_print = QPushButton("Imprimir…")
        set_role(self.btn_save, "primary")
        self.btn_save.clicked.connect(self._save)
        self.btn_export_pdf.clicked.connect(self._export_pdf)
        self.btn_print.clicked.connect(self._print)
        save_row.addWidget(self.btn_save)
        save_row.addWidget(self.btn_export_pdf)
        save_row.addWidget(self.btn_print)
        self.editor_layout.addLayout(save_row)
        splitter.addWidget(editor)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        root.addWidget(splitter, 1)
        self._set_enabled(False)

    def set_campaign(self, campaign: Campaign | None) -> None:
        self._save_current_silent()
        self.campaign = campaign
        if campaign is None:
            self.hint.setText("Abra uma campanha para gerenciar fichas.")
            self._set_enabled(False)
            self.list.clear()
            self.search.clear()
            self._characters = []
            self._detach_sheet()
            self._current = None
            self.list_empty.setText(EMPTY_NO_CAMPAIGN)
            set_empty_state(self.list, self.list_empty, True)
            return
        self.hint.setText(f"{campaign.name}  ·  {campaign.system_name}")
        self._set_enabled(True)
        self._ensure_sheet(campaign.system_slug)
        self.reload()

    def reload(self, select_id: int | None = None) -> None:
        if self.campaign is None:
            return
        if self.search.text().strip():
            self._run_search(select_id)
            return
        self._searching = False
        self._characters = queries.list_characters(self.db.conn, self.campaign.id)
        self._fill_list(select_id)

    def _fill_list(self, select_id: int | None = None, snippets: list[str] | None = None) -> None:
        self.list.blockSignals(True)
        self.list.clear()
        selected = 0
        for i, character in enumerate(self._characters):
            label = f"[{character.kind.upper()}] {character.name}"
            if snippets and i < len(snippets) and snippets[i]:
                label += f"\n{snippets[i]}"
            self.list.addItem(QListWidgetItem(label))
            if select_id is not None and character.id == select_id:
                selected = i
        self.list.blockSignals(False)
        if self._searching:
            self.list_empty.setText("Nenhuma ficha encontrada")
        else:
            self.list_empty.setText("Nenhuma ficha ainda")
        set_empty_state(self.list, self.list_empty, not self._characters)
        if self._characters:
            self.list.setCurrentRow(selected)
        else:
            self._current = None
            self._clear_form()
            if self._sheet and self.campaign:
                plugin = self.registry.get(self.campaign.system_slug)
                self._sheet.set_attributes(plugin.default_attributes())

    def _run_search(self, select_id: int | None = None) -> None:
        if self.campaign is None:
            return
        query = self.search.text().strip()
        if not query:
            self.reload(select_id)
            return
        self._searching = True
        hits = queries.search_characters(self.db.conn, query, self.campaign.id)
        self._characters = []
        snippets: list[str] = []
        for hit in hits:
            character = queries.get_character(self.db.conn, hit.id)
            if character is None:
                continue
            self._characters.append(character)
            snippets.append(hit.snippet)
        self._fill_list(select_id, snippets)

    def _clear_search(self) -> None:
        self.search.clear()
        self.reload(self._current.id if self._current else None)

    def add_character(self, character: Character) -> Character:
        created = queries.create_character(self.db.conn, character)
        self.reload(created.id)
        return created

    def _set_enabled(self, enabled: bool) -> None:
        for widget in (
            self.list,
            self.btn_pc,
            self.btn_npc,
            self.btn_delete,
            self.name,
            self.kind,
            self.motivation,
            self.story_hook,
            self.notes,
            self.btn_save,
            self.btn_export_pdf,
            self.btn_print,
            self.search,
            self.btn_search,
            self.btn_clear_search,
        ):
            widget.setEnabled(enabled)

    def _ensure_sheet(self, slug: str) -> None:
        self._detach_sheet()
        plugin = self.registry.get(slug)
        self._sheet = plugin.create_sheet_widget(self)
        self.sheet_host.addWidget(self._sheet)
        polish_placeholders(self._sheet)

    def _detach_sheet(self) -> None:
        if self._sheet is not None:
            self.sheet_host.removeWidget(self._sheet)
            self._sheet.deleteLater()
            self._sheet = None

    def _clear_form(self) -> None:
        self.name.clear()
        self.kind.setCurrentIndex(0)
        self.motivation.clear()
        self.story_hook.clear()
        self.notes.clear()

    def _on_row(self, row: int) -> None:
        self._save_current_silent()
        if not (0 <= row < len(self._characters)):
            self._current = None
            return
        character = queries.get_character(self.db.conn, self._characters[row].id or 0)
        if character is None:
            return
        self._current = character
        self.name.setText(character.name)
        kind_index = self.kind.findData(character.kind)
        self.kind.setCurrentIndex(kind_index if kind_index >= 0 else 0)
        self.motivation.setText(character.motivation)
        self.story_hook.setText(character.story_hook)
        self.notes.setPlainText(character.notes)
        if self._sheet:
            self._sheet.set_attributes(character.attributes)

    def _collect(self) -> Character | None:
        if self.campaign is None:
            return None
        attributes = self._sheet.get_attributes() if self._sheet else {}
        name = self.name.text().strip() or "Sem nome"
        current = self._current
        return Character(
            id=current.id if current else None,
            uuid=current.uuid if current else str(uuid.uuid4()),
            campaign_id=self.campaign.id,
            system_id=self.campaign.system_id,
            kind=self.kind.currentData(),
            name=name,
            notes=self.notes.toPlainText(),
            motivation=self.motivation.text().strip(),
            story_hook=self.story_hook.text().strip(),
            attributes=attributes,
        )

    def _sheet_payload(self) -> dict | None:
        character = self._collect()
        if character is None or self.campaign is None:
            return None
        return {
            "name": character.name,
            "kind": character.kind,
            "notes": character.notes,
            "motivation": character.motivation,
            "story_hook": character.story_hook,
            "attributes": character.attributes,
            "system_name": self.campaign.system_name,
        }

    def _prepare_sheet_html(self) -> str | None:
        if self._current is None or self.campaign is None:
            QMessageBox.information(self, "Ficha", "Selecione uma ficha primeiro.")
            return None
        self._save_current_silent()
        payload = self._sheet_payload()
        if payload is None:
            return None
        plugin = self.registry.get(self.campaign.system_slug)
        return plugin.format_sheet_html(payload)

    def _export_pdf(self) -> None:
        html = self._prepare_sheet_html()
        if html is None or self._current is None:
            return
        suggested = f"{_safe_filename(self._current.name)}.pdf"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar ficha",
            suggested,
            "PDF (*.pdf)",
        )
        if not path:
            return
        target = Path(path)
        if target.suffix.lower() != ".pdf":
            target = target.with_suffix(".pdf")
        try:
            write_sheet_pdf(html, target)
        except OSError as exc:
            QMessageBox.warning(self, "Ficha", f"Não foi possível exportar: {exc}")
            return
        QMessageBox.information(self, "Ficha", "Ficha exportada em PDF.")

    def _print(self) -> None:
        html = self._prepare_sheet_html()
        if html is None:
            return
        print_sheet(html, self)

    def _save(self) -> None:
        character = self._collect()
        if character is None or self.campaign is None:
            return
        plugin = self.registry.get(self.campaign.system_slug)
        errors = plugin.validate_attributes(character.attributes)
        if errors:
            QMessageBox.warning(
                self,
                "Ficha",
                "A ficha tem campos inválidos:\n- " + "\n- ".join(errors),
            )
            return
        if character.id is None:
            created = queries.create_character(self.db.conn, character)
            self._current = created
            self.reload(created.id)
        else:
            queries.update_character(self.db.conn, character)
            self._current = queries.get_character(self.db.conn, character.id)
            self.reload(character.id)
        QMessageBox.information(self, "Ficha", "Ficha salva.")

    def _save_current_silent(self) -> None:
        if self._current is None or self.campaign is None or self._sheet is None:
            return
        character = self._collect()
        if character is None or character.id is None:
            return
        queries.update_character(self.db.conn, character)

    def _new(self, kind: str) -> None:
        if self.campaign is None:
            return
        self._save_current_silent()
        plugin = self.registry.get(self.campaign.system_slug)
        character = Character(
            id=None,
            uuid=str(uuid.uuid4()),
            campaign_id=self.campaign.id,
            system_id=self.campaign.system_id,
            kind=kind,
            name={"pc": "Novo personagem", "npc": "Novo NPC", "monster": "Novo monstro"}.get(
                kind, "Novo"
            ),
            attributes=plugin.default_attributes(),
        )
        created = queries.create_character(self.db.conn, character)
        self.reload(created.id)

    def _delete(self) -> None:
        current = self._current
        if current is None or current.id is None:
            return
        if QMessageBox.question(self, "Excluir", f"Excluir «{current.name}»?") != QMessageBox.StandardButton.Yes:
            return
        queries.delete_character(self.db.conn, current.id)
        self._current = None
        self.reload()
