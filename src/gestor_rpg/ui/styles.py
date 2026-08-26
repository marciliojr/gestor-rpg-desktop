# Paleta clara azul: papel frio + ardósia azul + aço.
from pathlib import Path

CANVAS = "#E8EEF4"
SURFACE = "#F5F8FC"
INK = "#1B2838"
MUTED = "#5B6B7C"
LINE = "#C5D0DC"
SIDE = "#243044"
SIDE_RAISED = "#2F3F58"
SIDE_TEXT = "#E8EEF5"
SIDE_LINE = "#4A5D78"
SAGE = "#3D6FA3"
SAGE_SOFT = "#C5D6EA"
TERRACOTTA = "#2E5A87"
TERRACOTTA_SOFT = "#B7CDE4"
MAP_ALLY = SAGE
MAP_FOE = "#C4785A"
MAP_FOE_SOFT = "#E8D0C6"
MAP_LINE = "#6A7E92"
MAP_DARK = "#D5E0EC"
MAP_AXIS = MUTED
HIGHLIGHT_HTML = f"background:{SAGE_SOFT};color:{INK}"
EMPTY_NO_CAMPAIGN = "Abra uma campanha"

_RES = Path(__file__).resolve().parent.parent / "resources"
_ARROW_INK = '"' + (_RES / "combo-arrow.png").as_posix() + '"'
_ARROW_ICE = '"' + (_RES / "combo-arrow-ice.png").as_posix() + '"'

_DARK = "QWidget#appSidebar, QWidget#appRail, QWidget#sidePanel, QWidget#dicePanel, QWidget#mapPanel"

