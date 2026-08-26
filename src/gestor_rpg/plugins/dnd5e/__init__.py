from __future__ import annotations

import random
import re
from typing import Any

from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from gestor_rpg.core.models import ParsedSheet, PdfExtract
from gestor_rpg.core.plugin import RPGSystemPlugin, SheetWidget
from gestor_rpg.plugins._dnd_bestiary import (
    BESTIARY,
    cr_float,
    filter_dnd_bestiary,
    find_dnd_bestiary,
)

SKILLS = [
    "Acrobacia",
    "Adestrar Animais",
    "Arcanismo",
    "Atletismo",
    "Atuação",
    "Enganação",
    "Furtividade",
    "História",
    "Intimidação",
    "Intuição",
    "Investigação",
    "Medicina",
    "Natureza",
    "Percepção",
    "Persuasão",
    "Prestidigitação",
    "Religião",
    "Sobrevivência",
]

SAVES = ["Força", "Destreza", "Constituição", "Inteligência", "Sabedoria", "Carisma"]

SKILL_EN = {
    "Athletics": "Atletismo",
    "Acrobatics": "Acrobacia",
    "Sleight of Hand": "Prestidigitação",
    "Stealth": "Furtividade",
    "Arcana": "Arcanismo",
    "History": "História",
    "Investigation": "Investigação",
    "Nature": "Natureza",
    "Religion": "Religião",
    "Animal Handling": "Adestrar Animais",
    "Insight": "Intuição",
    "Medicine": "Medicina",
    "Perception": "Percepção",
    "Survival": "Sobrevivência",
    "Deception": "Enganação",
    "Intimidation": "Intimidação",
    "Performance": "Atuação",
    "Persuasion": "Persuasão",
}

CLASSES = [
    "Guerreiro",
    "Mago",
    "Ladino",
    "Clérigo",
    "Patrulheiro",
    "Bárbaro",
    "Bardo",
    "Feiticeiro",
    "Bruxo",
    "Paladino",
    "Monge",
    "Druida",
]
RACES = ["Humano", "Elfo", "Anão", "Halfling", "Meio-Orc", "Tiefling"]

MOTIVATIONS = [
    "Recuperar uma relíquia da ordem a que pertenceu",
    "Proteger a aldeia natal de uma ameaça crescente",
    "Ganhar fama nas guildas da capital",
    "Desvendar um crime que a milícia ignorou",
]
HOOKS = [
    "Um nobre oferece pouso em troca de um recado perigoso",
    "Há um contrato na taverna com o nome de um dos heróis",
    "Uma ruína próxima brilha à noite desde a última lua",
    "O NPC reconhece um símbolo no equipamento do grupo",
]


def _spin(lo: int, hi: int, value: int) -> QSpinBox:
    box = QSpinBox()
    box.setRange(lo, hi)
    box.setValue(value)
    box.setFixedWidth(80)
    return box


def _lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _ability_mod(score: int) -> int:
    return (int(score) - 10) // 2


def _fmt_mod(score: int) -> str:
    value = _ability_mod(score)
    return f"{value:+d}"


def _proficiency_for_level(level: int) -> int:
    return 2 + (max(1, min(20, int(level))) - 1) // 4


def _empty_slots() -> dict:
    return {str(level): {"max": 0, "usados": 0} for level in range(1, 10)}


def _empty_weapons() -> list[dict]:
    return [{"nome": "", "bonus": "", "dano": ""} for _ in range(3)]


ABILITY_LABELS = [
    ("FOR", "str"),
    ("DES", "dex"),
    ("CON", "con"),
    ("INT", "int"),
    ("SAB", "wis"),
    ("CAR", "cha"),
]


def _signed(value: object) -> str:
    try:
        return f"{int(value):+d}"
    except (TypeError, ValueError):
        return str(value or "0")


def _ability_scores(attrs: dict[str, Any]) -> list[tuple[str, int, str]]:
    abilities = attrs.get("abilities") or {}
    rows: list[tuple[str, int, str]] = []
    for label, key in ABILITY_LABELS:
        score = int(abilities.get(key, 10) or 10)
        rows.append((label, score, _fmt_mod(score)))
    return rows


def _identity_headline(attrs: dict[str, Any]) -> str:
    bits: list[str] = []
    classe = str(attrs.get("classe") or "").strip()
    nivel = attrs.get("nivel")
    if classe and nivel not in (None, ""):
        bits.append(f"{classe} {nivel}")
    elif classe:
        bits.append(classe)
    elif nivel not in (None, ""):
        bits.append(f"Nível {nivel}")
    for key in ("arquetipo", "raca", "antecedente", "alinhamento"):
        value = str(attrs.get(key) or "").strip()
        if value:
            bits.append(value)
    return " · ".join(bits)


def _join_names(values: object) -> str:
    if not isinstance(values, list):
        return str(values or "").strip()
    return ", ".join(str(item).strip() for item in values if str(item).strip())


def _skills_line(attrs: dict[str, Any]) -> str:
    proficient = [str(name).strip() for name in (attrs.get("pericias") or []) if str(name).strip()]
    expertise = {str(name).strip() for name in (attrs.get("expertise") or []) if str(name).strip()}
    labels: list[str] = []
    seen: set[str] = set()
    for name in proficient:
        labels.append(f"{name} (expertise)" if name in expertise else name)
        seen.add(name)
    for name in expertise:
        if name not in seen:
            labels.append(f"{name} (expertise)")
    return ", ".join(labels)


def _filled_weapons(attrs: dict[str, Any]) -> list[dict[str, str]]:
    filled: list[dict[str, str]] = []
    for item in attrs.get("armas") or []:
        if isinstance(item, dict):
            nome = str(item.get("nome") or "").strip()
            bonus = str(item.get("bonus") or "").strip()
            dano = str(item.get("dano") or "").strip()
            if nome or bonus or dano:
                filled.append({"nome": nome, "bonus": bonus, "dano": dano})
            continue
        text = str(item).strip()
        if text:
            filled.append({"nome": text, "bonus": "", "dano": ""})
    return filled


def _filled_str_list(values: object) -> list[str]:
    if not isinstance(values, list):
        text = str(values or "").strip()
        return [text] if text else []
    return [str(item).strip() for item in values if str(item).strip()]


