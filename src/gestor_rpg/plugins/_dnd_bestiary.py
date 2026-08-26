"""Catálogo D&D 5e a partir do compêndio local anexado pelo usuário."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

TABLE_ROWS: list[tuple[str, str, str, int, list[str]]] = [
    ("Plebeu", "Humanoide", "0", 10, ["Urbano", "Ártico", "Colina"]),
    ("Coruja", "Besta", "0", 10, ["Floresta", "Ártico"]),
    ("Bode", "Besta", "0", 10, ["Montanha", "Colina", "Urbano"]),
    ("Abutre", "Besta", "0", 10, ["Colina", "Deserto", "Planície"]),
    ("Chacal", "Besta", "0", 10, ["Deserto", "Planície"]),
    ("Gato", "Besta", "0", 10, ["Urbano", "Deserto", "Floresta"]),
    ("Caranguejo", "Besta", "0", 10, ["Costa"]),
    ("Besouro de Fogo Gigante", "Besta", "0", 10, ["Subterrâneo"]),
    ("Guinchador", "Planta", "0", 10, ["Subterrâneo"]),
    ("Miconide Esporo", "Planta", "0", 10, ["Subterrâneo"]),
    ("Bandido", "Humanoide", "1/8", 25, ["Urbano", "Ártico", "Colina"]),
    ("Falcão de Sangue", "Besta", "1/8", 25, ["Costa", "Colina", "Montanha"]),
    ("Kobold", "Humanoide", "1/8", 25, ["Subterrâneo", "Deserto", "Ártico"]),
    ("Povo do Mar", "Humanoide", "1/8", 25, ["Subaquático", "Costa"]),
    ("Stirge", "Monstruosidade", "1/8", 25, ["Pântano", "Floresta", "Urbano"]),
    ("Cultista", "Humanoide", "1/8", 25, ["Urbano"]),
    ("Guarda", "Humanoide", "1/8", 25, ["Urbano", "Colina", "Floresta"]),
    ("Guerreiro Tribal", "Humanoide", "1/8", 25, ["Colina", "Ártico", "Costa"]),
    ("Mastim", "Besta", "1/8", 25, ["Floresta", "Urbano", "Colina"]),
    ("Galho Infectado", "Planta", "1/8", 25, ["Floresta"]),
    ("Kobold Alado", "Humanoide", "1/4", 50, ["Montanha", "Subterrâneo", "Colina"]),
    ("Coruja Gigante", "Besta", "1/4", 50, ["Floresta", "Ártico", "Colina"]),
    ("Bico de Machado", "Besta", "1/4", 50, ["Colina", "Planície"]),
    ("Javali", "Besta", "1/4", 50, ["Floresta", "Planície", "Colina"]),
    ("Alce", "Besta", "1/4", 50, ["Floresta", "Planície", "Colina"]),
    ("Aranha-Lobo Gigante", "Besta", "1/4", 50, ["Colina", "Planície", "Floresta"]),
    ("Goblin", "Humanoide", "1/4", 50, ["Subterrâneo", "Floresta", "Colina"]),
    ("Pseudodragão", "Dragão", "1/4", 50, ["Floresta", "Urbano", "Montanha"]),
    ("Pixie", "Fada", "1/4", 50, ["Floresta"]),
    ("Sprite", "Fada", "1/4", 50, ["Floresta"]),
    ("Kenku", "Humanoide", "1/4", 50, ["Floresta", "Urbano"]),
    ("Grimlock", "Humanoide", "1/4", 50, ["Subterrâneo"]),
    ("Drow", "Humanoide", "1/4", 50, ["Subterrâneo"]),
    ("Esqueleto", "Morto-Vivo", "1/4", 50, ["Urbano", "Subterrâneo"]),
    ("Zumbi", "Morto-Vivo", "1/4", 50, ["Urbano", "Subterrâneo"]),
    ("Orc", "Humanoide", "1/2", 100, ["Subterrâneo", "Pântano", "Ártico"]),
    ("Gnoll", "Humanoide", "1/2", 100, ["Colina", "Deserto", "Floresta"]),
    ("Hobgoblin", "Humanoide", "1/2", 100, ["Colina", "Planície", "Subterrâneo"]),
    ("Povo Lagarto", "Humanoide", "1/2", 100, ["Pântano", "Floresta"]),
    ("Sátiro", "Fada", "1/2", 100, ["Floresta"]),
    ("Sahuagin", "Humanoide", "1/2", 100, ["Subaquático", "Costa"]),
    ("Batedor", "Humanoide", "1/2", 100, ["Floresta", "Montanha", "Deserto"]),
    ("Homem-Chacal", "Humanoide", "1/2", 100, ["Deserto", "Planície"]),
    ("Gnomo das Profundezas", "Humanoide", "1/2", 100, ["Subterrâneo"]),
    ("Sombra", "Morto-Vivo", "1/2", 100, ["Subterrâneo", "Urbano"]),
    ("Meio-Ogro", "Gigante", "1", 200, ["Colina", "Ártico", "Urbano"]),
    ("Urso Marrom", "Besta", "1", 200, ["Floresta", "Ártico", "Colina"]),
    ("Bugbear", "Humanoide", "1", 200, ["Floresta", "Planície", "Subterrâneo"]),
    ("Carniça (Verme da)", "Monstruosidade", "2", 450, ["Subterrâneo"]),
    ("Carniçal", "Morto-Vivo", "1", 200, ["Subterrâneo", "Pântano", "Urbano"]),
    ("Harpia", "Monstruosidade", "1", 200, ["Colina", "Costa", "Montanha"]),
    ("Hipogrifo", "Monstruosidade", "1", 200, ["Colina", "Montanha", "Planície"]),
    ("Leão", "Besta", "1", 200, ["Colina", "Deserto", "Planície"]),
    ("Lobo Atroz", "Besta", "1", 200, ["Colina", "Floresta", "Planície"]),
    ("Águia Gigante", "Besta", "1", 200, ["Costa", "Montanha", "Planície"]),
    ("Duergar", "Humanoide", "1", 200, ["Subterrâneo"]),
    ("Espantalho", "Constructo", "1", 200, ["Planície"]),
    ("Fogo-Fátuo", "Monstruosidade", "2", 450, ["Floresta", "Pântano", "Urbano"]),
    ("Ogro", "Gigante", "2", 450, ["Floresta", "Colina", "Pântano"]),
    ("Centauro", "Monstruosidade", "2", 450, ["Floresta", "Planície"]),
    ("Grifo", "Monstruosidade", "2", 450, ["Colina", "Montanha", "Planície"]),
    ("Pégaso", "Celestial", "2", 450, ["Colina", "Floresta", "Planície"]),
    ("Basilisco", "Monstruosidade", "3", 700, ["Montanha", "Subterrâneo"]),
    ("Cão Infernal", "Corruptor", "3", 700, ["Montanha", "Subterrâneo"]),
    ("Manticora", "Monstruosidade", "3", 700, ["Colina", "Costa", "Montanha"]),
    ("Veterano", "Humanoide", "3", 700, ["Urbano", "Montanha", "Costa"]),
    ("Lobisomem", "Humanoide", "3", 700, ["Floresta", "Colina"]),
    ("Bruxa Verde", "Fada", "3", 700, ["Floresta", "Pântano", "Colina"]),
    ("Duplo", "Monstruosidade", "3", 700, ["Urbano", "Subterrâneo"]),
    ("Horror de Gancho", "Monstruosidade", "3", 700, ["Subterrâneo"]),
    ("Espectador", "Aberração", "3", 700, ["Subterrâneo"]),
    ("Pudim Negro", "Limo", "4", 1100, ["Subterrâneo"]),
    ("Banshee", "Morto-Vivo", "4", 1100, ["Floresta", "Costa"]),
    ("Ettin", "Gigante", "4", 1100, ["Montanha", "Colina"]),
    ("Fantasma", "Morto-Vivo", "4", 1100, ["Urbano", "Subterrâneo"]),
    ("Súcubo ou Íncubo", "Corruptor", "4", 1100, ["Urbano"]),
    ("Cambion", "Corruptor", "5", 1800, ["Urbano"]),
    ("Elemental da Água", "Elemental", "5", 1800, ["Costa", "Pântano", "Subterrâneo"]),
    ("Bulette", "Monstruosidade", "5", 1800, ["Colina", "Montanha", "Planície"]),
    ("Troll", "Gigante", "5", 1800, ["Pântano", "Floresta", "Montanha"]),
    ("Ciclope", "Gigante", "6", 2300, ["Pântano", "Colina", "Montanha"]),
    ("Quimera", "Monstruosidade", "6", 2300, ["Colina", "Montanha", "Planície"]),
    ("Wyvern", "Dragão", "6", 2300, ["Colina", "Montanha"]),
    ("Oni", "Gigante", "7", 2900, ["Floresta", "Urbano"]),
    ("Hidra", "Monstruosidade", "8", 3900, ["Pântano"]),
    ("Gigante do Gelo", "Gigante", "8", 3900, ["Ártico", "Montanha"]),
    ("Tiranossauro", "Besta", "8", 3900, ["Planície"]),
    ("Assassino", "Humanoide", "8", 3900, ["Urbano"]),
    ("Gigante das Nuvens", "Gigante", "9", 5000, ["Montanha"]),
    ("Ente", "Planta", "9", 5000, ["Floresta"]),
    ("Abolete", "Aberração", "10", 5900, ["Subterrâneo"]),
    ("Behir", "Monstruosidade", "11", 7200, ["Subterrâneo"]),
    ("Roca", "Besta", "11", 7200, ["Montanha", "Deserto", "Costa"]),
    ("Djinni", "Elemental", "11", 7200, ["Costa"]),
    ("Efreeti", "Elemental", "11", 7200, ["Deserto"]),
    ("Verme Púrpura", "Monstruosidade", "15", 13000, ["Deserto", "Subterrâneo"]),
    ("Vampiro", "Morto-Vivo", "13", 10000, ["Urbano"]),
    ("Dragão Branco Ancião", "Dragão", "20", 25000, ["Ártico"]),
    ("Dragão Vermelho Ancião", "Dragão", "24", 62000, ["Montanha", "Colina"]),
    ("Tarrasque", "Monstruosidade", "30", 155000, ["Urbano"]),
]

EXTRA_ROWS: list[tuple[str, str, str, int, list[str]]] = [
    ("Aarakocra", "Humanoide", "1/4", 50, ["Montanha"]),
    ("Orc Olho de Gruumsh", "Humanoide", "2", 450, ["Subterrâneo", "Pântano"]),
    ("Orog", "Humanoide", "2", 450, ["Subterrâneo"]),
    ("Esqueleto de Minotauro", "Morto-Vivo", "2", 450, ["Subterrâneo"]),
    ("Sacerdote", "Humanoide", "2", 450, ["Urbano"]),
    ("Tubarão Gigante", "Besta", "5", 1800, ["Costa", "Subaquático"]),
    ("Nótico", "Aberração", "2", 450, ["Subterrâneo"]),
    ("Enxame de Serpentes Venenosas", "Besta", "2", 450, ["Pântano", "Floresta"]),
    ("Manto Negro (Manto da Caverna)", "Besta", "1/2", 100, ["Subterrâneo"]),
]

CR_BASE: list[tuple[float, int, int]] = [
    (0, 4, 10),
    (0.125, 9, 12),
    (0.25, 15, 12),
    (0.5, 22, 13),
    (1, 30, 13),
    (2, 45, 13),
    (3, 59, 14),
    (4, 75, 14),
    (5, 90, 15),
    (6, 110, 15),
    (7, 125, 15),
    (8, 136, 16),
    (9, 150, 16),
    (10, 165, 17),
    (11, 180, 17),
    (13, 187, 17),
    (15, 230, 18),
    (20, 333, 19),
    (24, 444, 22),
    (30, 676, 25),
]

TYPE_FOCUS = {
    "Humanoide": ("str", "con"),
    "Besta": ("str", "dex"),
    "Monstruosidade": ("str", "con"),
    "Morto-Vivo": ("con", "wis"),
    "Dragão": ("str", "cha"),
    "Gigante": ("str", "con"),
    "Fada": ("dex", "cha"),
    "Planta": ("con", "wis"),
    "Constructo": ("str", "con"),
    "Aberração": ("int", "wis"),
    "Elemental": ("con", "str"),
    "Corruptor": ("cha", "dex"),
    "Celestial": ("wis", "cha"),
    "Limo": ("con", "str"),
}

DETAILS: dict[str, dict[str, Any]] = {
    "aarakocra": {
        "size": "Médio",
        "alinhamento": "neutro e bom",
        "ca": 12,
        "hp": 13,
        "hit_dice": "3d8",
        "speed": 6,
        "speed_text": "6 m, voo 15 m",
        "abilities": {"str": 10, "dex": 14, "con": 10, "int": 11, "wis": 12, "cha": 11},
        "pericias": ["Percepção"],
        "passive": 15,
        "idiomas": "Aarakocra, Auran",
        "armas": [
            {"nome": "Garra", "bonus": "+4", "dano": "4 (1d4+2) cortante"},
            {"nome": "Azagaia", "bonus": "+4", "dano": "5 (1d6+2) perfurante"},
            {"nome": "", "bonus": "", "dano": ""},
        ],
        "poderes": [
            "Ataque de Mergulho: se voar e mergulhar 9 m em linha reta, o acerto corpo-a-corpo causa 3 (1d6) extra.",
        ],
    },
    "orc-olho-de-gruumsh": {
        "size": "Médio",
        "alinhamento": "caótico e mau",
        "ca": 16,
        "hp": 45,
        "hit_dice": "6d8+18",
        "speed": 9,
        "abilities": {"str": 16, "dex": 12, "con": 16, "int": 9, "wis": 13, "cha": 12},
        "pericias": ["Intimidação", "Religião"],
        "passive": 11,
        "idiomas": "Comum, Orc",
        "armas": [
            {"nome": "Lança", "bonus": "+5", "dano": "11 (1d6+3+1d8) perfurante"},
            {"nome": "", "bonus": "", "dano": ""},
            {"nome": "", "bonus": "", "dano": ""},
        ],
        "poderes": [
            "Agressivo: ação bônus para se mover até o deslocamento em direção a um inimigo visível.",
            "Fúria de Gruumsh: +4 (1d8) de dano em acertos com arma (já incluso).",
            "Conjuração 3º nível (CD 11, +3): truques orientação, resistência, taumaturgia; 1º bênção, comando; 2º arma espiritual, augúrio.",
        ],
    },
    "orog": {
        "size": "Médio",
        "alinhamento": "caótico e mau",
        "ca": 18,
        "hp": 42,
        "hit_dice": "5d8+20",
        "speed": 9,
        "abilities": {"str": 18, "dex": 12, "con": 18, "int": 12, "wis": 11, "cha": 12},
        "pericias": ["Intimidação", "Sobrevivência"],
        "passive": 10,
        "idiomas": "Comum, Orc",
        "armas": [
            {"nome": "Machado Grande", "bonus": "+6", "dano": "10 (1d12+4) cortante"},
            {"nome": "Azagaia", "bonus": "+6", "dano": "7 (1d6+4) perfurante"},
            {"nome": "", "bonus": "", "dano": ""},
        ],
        "poderes": [
            "Agressivo: ação bônus para se mover até o deslocamento em direção a um inimigo visível.",
            "Ataques Múltiplos: dois ataques com machado grande.",
        ],
    },
    "esqueleto-de-minotauro": {
        "size": "Grande",
        "alinhamento": "caótico e mau",
        "ca": 12,
        "hp": 67,
        "hit_dice": "9d10+18",
        "speed": 12,
        "abilities": {"str": 18, "dex": 11, "con": 15, "int": 6, "wis": 8, "cha": 5},
        "pericias": [],
        "passive": 9,
        "idiomas": "Compreende os idiomas que conhecia em vida, mas não fala",
        "armas": [
            {"nome": "Machado Grande", "bonus": "+6", "dano": "17 (2d12+4) cortante"},
            {"nome": "Chifre", "bonus": "+6", "dano": "13 (2d8+4) perfurante"},
            {"nome": "", "bonus": "", "dano": ""},
        ],
        "poderes": [
            "Vulnerável a concussão; imune a veneno; imune a envenenado e exausto.",
            "Investida: após 3 m em linha reta, chifre causa 9 (2d8) extra; CD 14 Força ou é empurrado 3 m e cai.",
        ],
    },
    "sacerdote": {
        "size": "Médio",
        "alinhamento": "qualquer tendência",
        "ca": 13,
        "hp": 27,
        "hit_dice": "5d8+5",
        "speed": 9,
        "abilities": {"str": 10, "dex": 10, "con": 12, "int": 13, "wis": 16, "cha": 13},
        "pericias": ["Medicina", "Persuasão", "Religião"],
        "passive": 13,
        "idiomas": "Dois idiomas quaisquer",
        "armas": [
            {"nome": "Maça", "bonus": "+2", "dano": "3 (1d6) concussão"},
            {"nome": "", "bonus": "", "dano": ""},
            {"nome": "", "bonus": "", "dano": ""},
        ],
        "poderes": [
            "Eminência Divina: ação bônus, gasta espaço de magia para +10 (3d6) radiante em ataques corpo-a-corpo no turno (+1d6 por nível acima do 1º).",
            "Conjuração 5º nível (CD 13, +5): truques chama sagrada, luz, taumaturgia; 1º curar ferimentos, raio teleguiado, santuário; 2º arma espiritual, restauração menor; 3º dissipar magia, espíritos guardiões.",
        ],
    },
    "veterano": {
        "size": "Médio",
        "alinhamento": "qualquer tendência",
        "ca": 17,
        "hp": 58,
        "hit_dice": "9d8+18",
        "speed": 9,
        "abilities": {"str": 16, "dex": 13, "con": 14, "int": 10, "wis": 11, "cha": 10},
        "pericias": ["Atletismo", "Percepção"],
        "passive": 12,
        "idiomas": "Um idioma qualquer (geralmente Comum)",
        "armas": [
            {"nome": "Espada Longa", "bonus": "+5", "dano": "7 (1d8+3) cortante"},
            {"nome": "Espada Curta", "bonus": "+5", "dano": "6 (1d6+3) perfurante"},
            {"nome": "Besta Pesada", "bonus": "+3", "dano": "6 (1d10+1) perfurante"},
        ],
        "poderes": [
            "Ataques Múltiplos: dois ataques com espada longa; se tiver espada curta sacada, adiciona um ataque com ela.",
        ],
    },
    "tubarao-gigante": {
        "size": "Imenso",
        "alinhamento": "imparcial",
        "ca": 13,
        "hp": 126,
        "hit_dice": "11d12+55",
        "speed": 0,
        "speed_text": "0 m, natação 15 m",
        "abilities": {"str": 23, "dex": 11, "con": 21, "int": 1, "wis": 10, "cha": 5},
        "pericias": ["Percepção"],
        "passive": 13,
        "idiomas": "—",
        "armas": [
            {"nome": "Mordida", "bonus": "+9", "dano": "22 (3d10+6) perfurante"},
            {"nome": "", "bonus": "", "dano": ""},
            {"nome": "", "bonus": "", "dano": ""},
        ],
        "poderes": [
            "Frenesi de Sangue: vantagem em ataques corpo-a-corpo contra criaturas feridas.",
            "Respirar na Água: só respira debaixo d'água.",
        ],
    },
    "notico": {
        "size": "Médio",
        "alinhamento": "leal e neutro",
        "ca": 14,
        "hp": 39,
        "hit_dice": "6d8+12",
        "speed": 9,
        "abilities": {"str": 8, "dex": 14, "con": 14, "int": 13, "wis": 14, "cha": 11},
        "pericias": ["Arcanismo", "Furtividade", "Intuição", "Percepção"],
        "passive": 12,
        "idiomas": "Subcomum",
        "armas": [
            {"nome": "Garra", "bonus": "+4", "dano": "6 (1d6+3) cortante"},
            {"nome": "Olhar Pútrido", "bonus": "CD 12", "dano": "10 (3d6) necrótico"},
            {"nome": "", "bonus": "", "dano": ""},
        ],
        "poderes": [
            "Visão Aguçada: vantagem em Percepção relacionadas à visão.",
            "Ataques Múltiplos: dois ataques de garra.",
            "Intuição Estranha: teste resistido de Enganação vs Intuição; se vencer, aprende um segredo (imune se imune a enfeitiçado).",
        ],
    },
    "enxame-de-serpentes-venenosas": {
        "size": "Médio (enxame de Miúdas)",
        "alinhamento": "imparcial",
        "ca": 14,
        "hp": 36,
        "hit_dice": "8d8",
        "speed": 9,
        "speed_text": "9 m, escalada 9 m",
        "abilities": {"str": 8, "dex": 18, "con": 11, "int": 1, "wis": 10, "cha": 3},
        "pericias": [],
        "passive": 10,
        "idiomas": "—",
        "armas": [
            {"nome": "Mordidas", "bonus": "+6", "dano": "7 (2d6) + veneno CD 10 14 (4d6)"},
            {"nome": "", "bonus": "", "dano": ""},
            {"nome": "", "bonus": "", "dano": ""},
        ],
        "poderes": [
            "Enxame: ocupa o espaço de outra criatura; passa por aberturas de serpente Miúda; não recupera PV.",
            "Resistente a concussão, cortante e perfurante; imune a várias condições de controle.",
        ],
    },
    "manto-negro-manto-da-caverna": {
        "size": "Pequeno",
        "alinhamento": "imparcial",
        "ca": 11,
        "hp": 22,
        "hit_dice": "5d6+5",
        "speed": 3,
        "speed_text": "3 m, voo 9 m",
        "abilities": {"str": 16, "dex": 12, "con": 13, "int": 2, "wis": 10, "cha": 5},
        "pericias": ["Furtividade"],
        "passive": 10,
        "idiomas": "—",
        "armas": [
            {"nome": "Esmagar", "bonus": "+5", "dano": "6 (1d6+3) concussão"},
            {"nome": "", "bonus": "", "dano": ""},
            {"nome": "", "bonus": "", "dano": ""},
        ],
        "poderes": [
            "Aparência Falsa: imóvel, indistinguível de formação de caverna.",
            "Eco Localização: não usa percepção às cegas se estiver surdo.",
            "Aura de Escuridão (1/Dia): raio de 4,5 m de escuridão mágica por até 10 min.",
        ],
    },
}


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = "".join(char for char in normalized if not unicodedata.combining(char))
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug or "criatura"


def cr_float(cr: str) -> float:
    text = str(cr).strip()
    if "/" in text:
        left, right = text.split("/", 1)
        return float(left) / float(right)
    return float(text)


def power_for_cr(cr: str) -> str:
    value = cr_float(cr)
    if value <= 0.5:
        return "fraco"
    if value <= 4:
        return "medio"
    if value <= 10:
        return "forte"
    return "lendario"


def estimate_hp_ac(cr: str) -> tuple[int, int]:
    value = cr_float(cr)
    best = CR_BASE[0]
    for row in CR_BASE:
        if row[0] <= value:
            best = row
    return best[1], best[2]


def estimate_abilities(tipo: str, power: str) -> dict[str, int]:
    base = {"fraco": 10, "medio": 12, "forte": 14, "lendario": 16}[power]
    scores = {key: base for key in ("str", "dex", "con", "int", "wis", "cha")}
    for key in TYPE_FOCUS.get(tipo, ("str", "con")):
        scores[key] = min(20, base + 4)
    if tipo == "Besta":
        scores["int"] = 2
        scores["cha"] = max(5, base - 6)
    if tipo == "Limo":
        scores["int"] = 1
        scores["dex"] = 8
    if tipo == "Planta":
        scores["int"] = max(5, base - 6)
    return scores


def _build_entry(
    name: str, tipo: str, cr: str, xp: int, habitats: list[str]
) -> dict[str, Any]:
    slug = slugify(name)
    power = power_for_cr(cr)
    hp, ac = estimate_hp_ac(cr)
    abilities = estimate_abilities(tipo, power)
    extra = DETAILS.get(slug, {})
    habitat_list = list(habitats)
    return {
        "slug": slug,
        "name": name,
        "points": xp,
        "power": power,
        "cr": cr,
        "escala": habitat_list[0] if habitat_list else "",
        "habitats": habitat_list,
        "category": slugify(tipo),
        "category_label": tipo,
        "origem": ", ".join(habitat_list),
        "tipo": tipo,
        "ca": int(extra.get("ca", ac)),
        "hp": int(extra.get("hp", hp)),
        "abilities": extra.get("abilities") or abilities,
        "speed": int(extra.get("speed", 9 if tipo != "Limo" else 6)),
        "speed_text": extra.get("speed_text") or "",
        "size": extra.get("size") or "",
        "alinhamento": extra.get("alinhamento") or "",
        "hit_dice": extra.get("hit_dice") or "",
        "pericias": list(extra.get("pericias") or []),
        "poderes": list(extra.get("poderes") or []),
        "armas": extra.get("armas"),
        "idiomas": extra.get("idiomas") or "",
        "passive": extra.get("passive"),
        "detailed": slug in DETAILS,
    }


def _build_bestiary() -> list[dict[str, Any]]:
    entries = [_build_entry(*row) for row in TABLE_ROWS]
    by_slug = {item["slug"]: item for item in entries}
    for row in EXTRA_ROWS:
        entry = _build_entry(*row)
        if entry["slug"] not in by_slug:
            entries.append(entry)
            by_slug[entry["slug"]] = entry
    return entries


BESTIARY: list[dict[str, Any]] = _build_bestiary()


def filter_dnd_bestiary(
    *,
    power: str | None = None,
    category: str | None = None,
    escala: str | None = None,
    query: str | None = None,
) -> list[dict[str, Any]]:
    needle = (query or "").strip().lower()
    out: list[dict[str, Any]] = []
    for entry in BESTIARY:
        if power and power not in {"", "todos"} and entry["power"] != power:
            continue
        if category and category not in {"", "todos"} and entry["category"] != category:
            continue
        habitats = entry.get("habitats") or [entry.get("escala")]
        if escala and escala not in {"", "todas"} and escala not in habitats:
            continue
        if needle:
            blob = " ".join(
                [
                    str(entry.get("name") or ""),
                    str(entry.get("origem") or ""),
                    str(entry.get("category_label") or ""),
                    str(entry.get("cr") or ""),
                    " ".join(habitats),
                    " ".join(entry.get("pericias") or []),
                    " ".join(entry.get("poderes") or []),
                ]
            ).lower()
            if needle not in blob:
                continue
        out.append(entry)
    return out


def find_dnd_bestiary(name_or_slug: str) -> dict[str, Any] | None:
    key = name_or_slug.strip().lower()
    for entry in BESTIARY:
        if entry["slug"] == key or entry["name"].lower() == key:
            return entry
    return None
