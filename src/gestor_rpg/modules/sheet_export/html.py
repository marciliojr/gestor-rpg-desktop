from __future__ import annotations

import json
import re
from html import escape as html_escape

from gestor_rpg.core.models import encounter_status_label, location_kind_label, person_attitude_label
from gestor_rpg.ui.styles import CANVAS, INK, LINE, MUTED, SAGE, SAGE_SOFT

KIND_LABELS = {"pc": "Personagem", "npc": "NPC", "monster": "Monstro"}

_SHEET_CSS = f"""
body {{
    font-family: "Noto Sans", "Liberation Sans", "Segoe UI", sans-serif;
    color: {INK};
    background-color: {CANVAS};
    font-size: 10pt;
}}
h1 {{
    color: {SAGE};
    font-size: 18pt;
    margin: 0 0 4px 0;
}}
.meta {{
    color: {MUTED};
    margin-bottom: 12px;
}}
h2 {{
    color: {SAGE};
    font-size: 12pt;
    border-bottom: 1px solid {LINE};
    margin: 14px 0 6px 0;
}}
.headline {{
    color: {INK};
    font-size: 12pt;
    margin: 0 0 12px 0;
}}
table.stats, table.kv, table.list {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 6px;
}}
table.stats th, table.stats td, table.kv th, table.kv td, table.list th, table.list td {{
    border: 1px solid {LINE};
    padding: 4px 8px;
}}
table.stats th, table.list th {{
    background-color: {SAGE_SOFT};
    text-align: center;
}}
table.stats td {{
    text-align: center;
}}
table.kv th {{
    text-align: left;
    width: 28%;
    color: {MUTED};
    font-weight: normal;
}}
.empty {{
    color: {MUTED};
}}
pre {{
    white-space: pre-wrap;
    font-size: 9pt;
}}
"""


def esc(value: object) -> str:
    if value is None or value == "":
        return "—"
    return html_escape(str(value), quote=True)


def kind_label(kind: str) -> str:
    return KIND_LABELS.get(kind, kind or "Personagem")


def section(title: str, inner: str) -> str:
    return f"<h2>{html_escape(title, quote=True)}</h2>{inner}"


def list_html(items: object) -> str:
    if not isinstance(items, list):
        text = str(items or "").strip()
        if not text:
            return "<p class='empty'>—</p>"
        return f"<p>{esc(text)}</p>"
    values = [str(item).strip() for item in items if str(item).strip()]
    if not values:
        return "<p class='empty'>—</p>"
    return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in values) + "</ul>"


def kv_table(rows: list[tuple[str, object]], *, skip_empty: bool = False) -> str:
    cells = []
    for label, value in rows:
        if skip_empty and _is_empty_sheet_value(value):
            continue
        cells.append(
            f"<tr><th>{html_escape(label, quote=True)}</th><td>{esc(value)}</td></tr>"
        )
    if not cells:
        return "<p class='empty'>—</p>"
    return f"<table class='kv'>{''.join(cells)}</table>"


def _is_empty_sheet_value(value: object) -> bool:
    if value is None or value is False:
        return True
    if isinstance(value, str) and value.strip() in {"", "—"}:
        return True
    if isinstance(value, (list, tuple, dict)) and not value:
        return True
    return False


def stats_table(headers: list[str], values: list[object]) -> str:
    th = "".join(f"<th>{html_escape(header, quote=True)}</th>" for header in headers)
    td = "".join(f"<td>{esc(value)}</td>" for value in values)
    return f"<table class='stats'><tr>{th}</tr><tr>{td}</tr></table>"


def extra_blocks(payload: dict) -> str:
    parts: list[str] = []
    for key, title in (("motivation", "Motivação"), ("story_hook", "Gancho"), ("notes", "Notas")):
        text = str(payload.get(key) or "").strip()
        if text:
            parts.append(section(title, f"<p>{esc(text)}</p>"))
    return "".join(parts)


def wrap_sheet(payload: dict, body: str) -> str:
    name = str(payload.get("name") or "Sem nome")
    system = str(payload.get("system_name") or "")
    kind = kind_label(str(payload.get("kind") or "pc"))
    meta = " · ".join(part for part in (system, kind) if part)
    return (
        "<html><head><meta charset='utf-8'>"
        f"<style>{_SHEET_CSS}</style></head><body>"
        f"<h1>{esc(name)}</h1>"
        f"<p class='meta'>{esc(meta)}</p>"
        f"{body}{extra_blocks(payload)}"
        "</body></html>"
    )


def _sheet_body(html: str) -> str:
    match = re.search(r"<body[^>]*>(.*)</body>", html, re.I | re.S)
    return match.group(1).strip() if match else html


