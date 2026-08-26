from __future__ import annotations

import random
import re
from typing import Any

from gestor_rpg.core.models import ParsedSheet, PdfExtract
from gestor_rpg.plugins._ddt_bestiary import (
    POWER_LABELS,
    filter_bestiary,
    find_bestiary,
)


def ddt_defaults() -> dict:
    return {
        "poder": 0,
        "habilidade": 0,
        "resistencia": 0,
        "pv_max": 5,
        "pv_atual": 5,
        "pm_max": 0,
        "pm_atual": 0,
        "pa_max": 1,
        "pa_atual": 1,
        "escala": "Ningen",
        "arquetipo": "",
        "xp": 0,
        "vantagens": [],
        "desvantagens": [],
        "pericias": [],
        "tecnicas": [],
        "inventario_comum": [],
        "inventario_incomum": [],
        "inventario_raro": [],
    }


def normalize_victory_attributes(data: dict[str, Any]) -> dict[str, Any]:
    """Aceita fichas antigas (F/A/PdF) e grava no recorte Victory (P/H/R)."""
    attrs = dict(data)
    if "poder" not in attrs:
        attrs["poder"] = int(attrs.get("forca") or 0)
    return attrs


def recalc_ddt_pools(attrs: dict) -> dict:
    r = int(attrs.get("resistencia") or 0)
    h = int(attrs.get("habilidade") or 0)
    attrs["pv_max"] = max(1, r * 5)
    attrs["pm_max"] = max(0, h * 5)
    attrs["pv_atual"] = attrs["pv_max"]
    attrs["pm_atual"] = attrs["pm_max"]
    return attrs


POWER_RANGES = {
    "fraco": (0, 1),
    "medio": (1, 2),
    "forte": (2, 4),
}

DDT_HP_PATHS: dict[str, tuple[str, str]] = {
    "hp": ("pv_atual", "pv_max"),
    "resource": ("pm_atual", "pm_max"),
}

VICTORY_HP_PATHS: dict[str, tuple[str, str]] = {
    **DDT_HP_PATHS,
    "action": ("pa_atual", "pa_max"),
}

def _resolve_ddt_power(params: dict[str, Any]) -> tuple[str, int]:
    raw = params.get("level")
    if raw is None:
        raw = params.get("challenge")
    if raw is not None:
        try:
            level = max(0, int(raw))
        except (TypeError, ValueError):
            level = 3
        power = "fraco" if level <= 1 else "forte" if level >= 5 else "medio"
        return power, level
    power = str(params.get("power") or "medio")
    if power not in POWER_RANGES:
        power = "medio"
    return power, {"fraco": 1, "medio": 3, "forte": 5}[power]


def catalog_entry_to_monster(entry: dict[str, Any]) -> dict[str, Any]:
    attrs = ddt_defaults()
    attrs["poder"] = int(entry.get("poder") or 0)
    attrs["habilidade"] = int(entry.get("habilidade") or 0)
    attrs["resistencia"] = int(entry.get("resistencia") or 0)
    pv = max(1, int(entry.get("pv") or 1))
    attrs["pv_max"] = pv
    attrs["pv_atual"] = pv
    attrs["pm_max"] = 0
    attrs["pm_atual"] = 0
    attrs["vantagens"] = list(entry.get("vantagens") or [])
    attrs["desvantagens"] = list(entry.get("desvantagens") or [])
    attrs["pericias"] = list(entry.get("pericias") or [])
    tesouro = str(entry.get("tesouro") or "").strip()
    attrs["escala"] = str(entry.get("escala") or "Ningen")
    attrs["arquetipo"] = str(entry.get("origem") or entry.get("category_label") or "")
    attrs["tecnicas"] = list(entry.get("poderes") or [])
    attrs["xp"] = int(entry.get("points") or 0)
    attrs["pa_max"] = 0
    attrs["pa_atual"] = 0
    if tesouro and not tesouro.lower().startswith("nenhum"):
        attrs["inventario_comum"] = [tesouro]
    points = entry.get("points")
    challenge: int | str = points if points is not None else "Lendário"
    label = POWER_LABELS.get(str(entry.get("power") or ""), str(entry.get("power") or ""))
    pts_txt = f"{points} pt" if points is not None else "Desafio lendário"
    note_parts = [
        f"{entry.get('origem') or entry.get('category_label')} · {entry.get('escala')} · {pts_txt} · {label}."
    ]
    for extra in entry.get("notas") or []:
        note_parts.append(str(extra))
    if entry.get("poder_alt") is not None:
        note_parts.append(f"Poder alternativo (tentáculos): {entry['poder_alt']}.")
    if tesouro:
        note_parts.append(f"Tesouro: {tesouro}")
    return {
        "name": str(entry.get("name") or "Desafio"),
        "attributes": attrs,
        "challenge": challenge,
        "notes": "\n".join(note_parts),
        "slug": entry.get("slug"),
    }


