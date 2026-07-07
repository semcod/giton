"""Commands for the *plugins* bounded context.

Handlers delegate the real work to :mod:`giton.plugins` / :mod:`giton.config`
(the existing implementation, left untouched) and emit domain events through
the shared :class:`~giton.events.EventBus` so plugin lifecycle changes become
observable and replayable from the event-store.
"""
from __future__ import annotations

from dataclasses import dataclass

from giton.commands.base import Command, CommandBus
from giton.events.base import EventBus
from giton.events import plugins as ev


@dataclass(kw_only=True)
class InstallPlugin(Command):
    name: str
    prefer_local: bool = True


@dataclass(kw_only=True)
class InstallDefaults(Command):
    pass


@dataclass(kw_only=True)
class InstallCategory(Command):
    category: str


@dataclass(kw_only=True)
class UninstallPlugin(Command):
    name: str


@dataclass(kw_only=True)
class SetPluginEnabled(Command):
    name: str
    enabled: bool


def register(bus: CommandBus, events: EventBus) -> None:
    """Wire the plugin commands onto *bus*, publishing to *events*."""
    from giton import catalog
    from giton import plugins as plug
    from giton.config import load_plugins, save_plugins

    def _install(cmd: InstallPlugin) -> bool:
        ok = plug.install_from_catalog(cmd.name, prefer_local=cmd.prefer_local)
        if ok:
            events.publish(
                ev.PluginInstalled(name=cmd.name, source="catalog"),
                stream=ev.STREAM,
            )
        return ok

    def _install_defaults(_cmd: InstallDefaults) -> None:
        plug.install_defaults()
        for name in catalog.DEFAULT_PLUGIN_NAMES:
            events.publish(
                ev.PluginInstalled(name=name, source="default"),
                stream=ev.STREAM,
            )

    def _install_category(cmd: InstallCategory) -> int:
        return plug.install_category(cmd.category)

    def _uninstall(cmd: UninstallPlugin) -> bool:
        ok = plug.uninstall(cmd.name)
        if ok:
            events.publish(
                ev.PluginUninstalled(name=cmd.name), stream=ev.STREAM
            )
        return ok

    def _set_enabled(cmd: SetPluginEnabled) -> bool:
        plugins = load_plugins()
        found = any(p.name == cmd.name for p in plugins)
        if not found:
            return False
        for p in plugins:
            if p.name == cmd.name:
                p.enabled = cmd.enabled
        save_plugins(plugins)
        event = ev.PluginEnabled if cmd.enabled else ev.PluginDisabled
        events.publish(event(name=cmd.name), stream=ev.STREAM)
        return True

    bus.register(InstallPlugin, _install)
    bus.register(InstallDefaults, _install_defaults)
    bus.register(InstallCategory, _install_category)
    bus.register(UninstallPlugin, _uninstall)
    bus.register(SetPluginEnabled, _set_enabled)
