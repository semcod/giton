"""Plugin install / list / enable management."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from gix import catalog
from gix.config import (
    PluginRecord,
    load_plugins,
    remove_plugin,
    upsert_plugin,
)

console = Console()


def _pip_install(target: str) -> int:
    cmd = [sys.executable, "-m", "pip", "install", target]
    console.print(f"[dim]$ {' '.join(cmd)}[/dim]")
    return subprocess.run(cmd, check=False).returncode


def install_from_catalog(name: str, *, prefer_local: bool = True) -> bool:
    entry = catalog.find(name)
    if entry is None:
        console.print(f"[red]Unknown plugin: {name}[/red]")
        return False

    target: str | None = None
    if prefer_local and entry.pip_local_path:
        local = (Path(__file__).resolve().parents[2] / entry.pip_local_path).resolve()
        if local.exists() and (local / "pyproject.toml").exists():
            target = str(local)
    if target is None:
        target = entry.record.install or name

    rc = _pip_install(target)
    if rc != 0:
        console.print(
            f"[yellow]pip install failed for {name}; "
            f"registering plugin record anyway[/yellow]"
        )
    upsert_plugin(entry.record)
    console.print(f"[green]✓ registered plugin '{name}'[/green]")
    return rc == 0


def install_defaults() -> None:
    for entry in catalog.defaults():
        install_from_catalog(entry.record.name)


def install_category(category: str) -> int:
    matches = [e for e in catalog.CATALOG.values() if e.record.category == category]
    if not matches:
        console.print(f"[red]No plugins in category '{category}'[/red]")
        return 0
    n = 0
    for e in matches:
        if install_from_catalog(e.record.name):
            n += 1
    return n


def uninstall(name: str) -> bool:
    if remove_plugin(name):
        console.print(f"[green]✓ removed plugin '{name}'[/green]")
        return True
    console.print(f"[yellow]plugin '{name}' was not registered[/yellow]")
    return False


def show_table() -> None:
    plugins = load_plugins()
    table = Table(title="gix plugins", show_lines=False)
    table.add_column("name", style="bold")
    table.add_column("category")
    table.add_column("triggers")
    table.add_column("command", style="dim")
    table.add_column("status")
    for p in plugins:
        present = "✓" if shutil.which(p.command.split()[0]) else "✗"
        status = f"{'enabled' if p.enabled else 'disabled'} / cmd:{present}"
        table.add_row(
            p.name,
            p.category,
            ",".join(p.triggers),
            p.command,
            status,
        )
    if not plugins:
        console.print("[dim]No plugins registered. Try: gix plugin install-defaults[/dim]")
    else:
        console.print(table)


def show_catalog() -> None:
    table = Table(title="gix catalog (available plugins)")
    table.add_column("name", style="bold")
    table.add_column("category")
    table.add_column("default", justify="center")
    table.add_column("description")
    defaults = set(catalog.DEFAULT_PLUGIN_NAMES)
    for name, entry in catalog.CATALOG.items():
        table.add_row(
            name,
            entry.record.category,
            "★" if name in defaults else "",
            entry.record.description,
        )
    console.print(table)
    console.print("\n[bold]Categories[/bold]")
    for cat, names in catalog.list_categories().items():
        console.print(f"  [cyan]{cat}[/cyan]: {', '.join(names)}")