def format_ddt_sheet_html(payload: dict[str, Any]) -> str:
    from gestor_rpg.modules.sheet_export.html import (
        kv_table,
        list_html,
        section,
        stats_table,
        wrap_sheet,
    )

    attrs = payload.get("attributes") or {}
    parts: list[str] = [
        section(
            "Identidade",
            kv_table(
                [
                    ("Arquétipo", attrs.get("arquetipo") or "—"),
                    ("Escala", attrs.get("escala") or "—"),
                    ("Pts XP", attrs.get("xp", 0)),
                ]
            ),
        ),
        section(
            "Características",
            stats_table(
                ["P", "H", "R"],
                [
                    attrs.get("poder", attrs.get("forca", 0)),
                    attrs.get("habilidade", 0),
                    attrs.get("resistencia", 0),
                ],
            ),
        ),
        section(
            "Pontos",
            stats_table(
                ["PA", "PV", "PM"],
                [
                    f"{attrs.get('pa_atual', 0)}/{attrs.get('pa_max', 0)}",
                    f"{attrs.get('pv_atual', 0)}/{attrs.get('pv_max', 0)}",
                    f"{attrs.get('pm_atual', 0)}/{attrs.get('pm_max', 0)}",
                ],
            ),
        ),
        section("Vantagens", list_html(attrs.get("vantagens"))),
        section("Desvantagens", list_html(attrs.get("desvantagens"))),
        section("Perícias", list_html(attrs.get("pericias"))),
        section("Técnicas", list_html(attrs.get("tecnicas"))),
        section("Inventário comum", list_html(attrs.get("inventario_comum"))),
        section("Inventário incomum", list_html(attrs.get("inventario_incomum"))),
        section("Inventário raro", list_html(attrs.get("inventario_raro"))),
    ]
    return wrap_sheet(payload, "".join(parts))


def format_ddt_monster_preview(payload: dict[str, Any]) -> str:
    attrs = payload.get("attributes") or {}
    notes = str(payload.get("notes") or "").strip()
    header, *rest = (notes.split("\n", 1) + [""])[:2] if notes else ("", "")
    extra_notes = rest[0].strip().split("\n") if rest and rest[0] else []
    lines = [str(payload.get("name") or "Desafio")]
    if header:
        lines.append(header)
    lines.append("")
    lines.append(
        f"P {attrs.get('poder', attrs.get('forca', 0))}   "
        f"H {attrs.get('habilidade', 0)}   "
        f"R {attrs.get('resistencia', 0)}"
    )
    lines.append(
        f"PV {attrs.get('pv_atual', 0)}/{attrs.get('pv_max', 0)}   "
        f"Escala {attrs.get('escala') or '—'}"
    )
    lines.extend(
        [
            "",
            "Perícias: " + _join_preview_list(attrs.get("pericias")),
            "Vantagens: " + _join_preview_list(attrs.get("vantagens")),
            "Desvantagens: " + _join_preview_list(attrs.get("desvantagens")),
        ]
    )
    tecnicas = attrs.get("tecnicas") or attrs.get("poderes") or attrs.get("magias") or []
    if tecnicas:
        lines.append("")
        lines.append("Técnicas:")
        lines.extend(f"• {item}" for item in tecnicas)
    tesouro = attrs.get("inventario_comum") or []
    if tesouro:
        lines.append("")
        lines.append("Tesouro: " + _join_preview_list(tesouro))
    extras = [line for line in extra_notes if line and not line.startswith("Tesouro:")]
    if extras:
        lines.append("")
        lines.extend(extras)
    return "\n".join(lines)


def _join_preview_list(values: object) -> str:
    if not isinstance(values, list) or not values:
        return "—"
    return ", ".join(str(item) for item in values)