APP_QSS = f"""
* {{
    font-family: "Segoe UI", "Ubuntu", "Cantarell", "Noto Sans", sans-serif;
}}
QMainWindow, QDialog, QWidget {{
    background-color: {CANVAS};
    color: {INK};
    font-size: 13px;
}}
QWidget#appShell, QWidget#appBody, QWidget#appContent, QStackedWidget#contentStack {{
    background-color: {CANVAS};
}}
{_DARK} {{
    background-color: {SIDE};
}}
QWidget#appSidebar {{
    min-width: 232px;
    max-width: 232px;
}}
QWidget#appRail {{
    min-width: 288px;
    max-width: 288px;
}}
QWidget#appRail[combatMap="true"] {{
    min-width: 380px;
    max-width: 420px;
}}
QWidget#mapPanel {{
    background-color: {SIDE};
}}
QWidget#sidePanel {{
    min-width: 260px;
    max-width: 360px;
}}
QLabel {{
    background-color: transparent;
    color: {INK};
    padding: 2px 0;
}}
QLabel#pageTitle {{
    color: {INK};
    font-size: 22px;
    font-weight: 700;
    padding: 4px 0 4px 0;
}}
QLabel#pageSubtitle {{
    color: {MUTED};
    font-size: 13px;
    font-weight: 500;
    padding: 0 0 12px 0;
}}
QLabel#sectionTitle {{
    color: {SAGE};
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.8px;
    padding: 6px 0;
}}
QWidget#appContent QLabel,
QDialog QLabel {{
    color: {INK};
    background: transparent;
}}
QWidget#appContent QLabel#pageSubtitle {{
    color: {MUTED};
}}
QLabel#helpHeading {{
    color: {INK};
    font-size: 16px;
    font-weight: 700;
    padding: 2px 0 4px 0;
}}
QWidget#appContent QLabel#helpHeading {{
    color: {INK};
}}
QLabel#helpBody,
QWidget#appContent QLabel#helpBody {{
    color: {INK};
    font-size: 13px;
    font-weight: 400;
    letter-spacing: 0;
    padding: 0 0 6px 0;
}}
QLabel#helpLead,
QWidget#appContent QLabel#helpLead {{
    color: {MUTED};
    font-size: 13px;
    font-weight: 500;
    padding: 0 0 8px 0;
}}
QWidget#helpCard {{
    background-color: {SURFACE};
    border: 1px solid {LINE};
    border-radius: 10px;
}}
QWidget#helpCard QLabel#helpHeading {{
    color: {SAGE};
}}
QWidget#appContent QLabel#roundBadge {{
    background-color: {SAGE_SOFT};
    color: {INK};
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 13px;
    font-weight: 700;
    min-width: 88px;
}}
QWidget#mapPanel QLabel#mutedHint {{
    color: {SAGE_SOFT};
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0;
    padding: 2px 0 0 0;
}}
QLabel#emptyHint {{
    color: {MUTED};
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0;
    padding: 18px 10px;
}}
QWidget#appSidebar QLabel#emptyHint,
QWidget#appRail QLabel#emptyHint,
QWidget#sidePanel QLabel#emptyHint,
QWidget#dicePanel QLabel#emptyHint,
QWidget#mapPanel QLabel#emptyHint {{
    color: {SAGE_SOFT};
}}
QWidget#sidePanel[tone="paper"] QLabel#emptyHint {{
    color: {MUTED};
}}
QLabel#diceDetail,
QWidget#appRail QLabel#diceDetail,
QWidget#dicePanel QLabel#diceDetail {{
    color: {SIDE_TEXT};
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0;
    padding: 4px 0 2px 0;
}}
QWidget#appSidebar QLabel,
QWidget#appRail QLabel,
QWidget#sidePanel QLabel,
QWidget#dicePanel QLabel,
QWidget#mapPanel QLabel {{
    color: {SIDE_TEXT};
    background: transparent;
}}
QLabel#navCaption,
QWidget#appSidebar QLabel#navCaption,
QWidget#appRail QLabel#sectionTitle,
QWidget#sidePanel QLabel#sectionTitle,
QWidget#dicePanel QLabel#sectionTitle,
QWidget#mapPanel QLabel#sectionTitle {{
    color: {SAGE_SOFT};
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.3px;
    padding: 8px 8px 4px 8px;
}}
QLabel#appBrand {{
    color: {SIDE_TEXT};
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 0.5px;
    padding: 4px 8px 2px 8px;
}}
QLabel#headerCampaign {{
    color: {TERRACOTTA_SOFT};
    font-size: 12px;
    font-weight: 600;
    padding: 0 8px 12px 8px;
}}
QListWidget#navList, QListWidget#toolsList {{
    background-color: {SIDE};
    color: {SIDE_TEXT};
    border: none;
    outline: none;
    padding: 4px 8px;
    font-size: 14px;
    font-weight: 650;
}}
QListWidget#navList::item, QListWidget#toolsList::item {{
    padding: 10px 12px;
    margin: 3px 0;
    border-radius: 8px;
    color: {SIDE_TEXT};
    background-color: transparent;
}}
QListWidget#navList::item:hover, QListWidget#toolsList::item:hover {{
    background-color: {SIDE_RAISED};
    color: {SIDE_TEXT};
}}
QListWidget#navList::item:selected, QListWidget#toolsList::item:selected {{
    background-color: {SAGE};
    color: {SIDE_TEXT};
}}
QListWidget#navList::item:selected:hover, QListWidget#toolsList::item:selected:hover {{
    background-color: {SAGE};
    color: {SIDE_TEXT};
}}
QListWidget#navList::item:disabled {{
    background-color: transparent;
    color: {SAGE_SOFT};
    font-size: 11px;
    font-weight: 800;
    padding: 10px 12px 2px 12px;
    margin: 8px 0 0 0;
    border-radius: 0;
}}
QListWidget#navList::item:disabled:hover {{
    background-color: transparent;
    color: {SAGE_SOFT};
}}
QFrame#sidebarRule {{
    background-color: {SIDE_LINE};
    border: none;
    max-height: 1px;
    min-height: 1px;
    margin: 8px 8px 4px 8px;
}}
QListWidget, QPlainTextEdit, QTextEdit, QLineEdit, QComboBox, QSpinBox, QAbstractSpinBox, QGraphicsView {{
    background-color: {SURFACE};
    color: {INK};
    border: 1px solid {LINE};
    border-radius: 8px;
    padding: 6px 10px;
    min-height: 32px;
    selection-background-color: {SAGE_SOFT};
    selection-color: {INK};
}}
QWidget#mapCard {{
    background-color: {MAP_DARK};
    border: 1px solid {MAP_LINE};
    border-radius: 10px;
}}
QGraphicsView#combatGrid {{
    background-color: {MAP_DARK};
    border: none;
    border-radius: 8px;
    padding: 0;
    min-height: 160px;
}}
QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QAbstractSpinBox:focus {{
    border: 1px solid {SAGE};
}}
QLineEdit:disabled, QPlainTextEdit:disabled, QTextEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QAbstractSpinBox:disabled {{
    background-color: {CANVAS};
    color: {MUTED};
    border: 1px solid {LINE};
}}
QWidget#appSidebar QListWidget,
QWidget#appRail QListWidget,
QWidget#sidePanel QListWidget,
QWidget#dicePanel QListWidget,
QWidget#appSidebar QLineEdit,
QWidget#appRail QLineEdit,
QWidget#sidePanel QLineEdit,
QWidget#dicePanel QLineEdit,
QWidget#appRail QPlainTextEdit,
QWidget#sidePanel QPlainTextEdit,
QWidget#dicePanel QPlainTextEdit,
QWidget#appContent QWidget#sidePanel QComboBox,
QWidget#appRail QComboBox,
QWidget#sidePanel QComboBox,
QWidget#dicePanel QComboBox,
QWidget#appRail QSpinBox,
QWidget#sidePanel QSpinBox,
QWidget#dicePanel QSpinBox {{
    background-color: {SIDE_RAISED};
    color: {SIDE_TEXT};
    border: 1px solid {SIDE_LINE};
    selection-background-color: {SAGE};
    selection-color: {SIDE_TEXT};
}}
QListWidget::item {{
    padding: 8px 10px;
    border-radius: 6px;
    color: {INK};
}}
QWidget#appSidebar QListWidget::item,
QWidget#appRail QListWidget::item,
QWidget#sidePanel QListWidget::item,
QWidget#dicePanel QListWidget::item {{
    color: {SIDE_TEXT};
}}
QListWidget::item:selected {{
    background-color: {SAGE_SOFT};
    color: {INK};
}}
QListWidget::item:hover {{
    background-color: {SAGE_SOFT};
    color: {INK};
}}
QWidget#appRail QListWidget::item:hover,
QWidget#sidePanel QListWidget::item:hover,
QWidget#dicePanel QListWidget::item:hover {{
    background-color: {SAGE};
    color: {SIDE_TEXT};
}}
QWidget#appSidebar QListWidget::item:selected,
QWidget#appRail QListWidget::item:selected,
QWidget#sidePanel QListWidget::item:selected,
QWidget#dicePanel QListWidget::item:selected {{
    background-color: {SAGE};
    color: {SIDE_TEXT};
}}
QComboBox {{
    combobox-popup: 0;
    color: {INK};
    background-color: {SURFACE};
    padding-right: 28px;
}}
QComboBox QLabel,
QComboBox QLineEdit {{
    color: {INK};
    background: transparent;
    min-height: 0;
    padding: 0;
    border: none;
}}
QComboBox:disabled QLabel,
QComboBox:disabled QLineEdit {{
    color: {MUTED};
}}
QWidget#sidePanel QComboBox QLabel,
QWidget#appRail QComboBox QLabel,
QWidget#dicePanel QComboBox QLabel,
QWidget#sidePanel QComboBox QLineEdit,
QWidget#appRail QComboBox QLineEdit,
QWidget#dicePanel QComboBox QLineEdit {{
    color: {SIDE_TEXT};
    background: transparent;
}}
QComboBox QAbstractItemView {{
    background: {SURFACE};
    color: {INK};
    selection-background-color: {SAGE_SOFT};
    selection-color: {INK};
    border: 1px solid {LINE};
    outline: none;
    padding: 4px;
}}
QComboBox QAbstractItemView::item {{
    color: {INK};
    background: {SURFACE};
    min-height: 28px;
    padding: 6px 10px;
}}
QComboBox QAbstractItemView::item:selected,
QComboBox QAbstractItemView::item:hover {{
    background: {SAGE_SOFT};
    color: {INK};
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    border: none;
    border-left: 1px solid {LINE};
    width: 28px;
    background: transparent;
}}
QComboBox::down-arrow {{
    image: url({_ARROW_INK});
    width: 10px;
    height: 6px;
}}
QWidget#appContent QWidget#sidePanel QComboBox::drop-down,
QWidget#appRail QComboBox::drop-down,
QWidget#sidePanel QComboBox::drop-down,
QWidget#dicePanel QComboBox::drop-down {{
    border-left: 1px solid {SIDE_LINE};
}}
QWidget#appContent QWidget#sidePanel QComboBox::down-arrow,
QWidget#appRail QComboBox::down-arrow,
QWidget#sidePanel QComboBox::down-arrow,
QWidget#dicePanel QComboBox::down-arrow {{
    image: url({_ARROW_ICE});
}}
QPushButton {{
    background-color: {SURFACE};
    color: {INK};
    border: 1px solid {LINE};
    border-radius: 8px;
    padding: 8px 16px;
    min-height: 36px;
    min-width: 96px;
    font-weight: 650;
}}
QPushButton:hover {{
    background-color: {SAGE_SOFT};
    border: 1px solid {SAGE};
    color: {INK};
}}
QPushButton:pressed {{
    background-color: {SAGE};
    color: {SIDE_TEXT};
}}
QPushButton:disabled {{
    background-color: {CANVAS};
    color: {MUTED};
    border: 1px solid {LINE};
}}
QPushButton[role="primary"] {{
    background-color: {SAGE};
    color: {SIDE_TEXT};
    border: 1px solid {SAGE};
}}
QPushButton[role="primary"]:hover {{
    background-color: {TERRACOTTA};
    border: 1px solid {TERRACOTTA};
    color: {SIDE_TEXT};
}}
QPushButton[role="primary"]:pressed {{
    background-color: {INK};
    color: {SURFACE};
}}
QPushButton[role="compact"] {{
    min-height: 36px;
    min-width: 52px;
    padding: 6px 8px;
    font-size: 13px;
}}
QPushButton[role="quiet"] {{
    background-color: {CANVAS};
    color: {MUTED};
    border: 1px solid {LINE};
    font-weight: 600;
}}
QPushButton[role="quiet"]:hover {{
    background-color: {SURFACE};
    color: {INK};
    border: 1px solid {SAGE};
}}
QPushButton[role="foe"] {{
    background-color: {SURFACE};
    color: {MAP_FOE};
    border: 1px solid {MAP_FOE};
}}
QPushButton[role="foe"]:hover {{
    background-color: {MAP_FOE_SOFT};
    color: {MAP_FOE};
    border: 1px solid {MAP_FOE};
}}
QPushButton[role="foe"]:pressed {{
    background-color: {MAP_FOE};
    color: {SIDE_TEXT};
    border: 1px solid {MAP_FOE};
}}
QWidget#appSidebar QPushButton,
QWidget#appRail QPushButton,
QWidget#sidePanel QPushButton,
QWidget#dicePanel QPushButton {{
    background-color: {SIDE_RAISED};
    color: {SIDE_TEXT};
    border: 1px solid {SIDE_LINE};
}}
QWidget#appSidebar QPushButton:hover,
QWidget#appRail QPushButton:hover,
QWidget#sidePanel QPushButton:hover,
QWidget#dicePanel QPushButton:hover {{
    background-color: {SAGE};
    color: {SIDE_TEXT};
    border: 1px solid {SAGE};
}}
QWidget#sidePanel[tone="paper"] {{
    background-color: {SURFACE};
    border: 1px solid {LINE};
    border-radius: 10px;
}}
QWidget#sidePanel[tone="paper"] QLabel {{
    color: {INK};
    background: transparent;
}}
QWidget#sidePanel[tone="paper"] QLabel#sectionTitle {{
    color: {SAGE};
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.8px;
    padding: 6px 0;
}}
QWidget#sidePanel[tone="paper"] QListWidget {{
    background-color: {SURFACE};
    color: {INK};
    border: 1px solid {LINE};
    selection-background-color: {SAGE_SOFT};
    selection-color: {INK};
}}
QWidget#sidePanel[tone="paper"] QListWidget::item {{
    color: {INK};
}}
QWidget#sidePanel[tone="paper"] QListWidget::item:hover,
QWidget#sidePanel[tone="paper"] QListWidget::item:selected {{
    background-color: {SAGE_SOFT};
    color: {INK};
}}
QWidget#sidePanel[tone="paper"] QPushButton {{
    background-color: {SURFACE};
    color: {INK};
    border: 1px solid {LINE};
}}
QWidget#sidePanel[tone="paper"] QPushButton:hover {{
    background-color: {SAGE_SOFT};
    color: {INK};
    border: 1px solid {SAGE};
}}
QGroupBox {{
    background: {SURFACE};
    color: {INK};
    border: 1px solid {LINE};
    border-radius: 10px;
    margin-top: 14px;
    padding: 14px 12px 12px 12px;
    font-weight: 700;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {SAGE};
    background: {CANVAS};
}}
QGroupBox QLabel {{
    color: {INK};
}}
QLabel#diceResult,
QWidget#appRail QLabel#diceResult,
QWidget#dicePanel QLabel#diceResult {{
    font-size: 36px;
    color: {INK};
    font-weight: 800;
    background: {SAGE_SOFT};
    border: 1px solid {SAGE};
    border-radius: 12px;
    padding: 12px;
    min-height: 64px;
}}
QStatusBar {{
    background: {CANVAS};
    color: {MUTED};
    border-top: 1px solid {LINE};
}}
QMenu {{
    background: {SURFACE};
    color: {INK};
    border: 1px solid {LINE};
}}
QMenu::item {{
    color: {INK};
    padding: 6px 18px;
}}
QMenu::item:selected {{
    background: {SAGE_SOFT};
    color: {INK};
}}
QTabWidget::pane {{
    border: 1px solid {LINE};
    border-radius: 8px;
    background: {SURFACE};
}}
QTabBar::tab {{
    background: {CANVAS};
    color: {INK};
    border: 1px solid {LINE};
    border-bottom: none;
    padding: 8px 14px;
    margin-right: 4px;
    font-weight: 650;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}}
QTabBar::tab:selected {{
    background: {SAGE_SOFT};
    color: {INK};
}}
QScrollArea {{
    border: none;
    background: {CANVAS};
}}
QHeaderView::section {{
    background: {SAGE};
    color: {SIDE_TEXT};
    padding: 6px;
    border: none;
    font-weight: 700;
}}
QCheckBox {{
    spacing: 8px;
    color: {INK};
    background: transparent;
}}
QGroupBox QCheckBox {{
    color: {INK};
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {SAGE};
    border-radius: 4px;
    background: {SURFACE};
}}
QCheckBox::indicator:checked {{
    background: {SAGE};
}}
QSplitter::handle {{
    background: {CANVAS};
}}
QSplitter::handle:horizontal {{
    width: 12px;
}}
QSplitter::handle:vertical {{
    height: 12px;
}}
QSplitter::handle:hover {{
    background: {SAGE_SOFT};
}}
QScrollBar:vertical {{
    background: {CANVAS};
    width: 10px;
    margin: 0;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {LINE};
    min-height: 24px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{
    background: {SAGE};
}}
QScrollBar:horizontal {{
    background: {CANVAS};
    height: 10px;
    margin: 0;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {LINE};
    min-width: 24px;
    border-radius: 4px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0;
    width: 0;
}}
QToolTip {{
    background: {SURFACE};
    color: {INK};
    border: 1px solid {SAGE};
    padding: 4px 8px;
}}
"""


