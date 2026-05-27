"""Tiny interactive helpers used by hooks and the shell.

Kept dependency-free (stdlib + rich) so it works even in headless CI
when `--non-interactive` is set.
"""
from __future__ import annotations

import os
import sys

from rich.console import Console

console = Console()


def is_tty() -> bool:
    if os.environ.get("GITON_NON_INTERACTIVE"):
        return False
    return sys.stdin.isatty() and sys.stdout.isatty()


def confirm(question: str, *, default: bool = True) -> bool:
    """Ask a yes/no question. Returns `default` when not on a TTY."""
    if not is_tty():
        return default
    suffix = " [Y/n] " if default else " [y/N] "
    try:
        ans = input(question + suffix).strip().lower()
    except (EOFError, KeyboardInterrupt):
        console.print()
        return False
    if not ans:
        return default
    return ans[0] == "y"


def choose(question: str, options: list[str], *, default: int = 0) -> int:
    """Pick one of `options` by index. Returns `default` when not on TTY."""
    if not is_tty():
        return default
    console.print(question)
    for i, opt in enumerate(options):
        marker = "›" if i == default else " "
        console.print(f"  {marker} [{i + 1}] {opt}")
    try:
        ans = input(f"select [1-{len(options)}, default {default + 1}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        console.print()
        return default
    if not ans:
        return default
    try:
        n = int(ans)
    except ValueError:
        return default
    if 1 <= n <= len(options):
        return n - 1
    return default
