"""Event-sourcing layer for giton.

The ``events`` package holds the *facts* of the system: things that have
already happened (a plugin was installed, a policy was evaluated, …).
It exposes three building blocks:

* :class:`Event`           — base dataclass for every domain event.
* :class:`EventBus`        — in-process publish/subscribe ("event-bus").
* :class:`EventStore`      — append-only JSONL log ("event-store").

Per bounded-context domain events live next to their siblings:
:mod:`giton.events.plugins` and :mod:`giton.events.policy`.
"""
from giton.events.base import Event, EventHandler, EventBus, EventStore

__all__ = ["Event", "EventHandler", "EventBus", "EventStore"]
