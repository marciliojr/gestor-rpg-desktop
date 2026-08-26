from __future__ import annotations

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from gestor_rpg.modules.names.generator import CULTURES, generate_many
from gestor_rpg.ui.styles import polish_placeholders, set_role


class NamesDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Gerador de nomes")
        self.resize(420, 480)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        self.culture = QComboBox()
        for slug, label in CULTURES.items():
            self.culture.addItem(label, slug)
        self.kind = QComboBox()
        self.kind.addItem("Nome completo", "full")
        self.kind.addItem("Prenome", "given")
        self.kind.addItem("Sobrenome", "surname")
        self.kind.addItem("Com apelido", "nickname")
        self.count = QSpinBox()
        self.count.setRange(1, 40)
        self.count.setValue(10)
        form.addRow("Cultura / tema", self.culture)
        form.addRow("Tipo", self.kind)
        form.addRow("Quantidade", self.count)
        layout.addLayout(form)

        self.list = QListWidget()
        layout.addWidget(self.list, 1)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        gen = QPushButton("Gerar")
        copy = QPushButton("Copiar selecionado")
        close = QPushButton("Fechar")
        set_role(gen, "primary")
        gen.clicked.connect(self._generate)
        copy.clicked.connect(self._copy)
        close.clicked.connect(self.close)
        buttons.addWidget(gen)
        buttons.addWidget(copy)
        buttons.addWidget(close)
        layout.addLayout(buttons)
        polish_placeholders(self)
        self._generate()

    def _generate(self) -> None:
        names = generate_many(
            self.culture.currentData(),
            self.kind.currentData(),
            self.count.value(),
        )
        self.list.clear()
        self.list.addItems(names)

    def _copy(self) -> None:
        item = self.list.currentItem()
        if item:
            QApplication.clipboard().setText(item.text())