def light_palette():
    from PySide6.QtGui import QColor, QPalette

    ink = QColor(INK)
    canvas = QColor(CANVAS)
    surface = QColor(SURFACE)
    muted = QColor(MUTED)
    wash = QColor(SAGE_SOFT)
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, canvas)
    palette.setColor(QPalette.ColorRole.WindowText, ink)
    palette.setColor(QPalette.ColorRole.Base, surface)
    palette.setColor(QPalette.ColorRole.AlternateBase, canvas)
    palette.setColor(QPalette.ColorRole.Text, ink)
    palette.setColor(QPalette.ColorRole.Button, surface)
    palette.setColor(QPalette.ColorRole.ButtonText, ink)
    palette.setColor(QPalette.ColorRole.BrightText, QColor(SIDE_TEXT))
    palette.setColor(QPalette.ColorRole.ToolTipBase, surface)
    palette.setColor(QPalette.ColorRole.ToolTipText, ink)
    palette.setColor(QPalette.ColorRole.PlaceholderText, muted)
    palette.setColor(QPalette.ColorRole.Highlight, wash)
    palette.setColor(QPalette.ColorRole.HighlightedText, ink)
    palette.setColor(QPalette.ColorRole.Link, QColor(SAGE))
    disabled = QPalette.ColorGroup.Disabled
    palette.setColor(disabled, QPalette.ColorRole.WindowText, muted)
    palette.setColor(disabled, QPalette.ColorRole.Text, muted)
    palette.setColor(disabled, QPalette.ColorRole.ButtonText, muted)
    palette.setColor(disabled, QPalette.ColorRole.Base, canvas)
    palette.setColor(disabled, QPalette.ColorRole.Button, canvas)
    return palette