def format_campaign_html(payload: dict, plugin=None) -> str:
    info = payload.get("campaign") or {}
    name = str(info.get("name") or "Campanha")
    system = ""
    if plugin is not None:
        system = str(getattr(plugin, "display_name", "") or "")
    system = system or str(info.get("system_slug") or "")
    notes = str(info.get("notes") or "").strip()
    characters = [item for item in (payload.get("characters") or []) if isinstance(item, dict)]
    locations = [item for item in (payload.get("locations") or []) if isinstance(item, dict)]
    people = [item for item in (payload.get("people") or []) if isinstance(item, dict)]
    encounters = [item for item in (payload.get("encounters") or []) if isinstance(item, dict)]
    session_entries = [
        item for item in (payload.get("session_entries") or []) if isinstance(item, dict)
    ]
    documents = [item for item in (payload.get("documents") or []) if isinstance(item, dict)]

    parts: list[str] = [
        f"<h1>{esc(name)}</h1>",
        f"<p class='meta'>{esc(' · '.join(part for part in (system, 'Gestor RPG') if part))}</p>",
    ]
    if notes:
        parts.append(section("Notas da mesa", f"<p>{esc(notes)}</p>"))

    if characters:
        rows = [
            (
                "<tr>"
                f"<td>{esc(kind_label(str(item.get('kind') or '')))}</td>"
                f"<td>{esc(item.get('name'))}</td>"
                f"<td>{esc(item.get('motivation'))}</td>"
                "</tr>"
            )
            for item in characters
        ]
        parts.append(
            section(
                "Personagens",
                "<table class='list'><tr><th>Tipo</th><th>Nome</th><th>Motivação</th></tr>"
                + "".join(rows)
                + "</table>",
            )
        )
        for item in characters:
            sheet_payload = {
                **item,
                "system_name": system,
            }
            if plugin is not None:
                inner = _sheet_body(plugin.format_sheet_html(sheet_payload))
            else:
                inner = _sheet_body(fallback_sheet_html(sheet_payload, system))
            parts.append(f"<div style='page-break-before: always'></div>{inner}")
    else:
        parts.append(section("Personagens", "<p class='empty'>Nenhuma ficha.</p>"))

    if locations:
        loc_rows = [
            (
                "<tr>"
                f"<td>{esc(location_kind_label(str(item.get('kind') or '')))}</td>"
                f"<td>{esc(item.get('name'))}</td>"
                f"<td>{esc(item.get('notes'))}</td>"
                "</tr>"
            )
            for item in locations
        ]
        parts.append(
            section(
                "Locais",
                "<table class='list'><tr><th>Tipo</th><th>Nome</th><th>Descrição</th></tr>"
                + "".join(loc_rows)
                + "</table>",
            )
        )
    else:
        parts.append(section("Locais", "<p class='empty'>Nenhum local.</p>"))

    if people:
        loc_name = {
            str(item.get("uuid") or ""): str(item.get("name") or "")
            for item in locations
        }
        people_rows = []
        for item in people:
            place = loc_name.get(str(item.get("location_uuid") or ""), "")
            people_rows.append(
                "<tr>"
                f"<td>{esc(item.get('name'))}</td>"
                f"<td>{esc(item.get('role'))}</td>"
                f"<td>{esc(place)}</td>"
                f"<td>{esc(person_attitude_label(str(item.get('attitude') or '')))}</td>"
                "</tr>"
            )
        parts.append(
            section(
                "Pessoas",
                "<table class='list'><tr><th>Nome</th><th>Papel</th><th>Local</th><th>Atitude</th></tr>"
                + "".join(people_rows)
                + "</table>",
            )
        )
    else:
        parts.append(section("Pessoas", "<p class='empty'>Nenhuma pessoa.</p>"))

    encounter_blocks: list[str] = []
    for encounter in encounters:
        combatants = [
            item for item in (encounter.get("combatants") or []) if isinstance(item, dict)
        ]
        header = (
            f"<p class='headline'>{esc(encounter.get('name'))}  ·  "
            f"{esc(encounter_status_label(str(encounter.get('status') or 'preparado')))}  ·  "
            f"rodada {esc(encounter.get('round'))}  ·  "
            f"mapa {esc(encounter.get('grid_cols'))}×{esc(encounter.get('grid_rows'))}</p>"
        )
        if not combatants:
            encounter_blocks.append(header + "<p class='empty'>Nenhum combatente.</p>")
            continue
        body_rows = []
        for combatant in combatants:
            hp = f"{combatant.get('hp_current')}/{combatant.get('hp_max')}"
            body_rows.append(
                "<tr>"
                f"<td>{esc(combatant.get('initiative'))}</td>"
                f"<td>{esc(combatant.get('name'))}</td>"
                f"<td>{esc(hp)}</td>"
                "</tr>"
            )
        encounter_blocks.append(
            header
            + "<table class='list'><tr><th>Init</th><th>Nome</th><th>PV / HP</th></tr>"
            + "".join(body_rows)
            + "</table>"
        )
    parts.append(
        section(
            "Combates",
            "".join(encounter_blocks) or "<p class='empty'>Nenhum combate.</p>",
        )
    )

    log_blocks: list[str] = []
    for entry in session_entries:
        log_blocks.append(
            kv_table(
                [
                    ("Título", entry.get("title")),
                    ("Encontro", entry.get("encounter_name")),
                    ("XP", entry.get("xp")),
                    ("Tesouro", entry.get("treasure")),
                    ("O que aconteceu", entry.get("body")),
                    ("Próxima sessão", entry.get("hooks")),
                ],
                skip_empty=True,
            )
        )
    parts.append(
        section("Sessão", "".join(log_blocks) or "<p class='empty'>Nenhum registro.</p>")
    )

    if documents:
        doc_rows = [
            (
                "<tr>"
                f"<td>{esc(item.get('doc_type'))}</td>"
                f"<td>{esc(item.get('title'))}</td>"
                "</tr>"
            )
            for item in documents
        ]
        parts.append(
            section(
                "Manuais",
                "<table class='list'><tr><th>Tipo</th><th>Título</th></tr>"
                + "".join(doc_rows)
                + "</table>",
            )
        )

    return (
        "<html><head><meta charset='utf-8'>"
        f"<style>{_SHEET_CSS}</style></head><body>"
        f"{''.join(parts)}"
        "</body></html>"
    )


def fallback_sheet_html(payload: dict, system_name: str | None = None) -> str:
    attrs = payload.get("attributes") or {}
    dumped = json.dumps(attrs, ensure_ascii=False, indent=2)
    merged = dict(payload)
    if system_name and not merged.get("system_name"):
        merged["system_name"] = system_name
    return wrap_sheet(merged, f"<pre>{esc(dumped)}</pre>")
