from __future__ import annotations

import html
import re
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
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

from gestor_rpg.core.models import Campaign, DocumentHit, ImportedDocument
from gestor_rpg.db import queries
from gestor_rpg.db.connection import Database
from gestor_rpg.ui.styles import HIGHLIGHT_HTML, make_empty_hint, set_empty_state, set_role


class DocumentsPage(QWidget):
    def __init__(self, db: Database, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self.campaign: Campaign | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel("Documentos")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        self.hint = QLabel("Manuais de todos os sistemas.")
        self.hint.setObjectName("pageSubtitle")
        layout.addWidget(self.hint)

        splitter = QSplitter()
        left = QWidget()
        left.setObjectName("sidePanel")
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(12, 12, 12, 12)
        left_l.setSpacing(10)
        section = QLabel("MANUAIS")
        section.setObjectName("sectionTitle")
        left_l.addWidget(section)
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._on_row)
        self.list_empty = make_empty_hint("Nenhum manual ainda")
        left_l.addWidget(self.list, 1)
        left_l.addWidget(self.list_empty, 1)
        self.list.hide()
        doc_btns = QHBoxLayout()
        doc_btns.setSpacing(8)
        self.btn_import = QPushButton("Importar PDF…")
        set_role(self.btn_import, "primary")
        self.btn_open_file = QPushButton("Abrir arquivo")
        self.btn_delete = QPushButton("Excluir")
        self.btn_open_file.clicked.connect(self._open_file)
        self.btn_delete.clicked.connect(self._delete)
        left_l.addWidget(self.btn_import)
        doc_btns.addWidget(self.btn_open_file)
        doc_btns.addWidget(self.btn_delete)
        left_l.addLayout(doc_btns)
        splitter.addWidget(left)

        center = QWidget()
        center_l = QVBoxLayout(center)
        center_l.setContentsMargins(12, 0, 0, 0)
        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar nos manuais…")
        self.search.returnPressed.connect(self._run_search)
        self.btn_search = QPushButton("Buscar")
        self.btn_search.clicked.connect(self._run_search)
        self.btn_clear = QPushButton("Limpar")
        self.btn_clear.clicked.connect(self._clear_search)
        search_row.addWidget(self.search, 1)
        search_row.addWidget(self.btn_search)
        search_row.addWidget(self.btn_clear)
        center_l.addLayout(search_row)
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        center_l.addWidget(self.preview, 1)
        splitter.addWidget(center)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        layout.addWidget(splitter, 1)
        self._docs: list[ImportedDocument] = []
        self._hits: list[DocumentHit] = []
        self._searching = False
        self.reload()

    def set_campaign(self, campaign: Campaign | None) -> None:
        self.campaign = campaign
        if campaign is None:
            self.hint.setText("Manuais de todos os sistemas.")
        else:
            self.hint.setText(f"{campaign.name}  ·  {campaign.system_name}")
        self.reload()

    def reload(self) -> None:
        if self.search.text().strip():
            self._run_search()
            return
        self._searching = False
        system_id = self.campaign.system_id if self.campaign else None
        self._docs = queries.list_documents(self.db.conn, system_id)
        self._hits = []
        self.list.clear()
        self.preview.clear()
        for doc in self._docs:
            item = QListWidgetItem(f"[{doc.doc_type}] {doc.title}")
            self.list.addItem(item)
        self.list_empty.setText("Nenhum manual ainda")
        set_empty_state(self.list, self.list_empty, not self._docs)

    def _clear_search(self) -> None:
        self.search.clear()
        self.reload()

    def _run_search(self) -> None:
        query = self.search.text().strip()
        if not query:
            self.reload()
            return
        self._searching = True
        system_id = self.campaign.system_id if self.campaign else None
        self._hits = queries.search_documents(self.db.conn, query, system_id)
        self._docs = []
        self.list.clear()
        self.preview.clear()
        if not self._hits:
            self.preview.setPlainText("Nenhum trecho encontrado.")
            self.list_empty.setText("Nenhum trecho encontrado")
            set_empty_state(self.list, self.list_empty, True)
            return
        for hit in self._hits:
            snippet = hit.snippet.replace("\n", " ")
            item = QListWidgetItem(f"[{hit.doc_type}] {hit.title}\n{snippet}")
            self.list.addItem(item)
        set_empty_state(self.list, self.list_empty, False)
        self.list.setCurrentRow(0)

    def _on_row(self, row: int) -> None:
        if self._searching:
            if not (0 <= row < len(self._hits)):
                self.preview.clear()
                return
            hit = self._hits[row]
            self._show_hit(hit)
            return
        if not (0 <= row < len(self._docs)):
            self.preview.clear()
            return
        doc = self._docs[row]
        header = f"{html.escape(doc.title)}<br>{html.escape(doc.source_path)}<br><br>"
        body = html.escape((doc.extracted_text or "")[:20000]).replace("\n", "<br>")
        self.preview.setHtml(header + body)

    def _show_hit(self, hit: DocumentHit) -> None:
        snippet_html = html.escape(hit.snippet)
        snippet_html = snippet_html.replace("[[", f'<span style="{HIGHLIGHT_HTML}">')
        snippet_html = snippet_html.replace("]]", "</span>")
        terms = re.findall(r"[A-Za-zÀ-ÿ0-9]+", self.search.text())
        full = html.escape((hit.extracted_text or "")[:20000])
        for term in terms:
            pattern = re.compile(re.escape(html.escape(term)), re.IGNORECASE)
            full = pattern.sub(
                lambda match: (f'<span style="{HIGHLIGHT_HTML}">{match.group(0)}</span>'),
                full,
            )
        full = full.replace("\n", "<br>")
        header = (
            f"<b>{html.escape(hit.title)}</b><br>"
            f"{html.escape(hit.source_path)}<br><br>"
            f"<i>Trecho:</i> {snippet_html}<br><br>"
        )
        self.preview.setHtml(header + full)

    def _selected_document(self) -> ImportedDocument | None:
        row = self.list.currentRow()
        if self._searching:
            if not (0 <= row < len(self._hits)):
                return None
            return queries.get_document(self.db.conn, self._hits[row].id)
        if not (0 <= row < len(self._docs)):
            return None
        return self._docs[row]

    def _open_file(self) -> None:
        doc = self._selected_document()
        if doc is None:
            QMessageBox.warning(self, "Documentos", "Selecione um documento.")
            return
        path = Path(doc.source_path)
        if not doc.source_path or not path.exists():
            QMessageBox.warning(
                self,
                "Documentos",
                "Arquivo original não encontrado neste computador.",
            )
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.resolve())))

    def _delete(self) -> None:
        doc = self._selected_document()
        if doc is None or doc.id is None:
            QMessageBox.warning(self, "Documentos", "Selecione um documento.")
            return
        if (
            QMessageBox.question(self, "Excluir", f"Excluir «{doc.title}»?")
            != QMessageBox.StandardButton.Yes
        ):
            return
        queries.delete_document(self.db.conn, doc.id)
        self.reload()
