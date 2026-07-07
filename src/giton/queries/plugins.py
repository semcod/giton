"""Queries for the *plugins* bounded context (read side)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from giton.queries.base import Query, QueryBus


@dataclass(kw_only=True)
class ListPlugins(Query):
    """Return the user's registered plugin records."""


@dataclass(kw_only=True)
class ListCatalog(Query):
    """Return the full built-in catalog as ``{name: CatalogEntry}``."""


@dataclass(kw_only=True)
class ListCategories(Query):
    """Return ``{category: [plugin_name, …]}``."""


@dataclass(kw_only=True)
class PluginExists(Query):
    """Is *name* present in the user registry?"""

    name: str


def register(bus: QueryBus) -> None:
    """Wire the plugin queries onto *bus*."""
    from giton import catalog
    from giton.config import load_plugins

    def _list(_q: ListPlugins) -> list[Any]:
        return load_plugins()

    def _catalog(_q: ListCatalog) -> dict[str, Any]:
        return dict(catalog.CATALOG)

    def _categories(_q: ListCategories) -> dict[str, list[str]]:
        return catalog.list_categories()

    def _exists(q: PluginExists) -> bool:
        return any(p.name == q.name for p in load_plugins())

    bus.register(ListPlugins, _list)
    bus.register(ListCatalog, _catalog)
    bus.register(ListCategories, _categories)
    bus.register(PluginExists, _exists)
