"""Install / uninstall git hooks that delegate to `gix hook <name>`."""
from __future__ import annotations

import os
import stat
from pathlib import Path

HOOKS = ("pre-commit", "post-commit", "pre-push")

HOOK_TEMPLATE = """#!/bin/sh
# Installed by gix — delegates to: gix hook {name}
exec gix hook {name} "$@"
"""


def hooks_dir(repo_root: Path) -> Path:
    return repo_root / ".git" / "hooks"


def install(repo_root: Path) -> list[Path]:
    hd = hooks_dir(repo_root)
    if not hd.exists():
        raise FileNotFoundError(f"Not a git repository: {repo_root}")
    written: list[Path] = []
    for hook in HOOKS:
        target = hd / hook
        if target.exists():
            backup = target.with_suffix(target.suffix + ".gix-backup")
            if not backup.exists():
                target.rename(backup)
        target.write_text(HOOK_TEMPLATE.format(name=hook))
        target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        written.append(target)
    return written


def uninstall(repo_root: Path) -> list[Path]:
    hd = hooks_dir(repo_root)
    removed: list[Path] = []
    for hook in HOOKS:
        target = hd / hook
        if target.exists() and "gix hook" in target.read_text():
            target.unlink()
            backup = target.with_suffix(target.suffix + ".gix-backup")
            if backup.exists():
                backup.rename(target)
            removed.append(target)
    return removed
