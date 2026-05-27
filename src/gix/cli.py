"""gix CLI — Typer entry point."""
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from gix import __version__, plugins as plug, shell as gix_shell
from gix.context import collect, repo_root
from gix.hooks import install as install_hooks, uninstall as uninstall_hooks
from gix.runner import run_trigger

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="gix — local AI layer for git, between commit and push.",
)
plugin_app = typer.Typer(no_args_is_help=True, help="Manage plugins")
hook_app = typer.Typer(no_args_is_help=True, help="Run hook logic (used by .git/hooks)")
app.add_typer(plugin_app, name="plugin")
app.add_typer(hook_app, name="hook")

console = Console()


@app.callback(invoke_without_command=False)
def _root(
    version: bool = typer.Option(False, "--version", help="Show version and exit."),
):
    if version:
        console.print(f"gix {__version__}")
        raise typer.Exit()


# --- top-level commands -----------------------------------------------------

@app.command()
def init(
    install_default_plugins: bool = typer.Option(
        True, "--with-defaults/--no-defaults",
        help="Also install the 3 default plugins.",
    ),
):
    """Install gix git hooks in the current repository."""
    root = repo_root()
    if not root:
        console.print("[red]not inside a git repository[/red]")
        raise typer.Exit(1)
    written = install_hooks(root)
    console.print(f"[green]✓ installed {len(written)} hook(s) in {root}/.git/hooks[/green]")
    for w in written:
        console.print(f"  • {w.name}")
    if install_default_plugins:
        console.print("\n[bold]Installing default plugins…[/bold]")
        plug.install_defaults()
    console.print(
        "\n[dim]Tip: open the interactive shell with `gix shell`.[/dim]"
    )


@app.command()
def uninit():
    """Remove gix hooks from the current repository (restore backups)."""
    root = repo_root()
    if not root:
        console.print("[red]not inside a git repository[/red]")
        raise typer.Exit(1)
    removed = uninstall_hooks(root)
    console.print(f"[green]removed {len(removed)} gix hook(s)[/green]")


@app.command()
def status():
    """Show repo summary."""
    ctx = collect()
    if not ctx:
        console.print("[yellow]not inside a git repository[/yellow]")
        raise typer.Exit(1)
    console.print(f"[bold]repo[/bold]    {ctx.root}")
    console.print(f"[bold]last[/bold]    {ctx.last_commit_subject or '(no commits yet)'}")
    console.print(f"[bold]staged[/bold]  {len(ctx.staged_paths)} file(s)")
    for p in ctx.staged_paths:
        console.print(f"   • {p}")


@app.command()
def shell():
    """Launch the interactive gix shell."""
    gix_shell.run()


@app.command()
def doctor():
    """Quick environment check."""
    import shutil
    git_ok = shutil.which("git") is not None
    console.print(f"git available: {'[green]yes[/green]' if git_ok else '[red]no[/red]'}")
    root = repo_root()
    console.print(f"git repo:      {root if root else '[yellow]not in a repo[/yellow]'}")
    plug.show_table()


# --- plugin subcommands -----------------------------------------------------

@plugin_app.command("list")
def plugin_list():
    """List registered plugins."""
    plug.show_table()


@plugin_app.command("catalog")
def plugin_catalog():
    """Show the catalog of available plugins."""
    plug.show_catalog()


@plugin_app.command("install")
def plugin_install(name: str):
    """Install a plugin by catalog name."""
    plug.install_from_catalog(name)


@plugin_app.command("install-defaults")
def plugin_install_defaults():
    """Install the 3 default plugins (pyqual, vallm, pretest)."""
    plug.install_defaults()


@plugin_app.command("install-category")
def plugin_install_category(category: str):
    """Install every plugin in the given catalog category (e.g. lang:python)."""
    n = plug.install_category(category)
    console.print(f"[green]installed {n} plugin(s) from category '{category}'[/green]")


@plugin_app.command("remove")
def plugin_remove(name: str):
    """Unregister a plugin."""
    plug.uninstall(name)


# --- hook subcommands -------------------------------------------------------

@hook_app.command("pre-commit")
def hook_pre_commit():
    """Run pre-commit plugins."""
    results = run_trigger("pre-commit")
    if any(not r.ok for r in results):
        raise typer.Exit(1)


@hook_app.command("post-commit")
def hook_post_commit():
    """Run post-commit plugins (never blocks the commit)."""
    run_trigger("post-commit")


@hook_app.command("pre-push")
def hook_pre_push():
    """Run pre-push plugins."""
    results = run_trigger("pre-push")
    if any(not r.ok for r in results):
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
