from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from PySide6.QtWidgets import QWidget

from gestor_rpg.core.models import ParsedSheet, PdfExtract


class SheetWidget(QWidget):
    """Ficha visual de um sistema. Lê e grava o dicionário de atributos."""

    def get_attributes(self) -> dict:
        raise NotImplementedError

    def set_attributes(self, data: dict) -> None:
        raise NotImplementedError


class RPGSystemPlugin(ABC):
    slug: str
    display_name: str

    @abstractmethod
    def default_attributes(self) -> dict:
        ...

    def validate_attributes(self, data: dict) -> list[str]:
        errors: list[str] = []
        expected = self.default_attributes()
        if not isinstance(data, dict):
            return ["Atributos devem ser um objeto JSON"]
        for key, sample in expected.items():
            if key not in data:
                errors.append(f"Campo ausente: {key}")
                continue
            if not _compatible_type(data[key], sample):
                errors.append(f"Tipo inválido em {key}")
        return errors

    @abstractmethod
    def create_sheet_widget(self, parent: QWidget | None = None) -> SheetWidget:
        ...

    @abstractmethod
    def generate_npc(self, params: dict[str, Any] | None = None) -> dict:
        """Retorna attributes, motivation e story_hook."""

    def try_parse_sheet(self, extracted: PdfExtract) -> ParsedSheet | None:
        return None

    def hp_paths(self) -> dict[str, tuple[str, str]]:
        """Paths JSON: hp obrigatório; resource e action opcionais."""
        return {"hp": ("hp_atual", "hp_max")}

    def format_monster_preview(self, payload: dict[str, Any]) -> str:
        lines = [str(payload.get("name") or "Criatura")]
        notes = str(payload.get("notes") or "").strip()
        if notes:
            lines.extend(["", notes])
        attrs = payload.get("attributes") or {}
        if isinstance(attrs, dict) and attrs:
            lines.append("")
            for key, value in attrs.items():
                if value in (None, "", [], {}, False):
                    continue
                if isinstance(value, list):
                    rendered = ", ".join(str(item) for item in value if str(item).strip())
                    if rendered:
                        lines.append(f"{key}: {rendered}")
                elif isinstance(value, dict):
                    continue
                else:
                    lines.append(f"{key}: {value}")
        return "\n".join(lines)

    def format_sheet_html(self, payload: dict[str, Any]) -> str:
        from gestor_rpg.modules.sheet_export.html import fallback_sheet_html

        return fallback_sheet_html(payload, self.display_name)

    def monster_catalog(self) -> list[dict]:
        """Catálogo categorizado do sistema. Vazio se o plugin só gera aleatório."""
        return []

    def generate_monster(self, params: dict[str, Any] | None = None) -> dict:
        """Retorna name, attributes, challenge e notes."""
        payload = self.generate_npc(params)
        power = str((params or {}).get("power") or "medio")
        return {
            "name": "Criatura",
            "attributes": payload.get("attributes") or self.default_attributes(),
            "challenge": power,
            "notes": payload.get("story_hook") or "",
        }

    def initiative_bonus(self, attributes: dict) -> int:
        return 0


def get_attr_path(data: dict, path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def set_attr_path(data: dict, path: str, value: Any) -> None:
    parts = path.split(".")
    current: Any = data
    for part in parts[:-1]:
        nxt = current.get(part)
        if not isinstance(nxt, dict):
            nxt = {}
            current[part] = nxt
        current = nxt
    current[parts[-1]] = value


def read_pool(attributes: dict, hp_paths: dict[str, tuple[str, str]]) -> dict[str, int]:
    hp_cur, hp_max = hp_paths.get("hp", ("hp_atual", "hp_max"))
    result = {
        "hp_current": int(get_attr_path(attributes, hp_cur) or 0),
        "hp_max": int(get_attr_path(attributes, hp_max) or 0),
        "resource_current": 0,
        "resource_max": 0,
        "action_current": 0,
        "action_max": 0,
    }
    resource = hp_paths.get("resource")
    if resource:
        result["resource_current"] = int(get_attr_path(attributes, resource[0]) or 0)
        result["resource_max"] = int(get_attr_path(attributes, resource[1]) or 0)
    action = hp_paths.get("action")
    if action:
        result["action_current"] = int(get_attr_path(attributes, action[0]) or 0)
        result["action_max"] = int(get_attr_path(attributes, action[1]) or 0)
    return result


def write_pool(
    attributes: dict,
    hp_paths: dict[str, tuple[str, str]],
    *,
    hp_current: int | None = None,
    hp_max: int | None = None,
    resource_current: int | None = None,
    resource_max: int | None = None,
    action_current: int | None = None,
    action_max: int | None = None,
) -> dict:
    hp_cur, hp_mx = hp_paths.get("hp", ("hp_atual", "hp_max"))
    if hp_current is not None:
        set_attr_path(attributes, hp_cur, int(hp_current))
    if hp_max is not None:
        set_attr_path(attributes, hp_mx, int(hp_max))
    resource = hp_paths.get("resource")
    if resource:
        if resource_current is not None:
            set_attr_path(attributes, resource[0], int(resource_current))
        if resource_max is not None:
            set_attr_path(attributes, resource[1], int(resource_max))
    action = hp_paths.get("action")
    if action:
        if action_current is not None:
            set_attr_path(attributes, action[0], int(action_current))
        if action_max is not None:
            set_attr_path(attributes, action[1], int(action_max))
    return attributes


def _compatible_type(value: object, sample: object) -> bool:
    if sample is None:
        return True
    if isinstance(sample, bool):
        return isinstance(value, bool)
    if isinstance(sample, int) and not isinstance(sample, bool):
        return isinstance(value, int) and not isinstance(value, bool)
    if isinstance(sample, float):
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if isinstance(sample, str):
        return isinstance(value, str)
    if isinstance(sample, list):
        return isinstance(value, list)
    if isinstance(sample, dict):
        return isinstance(value, dict)
    return True
