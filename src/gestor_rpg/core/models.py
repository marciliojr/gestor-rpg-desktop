from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Campaign:
    id: int
    name: str
    system_id: int
    system_slug: str
    system_name: str
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Character:
    id: int | None
    uuid: str
    campaign_id: int | None
    system_id: int
    kind: str
    name: str
    notes: str = ""
    motivation: str = ""
    story_hook: str = ""
    attributes: dict = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


@dataclass
class ImportedDocument:
    id: int | None
    uuid: str
    title: str
    source_path: str
    doc_type: str
    system_id: int | None
    character_id: int | None
    extracted_text: str = ""
    metadata: dict = field(default_factory=dict)
    created_at: str = ""


@dataclass
class DiceRecord:
    id: int | None
    expression: str
    total: int
    detail: list = field(default_factory=list)
    created_at: str = ""


@dataclass
class PdfExtract:
    path: str
    full_text: str
    page_texts: list[str]
    used_ocr: bool
    metadata: dict = field(default_factory=dict)


@dataclass
class ParsedSheet:
    name: str | None
    attributes: dict


@dataclass
class DocumentHit:
    id: int
    title: str
    source_path: str
    doc_type: str
    system_id: int | None
    snippet: str
    rank: float
    extracted_text: str = ""


@dataclass
class CharacterHit:
    id: int
    name: str
    kind: str
    snippet: str
    rank: float


@dataclass
class SessionEntry:
    id: int | None
    uuid: str
    campaign_id: int
    encounter_id: int | None = None
    title: str = ""
    body: str = ""
    xp: str = ""
    treasure: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Encounter:
    id: int | None
    campaign_id: int
    name: str
    round: int = 1
    grid_cols: int = 12
    grid_rows: int = 8
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Combatant:
    id: int | None
    encounter_id: int
    character_id: int | None
    name: str
    initiative: int = 0
    hp_current: int = 0
    hp_max: int = 0
    resource_current: int = 0
    resource_max: int = 0
    action_current: int = 0
    action_max: int = 0
    is_active: bool = False
    sort_order: int = 0
    notes: str = ""
    snapshot: dict = field(default_factory=dict)
    grid_x: int = -1
    grid_y: int = -1
