from __future__ import annotations

from PySide6.QtCore import QSize, QTimer, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from gestor_rpg.core.models import Campaign
from gestor_rpg.core.registry import registry
from gestor_rpg.db import queries
from gestor_rpg.db.connection import Database
from gestor_rpg.ui.campaigns_page import CampaignsPage
from gestor_rpg.ui.combat_page import CombatPage
from gestor_rpg.ui.dice_panel import DicePanel
from gestor_rpg.ui.documents_page import DocumentsPage
from gestor_rpg.ui.help_page import HelpPage
from gestor_rpg.ui.monsters_page import MonstersPage
from gestor_rpg.ui.names_dialog import NamesDialog
from gestor_rpg.ui.npc_dialog import NpcDialog
from gestor_rpg.ui.pdf_import_dialog import PdfImportDialog
from gestor_rpg.ui.session_page import SessionPage
from gestor_rpg.ui.sheets.page import SheetsPage
from gestor_rpg.ui.styles import SAGE_SOFT, apply_theme, polish_placeholders

PAGE_HELP = 6
NAV_GROUPS = (
    ("MESA", (("Campanhas", 0),)),
    ("PREPARAR", (("Fichas", 1), ("Documentos", 2), ("Monstros", 3))),
    ("JOGAR", (("Combate", 4), ("Sessão", 5))),
)


def _nav_header(text: str) -> QListWidgetItem:
    item = QListWidgetItem(text)
    item.setFlags(Qt.ItemFlag.NoItemFlags)
    font = QFont(item.font())
    font.setBold(True)
    font.setPointSize(10)
    item.setFont(font)
    item.setForeground(QColor(SAGE_SOFT))
    item.setSizeHint(QSize(10, 28))
    return item


def _nav_page(text: str, page: int) -> QListWidgetItem:
    item = QListWidgetItem(text)
    item.setData(Qt.ItemDataRole.UserRole, page)
    return item


