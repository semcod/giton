"""Core event-sourcing primitives: ``Event``, ``EventBus``, ``EventStore``.

Design notes
------------
* Events are value objects describing a fact that already happened. They are
  treated as immutable by convention; the bus stamps ``event_id`` /
  ``occurred_at`` at publish time, so the base dataclass is intentionally not
  frozen.
* The :class:`EventBus` is synchronous and in-process. Handler failures are
  isolated: a buggy subscriber prints a warning and the remaining subscribers
  still receive the event. The publishing command is never broken by a
  listener.
* The :class:`EventStore` is an append-only JSONL log. One line == one event.
  Its path is resolved lazily through a callable so the same store can be
  repo-aware in production (``.giton/events.jsonl``) and pinned to a temp file
  in tests.
"""
from __future__ import annotations

import datetime as _dt
import json
import sys
import threading
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
# ``kw_only=True`` is used on every dataclass in the event/command/query
# hierarchies so subclasses can add required fields on top of the defaulted
# base fields (e.g. ``PluginInstalled(name="…")``) without tripping the
# "non-default argument follows default argument" rule.
from typing import Any, Callable, Union

EventHandler = Callable[["Event"], None]

#: A path is either a concrete ``Path``, ``None`` (in-memory / disabled), or a
#: callable that returns one of those (resolved lazily on every append/read).
PathLike = Union[Path, None, Callable[[], Union[Path, None]]]


def _utcnow_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


@dataclass(kw_only=True)
class Event:
    """Base class for every domain event.

    Subclasses add the fields that describe the fact, e.g.::

        @dataclass
        class PluginInstalled(Event):
            name: str
            source: str = "catalog"

    ``event_id`` and ``occurred_at`` are filled in by the bus at publish time.
    """

    event_id: str = ""
    occurred_at: str = ""

    @property
    def event_type(self) -> str:
        return type(self).__name__

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["event_type"] = self.event_type
        return data


class EventBus:
    """In-process publish/subscribe event bus.

    Subscribers may register globally (receive every event) or for a specific
    event type (given as a string or an :class:`Event` subclass).
    """

    def __init__(self, store: "EventStore | None" = None) -> None:
        self._store = store
        self._typed: dict[str, list[EventHandler]] = {}
        self._global: list[EventHandler] = []
        self._lock = threading.RLock()

    # -- subscription ------------------------------------------------------

    def subscribe(
        self,
        handler: EventHandler,
        *,
        event_type: "str | type[Event] | None" = None,
    ) -> None:
        key: str | None = None
        if event_type is not None:
            key = event_type if isinstance(event_type, str) else event_type.__name__
        with self._lock:
            if key is None:
                self._global.append(handler)
            else:
                self._typed.setdefault(key, []).append(handler)

    def clear(self) -> None:
        """Remove every subscriber (used by tests)."""
        with self._lock:
            self._typed.clear()
            self._global.clear()

    # -- publication -------------------------------------------------------

    def publish(self, event: Event, *, stream: str = "default") -> Event:
        """Stamp, persist (if a store is configured) and dispatch *event*."""
        self._stamp(event)
        if self._store is not None:
            self._store.append(event, stream=stream)
        self._dispatch(event)
        return event

    # -- internals ---------------------------------------------------------

    @staticmethod
    def _stamp(event: Event) -> None:
        if not event.event_id:
            event.event_id = uuid.uuid4().hex
        if not event.occurred_at:
            event.occurred_at = _utcnow_iso()

    def _dispatch(self, event: Event) -> None:
        with self._lock:
            handlers = list(self._global) + list(
                self._typed.get(event.event_type, [])
            )
        for handler in handlers:
            try:
                handler(event)
            except Exception as exc:  # pragma: no cover - defensive logging
                name = getattr(handler, "__name__", repr(handler))
                print(
                    f"giton: event handler {name} raised on "
                    f"{event.event_type}: {exc}",
                    file=sys.stderr,
                )


class EventStore:
    """Append-only JSONL event store.

    Pass either a concrete :class:`~pathlib.Path`, ``None`` (events are then
    delivered to subscribers but not persisted), or a zero-arg callable
    returning a path (resolved on every call — handy for repo-aware paths).
    """

    def __init__(self, path: PathLike = None) -> None:
        self._path = path

    def _resolve(self) -> Path | None:
        resolved = self._path() if callable(self._path) else self._path
        return resolved

    def append(self, event: Event, *, stream: str = "default") -> None:
        path = self._resolve()
        if path is None:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {"stream": stream, **event.to_dict()}
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")

    def read(self, *, stream: str | None = None) -> list[dict[str, Any]]:
        """Return stored event records, optionally filtered by *stream*."""
        path = self._resolve()
        if path is None or not path.exists():
            return []
        out: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if stream is None or rec.get("stream") == stream:
                out.append(rec)
        return out

    def clear(self) -> None:
        """Truncate the underlying file (used by tests)."""
        path = self._resolve()
        if path is not None and path.exists():
            path.unlink()
