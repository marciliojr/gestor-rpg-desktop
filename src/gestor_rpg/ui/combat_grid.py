from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsEllipseItem,
    QGraphicsPathItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QWidget,
)

from gestor_rpg.core.models import Combatant
from gestor_rpg.modules.combat_grid import clamp_cell, token_label
from gestor_rpg.ui.styles import (
    INK,
    LINE,
    MAP_ALLY,
    MAP_DARK,
    MAP_FOE,
    MAP_LINE,
    SIDE_TEXT,
    SURFACE,
    TERRACOTTA,
)

CELL = 64
TOKEN = 40
AXIS = 28
BOARD_PAD = 12


class TokenItem(QGraphicsEllipseItem):
    def __init__(self, combatant: Combatant, color: str, parent=None) -> None:
        pad = (CELL - TOKEN) / 2
        super().__init__(pad, 6, TOKEN, TOKEN, parent)
        self.combatant_id = combatant.id
        self.is_active = combatant.is_active
        self.setBrush(QBrush(QColor(color)))
        self.setPen(QPen(QColor(INK), 1.5))
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setZValue(1)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        initials = QGraphicsSimpleTextItem(token_label(combatant.name), self)
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        initials.setFont(font)
        initials.setBrush(QBrush(QColor(SIDE_TEXT)))
        box = initials.boundingRect()
        initials.setPos(pad + (TOKEN - box.width()) / 2, 6 + (TOKEN - box.height()) / 2)

        caption = combatant.name.strip() or "?"
        if len(caption) > 12:
            caption = caption[:11] + "…"
        plate = QGraphicsSimpleTextItem(caption, self)
        small = QFont()
        small.setBold(True)
        small.setPointSize(8)
        plate.setFont(small)
        plate.setBrush(QBrush(QColor(INK)))
        name_box = plate.boundingRect()
        pad_x, pad_y = 4.0, 1.5
        plate_w = name_box.width() + pad_x * 2
        plate_h = name_box.height() + pad_y * 2
        plate_x = (CELL - plate_w) / 2
        plate_y = CELL - plate_h - 2
        path = QPainterPath()
        path.addRoundedRect(plate_x, plate_y, plate_w, plate_h, 3, 3)
        backdrop = QGraphicsPathItem(path, self)
        backdrop.setBrush(QBrush(QColor(SURFACE)))
        backdrop.setPen(QPen(QColor(LINE), 1))
        backdrop.setZValue(0)
        plate.setZValue(1)
        plate.setPos(plate_x + pad_x, plate_y + pad_y)


