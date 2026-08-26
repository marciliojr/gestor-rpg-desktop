from __future__ import annotations

from pathlib import Path

from gestor_rpg.core.models import PdfExtract
from gestor_rpg.modules.pdf_import.ocr import ocr_page

MIN_CHARS_PER_PAGE = 50


def _tables_text(page) -> str:
    try:
        finder = page.find_tables()
    except Exception:
        return ""
    tables = getattr(finder, "tables", finder) or []
    chunks: list[str] = []
    for table in tables:
        try:
            rows = table.extract()
        except Exception:
            continue
        for row in rows or []:
            cells = [str(cell).strip() for cell in row if cell]
            if cells:
                chunks.append(" | ".join(cells))
    return "\n".join(chunks)


_FIELD_LABELS = {
    "Character Name": "Name",
    "Str Score": "Strength",
    "Dex Score": "Dexterity",
    "Con Score": "Constitution",
    "Int Score": "Intelligence",
    "Wis Score": "Wisdom",
    "Cha Score": "Charisma",
    "Max HP": "HP",
    "Current HP": "HP atual",
    "Temp HP": "Temp HP",
    "AC": "AC",
    "Speed": "Speed",
    "Level": "Level",
    "Race": "Race",
    "Background": "Background",
    "Alignment": "Alignment",
    "Archetype": "Archetype",
    "XP": "XP",
    "Proficiency": "Proficiency",
    "Initiative": "Initiative",
    "Spell Atk": "Spell Attack",
    "Spell DC": "Spell DC",
    "Sorcery Points Total": "Sorcery Points",
    "Sorcery Points Used": "Sorcery Points Used",
    "Cantrips Known": "Cantrips",
    "Metamagic Options": "Metamagic",
}


def _friendly_field(name: str) -> str:
    cleaned = (
        name.replace("Front_", "")
        .replace("Back_", "")
        .replace(" Text", "")
        .replace(" CheckBox", "")
        .strip()
    )
    return _FIELD_LABELS.get(cleaned, cleaned)


def _widgets_text(page) -> str:
    lines: list[str] = []
    try:
        widgets = list(page.widgets() or [])
    except Exception:
        return ""
    for widget in widgets:
        name = (widget.field_name or "").strip()
        value = widget.field_value
        if value in (None, "", False, "Off", "No"):
            continue
        if value is True or str(value).lower() in {"yes", "on", "true", "1"}:
            value = "yes"
        lines.append(f"{_friendly_field(name)}: {value}")
    return "\n".join(lines)


def extract_pdf(path: str | Path) -> PdfExtract:
    import fitz

    pdf_path = str(path)
    document = fitz.open(pdf_path)
    page_texts: list[str] = []
    used_ocr = False
    metadata = dict(document.metadata or {})

    for page in document:
        text = (page.get_text("text") or "").strip()
        tables = _tables_text(page)
        widgets = _widgets_text(page)
        extra = "\n".join(chunk for chunk in (tables, widgets) if chunk)
        if extra:
            text = f"{text}\n{extra}".strip()
        if len(text) < MIN_CHARS_PER_PAGE:
            ocr_text = ocr_page(page).strip()
            if ocr_text:
                text = ocr_text
                used_ocr = True
        page_texts.append(text)

    document.close()
    title = str(metadata.get("title") or Path(pdf_path).stem)
    return PdfExtract(
        path=pdf_path,
        full_text="\n\n".join(page_texts),
        page_texts=page_texts,
        used_ocr=used_ocr,
        metadata={**metadata, "title": title, "pages": len(page_texts)},
    )