class MainWindow(QMainWindow):
    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db
        self.plugins = registry()
        self.campaign: Campaign | None = None
        self.setWindowTitle("Gestor RPG")
        self.resize(1360, 860)
        app = QApplication.instance()
        if app is not None:
            apply_theme(app)
        self.menuBar().hide()
        self.statusBar().hide()

        self.nav = QListWidget()
        self.nav.setObjectName("navList")
        self.nav.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        for caption, entries in NAV_GROUPS:
            self.nav.addItem(_nav_header(caption))
            for label, page in entries:
                self.nav.addItem(_nav_page(label, page))

        self.tools = QListWidget()
        self.tools.setObjectName("toolsList")
        self.tools.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        for label in ("NPC rápido…", "Gerador de nomes…", "Importar PDF…"):
            self.tools.addItem(QListWidgetItem(label))
        self.tools.setMaximumHeight(148)
        self.tools.itemClicked.connect(self._on_tool)

        self.help_nav = QListWidget()
        self.help_nav.setObjectName("navList")
        self.help_nav.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.help_nav.addItem(QListWidgetItem("Como usar"))
        self.help_nav.setMaximumHeight(52)

        self.btn_quit = QPushButton("Sair")
        self.btn_quit.clicked.connect(self.close)

        self.campaigns_page = CampaignsPage(db)
        self.sheets_page = SheetsPage(db, self.plugins)
        self.documents_page = DocumentsPage(db)
        self.monsters_page = MonstersPage(db, self.plugins)
        self.combat_page = CombatPage(db, self.plugins)
        self.session_page = SessionPage(db)
        self.help_page = HelpPage()
        self.stack = QStackedWidget()
        self.stack.setObjectName("contentStack")
        self.stack.addWidget(self.campaigns_page)
        self.stack.addWidget(self.sheets_page)
        self.stack.addWidget(self.documents_page)
        self.stack.addWidget(self.monsters_page)
        self.stack.addWidget(self.combat_page)
        self.stack.addWidget(self.session_page)
        self.stack.addWidget(self.help_page)

        self.nav.currentRowChanged.connect(self._on_nav)
        self.help_nav.currentRowChanged.connect(self._on_help_nav)
        self.campaigns_page.campaign_selected.connect(self._set_campaign)
        self.documents_page.btn_import.clicked.connect(self._import_pdf)

        self.dice_panel = DicePanel(db)
        self.setCentralWidget(self._build_shell())
        self._show_combat_map(False)
        self.select_page(0)
        self._restore_campaign()
        self._refresh_status()
        polish_placeholders(self)

    def nav_page_labels(self) -> list[str]:
        labels: list[str] = []
        for index in range(self.nav.count()):
            item = self.nav.item(index)
            if item is not None and isinstance(item.data(Qt.ItemDataRole.UserRole), int):
                labels.append(item.text())
        return labels

    def select_page(self, page: int) -> None:
        if page == PAGE_HELP:
            self.help_nav.setCurrentRow(0)
            return
        for index in range(self.nav.count()):
            item = self.nav.item(index)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == page:
                self.nav.setCurrentRow(index)
                return

    def _build_shell(self) -> QWidget:
        shell = QWidget()
        shell.setObjectName("appShell")
        body = QHBoxLayout(shell)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._build_sidebar())
        content = QWidget()
        content.setObjectName("appContent")
        content_l = QVBoxLayout(content)
        content_l.setContentsMargins(20, 20, 20, 20)
        content_l.addWidget(self.stack, 1)
        body.addWidget(content, 1)
        body.addWidget(self._build_rail())
        return shell

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("appSidebar")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 16)
        layout.setSpacing(4)
        brand = QLabel("GESTOR RPG")
        brand.setObjectName("appBrand")
        self.header_campaign = QLabel("Nenhuma campanha aberta")
        self.header_campaign.setObjectName("headerCampaign")
        self.header_campaign.setWordWrap(True)
        layout.addWidget(brand)
        layout.addWidget(self.header_campaign)
        layout.addWidget(self.nav, 1)
        tools_caption = QLabel("FERRAMENTAS")
        tools_caption.setObjectName("navCaption")
        layout.addWidget(tools_caption)
        layout.addWidget(self.tools)
        rule = QFrame()
        rule.setObjectName("sidebarRule")
        rule.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(rule)
        layout.addWidget(self.help_nav)
        layout.addWidget(self.btn_quit)
        return sidebar

    def _build_rail(self) -> QWidget:
        rail = QWidget()
        rail.setObjectName("appRail")
        self._rail = rail
        layout = QVBoxLayout(rail)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        split = QSplitter()
        split.setOrientation(Qt.Orientation.Vertical)
        split.setChildrenCollapsible(False)
        split.addWidget(self.combat_page.map_panel)
        split.addWidget(self.dice_panel)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 2)
        self._rail_split = split
        layout.addWidget(split)
        return rail

    def _on_tool(self, item: QListWidgetItem) -> None:
        label = item.text()
        self.tools.clearSelection()
        if label.startswith("Importar"):
            self._import_pdf()
        elif label.startswith("NPC"):
            self._npc()
        elif label.startswith("Gerador de nomes"):
            self._names()

    def _on_nav(self, row: int) -> None:
        item = self.nav.item(row) if row >= 0 else None
        if item is None:
            return
        page = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(page, int):
            return
        self.help_nav.blockSignals(True)
        self.help_nav.clearSelection()
        self.help_nav.setCurrentRow(-1)
        self.help_nav.blockSignals(False)
        self._goto_page(page)

    def _on_help_nav(self, row: int) -> None:
        if row < 0:
            return
        self.nav.blockSignals(True)
        self.nav.clearSelection()
        self.nav.setCurrentRow(-1)
        self.nav.blockSignals(False)
        self._goto_page(PAGE_HELP)

    def _goto_page(self, page: int) -> None:
        self.stack.setCurrentIndex(page)
        self._show_combat_map(page == 4)
        if page == 1:
            self.sheets_page.reload()
        elif page == 3:
            self.monsters_page.reload()
        elif page == 4:
            self.combat_page.reload()
        elif page == 5:
            self.session_page.reload()

    def _show_combat_map(self, visible: bool) -> None:
        self.combat_page.map_panel.setVisible(visible)
        self._rail.setProperty("combatMap", "true" if visible else "false")
        self._rail.style().unpolish(self._rail)
        self._rail.style().polish(self._rail)
        if visible:
            total = max(self._rail.height(), 400)
            self._rail_split.setSizes([int(total * 0.58), int(total * 0.42)])
            QTimer.singleShot(0, self.combat_page.grid.refit)

    def _set_campaign(self, campaign: Campaign | None, *, switch_page: bool = True) -> None:
        self.campaign = campaign
        self.sheets_page.set_campaign(campaign)
        self.documents_page.set_campaign(campaign)
        self.monsters_page.set_campaign(campaign)
        self.combat_page.set_campaign(campaign)
        self.session_page.set_campaign(campaign)
        if campaign is not None:
            queries.set_setting(self.db.conn, "current_campaign_id", str(campaign.id))
            if switch_page:
                self.select_page(1)
        else:
            queries.set_setting(self.db.conn, "current_campaign_id", "")
        self._refresh_status()

    def _restore_campaign(self) -> None:
        raw = queries.get_setting(self.db.conn, "current_campaign_id")
        if not raw:
            return
        try:
            campaign_id = int(raw)
        except ValueError:
            return
        campaign = queries.get_campaign(self.db.conn, campaign_id)
        if campaign:
            self._set_campaign(campaign, switch_page=False)

    def _refresh_status(self) -> None:
        if self.campaign:
            text = f"{self.campaign.name}\n{self.campaign.system_name}"
        else:
            text = "Nenhuma campanha aberta"
        self.header_campaign.setText(text)

    def _import_pdf(self) -> None:
        dialog = PdfImportDialog(
            self.db, self.plugins, self.sheets_page, self.campaign, self
        )
        if dialog.exec():
            self.documents_page.reload()

    def _npc(self) -> None:
        dialog = NpcDialog(self.db, self.plugins, self.sheets_page, self.campaign, self)
        dialog.exec()

    def _names(self) -> None:
        NamesDialog(self).exec()
