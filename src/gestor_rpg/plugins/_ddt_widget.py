from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from gestor_rpg.core.plugin import SheetWidget


def _lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _spin(minimum: int, maximum: int, value: int = 0) -> QSpinBox:
    box = QSpinBox()
    box.setRange(minimum, maximum)
    box.setValue(value)
    box.setFixedWidth(90)
    return box


def _memo(placeholder: str = "Uma por linha") -> QPlainTextEdit:
    widget = QPlainTextEdit()
    widget.setPlaceholderText(placeholder)
    widget.setTabChangesFocus(True)
    return widget


class DdtSheetWidget(SheetWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        inner = QWidget()
        root = QVBoxLayout(inner)
        root.addWidget(self._victory_stats())

        extras = QFormLayout()
        extras.setHorizontalSpacing(12)
        extras.setVerticalSpacing(10)
        extras_box = QGroupBox("Identidade")
        self.arquetipo = QLineEdit()
        self.arquetipo.setPlaceholderText("Arquétipo")
        self.escala = QComboBox()
        self.escala.addItems(["Ningen", "Sugoi", "Kiodai", "Kami"])
        self.xp = _spin(0, 99999, 0)
        extras.addRow("Arquétipo", self.arquetipo)
        extras.addRow("Escala", self.escala)
        extras.addRow("Pts XP", self.xp)
        extras_box.setLayout(extras)
        root.addWidget(extras_box)

        lists = QGridLayout()
        lists.setHorizontalSpacing(10)
        lists.setVerticalSpacing(8)
        self.vantagens = _memo()
        self.desvantagens = _memo()
        self.pericias = _memo()
        self.tecnicas = _memo()
        self.inventario_comum = _memo("Itens comuns, um por linha")
        self.inventario_incomum = _memo("Itens incomuns, um por linha")
        self.inventario_raro = _memo("Itens raros, um por linha")
        lists.addWidget(QLabel("Vantagens"), 0, 0)
        lists.addWidget(self.vantagens, 1, 0)
        lists.addWidget(QLabel("Desvantagens"), 0, 1)
        lists.addWidget(self.desvantagens, 1, 1)
        lists.addWidget(QLabel("Perícias"), 2, 0)
        lists.addWidget(self.pericias, 3, 0)
        lists.addWidget(QLabel("Técnicas"), 2, 1)
        lists.addWidget(self.tecnicas, 3, 1)
        lists.addWidget(QLabel("Inventário comuns"), 4, 0)
        lists.addWidget(self.inventario_comum, 5, 0)
        lists.addWidget(QLabel("Inventário incomuns"), 4, 1)
        lists.addWidget(self.inventario_incomum, 5, 1)
        lists.addWidget(QLabel("Inventário raro"), 6, 0, 1, 2)
        lists.addWidget(self.inventario_raro, 7, 0, 1, 2)
        lists_box = QGroupBox("Ficha")
        lists_box.setLayout(lists)
        root.addWidget(lists_box, 1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(inner)
        host = QVBoxLayout(self)
        host.setContentsMargins(0, 0, 0, 0)
        host.addWidget(scroll)

    def _victory_stats(self) -> QWidget:
        box = QGroupBox("Características")
        grid = QGridLayout(box)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)
        self._stats: dict[str, QSpinBox] = {
            "poder": _spin(-5, 20, 0),
            "habilidade": _spin(-5, 20, 0),
            "resistencia": _spin(-5, 20, 0),
        }
        self.pa_atual = _spin(0, 99, 1)
        self.pa_max = _spin(0, 99, 1)
        self.pm_atual = _spin(0, 999, 0)
        self.pm_max = _spin(0, 999, 0)
        self.pv_atual = _spin(0, 999, 5)
        self.pv_max = _spin(0, 999, 5)
        rows = [
            (0, "P Poder", self._stats["poder"], "PA", self.pa_atual, self.pa_max),
            (1, "H Habilidade", self._stats["habilidade"], "PM", self.pm_atual, self.pm_max),
            (2, "R Resistência", self._stats["resistencia"], "PV", self.pv_atual, self.pv_max),
        ]
        for row, attr_label, attr_spin, pool_label, atual, maximo in rows:
            grid.addWidget(QLabel(attr_label), row, 0)
            grid.addWidget(attr_spin, row, 1)
            grid.addWidget(QLabel(pool_label), row, 2)
            atual_box = QVBoxLayout()
            atual_box.setSpacing(2)
            atual_box.addWidget(QLabel("atuais"))
            atual_box.addWidget(atual)
            max_box = QVBoxLayout()
            max_box.setSpacing(2)
            max_box.addWidget(QLabel("máx."))
            max_box.addWidget(maximo)
            grid.addLayout(atual_box, row, 3)
            grid.addLayout(max_box, row, 4)
        return box

    def get_attributes(self) -> dict:
        data = {key: int(spin.value()) for key, spin in self._stats.items()}
        data.update(
            {
                "pv_max": int(self.pv_max.value()),
                "pv_atual": int(self.pv_atual.value()),
                "pm_max": int(self.pm_max.value()),
                "pm_atual": int(self.pm_atual.value()),
                "pa_atual": int(self.pa_atual.value()),
                "pa_max": int(self.pa_max.value()),
                "vantagens": _lines(self.vantagens.toPlainText()),
                "desvantagens": _lines(self.desvantagens.toPlainText()),
                "pericias": _lines(self.pericias.toPlainText()),
                "tecnicas": _lines(self.tecnicas.toPlainText()),
                "inventario_comum": _lines(self.inventario_comum.toPlainText()),
                "inventario_incomum": _lines(self.inventario_incomum.toPlainText()),
                "inventario_raro": _lines(self.inventario_raro.toPlainText()),
                "escala": self.escala.currentText(),
                "arquetipo": self.arquetipo.text().strip(),
                "xp": int(self.xp.value()),
            }
        )
        return data

    def set_attributes(self, data: dict) -> None:
        self._stats["poder"].setValue(int(data.get("poder", data.get("forca", 0)) or 0))
        for key, spin in self._stats.items():
            if key == "poder":
                continue
            spin.setValue(int(data.get(key, 0) or 0))
        self.pv_max.setValue(int(data.get("pv_max", 5) or 0))
        self.pv_atual.setValue(int(data.get("pv_atual", data.get("pv_max", 5)) or 0))
        self.pm_max.setValue(int(data.get("pm_max", 0) or 0))
        self.pm_atual.setValue(int(data.get("pm_atual", data.get("pm_max", 0)) or 0))
        self.pa_max.setValue(int(data.get("pa_max", 1) or 0))
        self.pa_atual.setValue(int(data.get("pa_atual", data.get("pa_max", 1)) or 0))
        self.vantagens.setPlainText("\n".join(data.get("vantagens") or []))
        self.desvantagens.setPlainText("\n".join(data.get("desvantagens") or []))
        self.pericias.setPlainText("\n".join(data.get("pericias") or []))
        tecnicas = data.get("tecnicas") or data.get("poderes") or data.get("magias") or []
        self.tecnicas.setPlainText("\n".join(tecnicas))
        comuns = data.get("inventario_comum") or data.get("equipamentos") or []
        self.inventario_comum.setPlainText("\n".join(comuns))
        self.inventario_incomum.setPlainText("\n".join(data.get("inventario_incomum") or []))
        self.inventario_raro.setPlainText("\n".join(data.get("inventario_raro") or []))
        escala = str(data.get("escala") or "Ningen")
        index = self.escala.findText(escala)
        self.escala.setCurrentIndex(max(0, index))
        self.arquetipo.setText(str(data.get("arquetipo") or ""))
        self.xp.setValue(int(data.get("xp", 0) or 0))