def apply_theme(app) -> None:
    from PySide6.QtWidgets import QStyleFactory

    if "Fusion" in QStyleFactory.keys():
        app.setStyle("Fusion")
    app.setPalette(light_palette())
    app.setStyleSheet(APP_QSS)


def set_role(widget, role: str) -> None:
    widget.setProperty("role", role)
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()
    fit_button(widget)


def fit_button(widget) -> None:
    from PySide6.QtGui import QFontMetrics
    from PySide6.QtWidgets import QPushButton

    if not isinstance(widget, QPushButton):
        return
    if widget.property("role") == "compact":
        return
    text = widget.text().replace("&", "")
    if not text:
        return
    needed = QFontMetrics(widget.font()).horizontalAdvance(text) + 40
    widget.setMinimumWidth(max(needed, 96))


def polish_buttons(root) -> None:
    from PySide6.QtWidgets import QPushButton, QWidget

    widgets = [root, *root.findChildren(QWidget)]
    for widget in widgets:
        if isinstance(widget, QPushButton):
            fit_button(widget)


def set_empty_state(list_widget, empty_label, is_empty: bool) -> None:
    list_widget.setVisible(not is_empty)
    empty_label.setVisible(is_empty)


def make_empty_hint(text: str):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QLabel

    label = QLabel(text)
    label.setObjectName("emptyHint")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setWordWrap(True)
    return label