def _pick_bestiary_entry(params: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    named = str(params.get("name") or params.get("slug") or "").strip()
    if named:
        found = find_bestiary(named)
        if found is not None:
            return found
    power = str(params.get("power") or "").strip()
    if params.get("level") is not None and not named:
        power, _level = _resolve_ddt_power(params)
    filtered = filter_bestiary(
        power=power or None,
        category=params.get("category"),
        escala=params.get("escala"),
        query=params.get("query"),
    )
    if not filtered:
        filtered = filter_bestiary(
            category=params.get("category"),
            escala=params.get("escala"),
            query=params.get("query"),
        )
    if not filtered:
        filtered = filter_bestiary()
    return rng.choice(filtered)


def generate_ddt_monster(params: dict[str, Any] | None = None) -> dict:
    params = params or {}
    rng = params.get("rng") or random.Random()
    entry = _pick_bestiary_entry(params, rng)
    return catalog_entry_to_monster(entry)


def ddt_initiative_bonus(attributes: dict) -> int:
    return int(attributes.get("habilidade") or 0)

VANTAGENS = [
    "Ataque Especial",
    "Aceleração",
    "Parceiro",
    "Patrono",
    "Riqueza",
    "Sentidos Especiais",
]
DESVANTAGENS = [
    "Código de Honra",
    "Ponto Fraco",
    "Rival",
    "Casca Grossa Invertida",
    "Maldição",
]


def generate_ddt_npc(params: dict[str, Any] | None = None) -> dict:
    params = params or {}
    power = str(params.get("power") or "medio")
    lo, hi = POWER_RANGES.get(power, POWER_RANGES["medio"])
    rng = params.get("rng") or random.Random()
    attrs = ddt_defaults()
    for key in ("poder", "habilidade", "resistencia"):
        attrs[key] = rng.randint(lo, hi)
    recalc_ddt_pools(attrs)
    n_v = rng.randint(0, 2)
    n_d = rng.randint(0, 1)
    attrs["vantagens"] = rng.sample(VANTAGENS, k=min(n_v, len(VANTAGENS)))
    attrs["desvantagens"] = rng.sample(DESVANTAGENS, k=min(n_d, len(DESVANTAGENS)))
    attrs["escala"] = rng.choice(["Ningen", "Ningen", "Sugoi"])
    attrs["arquetipo"] = rng.choice(["Aventureiro", "Mago", "Guerreiro", "Ladino", "Lutador"])
    return {
        "attributes": attrs,
        "motivation": rng.choice(MOTIVATIONS),
        "story_hook": rng.choice(HOOKS),
    }


MOTIVATIONS = [
    "Proteger alguém que não pode se defender",
    "Pagar uma dívida de honra",
    "Descobrir a verdade sobre o próprio passado",
    "Acumular poder antes que o inimigo o faça",
    "Fugir de um destino que recusa aceitar",
    "Provar o próprio valor a um mestre antigo",
]

HOOKS = [
    "Carrega um amuleto que reage perto de ruínas",
    "Alguém poderoso ofereceu ouro demais por um favor simples",
    "Sonha todas as noites com o mesmo corredor de pedra",
    "Uma carta selada chegou com o nome de um dos heróis",
    "Um rival público desafiou o grupo em praça cheia",
    "Guarda um mapa rasgado cuja outra metade falta",
]


def _find_int(text: str, patterns: list[str]) -> int | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                continue
    return None


def _find_name(text: str) -> str | None:
    match = re.search(
        r"(?:nome|personagem)\s*[:\-]\s*([A-Za-zÀ-ÿ0-9 '\-]{2,40})",
        text,
        re.IGNORECASE,
    )
    if match:
        return match.group(1).strip()
    return None


def parse_ddt_sheet(extracted: PdfExtract) -> ParsedSheet | None:
    text = extracted.full_text
    if not text.strip():
        return None
    attrs = ddt_defaults()
    mapping = {
        "poder": [
            r"poder(?!\s+de\s+fogo)\s*[:\-]\s*(-?\d+)",
            r"(?<![A-Za-z])P(?![A-Za-zDdFfMm])\s*[:\-]?\s*(-?\d+)",
            r"for[cç]a\s*[:\-]\s*(-?\d+)",
        ],
        "habilidade": [r"habilidade\s*[:\-]\s*(-?\d+)", r"(?<![A-Za-z])H\s*[:\-]?\s*(-?\d+)"],
        "resistencia": [
            r"resist[eê]ncia\s*[:\-]\s*(-?\d+)",
            r"(?<![A-Za-z])R\s*[:\-]?\s*(-?\d+)",
        ],
        "pv_max": [r"p(?:ontos?\s+de\s+)?v(?:ida)?\s*[:\-]\s*(\d+)"],
        "pm_max": [r"p(?:ontos?\s+de\s+)?m(?:agia|ana)\s*[:\-]\s*(\d+)"],
        "pa_max": [r"p(?:ontos?\s+de\s+)?a(?:[cç][aã]o)?\s*[:\-]\s*(\d+)"],
        "xp": [r"(?:pts?\s*)?xp\s*[:\-]\s*(\d+)"],
    }
    found = 0
    for key, patterns in mapping.items():
        value = _find_int(text, patterns)
        if value is not None:
            attrs[key] = value
            found += 1
    if found < 3:
        return None
    if "pv_max" in attrs:
        attrs["pv_atual"] = attrs["pv_max"]
    if "pm_max" in attrs:
        attrs["pm_atual"] = attrs["pm_max"]
    if attrs.get("pa_max"):
        attrs["pa_atual"] = attrs["pa_max"]
    arq_match = re.search(r"arqu[eé]tipo\s*[:\-]\s*(.+)", text, re.IGNORECASE)
    if arq_match:
        attrs["arquetipo"] = arq_match.group(1).splitlines()[0].strip()[:80]
    return ParsedSheet(name=_find_name(text), attributes=attrs)
