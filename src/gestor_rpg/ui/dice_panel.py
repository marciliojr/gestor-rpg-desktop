from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from gestor_rpg.db import queries
from gestor_rpg.db.connection import Database
from gestor_rpg.modules.dice.parser import format_detail, roll
from gestor_rpg.ui.styles import make_empty_hint, set_empty_state, set_role


class DicePanel(QWidget):
    def __init__(self, db: Database, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.db = db
        self.setObjectName("dicePanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        title = QLabel("ROLAGENS")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        self.expression = QLineEdit()
        self.expression.setPlaceholderText("3d6+2  ·  1d20+1d4-1")
        self.expression.returnPressed.connect(self._roll)
        layout.addWidget(self.expression)

        quick = QGridLayout()
        quick.setContentsMargins(0, 2, 0, 2)
        quick.setHorizontalSpacing(8)
        quick.setVerticalSpacing(8)
        for index, faces in enumerate((4, 6, 8, 10, 12, 20, 100)):
            button = QPushButton(f"d{faces}")
            set_role(button, "compact")
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.clicked.connect(lambda _=False, f=faces: self._quick(f))
            quick.addWidget(button, index // 4, index % 4)
        layout.addLayout(quick)

        self.btn_roll = QPushButton("Rolar")
        set_role(self.btn_roll, "primary")
        self.btn_roll.clicked.connect(self._roll)
        layout.addWidget(self.btn_roll)

        self.result = QLabel("—")
        self.result.setObjectName("diceResult")
        self.result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.result)

        self.detail = QLabel("")
        self.detail.setObjectName("diceDetail")
        self.detail.setWordWrap(True)
        layout.addWidget(self.detail)

        self.history = QListWidget()
        self.history.setCursor(Qt.CursorShape.PointingHandCursor)
        self.history.itemClicked.connect(self._reroll)
        self.history_empty = make_empty_hint("Nenhuma rolagem ainda")
        layout.addWidget(self.history, 1)
        layout.addWidget(self.history_empty, 1)
        self.btn_clear = QPushButton("Limpar histórico")
        self.btn_clear.clicked.connect(self._clear)
        layout.addWidget(self.btn_clear)
        self.reload()

    def reload(self) -> None:
        self.history.clear()
        records = queries.list_dice_history(self.db.conn)
        for record in records:
            item = QListWidgetItem(f"{record.expression}  →  {record.total}")
            item.setData(Qt.ItemDataRole.UserRole, record.expression)
            self.history.addItem(item)
        set_empty_state(self.history, self.history_empty, not records)

    def _quick(self, faces: int) -> None:
        self.expression.setText(f"1d{faces}")
        self._roll()

    def _reroll(self, item: QListWidgetItem) -> None:
        expr = item.data(Qt.ItemDataRole.UserRole)
        if not expr:
            return
        self.expression.setText(str(expr))
        self._roll()

    def _roll(self) -> None:
        expr = self.expression.text().strip() or "1d20"
        try:
            result = roll(expr)
        except ValueError as exc:
            self.result.setText("!")
            self.detail.setText(str(exc))
            return
        self.result.setText(str(result.total))
        self.detail.setText(format_detail(result))
        queries.insert_dice_roll(self.db.conn, result.expression, result.total, result.detail)
        self.reload()

    def _clear(self) -> None:
        queries.clear_dice_history(self.db.conn)
        self.result.setText("—")
        self.detail.setText("")
        self.reload()
