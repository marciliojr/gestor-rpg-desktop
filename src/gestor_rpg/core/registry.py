from __future__ import annotations

from gestor_rpg.core.plugin import RPGSystemPlugin
from gestor_rpg.plugins.ddt_victory import DDTVictoryPlugin
from gestor_rpg.plugins.dnd5e import Dnd5ePlugin


class PluginRegistry:
    def __init__(self) -> None:
        plugins: list[RPGSystemPlugin] = [
            DDTVictoryPlugin(),
            Dnd5ePlugin(),
        ]
        self._by_slug = {p.slug: p for p in plugins}

    def all(self) -> list[RPGSystemPlugin]:
        return list(self._by_slug.values())

    def get(self, slug: str) -> RPGSystemPlugin:
        plugin = self._by_slug.get(slug)
        if plugin is None:
            raise KeyError(f"Sistema desconhecido: {slug}")
        return plugin

    def slugs(self) -> list[str]:
        return list(self._by_slug.keys())


_REGISTRY: PluginRegistry | None = None


def registry() -> PluginRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = PluginRegistry()
    return _REGISTRY