class CombatGridView(QGraphicsView):
    token_selected = Signal(int)
    token_moved = Signal(int, int, int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("combatGrid")
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setBackgroundBrush(QBrush(QColor(MAP_DARK)))
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.scene_obj = QGraphicsScene(self)
        self.setScene(self.scene_obj)
        self._cols = 12
        self._rows = 8
        self._tokens: dict[int, TokenItem] = {}
        self._placing = False
        self._dragged: TokenItem | None = None
        self._user_zoom = False

    def set_board(self, cols: int, rows: int, combatants: list[Combatant]) -> None:
        self._cols = max(4, cols)
        self._rows = max(4, rows)
        self._placing = True
        self.scene_obj.clear()
        self._tokens = {}
        self._dragged = None
        self._draw_grid()
        for combatant in combatants:
            if combatant.id is None or combatant.grid_x < 0 or combatant.grid_y < 0:
                continue
            self._add_token(combatant)
        self._placing = False
        self._user_zoom = False
        self._fit()

    def highlight(self, combatant_id: int | None) -> None:
        for item in self._tokens.values():
            selected = item.combatant_id == combatant_id
            if item.is_active:
                color, width, z = TERRACOTTA, 4, 3
            elif selected:
                color, width, z = INK, 3, 2
            else:
                color, width, z = INK, 1.5, 1
            item.setPen(QPen(QColor(color), width))
            item.setZValue(z)

    def resizeEvent(self, event) -> None:  # noqa: ANN001
        super().resizeEvent(event)
        if not self._user_zoom:
            self._fit()

    def wheelEvent(self, event) -> None:  # noqa: ANN001
        delta = event.angleDelta().y()
        if delta == 0:
            return super().wheelEvent(event)
        self._user_zoom = True
        factor = 1.12 if delta > 0 else 1 / 1.12
        self.scale(factor, factor)

    def mousePressEvent(self, event) -> None:  # noqa: ANN001
        token = self._token_from_item(self.itemAt(event.position().toPoint()))
        if token is not None and token.combatant_id is not None:
            self._dragged = token
            self.token_selected.emit(token.combatant_id)
        elif event.button() == Qt.MouseButton.LeftButton:
            self._dragged = None
            col, row = self._cell_at(event)
            if col is not None and self._token_at(col, row) is None:
                self.token_moved.emit(-1, col, row)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: ANN001
        dragged = self._dragged
        super().mouseReleaseEvent(event)
        self._dragged = None
        if self._placing or dragged is None or dragged.combatant_id is None:
            return
        col, row = clamp_cell(
            round((dragged.x() - AXIS) / CELL),
            round((dragged.y() - AXIS) / CELL),
            self._cols,
            self._rows,
        )
        self.token_moved.emit(dragged.combatant_id, col, row)

    def refit(self) -> None:
        self._user_zoom = False
        self._fit()

    def _fit(self) -> None:
        rect = self.scene_obj.sceneRect()
        if rect.isEmpty() or self.viewport().width() < 20:
            return
        self.resetTransform()
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

    def _draw_grid(self) -> None:
        width = self._cols * CELL
        height = self._rows * CELL
        self.scene_obj.setSceneRect(
            QRectF(
                -BOARD_PAD,
                -BOARD_PAD,
                AXIS + width + 8 + BOARD_PAD * 2,
                AXIS + height + 8 + BOARD_PAD * 2,
            )
        )
        light = QColor(SURFACE)
        dark = QColor(LINE)
        line = QPen(QColor(MAP_LINE))
        line.setWidth(1)
        for col in range(self._cols):
            for row in range(self._rows):
                x = AXIS + col * CELL
                y = AXIS + row * CELL
                fill = dark if (col + row) % 2 else light
                cell = self.scene_obj.addRect(x, y, CELL, CELL, line, QBrush(fill))
                cell.setZValue(0)
        axis_font = QFont()
        axis_font.setBold(True)
        axis_font.setPointSize(10)
        for col in range(self._cols):
            label = QGraphicsSimpleTextItem(_col_name(col))
            label.setFont(axis_font)
            label.setBrush(QBrush(QColor(INK)))
            box = label.boundingRect()
            label.setPos(AXIS + col * CELL + (CELL - box.width()) / 2, 4)
            self.scene_obj.addItem(label)
        for row in range(self._rows):
            label = QGraphicsSimpleTextItem(str(row + 1))
            label.setFont(axis_font)
            label.setBrush(QBrush(QColor(INK)))
            box = label.boundingRect()
            label.setPos((AXIS - box.width()) / 2, AXIS + row * CELL + (CELL - box.height()) / 2)
            self.scene_obj.addItem(label)

    def _add_token(self, combatant: Combatant) -> None:
        color = MAP_ALLY if combatant.character_id is not None else MAP_FOE
        item = TokenItem(combatant, color)
        x, y = clamp_cell(combatant.grid_x, combatant.grid_y, self._cols, self._rows)
        item.setPos(AXIS + x * CELL, AXIS + y * CELL)
        self.scene_obj.addItem(item)
        if combatant.id is not None:
            self._tokens[combatant.id] = item

    def _cell_at(self, event) -> tuple[int | None, int | None]:  # noqa: ANN001
        scene_pos = self.mapToScene(event.position().toPoint())
        col = int((scene_pos.x() - AXIS) // CELL)
        row = int((scene_pos.y() - AXIS) // CELL)
        if 0 <= col < self._cols and 0 <= row < self._rows:
            return col, row
        return None, None

    def _token_from_item(self, item) -> TokenItem | None:  # noqa: ANN001
        current = item
        while current is not None:
            if isinstance(current, TokenItem):
                return current
            current = current.parentItem()
        return None

    def _token_at(self, col: int, row: int) -> TokenItem | None:
        for item in self._tokens.values():
            item_col = round((item.x() - AXIS) / CELL)
            item_row = round((item.y() - AXIS) / CELL)
            if item_col == col and item_row == row:
                return item
        return None


def _col_name(col: int) -> str:
    return chr(ord("A") + col) if 0 <= col < 26 else str(col + 1)