def _active_spell_slots(attrs: dict[str, Any]) -> list[tuple[int, int, int]]:
    slots = attrs.get("espacos_magia") or {}
    active: list[tuple[int, int, int]] = []
    for level in range(1, 10):
        entry = slots.get(str(level)) or slots.get(level) or {}
        if not isinstance(entry, dict):
            continue
        maximum = int(entry.get("max") or 0)
        if maximum > 0:
            active.append((level, int(entry.get("usados") or 0), maximum))
    return active


def _has_magic_block(attrs: dict[str, Any]) -> bool:
    if _active_spell_slots(attrs):
        return True
    if _filled_str_list(attrs.get("truques")) or _filled_str_list(attrs.get("magias")):
        return True
    if int(attrs.get("recurso_max") or 0) > 0:
        return True
    return bool(str(attrs.get("metamagia") or "").strip())


def _coins_line(attrs: dict[str, Any]) -> str:
    coins = [
        ("PC", attrs.get("cobre", 0)),
        ("PP", attrs.get("prata", 0)),
        ("PE", attrs.get("electro", 0)),
        ("PO", attrs.get("ouro", 0)),
        ("PL", attrs.get("platina", 0)),
    ]
    parts = [f"{label} {int(value or 0)}" for label, value in coins if int(value or 0)]
    return " · ".join(parts)


