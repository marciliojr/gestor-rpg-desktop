from __future__ import annotations

import random
from typing import Any

from gestor_rpg.core.plugin import RPGSystemPlugin


def generate_monster(
    plugin: RPGSystemPlugin,
    *,
    power: str = "medio",
    level: int | None = None,
    rng: random.Random | None = None,
    category: str | None = None,
    escala: str | None = None,
    name: str | None = None,
    query: str | None = None,
) -> dict[str, Any]:
    rng = rng or random.Random()
    params: dict[str, Any] = {"power": power, "rng": rng}
    if level is not None:
        params["level"] = level
    if category:
        params["category"] = category
    if escala:
        params["escala"] = escala
    if name:
        params["name"] = name
    if query:
        params["query"] = query
    payload = plugin.generate_monster(params)
    attributes = payload.get("attributes") or plugin.default_attributes()
    return {
        "name": str(payload.get("name") or "Criatura"),
        "attributes": attributes,
        "challenge": payload.get("challenge", power),
        "notes": str(payload.get("notes") or ""),
        "slug": payload.get("slug"),
    }
