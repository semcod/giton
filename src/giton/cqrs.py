"""Composition root for giton's CQRS + Event-Sourcing layer.

This module wires the four singletons the rest of the codebase talks to:

* :data:`event_store` — append-only JSONL log at ``.giton/events.jsonl``
  (resolved lazily per repo; a no-op outside a git repository).
* :data:`event_bus`   — in-process pub/sub backed by the store.
* :data:`command_bus` — routes commands from the ``plugins`` and ``policy``
  bounded contexts (:mod:`giton.commands`).
* :data:`query_bus`   — answers queries from the same contexts
  (:mod:`giton.queries`).

The existing modules (``giton.plugins``, ``giton.policies``, ``giton.store``,
``giton.fixups``) remain the source of truth for the actual work; the buses
route to them and emit domain events so the system becomes observable and
replayable. Callers should prefer ``cqrs.command_bus.dispatch(...)`` /
``cqrs.query_bus.ask(...)`` over reaching into the implementation modules
directly.
"""
from __future__ import annotations

from pathlib import Path

from giton.commands.base import CommandBus
from giton.context import repo_root
from giton.events.base import EventBus, EventStore
from giton.queries.base import QueryBus

#: Where the event-store lands inside a repository (local-first, like
#: ``.giton/last_check.json``).
EVENT_STORE_REL = ".giton/events.jsonl"


def _event_store_path() -> Path | None:
    """Resolve the event-store path for the current repo, or ``None``."""
    root = repo_root()
    return (root / EVENT_STORE_REL) if root else None


# --- singletons -----------------------------------------------------------
event_store: EventStore = EventStore(_event_store_path)
event_bus: EventBus = EventBus(event_store)
command_bus: CommandBus = CommandBus()
query_bus: QueryBus = QueryBus()


def _wire() -> None:
    """Register every bounded-context handler onto the singletons above."""
    from giton.commands.plugins import register as _plugin_cmds
    from giton.commands.policy import register as _policy_cmds
    from giton.queries.plugins import register as _plugin_queries
    from giton.queries.policy import register as _policy_queries

    _plugin_cmds(command_bus, event_bus)
    _policy_cmds(command_bus, event_bus)
    _plugin_queries(query_bus)
    _policy_queries(query_bus)


_wire()