def default_dnd() -> dict:
    return {
        "nivel": 1,
        "classe": "",
        "raca": "",
        "antecedente": "",
        "alinhamento": "",
        "arquetipo": "",
        "xp": 0,
        "bonus_proficiencia": 2,
        "inspiracao": False,
        "abilities": {"str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10},
        "hp_max": 8,
        "hp_atual": 8,
        "hp_temp": 0,
        "ca": 10,
        "iniciativa": 0,
        "deslocamento": 9,
        "dados_vida": "1d8",
        "dados_vida_usados": 0,
        "mortes_sucesso": 0,
        "mortes_falha": 0,
        "percepcao_passiva": 10,
        "intuicao_passiva": 10,
        "pericias": [],
        "expertise": [],
        "salvaguardas": [],
        "armas": _empty_weapons(),
        "magia_ataque": 0,
        "magia_cd": 10,
        "recurso_nome": "Pontos de Feitiçaria",
        "recurso_atual": 0,
        "recurso_max": 0,
        "metamagia": "",
        "truques": [],
        "magias": [],
        "espacos_magia": _empty_slots(),
        "idiomas": "",
        "ferramentas": "",
        "tracos_raciais": "",
        "personalidade": "",
        "ideais": "",
        "vinculos": "",
        "falhas": "",
        "caracteristicas": "",
        "equipamentos": [],
        "cobre": 0,
        "prata": 0,
        "electro": 0,
        "ouro": 0,
        "platina": 0,
        "tracos": "",
    }


class Dnd5eSheetWidget(SheetWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        tabs = QTabWidget()
        tabs.addTab(self._tab_identity(), "Identidade")
        tabs.addTab(self._tab_combat(), "Combate")
        tabs.addTab(self._tab_skills(), "Perícias")
        tabs.addTab(self._tab_magic(), "Magia")
        tabs.addTab(self._tab_story(), "História e carga")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(tabs)
        self.nivel.valueChanged.connect(self._on_level)
        for spin in self.abilities.values():
            spin.valueChanged.connect(self._refresh_derived)
        self._refresh_derived()

    def _scroll(self, widget: QWidget) -> QScrollArea:
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(widget)
        return area

    def _tab_identity(self) -> QWidget:
        page = QWidget()
        root = QVBoxLayout(page)
        identity = QGroupBox("Personagem")
        form = QFormLayout(identity)
        self.classe = QLineEdit()
        self.classe.setPlaceholderText("Feiticeiro, guerreiro…")
        self.arquetipo = QLineEdit()
        self.arquetipo.setPlaceholderText("Origem / arquétipo / subclasse")
        self.raca = QLineEdit()
        self.antecedente = QLineEdit()
        self.alinhamento = QLineEdit()
        self.nivel = _spin(1, 20, 1)
        self.xp = _spin(0, 999999, 0)
        self.bonus_proficiencia = _spin(2, 6, 2)
        self.inspiracao = QCheckBox("Inspiração")
        form.addRow("Classe", self.classe)
        form.addRow("Arquétipo", self.arquetipo)
        form.addRow("Raça", self.raca)
        form.addRow("Antecedente", self.antecedente)
        form.addRow("Alinhamento", self.alinhamento)
        form.addRow("Nível", self.nivel)
        form.addRow("XP", self.xp)
        form.addRow("Bônus de proficiência", self.bonus_proficiencia)
        form.addRow(self.inspiracao)
        root.addWidget(identity)

        abilities = QGroupBox("Atributos")
        grid = QGridLayout(abilities)
        self.abilities: dict[str, QSpinBox] = {}
        self.ability_mods: dict[str, QLabel] = {}
        labels = [
            ("FOR", "str"),
            ("DES", "dex"),
            ("CON", "con"),
            ("INT", "int"),
            ("SAB", "wis"),
            ("CAR", "cha"),
        ]
        for col, (title, key) in enumerate(labels):
            grid.addWidget(QLabel(title), 0, col)
            spin = _spin(1, 30, 10)
            self.abilities[key] = spin
            grid.addWidget(spin, 1, col)
            mod = QLabel("+0")
            mod.setAlignment(spin.alignment())
            self.ability_mods[key] = mod
            grid.addWidget(mod, 2, col)
        root.addWidget(abilities)
        root.addStretch()
        return self._scroll(page)

    def _tab_combat(self) -> QWidget:
        page = QWidget()
        root = QVBoxLayout(page)
        combat = QGroupBox("Combate")
        combat_l = QGridLayout(combat)
        self.hp_atual = _spin(0, 999, 8)
        self.hp_max = _spin(0, 999, 8)
        self.hp_temp = _spin(0, 999, 0)
        self.ca = _spin(0, 40, 10)
        self.iniciativa = _spin(-10, 20, 0)
        self.deslocamento = _spin(0, 50, 9)
        fields = [
            (0, 0, "HP atual", self.hp_atual),
            (0, 1, "HP máx.", self.hp_max),
            (0, 2, "HP temp.", self.hp_temp),
            (1, 0, "CA", self.ca),
            (1, 1, "Iniciativa", self.iniciativa),
            (1, 2, "Desloc. (m)", self.deslocamento),
        ]
        for row, col, caption, widget in fields:
            box = QVBoxLayout()
            box.addWidget(QLabel(caption))
            box.addWidget(widget)
            combat_l.addLayout(box, row, col)
        root.addWidget(combat)

        dice = QGroupBox("Dados de vida e mortes")
        dice_l = QFormLayout(dice)
        self.dados_vida = QLineEdit()
        self.dados_vida.setPlaceholderText("1d6, 1d8, 1d10…")
        self.dados_vida_usados = _spin(0, 20, 0)
        self.mortes_sucesso = _spin(0, 3, 0)
        self.mortes_falha = _spin(0, 3, 0)
        dice_l.addRow("Dados de vida", self.dados_vida)
        dice_l.addRow("Usados", self.dados_vida_usados)
        dice_l.addRow("Sucessos contra a morte", self.mortes_sucesso)
        dice_l.addRow("Falhas contra a morte", self.mortes_falha)
        root.addWidget(dice)

        weapons = QGroupBox("Armas e ataques")
        wgrid = QGridLayout(weapons)
        wgrid.addWidget(QLabel("Nome"), 0, 0)
        wgrid.addWidget(QLabel("Bônus"), 0, 1)
        wgrid.addWidget(QLabel("Dano"), 0, 2)
        self.weapon_name: list[QLineEdit] = []
        self.weapon_bonus: list[QLineEdit] = []
        self.weapon_damage: list[QLineEdit] = []
        for row in range(3):
            name = QLineEdit()
            bonus = QLineEdit()
            damage = QLineEdit()
            self.weapon_name.append(name)
            self.weapon_bonus.append(bonus)
            self.weapon_damage.append(damage)
            wgrid.addWidget(name, row + 1, 0)
            wgrid.addWidget(bonus, row + 1, 1)
            wgrid.addWidget(damage, row + 1, 2)
        root.addWidget(weapons)
        root.addStretch()
        return self._scroll(page)

    def _tab_skills(self) -> QWidget:
        page = QWidget()
        root = QVBoxLayout(page)
        skills_box = QGroupBox("Perícias (proficiência e expertise)")
        skills_grid = QGridLayout(skills_box)
        self.skill_boxes: dict[str, QCheckBox] = {}
        self.expertise_boxes: dict[str, QCheckBox] = {}
        for i, name in enumerate(SKILLS):
            prof = QCheckBox("P")
            exp = QCheckBox("E")
            self.skill_boxes[name] = prof
            self.expertise_boxes[name] = exp
            cell = QHBoxLayout()
            cell.addWidget(QLabel(name), 1)
            cell.addWidget(prof)
            cell.addWidget(exp)
            host = QWidget()
            host.setLayout(cell)
            skills_grid.addWidget(host, i // 2, i % 2)
        root.addWidget(skills_box)

        saves_box = QGroupBox("Salvaguardas")
        saves_l = QHBoxLayout(saves_box)
        self.save_boxes: dict[str, QCheckBox] = {}
        for name in SAVES:
            box = QCheckBox(name)
            self.save_boxes[name] = box
            saves_l.addWidget(box)
        root.addWidget(saves_box)

        passive = QGroupBox("Passivos")
        passive_l = QFormLayout(passive)
        self.percepcao_passiva = _spin(0, 40, 10)
        self.intuicao_passiva = _spin(0, 40, 10)
        passive_l.addRow("Percepção passiva", self.percepcao_passiva)
        passive_l.addRow("Intuição passiva", self.intuicao_passiva)
        root.addWidget(passive)
        root.addStretch()
        return self._scroll(page)

    def _tab_magic(self) -> QWidget:
        page = QWidget()
        root = QVBoxLayout(page)
        stats = QGroupBox("Conjuração")
        form = QFormLayout(stats)
        self.magia_ataque = _spin(-5, 20, 0)
        self.magia_cd = _spin(0, 30, 10)
        self.recurso_nome = QLineEdit()
        self.recurso_nome.setPlaceholderText("Pontos de Feitiçaria, ki, raiva…")
        self.recurso_atual = _spin(0, 99, 0)
        self.recurso_max = _spin(0, 99, 0)
        self.metamagia = QPlainTextEdit()
        self.metamagia.setMaximumHeight(70)
        form.addRow("Ataque mágico", self.magia_ataque)
        form.addRow("CD de magia", self.magia_cd)
        form.addRow("Recurso de classe", self.recurso_nome)
        form.addRow("Recurso atual", self.recurso_atual)
        form.addRow("Recurso máx.", self.recurso_max)
        form.addRow("Metamagia / opções", self.metamagia)
        root.addWidget(stats)

        slots = QGroupBox("Espaços de magia")
        slot_grid = QGridLayout(slots)
        slot_grid.addWidget(QLabel("Nível"), 0, 0)
        slot_grid.addWidget(QLabel("Máx."), 0, 1)
        slot_grid.addWidget(QLabel("Usados"), 0, 2)
        self.slot_max: dict[str, QSpinBox] = {}
        self.slot_used: dict[str, QSpinBox] = {}
        for i, level in enumerate(range(1, 10), start=1):
            key = str(level)
            slot_grid.addWidget(QLabel(f"{level}º"), i, 0)
            mx = _spin(0, 9, 0)
            used = _spin(0, 9, 0)
            self.slot_max[key] = mx
            self.slot_used[key] = used
            slot_grid.addWidget(mx, i, 1)
            slot_grid.addWidget(used, i, 2)
        root.addWidget(slots)

        self.truques = QPlainTextEdit()
        self.magias = QPlainTextEdit()
        self.truques.setPlaceholderText("Truques conhecidos, um por linha")
        self.magias.setPlaceholderText("Magias conhecidas, um por linha")
        for widget, title in ((self.truques, "Truques"), (self.magias, "Magias")):
            box = QGroupBox(title)
            lay = QVBoxLayout(box)
            lay.addWidget(widget)
            root.addWidget(box, 1)
        return self._scroll(page)

    def _tab_story(self) -> QWidget:
        page = QWidget()
        root = QVBoxLayout(page)
        self.tracos_raciais = QPlainTextEdit()
        self.personalidade = QPlainTextEdit()
        self.ideais = QPlainTextEdit()
        self.vinculos = QPlainTextEdit()
        self.falhas = QPlainTextEdit()
        self.caracteristicas = QPlainTextEdit()
        self.tracos = QPlainTextEdit()
        self.idiomas = QLineEdit()
        self.ferramentas = QLineEdit()
        for widget, title in (
            (self.tracos_raciais, "Traços raciais"),
            (self.personalidade, "Traços de personalidade"),
            (self.ideais, "Ideais"),
            (self.vinculos, "Vínculos"),
            (self.falhas, "Defeitos"),
            (self.caracteristicas, "Características e talentos"),
            (self.tracos, "Anotações"),
        ):
            widget.setMaximumHeight(80)
            box = QGroupBox(title)
            lay = QVBoxLayout(box)
            lay.addWidget(widget)
            root.addWidget(box)

        extra = QFormLayout()
        extra.addRow("Idiomas", self.idiomas)
        extra.addRow("Ferramentas", self.ferramentas)
        extra_box = QGroupBox("Proficiências")
        extra_box.setLayout(extra)
        root.addWidget(extra_box)

        coins = QGroupBox("Moedas")
        coins_l = QHBoxLayout(coins)
        self.cobre = _spin(0, 99999, 0)
        self.prata = _spin(0, 99999, 0)
        self.electro = _spin(0, 99999, 0)
        self.ouro = _spin(0, 99999, 0)
        self.platina = _spin(0, 99999, 0)
        for caption, widget in (
            ("PC", self.cobre),
            ("PP", self.prata),
            ("PE", self.electro),
            ("PO", self.ouro),
            ("PL", self.platina),
        ):
            col = QVBoxLayout()
            col.addWidget(QLabel(caption))
            col.addWidget(widget)
            coins_l.addLayout(col)
        root.addWidget(coins)

        self.equipamentos = QPlainTextEdit()
        self.equipamentos.setPlaceholderText("Uma por linha")
        gear = QGroupBox("Equipamento e mochila")
        gear_l = QVBoxLayout(gear)
        gear_l.addWidget(self.equipamentos)
        root.addWidget(gear, 1)
        return self._scroll(page)

    def _on_level(self, value: int) -> None:
        self.bonus_proficiencia.setValue(_proficiency_for_level(value))
        self._refresh_derived()

    def _refresh_derived(self) -> None:
        for key, spin in self.abilities.items():
            self.ability_mods[key].setText(_fmt_mod(spin.value()))

    def get_attributes(self) -> dict:
        armas = []
        for name, bonus, damage in zip(self.weapon_name, self.weapon_bonus, self.weapon_damage):
            armas.append(
                {
                    "nome": name.text().strip(),
                    "bonus": bonus.text().strip(),
                    "dano": damage.text().strip(),
                }
            )
        slots = {}
        for level, mx in self.slot_max.items():
            slots[level] = {
                "max": int(mx.value()),
                "usados": int(self.slot_used[level].value()),
            }
        return {
            "nivel": int(self.nivel.value()),
            "classe": self.classe.text().strip(),
            "raca": self.raca.text().strip(),
            "antecedente": self.antecedente.text().strip(),
            "alinhamento": self.alinhamento.text().strip(),
            "arquetipo": self.arquetipo.text().strip(),
            "xp": int(self.xp.value()),
            "bonus_proficiencia": int(self.bonus_proficiencia.value()),
            "inspiracao": self.inspiracao.isChecked(),
            "abilities": {k: int(s.value()) for k, s in self.abilities.items()},
            "hp_max": int(self.hp_max.value()),
            "hp_atual": int(self.hp_atual.value()),
            "hp_temp": int(self.hp_temp.value()),
            "ca": int(self.ca.value()),
            "iniciativa": int(self.iniciativa.value()),
            "deslocamento": int(self.deslocamento.value()),
            "dados_vida": self.dados_vida.text().strip(),
            "dados_vida_usados": int(self.dados_vida_usados.value()),
            "mortes_sucesso": int(self.mortes_sucesso.value()),
            "mortes_falha": int(self.mortes_falha.value()),
            "percepcao_passiva": int(self.percepcao_passiva.value()),
            "intuicao_passiva": int(self.intuicao_passiva.value()),
            "pericias": [n for n, b in self.skill_boxes.items() if b.isChecked()],
            "expertise": [n for n, b in self.expertise_boxes.items() if b.isChecked()],
            "salvaguardas": [n for n, b in self.save_boxes.items() if b.isChecked()],
            "armas": armas,
            "magia_ataque": int(self.magia_ataque.value()),
            "magia_cd": int(self.magia_cd.value()),
            "recurso_nome": self.recurso_nome.text().strip() or "Pontos de Feitiçaria",
            "recurso_atual": int(self.recurso_atual.value()),
            "recurso_max": int(self.recurso_max.value()),
            "metamagia": self.metamagia.toPlainText().strip(),
            "truques": _lines(self.truques.toPlainText()),
            "magias": _lines(self.magias.toPlainText()),
            "espacos_magia": slots,
            "idiomas": self.idiomas.text().strip(),
            "ferramentas": self.ferramentas.text().strip(),
            "tracos_raciais": self.tracos_raciais.toPlainText().strip(),
            "personalidade": self.personalidade.toPlainText().strip(),
            "ideais": self.ideais.toPlainText().strip(),
            "vinculos": self.vinculos.toPlainText().strip(),
            "falhas": self.falhas.toPlainText().strip(),
            "caracteristicas": self.caracteristicas.toPlainText().strip(),
            "equipamentos": _lines(self.equipamentos.toPlainText()),
            "cobre": int(self.cobre.value()),
            "prata": int(self.prata.value()),
            "electro": int(self.electro.value()),
            "ouro": int(self.ouro.value()),
            "platina": int(self.platina.value()),
            "tracos": self.tracos.toPlainText().strip(),
        }

    def set_attributes(self, data: dict) -> None:
        self.nivel.blockSignals(True)
        self.nivel.setValue(int(data.get("nivel", 1) or 1))
        self.nivel.blockSignals(False)
        self.classe.setText(str(data.get("classe") or ""))
        self.arquetipo.setText(str(data.get("arquetipo") or data.get("arquétipo") or ""))
        self.raca.setText(str(data.get("raca") or ""))
        self.antecedente.setText(str(data.get("antecedente") or ""))
        self.alinhamento.setText(str(data.get("alinhamento") or ""))
        self.xp.setValue(int(data.get("xp", 0) or 0))
        self.bonus_proficiencia.setValue(
            int(data.get("bonus_proficiencia") or _proficiency_for_level(self.nivel.value()))
        )
        self.inspiracao.setChecked(bool(data.get("inspiracao")))
        abilities = data.get("abilities") or {}
        for key, spin in self.abilities.items():
            spin.blockSignals(True)
            spin.setValue(int(abilities.get(key, 10) or 10))
            spin.blockSignals(False)
        self.hp_max.setValue(int(data.get("hp_max", 8) or 0))
        self.hp_atual.setValue(int(data.get("hp_atual", data.get("hp_max", 8)) or 0))
        self.hp_temp.setValue(int(data.get("hp_temp", 0) or 0))
        self.ca.setValue(int(data.get("ca", 10) or 10))
        self.iniciativa.setValue(int(data.get("iniciativa", 0) or 0))
        self.deslocamento.setValue(int(data.get("deslocamento", 9) or 9))
        self.dados_vida.setText(str(data.get("dados_vida") or ""))
        self.dados_vida_usados.setValue(int(data.get("dados_vida_usados", 0) or 0))
        self.mortes_sucesso.setValue(int(data.get("mortes_sucesso", 0) or 0))
        self.mortes_falha.setValue(int(data.get("mortes_falha", 0) or 0))
        self.percepcao_passiva.setValue(int(data.get("percepcao_passiva", 10) or 10))
        self.intuicao_passiva.setValue(int(data.get("intuicao_passiva", 10) or 10))
        selected_skills = set(data.get("pericias") or [])
        selected_exp = set(data.get("expertise") or [])
        for name, box in self.skill_boxes.items():
            box.setChecked(name in selected_skills)
        for name, box in self.expertise_boxes.items():
            box.setChecked(name in selected_exp)
        selected_saves = set(data.get("salvaguardas") or [])
        for name, box in self.save_boxes.items():
            box.setChecked(name in selected_saves)
        armas = list(data.get("armas") or [])
        while len(armas) < 3:
            armas.append({"nome": "", "bonus": "", "dano": ""})
        for i in range(3):
            item = armas[i] if isinstance(armas[i], dict) else {}
            self.weapon_name[i].setText(str(item.get("nome") or ""))
            self.weapon_bonus[i].setText(str(item.get("bonus") or ""))
            self.weapon_damage[i].setText(str(item.get("dano") or ""))
        self.magia_ataque.setValue(int(data.get("magia_ataque", 0) or 0))
        self.magia_cd.setValue(int(data.get("magia_cd", 10) or 10))
        self.recurso_nome.setText(str(data.get("recurso_nome") or "Pontos de Feitiçaria"))
        self.recurso_atual.setValue(int(data.get("recurso_atual", 0) or 0))
        self.recurso_max.setValue(int(data.get("recurso_max", 0) or 0))
        self.metamagia.setPlainText(str(data.get("metamagia") or ""))
        self.truques.setPlainText("\n".join(data.get("truques") or []))
        self.magias.setPlainText("\n".join(data.get("magias") or []))
        slots = data.get("espacos_magia") or {}
        for level in self.slot_max:
            entry = slots.get(level) or slots.get(int(level)) or {}
            if not isinstance(entry, dict):
                entry = {}
            self.slot_max[level].setValue(int(entry.get("max", 0) or 0))
            self.slot_used[level].setValue(int(entry.get("usados", 0) or 0))
        self.idiomas.setText(str(data.get("idiomas") or ""))
        self.ferramentas.setText(str(data.get("ferramentas") or ""))
        self.tracos_raciais.setPlainText(str(data.get("tracos_raciais") or ""))
        self.personalidade.setPlainText(str(data.get("personalidade") or ""))
        self.ideais.setPlainText(str(data.get("ideais") or ""))
        self.vinculos.setPlainText(str(data.get("vinculos") or ""))
        self.falhas.setPlainText(str(data.get("falhas") or ""))
        self.caracteristicas.setPlainText(str(data.get("caracteristicas") or ""))
        self.equipamentos.setPlainText("\n".join(data.get("equipamentos") or []))
        self.cobre.setValue(int(data.get("cobre", 0) or 0))
        self.prata.setValue(int(data.get("prata", 0) or 0))
        self.electro.setValue(int(data.get("electro", 0) or 0))
        self.ouro.setValue(int(data.get("ouro", 0) or 0))
        self.platina.setValue(int(data.get("platina", 0) or 0))
        self.tracos.setPlainText(str(data.get("tracos") or ""))
        self._refresh_derived()


def _roll_ability(rng: random.Random) -> int:
    rolls = sorted(rng.randint(1, 6) for _ in range(4))
    return sum(rolls[1:])


def generate_dnd_npc(params: dict[str, Any] | None = None) -> dict:
    params = params or {}
    rng = params.get("rng") or random.Random()
    power = str(params.get("power") or "medio")
    level = {"fraco": 1, "medio": 3, "forte": 8}.get(power, 3)
    attrs = default_dnd()
    attrs["nivel"] = level
    attrs["classe"] = rng.choice(CLASSES)
    attrs["raca"] = rng.choice(RACES)
    attrs["abilities"] = {
        k: _roll_ability(rng) for k in ("str", "dex", "con", "int", "wis", "cha")
    }
    con_mod = (attrs["abilities"]["con"] - 10) // 2
    attrs["hp_max"] = max(4, 8 + con_mod * level)
    attrs["hp_atual"] = attrs["hp_max"]
    attrs["ca"] = 10 + (attrs["abilities"]["dex"] - 10) // 2
    attrs["iniciativa"] = (attrs["abilities"]["dex"] - 10) // 2
    attrs["bonus_proficiencia"] = _proficiency_for_level(level)
    attrs["percepcao_passiva"] = 10 + (attrs["abilities"]["wis"] - 10) // 2
    attrs["intuicao_passiva"] = attrs["percepcao_passiva"]
    attrs["pericias"] = rng.sample(SKILLS, k=2)
    attrs["salvaguardas"] = rng.sample(SAVES, k=2)
    if attrs["classe"] == "Feiticeiro":
        attrs["recurso_nome"] = "Pontos de Feitiçaria"
        attrs["recurso_max"] = level
        attrs["recurso_atual"] = level
        attrs["salvaguardas"] = ["Constituição", "Carisma"]
        attrs["dados_vida"] = f"{level}d6"
    return {
        "attributes": attrs,
        "motivation": rng.choice(MOTIVATIONS),
        "story_hook": rng.choice(HOOKS),
    }


DND_HP_PATHS: dict[str, tuple[str, str]] = {
    "hp": ("hp_atual", "hp_max"),
    "resource": ("recurso_atual", "recurso_max"),
}

def _proficiency_for_cr(cr: str) -> int:
    value = cr_float(cr)
    if value <= 4:
        return 2
    if value <= 8:
        return 3
    if value <= 12:
        return 4
    if value <= 16:
        return 5
    if value <= 20:
        return 6
    if value <= 24:
        return 7
    if value <= 28:
        return 8
    return 9


def _resolve_dnd_level(params: dict[str, Any]) -> tuple[str, int]:
    raw = params.get("level")
    if raw is None:
        raw = params.get("challenge")
    if raw is not None:
        try:
            level = max(0, int(raw))
        except (TypeError, ValueError):
            level = 3
        power = "fraco" if level <= 2 else "forte" if level >= 8 else "medio"
        return power, max(1, level)
    power = str(params.get("power") or "medio")
    level = {"fraco": 1, "medio": 3, "forte": 8, "lendario": 12}.get(power, 3)
    if power not in {"fraco", "medio", "forte", "lendario", "todos"}:
        power = "medio"
    return power, level


def catalog_entry_to_monster(entry: dict[str, Any]) -> dict:
    attrs = default_dnd()
    abilities = dict(entry.get("abilities") or attrs["abilities"])
    cr = str(entry.get("cr") or "0")
    hp = int(entry.get("hp") or 1)
    dex = int(abilities.get("dex") or 10)
    armas = entry.get("armas") or _empty_weapons()
    poderes = list(entry.get("poderes") or [])
    speed_text = str(entry.get("speed_text") or "").strip()
    if speed_text:
        poderes.insert(0, f"Deslocamento: {speed_text}")
    attrs.update(
        {
            "nivel": max(1, min(20, round(cr_float(cr)) or 1)),
            "classe": str(entry.get("tipo") or ""),
            "raca": str(entry.get("size") or ""),
            "alinhamento": str(entry.get("alinhamento") or ""),
            "xp": int(entry.get("points") or 0),
            "bonus_proficiencia": _proficiency_for_cr(cr),
            "abilities": abilities,
            "hp_max": hp,
            "hp_atual": hp,
            "ca": int(entry.get("ca") or 10),
            "iniciativa": (dex - 10) // 2,
            "deslocamento": int(entry.get("speed") or 9),
            "dados_vida": str(entry.get("hit_dice") or ""),
            "percepcao_passiva": int(entry.get("passive") or (10 + (int(abilities.get("wis") or 10) - 10) // 2)),
            "pericias": list(entry.get("pericias") or []),
            "armas": armas,
            "idiomas": str(entry.get("idiomas") or ""),
            "caracteristicas": "\n".join(poderes),
            "tracos": "\n".join(poderes),
        }
    )
    notes = [
        f"{entry.get('tipo') or 'Criatura'} · ND {cr} · {entry.get('points', 0)} XP · {entry.get('origem') or '—'}.",
        *poderes,
    ]
    return {
        "name": str(entry.get("name") or "Criatura"),
        "attributes": attrs,
        "challenge": cr,
        "notes": "\n".join(notes),
        "slug": entry.get("slug"),
    }


def generate_dnd_monster(params: dict[str, Any] | None = None) -> dict:
    params = params or {}
    rng = params.get("rng") or random.Random()
    named = str(params.get("name") or params.get("slug") or "").strip()
    if named:
        found = find_dnd_bestiary(named)
        if found is not None:
            return catalog_entry_to_monster(found)
    power = str(params.get("power") or "").strip()
    if params.get("level") is not None and not named:
        power, _level = _resolve_dnd_level(params)
    filtered = filter_dnd_bestiary(
        power=power or None,
        category=params.get("category"),
        escala=params.get("escala"),
        query=params.get("query"),
    )
    if not filtered:
        filtered = filter_dnd_bestiary(
            category=params.get("category"),
            escala=params.get("escala"),
            query=params.get("query"),
        )
    if not filtered:
        filtered = filter_dnd_bestiary()
    return catalog_entry_to_monster(rng.choice(filtered))


def format_dnd_sheet_html(payload: dict[str, Any]) -> str:
    from gestor_rpg.modules.sheet_export.html import (
        esc,
        kv_table,
        list_html,
        section,
        stats_table,
        wrap_sheet,
    )

    attrs = payload.get("attributes") or {}
    ability_rows = _ability_scores(attrs)
    ability_values = [f"{score} ({mod})" for _label, score, mod in ability_rows]
    combat_extra = [
        ("Bônus de proficiência", f"+{attrs.get('bonus_proficiencia', 2)}"),
        ("Percepção passiva", attrs.get("percepcao_passiva", 10)),
        ("Intuição passiva", attrs.get("intuicao_passiva", 10)),
    ]
    if int(attrs.get("hp_temp") or 0):
        combat_extra.append(("HP temporário", attrs.get("hp_temp")))
    if int(attrs.get("dados_vida_usados") or 0):
        combat_extra.append(("Dados de vida usados", attrs.get("dados_vida_usados")))
    if int(attrs.get("mortes_sucesso") or 0) or int(attrs.get("mortes_falha") or 0):
        combat_extra.append(
            (
                "Testes contra a morte",
                f"{attrs.get('mortes_sucesso', 0)} sucesso(s) · {attrs.get('mortes_falha', 0)} falha(s)",
            )
        )
    if int(attrs.get("xp") or 0):
        combat_extra.append(("XP", attrs.get("xp")))
    if attrs.get("inspiracao"):
        combat_extra.append(("Inspiração", "sim"))

    dados = str(attrs.get("dados_vida") or "").strip() or "—"
    parts = []
    headline = _identity_headline(attrs)
    if headline:
        parts.append(f"<p class='headline'>{esc(headline)}</p>")
    parts.append(
        section("Atributos", stats_table([label for label, _score, _mod in ability_rows], ability_values))
    )
    parts.append(
        section(
            "Combate",
            stats_table(
                ["CA", "HP", "Iniciativa", "Desloc.", "Dados de vida"],
                [
                    attrs.get("ca", 10),
                    f"{attrs.get('hp_atual', 0)}/{attrs.get('hp_max', 0)}",
                    _signed(attrs.get("iniciativa", 0)),
                    f"{attrs.get('deslocamento', 9)} m",
                    dados,
                ],
            )
            + kv_table(combat_extra),
        )
    )
    parts.append(section("Salvaguardas", f"<p>{esc(_join_names(attrs.get('salvaguardas')))}</p>"))
    parts.append(section("Perícias", f"<p>{esc(_skills_line(attrs))}</p>"))

    weapons = _filled_weapons(attrs)
    if weapons:
        weapon_rows = "".join(
            "<tr>"
            f"<td>{esc(item['nome'])}</td>"
            f"<td>{esc(item['bonus'])}</td>"
            f"<td>{esc(item['dano'])}</td>"
            "</tr>"
            for item in weapons
        )
        parts.append(
            section(
                "Armas",
                "<table class='list'><tr><th>Arma</th><th>Bônus</th><th>Dano</th></tr>"
                + weapon_rows
                + "</table>",
            )
        )

    if _has_magic_block(attrs):
        magic_rows: list[tuple[str, object]] = [
            ("Ataque mágico", _signed(attrs.get("magia_ataque", 0))),
            ("CD de magia", attrs.get("magia_cd", 10)),
        ]
        if int(attrs.get("recurso_max") or 0):
            magic_rows.append(
                (
                    str(attrs.get("recurso_nome") or "Recurso").strip() or "Recurso",
                    f"{attrs.get('recurso_atual', 0)}/{attrs.get('recurso_max', 0)}",
                )
            )
        if str(attrs.get("metamagia") or "").strip():
            magic_rows.append(("Metamagia", attrs.get("metamagia")))
        magic_html = kv_table(magic_rows)
        slots = _active_spell_slots(attrs)
        if slots:
            magic_html += stats_table(
                [f"{level}º" for level, _used, _maximum in slots],
                [f"{used}/{maximum}" for _level, used, maximum in slots],
            )
        truques = _filled_str_list(attrs.get("truques"))
        magias = _filled_str_list(attrs.get("magias"))
        if truques:
            magic_html += "<p><b>Truques</b></p>" + list_html(truques)
        if magias:
            magic_html += "<p><b>Magias</b></p>" + list_html(magias)
        parts.append(section("Magia", magic_html))

    story_rows = [
        ("Idiomas", attrs.get("idiomas") or ""),
        ("Ferramentas", attrs.get("ferramentas") or ""),
        ("Traços raciais", attrs.get("tracos_raciais") or ""),
        ("Personalidade", attrs.get("personalidade") or ""),
        ("Ideais", attrs.get("ideais") or ""),
        ("Vínculos", attrs.get("vinculos") or ""),
        ("Falhas", attrs.get("falhas") or ""),
        ("Características", attrs.get("caracteristicas") or ""),
        ("Anotações", attrs.get("tracos") or ""),
        ("Moedas", _coins_line(attrs)),
    ]
    story_html = kv_table(story_rows, skip_empty=True)
    equipamentos = _filled_str_list(attrs.get("equipamentos"))
    if story_html != "<p class='empty'>—</p>" or equipamentos:
        if story_html == "<p class='empty'>—</p>":
            story_html = ""
        if equipamentos:
            story_html += "<p><b>Equipamento</b></p>" + list_html(equipamentos)
        parts.append(section("História e carga", story_html))
    return wrap_sheet(payload, "".join(parts))


def format_dnd_monster_preview(payload: dict[str, Any]) -> str:
    attrs = payload.get("attributes") or {}
    header = str(payload.get("notes") or "").split("\n", 1)[0].strip()
    lines = [str(payload.get("name") or "Criatura")]
    if header:
        lines.append(header)
    lines.extend(
        [
            "",
            f"CA {attrs.get('ca', 10)}   HP {attrs.get('hp_atual', 0)}/{attrs.get('hp_max', 0)}   "
            f"Desloc. {attrs.get('deslocamento', 9)} m   Inic. {_signed(attrs.get('iniciativa', 0))}",
            "  ".join(f"{label} {score} ({mod})" for label, score, mod in _ability_scores(attrs)),
        ]
    )
    headline = _identity_headline(attrs)
    if headline:
        lines.append(headline)
    challenge = payload.get("challenge")
    if challenge not in (None, "") and str(challenge) not in headline:
        lines.append(f"ND {challenge}")
    saves = _join_names(attrs.get("salvaguardas"))
    if saves:
        lines.append(f"Salvaguardas: {saves}")
    skills = _skills_line(attrs)
    if skills:
        lines.append(f"Perícias: {skills}")
    weapons = _filled_weapons(attrs)
    if weapons:
        attacks = []
        for item in weapons:
            attacks.append(
                " ".join(part for part in (item["nome"], item["bonus"], item["dano"]) if part)
            )
        lines.append("Ataques: " + "; ".join(attacks))
    if _has_magic_block(attrs):
        slots = ", ".join(
            f"{level}º {used}/{maximum}" for level, used, maximum in _active_spell_slots(attrs)
        )
        if slots:
            lines.append(f"Espaços de magia: {slots}")
        truques = _join_names(_filled_str_list(attrs.get("truques")))
        magias = _join_names(_filled_str_list(attrs.get("magias")))
        if truques:
            lines.append(f"Truques: {truques}")
        if magias:
            lines.append(f"Magias: {magias}")
    traits = str(attrs.get("caracteristicas") or attrs.get("tracos") or "").strip()
    if traits:
        lines.extend(["", "Traços e ações:", traits])
    return "\n".join(lines)


def dnd_initiative_bonus(attributes: dict) -> int:
    abilities = attributes.get("abilities") or {}
    dex = int(abilities.get("dex") or 10)
    return (dex - 10) // 2


def _find_int(text: str, patterns: list[str]) -> int | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                continue
    return None


def parse_dnd_sheet(extracted: PdfExtract) -> ParsedSheet | None:
    text = extracted.full_text
    if not text.strip():
        return None
    attrs = default_dnd()
    abilities = attrs["abilities"]
    mapping = {
        "str": [r"(?:for[cç]a|strength|str)\s*[:\-]\s*(\d+)"],
        "dex": [r"(?:destreza|dexterity|dex)\s*[:\-]\s*(\d+)"],
        "con": [r"(?:constitui[cç][aã]o|constitution|con)\s*[:\-]\s*(\d+)"],
        "int": [r"(?:intelig[eê]ncia|intelligence)\s*[:\-]\s*(\d+)"],
        "wis": [r"(?:sabedoria|wisdom|wis)\s*[:\-]\s*(\d+)"],
        "cha": [r"(?:carisma|charisma|cha)\s*[:\-]\s*(\d+)"],
    }
    found = 0
    for key, patterns in mapping.items():
        value = _find_int(text, patterns)
        if value is not None:
            abilities[key] = value
            found += 1
    hp = _find_int(text, [r"(?:pontos?\s+de\s+vida|hit\s*points?|hp)\s*[:\-]\s*(\d+)"])
    ac = _find_int(text, [r"(?:classe\s+de\s+armadura|armor\s+class|ca|ac)\s*[:\-]\s*(\d+)"])
    nivel = _find_int(text, [r"(?:n[ií]vel|level)\s*[:\-]\s*(\d+)"])
    if hp is not None:
        attrs["hp_max"] = hp
        attrs["hp_atual"] = hp
        found += 1
    if ac is not None:
        attrs["ca"] = ac
        found += 1
    if nivel is not None:
        attrs["nivel"] = nivel
        attrs["bonus_proficiencia"] = _proficiency_for_level(nivel)
    xp = _find_int(text, [r"\bxp\s*[:\-]\s*(\d+)"])
    if xp is not None:
        attrs["xp"] = xp
    init = _find_int(text, [r"iniciativa\s*[:\-]\s*(-?\d+)", r"initiative\s*[:\-]\s*(-?\d+)"])
    if init is not None:
        attrs["iniciativa"] = init
    spell_atk = _find_int(text, [r"spell\s*attack\s*[:\-]\s*(-?\d+)", r"ataque\s*m[aá]gico\s*[:\-]\s*(-?\d+)"])
    if spell_atk is not None:
        attrs["magia_ataque"] = spell_atk
        found += 1
    spell_dc = _find_int(text, [r"spell\s*dc\s*[:\-]\s*(\d+)", r"cd\s*de\s*magia\s*[:\-]\s*(\d+)"])
    if spell_dc is not None:
        attrs["magia_cd"] = spell_dc
    sorcery = _find_int(text, [r"sorcery\s*points\s*[:\-]\s*(\d+)", r"pontos?\s+de\s+feiti[cç]aria\s*[:\-]\s*(\d+)"])
    if sorcery is not None:
        attrs["recurso_nome"] = "Pontos de Feitiçaria"
        attrs["recurso_max"] = sorcery
        attrs["recurso_atual"] = sorcery
        found += 1
    if found < 3:
        return None
    name_match = re.search(
        r"(?:nome|name|character)\s*[:\-]\s*([A-Za-zÀ-ÿ0-9 '\-]{2,40})",
        text,
        re.IGNORECASE,
    )
    class_match = re.search(r"(?:classe|class)\s*[:\-]\s*([A-Za-zÀ-ÿ \-]{2,30})", text, re.I)
    race_match = re.search(r"(?:ra[cç]a|race)\s*[:\-]\s*([A-Za-zÀ-ÿ \-]{2,30})", text, re.I)
    arch_match = re.search(r"(?:arqu[eé]tipo|archetype|origem)\s*[:\-]\s*([A-Za-zÀ-ÿ \-]{2,40})", text, re.I)
    bg_match = re.search(r"(?:antecedente|background)\s*[:\-]\s*([A-Za-zÀ-ÿ \-]{2,40})", text, re.I)
    align_match = re.search(r"(?:alinhamento|alignment)\s*[:\-]\s*([A-Za-zÀ-ÿ \-]{2,30})", text, re.I)
    if class_match:
        attrs["classe"] = class_match.group(1).splitlines()[0].strip()
    if race_match:
        attrs["raca"] = race_match.group(1).splitlines()[0].strip()
    if arch_match:
        attrs["arquetipo"] = arch_match.group(1).splitlines()[0].strip()
    if bg_match:
        attrs["antecedente"] = bg_match.group(1).splitlines()[0].strip()
    if align_match:
        attrs["alinhamento"] = align_match.group(1).splitlines()[0].strip()
    for english, portuguese in SKILL_EN.items():
        if re.search(rf"proficiency\s+{re.escape(english)}\s*:\s*yes", text, re.I):
            if portuguese not in attrs["pericias"]:
                attrs["pericias"].append(portuguese)
        if re.search(rf"expertise\s+{re.escape(english)}\s*:\s*yes", text, re.I):
            if portuguese not in attrs["expertise"]:
                attrs["expertise"].append(portuguese)
    return ParsedSheet(
        name=name_match.group(1).strip() if name_match else None,
        attributes=attrs,
    )


class Dnd5ePlugin(RPGSystemPlugin):
    slug = "dnd5e"
    display_name = "D&D 5e"

    def default_attributes(self) -> dict:
        return default_dnd()

    def create_sheet_widget(self, parent: QWidget | None = None) -> SheetWidget:
        return Dnd5eSheetWidget(parent)

    def generate_npc(self, params: dict[str, Any] | None = None) -> dict:
        return generate_dnd_npc(params)

    def try_parse_sheet(self, extracted: PdfExtract) -> ParsedSheet | None:
        return parse_dnd_sheet(extracted)

    def hp_paths(self) -> dict[str, tuple[str, str]]:
        return DND_HP_PATHS

    def generate_monster(self, params: dict[str, Any] | None = None) -> dict:
        return generate_dnd_monster(params)

    def monster_catalog(self) -> list[dict]:
        return BESTIARY

    def format_monster_preview(self, payload: dict[str, Any]) -> str:
        return format_dnd_monster_preview(payload)

    def format_sheet_html(self, payload: dict[str, Any]) -> str:
        return format_dnd_sheet_html(payload)

    def initiative_bonus(self, attributes: dict) -> int:
        return dnd_initiative_bonus(attributes)
