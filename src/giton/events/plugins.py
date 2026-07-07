"""Domain events for the *plugins* bounded context.

Stream name: ``"plugins"``.
"""
from __future__ import annotations

from dataclasses import dataclass

from giton.events.base import Event

STREAM = "plugins"


@dataclass(kw_only=True)
class PluginInstalled(Event):
    """A plugin was registered (and, where applicable, pip-installed)."""

    name: str
    source: str = "catalog"  # "catalog" | "default" | "category"


@dataclass(kw_only=True)
class PluginUninstalled(Event):
    """A plugin record was removed from the user registry."""

    name: str


@dataclass(kw_only=True)
class PluginEnabled(Event):
    """A registered plugin was enabled for its triggers."""

    name: str


@dataclass(kw_only=True)
class PluginDisabled(Event):
    """A registered plugin was disabled."""

    name: str
