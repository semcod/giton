"""Query side of giton's CQRS split.

A *query* reads state with no side effects (list plugins, evaluate policies,
load saved findings). Queries are answered through the :class:`QueryBus` by a
single registered handler.

Per bounded-context queries live in :mod:`giton.queries.plugins` and
:mod:`giton.queries.policy`.
"""
from giton.queries.base import Query, QueryBus, QueryHandler

__all__ = ["Query", "QueryBus", "QueryHandler"]
