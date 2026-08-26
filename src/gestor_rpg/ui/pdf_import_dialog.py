from __future__ import annotations

import uuid
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from gestor_rpg.core.models import Campaign, Character, ImportedDocument
from gestor_rpg.core.registry import PluginRegistry
from gestor_rpg.db import queries
from gestor_rpg.db.connection import Database
from gestor_rpg.modules.pdf_import.extractor import extract_pdf
from gestor_rpg.ui.sheets.page import SheetsPage
from gestor_rpg.ui.styles import polish_placeholders, set_role


class PdfImportDialog(QDialog):
    def __init__(
        self,
        db: Database,
        registry: PluginRegistry,
        sheets: SheetsPage,
        campaign: Campaign | None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.db = db
        self.registry = registry
        self.sheets = sheets
        self.campaign = campaign
        self._path: str | None = None
        self.setWindowTitle("Importar PDF")
        self.resize(640, 560)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        file_row = QHBoxLayout()
        file_row.setSpacing(8)
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        browse = QPushButton("Escolher arquivo…")
        browse.clicked.connect(self._browse)
        file_row.addWidget(self.path_edit, 1)
        file_row.addWidget(browse)
        layout.addLayout(file_row)

        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        self.doc_type = QComboBox()
        self.doc_type.addItem("Ficha", "sheet")
        self.doc_type.addItem("Manual", "manual")
        self.doc_type.addItem("Outro", "other")
        self.system = QComboBox()
        self.system.addItem("(usar campanha)", "")
        for plugin in registry.all():
            self.system.addItem(plugin.display_name, plugin.slug)
        self.create_sheet = QCheckBox("Criar ficha se o PDF for reconhecido")
        self.create_sheet.setChecked(True)
        form.addRow("Tipo", self.doc_type)
        form.addRow("Sistema", self.system)
        form.addRow(self.create_sheet)
        layout.addLayout(form)

        layout.addWidget(QLabel("Pré-visualização do texto extraído"))
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        layout.addWidget(self.preview, 1)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        extract_btn = QPushButton("Extrair")
        import_btn = QPushButton("Importar")
        close = QPushButton("Fechar")
        set_role(import_btn, "primary")
        extract_btn.clicked.connect(self._extract)
        import_btn.clicked.connect(self._import)
        close.clicked.connect(self.close)
        buttons.addWidget(extract_btn)
        buttons.addWidget(import_btn)
        buttons.addWidget(close)
        layout.addLayout(buttons)
        polish_placeholders(self)
        self._extract_result = None

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "PDF", str(Path.home()), "PDF (*.pdf)"
        )
        if path:
            self._path = path
            self.path_edit.setText(path)
            self._extract()

    def _extract(self) -> None:
        if not self._path:
            QMessageBox.information(self, "PDF", "Escolha um arquivo PDF.")
            return
        try:
            extracted = extract_pdf(self._path)
        except Exception as exc:
            QMessageBox.critical(self, "PDF", f"Falha ao extrair: {exc}")
            return
        self._extract_result = extracted
        header = f"Páginas: {len(extracted.page_texts)}  ·  OCR: {'sim' if extracted.used_ocr else 'não'}\n\n"
        self.preview.setPlainText(header + extracted.full_text[:12000])

    def _resolve_slug(self) -> str | None:
        slug = self.system.currentData()
        if slug:
            return slug
        if self.campaign is not None:
            return self.campaign.system_slug
        return None

    def _import(self) -> None:
        if self._extract_result is None:
            self._extract()
        extracted = self._extract_result
        if extracted is None:
            return
        slug = self._resolve_slug()
        system_id = None
        if slug:
            found = queries.system_by_slug(self.db.conn, slug)
            system_id = found[0] if found else None

        character_id = None
        parsed_name = Path(extracted.path).stem
        if self.doc_type.currentData() == "sheet" and self.create_sheet.isChecked() and slug:
            plugin = self.registry.get(slug)
            parsed = plugin.try_parse_sheet(extracted)
            if parsed and self.campaign is not None:
                if self.campaign.system_slug != slug:
                    QMessageBox.warning(
                        self,
                        "PDF",
                        "O sistema escolhido não coincide com a campanha aberta.",
                    )
                    return
                character = Character(
                    id=None,
                    uuid=str(uuid.uuid4()),
                    campaign_id=self.campaign.id,
                    system_id=self.campaign.system_id,
                    kind="pc",
                    name=parsed.name or parsed_name,
                    attributes=parsed.attributes,
                )
                created = self.sheets.add_character(character)
                character_id = created.id
                parsed_name = created.name
            elif parsed is None:
                QMessageBox.information(
                    self,
                    "PDF",
                    "Não foi possível reconhecer uma ficha neste PDF. O documento será salvo mesmo assim.",
                )

        title = str(extracted.metadata.get("title") or parsed_name)
        queries.insert_document(
            self.db.conn,
            ImportedDocument(
                id=None,
                uuid=str(uuid.uuid4()),
                title=title,
                source_path=extracted.path,
                doc_type=self.doc_type.currentData(),
                system_id=system_id,
                character_id=character_id,
                extracted_text=extracted.full_text,
                metadata={
                    "used_ocr": extracted.used_ocr,
                    "pages": extracted.metadata.get("pages"),
                },
            ),
        )
        extra = " Ficha criada." if character_id else ""
        QMessageBox.information(self, "PDF", f"Documento importado.{extra}")
        self.accept()
