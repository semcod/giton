"""Queries for the *policy* bounded context (read side)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from giton.queries.base import Query, QueryBus


@dataclass(kw_only=True)
class EvaluatePolicies(Query):
    """Run the built-in policy engine for *trigger*."""

    ctx: Any  # giton.context.GitContext
    repo_cfg: Any  # giton.repo_config.RepoConfig
    trigger: str


@dataclass(kw_only=True)
class LoadFindings(Query):
    """Load previously saved findings from the repo."""

    root: Path


@dataclass(kw_only=True)
class ListActivePolicies(Query):
    """Return ``{policy_name: enabled_bool}`` for the repo."""

    repo_cfg: Any  # giton.repo_config.RepoConfig


def register(bus: QueryBus) -> None:
    """Wire the policy queries onto *bus*."""
    from giton import policies, store

    def _evaluate(q: EvaluatePolicies) -> list[Any]:
        return policies.evaluate(q.ctx, q.repo_cfg, q.trigger)

    def _load(q: LoadFindings) -> list[Any]:
        return store.load_findings(q.root)

    def _active(q: ListActivePolicies) -> dict[str, bool]:
        return {
            name: bool(q.repo_cfg.policy(name).get("enabled", True))
            for name in policies.CHECKS
        }

    bus.register(EvaluatePolicies, _evaluate)
    bus.register(LoadFindings, _load)
    bus.register(ListActivePolicies, _active)
