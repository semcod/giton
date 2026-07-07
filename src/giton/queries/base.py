"""Query bus primitives."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(kw_only=True)
class Query:
    """Base class for every query (read request, no side effects)."""


QueryHandler = Callable[[Query], Any]


class QueryBus:
    """Routes queries to their single registered handler."""

    def __init__(self) -> None:
        self._handlers: dict[type[Query], QueryHandler] = {}

    def register(self, query_type: type[Query], handler: QueryHandler) -> None:
        self._handlers[query_type] = handler

    def ask(self, query: Query) -> Any:
        handler = self._handlers.get(type(query))
        if handler is None:
            raise KeyError(
                f"no query handler registered for {type(query).__name__}"
            )
        return handler(query)

    def handles(self, query_type: type[Query]) -> bool:
        return query_type in self._handlers
