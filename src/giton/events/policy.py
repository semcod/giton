"""Domain events for the *policy* bounded context.

Stream name: ``"policy"``.
"""
from __future__ import annotations

from dataclasses import dataclass

from giton.events.base import Event

STREAM = "policy"


@dataclass(kw_only=True)
class PolicyEvaluated(Event):
    """The built-in policy engine ran for a trigger."""

    trigger: str = ""
    finding_count: int = 0
    error_count: int = 0


@dataclass(kw_only=True)
class FindingsSaved(Event):
    """Policy findings were persisted to ``.giton/last_check.json``."""

    count: int = 0


@dataclass(kw_only=True)
class FindingFixed(Event):
    """The auto-fix command for a single finding was applied."""

    policy: str = ""
    location: str = ""


@dataclass(kw_only=True)
class FixesApplied(Event):
    """A batch of available auto-fixes was applied."""

    applied: int = 0
    total: int = 0
