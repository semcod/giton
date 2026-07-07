"""Commands for the *policy* bounded context.

Handlers delegate to :mod:`giton.store` and :mod:`giton.fixups` and emit
domain events (:mod:`giton.events.policy`).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from giton.commands.base import Command, CommandBus
from giton.events.base import EventBus
from giton.events import policy as ev


@dataclass(kw_only=True)
class SaveFindings(Command):
    """Persist policy findings so ``policy fix`` can read them later."""

    findings: list[Any]  # list[policies.Finding]
    root: Path


@dataclass(kw_only=True)
class ApplyFix(Command):
    """Apply the auto-fix for a single finding."""

    finding: Any  # policies.Finding
    cwd: Path
    yes: bool = False


@dataclass(kw_only=True)
class ApplyAllFixes(Command):
    """Apply every available auto-fix in *findings*."""

    findings: list[Any]
    cwd: Path
    yes: bool = False


def register(bus: CommandBus, events: EventBus) -> None:
    """Wire the policy commands onto *bus*, publishing to *events*."""
    from giton import fixups, store

    def _save(cmd: SaveFindings) -> Path:
        path = store.save_findings(cmd.findings, cmd.root)
        events.publish(ev.FindingsSaved(count=len(cmd.findings)), stream=ev.STREAM)
        return path

    def _apply_fix(cmd: ApplyFix) -> bool:
        ok = fixups.apply_fix(cmd.finding, cmd.cwd, yes=cmd.yes)
        if ok:
            events.publish(
                ev.FindingFixed(
                    policy=cmd.finding.policy, location=cmd.finding.location
                ),
                stream=ev.STREAM,
            )
        return ok

    def _apply_all(cmd: ApplyAllFixes) -> tuple[int, int]:
        applied, total = fixups.apply_all(cmd.findings, cmd.cwd, yes=cmd.yes)
        events.publish(
            ev.FixesApplied(applied=applied, total=total), stream=ev.STREAM
        )
        return applied, total

    bus.register(SaveFindings, _save)
    bus.register(ApplyFix, _apply_fix)
    bus.register(ApplyAllFixes, _apply_all)
