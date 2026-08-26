from __future__ import annotations

import random
from typing import Any

from gestor_rpg.core.plugin import RPGSystemPlugin
from gestor_rpg.modules.names.generator import generate_name


def generate_npc(
    plugin: RPGSystemPlugin,
    *,
    culture: str = "medieval",
    power: str = "medio",
    rng: random.Random | None = None,
) -> dict[str, Any]:
    rng = rng or random.Random()
    payload = plugin.generate_npc({"power": power, "rng": rng})
    name = generate_name(culture, "full", rng)
    return {
        "name": name,
        "attributes": payload.get("attributes") or plugin.default_attributes(),
        "motivation": payload.get("motivation") or "",
        "story_hook": payload.get("story_hook") or "",
    }