def _in_dark_panel(widget) -> bool:
    current = widget
    while current is not None:
        if current.objectName() in {"appSidebar", "appRail", "sidePanel", "dicePanel", "mapPanel"}:
            return True
        current = current.parentWidget()
    return False


def polish_placeholders(root) -> None:
    from PySide6.QtGui import QColor, QPalette
    from PySide6.QtWidgets import QAbstractSpinBox, QComboBox, QLineEdit, QPlainTextEdit, QTextEdit, QWidget

    widgets = [root, *root.findChildren(QWidget)]
    for widget in widgets:
        if isinstance(widget, (QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QAbstractSpinBox)):
            dark = _in_dark_panel(widget)
            text = QColor(SIDE_TEXT if dark else INK)
            hint = QColor(SAGE_SOFT if dark else MUTED)
            fill = QColor(SIDE_RAISED if dark else SURFACE)
            palette = widget.palette()
            palette.setColor(QPalette.ColorRole.PlaceholderText, hint)
            palette.setColor(QPalette.ColorRole.Text, text)
            palette.setColor(QPalette.ColorRole.WindowText, text)
            palette.setColor(QPalette.ColorRole.ButtonText, text)
            palette.setColor(QPalette.ColorRole.Base, fill)
            palette.setColor(QPalette.ColorRole.Button, fill)
            widget.setPalette(palette)
    polish_buttons(root)
