from __future__ import annotations

import json
import random
from importlib.resources import files
from typing import Any

CULTURES = {
    "medieval": "Medieval",
    "elfico": "Élfico",
    "anao": "Anão",
    "oriental": "Oriental",
}


def _load(culture: str) -> dict[str, list[str]]:
    resource = files("gestor_rpg.resources.names").joinpath(f"{culture}.json")
    data: dict[str, Any] = json.loads(resource.read_text(encoding="utf-8"))
    return {
        "given": list(data.get("given") or []),
        "surname": list(data.get("surname") or []),
        "nickname": list(data.get("nickname") or []),
    }


def generate_name(
    culture: str,
    kind: str = "full",
    rng: random.Random | None = None,
) -> str:
    rng = rng or random.Random()
    data = _load(culture)
    given = rng.choice(data["given"]) if data["given"] else "Nameless"
    surname = rng.choice(data["surname"]) if data["surname"] else ""
    nickname = rng.choice(data["nickname"]) if data["nickname"] else ""
    if kind == "given":
        return given
    if kind == "surname":
        return surname or given
    if kind == "nickname":
        return f"{given} {nickname}".strip()
    if surname:
        return f"{given} {surname}"
    return given


def generate_many(
    culture: str,
    kind: str = "full",
    count: int = 10,
    rng: random.Random | None = None,
) -> list[str]:
    rng = rng or random.Random()
    names: list[str] = []
    seen: set[str] = set()
    attempts = 0
    while len(names) < count and attempts < count * 20:
        attempts += 1
        name = generate_name(culture, kind, rng)
        if name not in seen:
            seen.add(name)
            names.append(name)
    return names
