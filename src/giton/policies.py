"""Built-in policy engine.

Policies operate on a `GitContext` (staged diff, paths, last commit) and
return a list of `Finding` objects. The engine is intentionally
plugin-free so giton always provides baseline value, even with no
external tools installed.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from giton.context import GitContext
from giton.repo_config import RepoConfig


Severity = str  # "error" | "warn" | "info"


@dataclass
class Finding:
    policy: str
    severity: Severity
    message: str
    location: str = ""

    @property
    def is_error(self) -> bool:
        return self.severity == "error"


# --- individual checks ----------------------------------------------------

def _check_conventional_commits(
    ctx: GitContext, opts: dict, trigger: str
) -> list[Finding]:
    if trigger not in {"commit-msg", "post-commit", "pre-push"}:
        return []
    subject = ctx.last_commit_subject.strip()
    if not subject:
        return []
    types = opts.get("types") or []
    max_len = int(opts.get("max_subject_length") or 72)
    require_scope = bool(opts.get("require_scope", False))
    findings: list[Finding] = []
    if len(subject) > max_len:
        findings.append(
            Finding(
                "conventional_commits", "warn",
                f"subject is {len(subject)} chars (max {max_len})",
                location="HEAD",
            )
        )
    type_alt = "|".join(map(re.escape, types)) if types else r"[a-z]+"
    scope_part = r"\([^)]+\)" if require_scope else r"(?:\([^)]+\))?"
    pattern = rf"^({type_alt}){scope_part}!?:\s.+"
    if not re.match(pattern, subject):
        findings.append(
            Finding(
                "conventional_commits", "error",
                f"subject does not match Conventional Commits "
                f"(types: {', '.join(types) or 'any'}): {subject!r}",
                location="HEAD",
            )
        )
    return findings


def _check_no_wip(ctx: GitContext, opts: dict, trigger: str) -> list[Finding]:
    if trigger not in {"commit-msg", "post-commit", "pre-push"}:
        return []
    subject = ctx.last_commit_subject.strip()
    if not subject:
        return []
    for raw in opts.get("patterns", []) or []:
        if re.search(raw, subject):
            return [Finding(
                "no_wip_commits", "error",
                f"WIP-style commit subject not allowed: {subject!r}",
                location="HEAD",
            )]
    return []


_SECRET_HUNK_RE = re.compile(r"^\+", re.MULTILINE)


def _check_no_secrets(ctx: GitContext, opts: dict, trigger: str) -> list[Finding]:
    if trigger != "pre-commit":
        return []
    if not ctx.staged_diff:
        return []
    findings: list[Finding] = []
    added_lines = [
        line[1:]
        for line in ctx.staged_diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    blob = "\n".join(added_lines)
    for pat in opts.get("patterns", []) or []:
        try:
            rx = re.compile(pat)
        except re.error:
            continue
        if rx.search(blob):
            findings.append(Finding(
                "no_secrets", "error",
                f"secret-like content detected (pattern: {pat})",
                location="staged diff",
            ))
    return findings


def _check_max_file_size(
    ctx: GitContext, opts: dict, trigger: str
) -> list[Finding]:
    if trigger != "pre-commit":
        return []
    limit = int(opts.get("kb") or 512) * 1024
    findings: list[Finding] = []
    for rel in ctx.staged_paths:
        p = ctx.root / rel
        try:
            sz = p.stat().st_size
        except FileNotFoundError:
            continue
        if sz > limit:
            findings.append(Finding(
                "max_file_size", "error",
                f"{rel} is {sz/1024:.1f} KB (limit {limit/1024:.0f} KB)",
                location=rel,
            ))
    return findings


CheckFn = Callable[[GitContext, dict, str], list[Finding]]
CHECKS: dict[str, CheckFn] = {
    "conventional_commits": _check_conventional_commits,
    "no_wip_commits": _check_no_wip,
    "no_secrets": _check_no_secrets,
    "max_file_size": _check_max_file_size,
}


# --- engine entry point ---------------------------------------------------

def evaluate(
    ctx: GitContext, repo_cfg: RepoConfig, trigger: str
) -> list[Finding]:
    out: list[Finding] = []
    for name, fn in CHECKS.items():
        opts = repo_cfg.policy(name)
        if not opts.get("enabled", True):
            continue
        try:
            out.extend(fn(ctx, opts, trigger))
        except Exception as e:  # pragma: no cover - defensive
            out.append(Finding(name, "warn", f"check raised: {e}"))
    return out


def has_errors(findings: list[Finding]) -> bool:
    return any(f.is_error for f in findings)
