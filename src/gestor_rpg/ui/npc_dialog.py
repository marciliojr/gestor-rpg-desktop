from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from gestor_rpg.core.models import Campaign, Character
from gestor_rpg.core.registry import PluginRegistry
from gestor_rpg.db.connection import Database
from gestor_rpg.modules.names.generator import CULTURES
from gestor_rpg.modules.npc.generator import generate_npc
from gestor_rpg.ui.sheets.page import SheetsPage
from gestor_rpg.ui.styles import polish_placeholders, set_role


class NpcDialog(QDialog):
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
        self._payload: dict | None = None
        self.setWindowTitle("NPC rápido")
        self.resize(520, 560)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        self.system = QComboBox()
        for plugin in registry.all():
            self.system.addItem(plugin.display_name, plugin.slug)
        if campaign is not None:
            index = self.system.findData(campaign.system_slug)
            if index >= 0:
                self.system.setCurrentIndex(index)
        self.culture = QComboBox()
        for slug, label in CULTURES.items():
            self.culture.addItem(label, slug)
        self.power = QComboBox()
        self.power.addItem("Fraco", "fraco")
        self.power.addItem("Médio", "medio")
        self.power.addItem("Forte", "forte")
        self.power.setCurrentIndex(1)
        form.addRow("Sistema", self.system)
        form.addRow("Cultura do nome", self.culture)
        form.addRow("Poder", self.power)
        layout.addLayout(form)

        self.name = QLineEdit()
        self.motivation = QLineEdit()
        self.hook = QLineEdit()
        extra = QFormLayout()
        extra.setHorizontalSpacing(12)
        extra.setVerticalSpacing(10)
        extra.addRow("Nome", self.name)
        extra.addRow("Motivação", self.motivation)
        extra.addRow("Gancho", self.hook)
        layout.addLayout(extra)

        layout.addWidget(QLabel("Ficha gerada"))
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        layout.addWidget(self.preview, 1)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        gen = QPushButton("Gerar")
        save = QPushButton("Salvar na campanha")
        close = QPushButton("Fechar")
        set_role(gen, "primary")
        gen.clicked.connect(self._generate)
        save.clicked.connect(self._save)
        close.clicked.connect(self.close)
        buttons.addWidget(gen)
        buttons.addWidget(save)
        buttons.addWidget(close)
        layout.addLayout(buttons)
        polish_placeholders(self)
        self._generate()

    def _generate(self) -> None:
        plugin = self.registry.get(self.system.currentData())
        payload = generate_npc(
            plugin,
            culture=self.culture.currentData(),
            power=self.power.currentData(),
        )
        self._payload = payload
        self.name.setText(payload["name"])
        self.motivation.setText(payload["motivation"])
        self.hook.setText(payload["story_hook"])
        self.preview.setHtml(
            plugin.format_sheet_html(
                {
                    "name": payload["name"],
                    "kind": "npc",
                    "motivation": payload.get("motivation"),
                    "story_hook": payload.get("story_hook"),
                    "attributes": payload.get("attributes") or {},
                    "system_name": plugin.display_name,
                }
            )
        )

    def _save(self) -> None:
        if self.campaign is None:
            QMessageBox.warning(self, "NPC", "Abra uma campanha antes de salvar o NPC.")
            return
        if self._payload is None:
            return
        slug = self.system.currentData()
        if slug != self.campaign.system_slug:
            QMessageBox.warning(
                self,
                "NPC",
                "O sistema do NPC precisa ser o mesmo da campanha aberta.",
            )
            return
        import uuid

        character = Character(
            id=None,
            uuid=str(uuid.uuid4()),
            campaign_id=self.campaign.id,
            system_id=self.campaign.system_id,
            kind="npc",
            name=self.name.text().strip() or self._payload["name"],
            motivation=self.motivation.text().strip(),
            story_hook=self.hook.text().strip(),
            attributes=self._payload["attributes"],
        )
        self.sheets.add_character(character)
        QMessageBox.information(self, "NPC", "NPC salvo na campanha.")
        self.accept()
