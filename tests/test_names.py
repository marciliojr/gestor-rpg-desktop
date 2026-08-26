from __future__ import annotations

import random

from gestor_rpg.core.registry import PluginRegistry
from gestor_rpg.modules.names.generator import CULTURES, generate_many, generate_name
from gestor_rpg.modules.npc.generator import generate_npc


def test_name_cultures():
    rng = random.Random(0)
    for culture in CULTURES:
        name = generate_name(culture, "full", rng)
        assert len(name) >= 3
    many = generate_many("medieval", "full", 8, random.Random(1))
    assert len(many) == 8
    assert len(set(many)) == 8


def test_npc_orchestrator():
    plugin = PluginRegistry().get("ddt_victory")
    npc = generate_npc(plugin, culture="medieval", power="forte", rng=random.Random(3))
    assert npc["name"]
    assert npc["attributes"]["poder"] >= 2
    assert npc["motivation"]
