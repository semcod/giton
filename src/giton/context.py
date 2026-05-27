"""Collect git context (status, staged diff, recent commits)."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path


def _run(cmd: list[str], cwd: Path | None = None) -> str:
    res = subprocess.run(
        cmd, cwd=cwd, check=False, capture_output=True, text=True
    )
    return res.stdout


def repo_root(cwd: Path | None = None) -> Path | None:
    out = _run(["git", "rev-parse", "--show-toplevel"], cwd=cwd).strip()
    return Path(out) if out else None


@dataclass
class GitContext:
    root: Path
    staged_paths: list[str] = field(default_factory=list)
    staged_diff: str = ""
    last_commit_subject: str = ""
    last_commit_body: str = ""
    upstream_range: str = ""

    def diff_file(self) -> Path:
        f = self.root / ".giton" / "last_diff.patch"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(self.staged_diff)
        return f

    def paths_arg(self) -> str:
        return " ".join(self.staged_paths) if self.staged_paths else "."


def collect(cwd: Path | None = None) -> GitContext | None:
    root = repo_root(cwd)
    if not root:
        return None
    staged_names = [
        p.strip()
        for p in _run(
            ["git", "diff", "--cached", "--name-only"], cwd=root
        ).splitlines()
        if p.strip()
    ]
    staged_diff = _run(["git", "diff", "--cached"], cwd=root)
    last_subject = _run(["git", "log", "-1", "--pretty=%s"], cwd=root).strip()
    last_body = _run(["git", "log", "-1", "--pretty=%b"], cwd=root).strip()
    upstream = _run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        cwd=root,
    ).strip()
    rng = f"{upstream}..HEAD" if upstream else ""
    return GitContext(
        root=root,
        staged_paths=staged_names,
        staged_diff=staged_diff,
        last_commit_subject=last_subject,
        last_commit_body=last_body,
        upstream_range=rng,
    )
