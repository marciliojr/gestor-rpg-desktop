from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QWidget

from gestor_rpg.core.models import ParsedSheet, PdfExtract
from gestor_rpg.core.plugin import RPGSystemPlugin, SheetWidget
from gestor_rpg.plugins._ddt import (
    ddt_defaults,
    ddt_initiative_bonus,
    VICTORY_HP_PATHS,
    format_ddt_monster_preview,
    format_ddt_sheet_html,
    generate_ddt_monster,
    generate_ddt_npc,
    normalize_victory_attributes,
    parse_ddt_sheet,
)
from gestor_rpg.plugins._ddt_bestiary import BESTIARY
from gestor_rpg.plugins._ddt_widget import DdtSheetWidget


class DDTVictoryPlugin(RPGSystemPlugin):
    slug = "ddt_victory"
    display_name = "3D&T Victory"

    def default_attributes(self) -> dict:
        return ddt_defaults()

    def validate_attributes(self, data: dict) -> list[str]:
        if not isinstance(data, dict):
            return super().validate_attributes(data)
        return super().validate_attributes(normalize_victory_attributes(data))

    def create_sheet_widget(self, parent: QWidget | None = None) -> SheetWidget:
        return DdtSheetWidget(parent=parent)

    def generate_npc(self, params: dict[str, Any] | None = None) -> dict:
        return generate_ddt_npc(params)

    def try_parse_sheet(self, extracted: PdfExtract) -> ParsedSheet | None:
        return parse_ddt_sheet(extracted)

    def hp_paths(self) -> dict[str, tuple[str, str]]:
        return VICTORY_HP_PATHS

    def monster_catalog(self) -> list[dict]:
        return BESTIARY

    def generate_monster(self, params: dict[str, Any] | None = None) -> dict:
        return generate_ddt_monster(params)

    def format_monster_preview(self, payload: dict[str, Any]) -> str:
        return format_ddt_monster_preview(payload)

    def format_sheet_html(self, payload: dict[str, Any]) -> str:
        return format_ddt_sheet_html(payload)

    def initiative_bonus(self, attributes: dict) -> int:
        return ddt_initiative_bonus(attributes)
