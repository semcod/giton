"""giton CLI — Typer entry point."""
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from giton import (
    __version__,
    history,
    interactive,
    plugins as plug,
    policies,
    repo_config,
    shell as giton_shell,
)
from giton.context import collect, repo_root
from giton.hooks import install as install_hooks, uninstall as uninstall_hooks
from giton.runner import run_trigger

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="giton — local AI layer for git, between commit and push.",
)
plugin_app = typer.Typer(no_args_is_help=True, help="Manage plugins")
hook_app = typer.Typer(no_args_is_help=True, help="Run hook logic (used by .git/hooks)")
policy_app = typer.Typer(no_args_is_help=True, help="Built-in policy engine")
history_app = typer.Typer(no_args_is_help=True, help="Safe history operations")
app.add_typer(plugin_app, name="plugin")
app.add_typer(hook_app, name="hook")
app.add_typer(policy_app, name="policy")
app.add_typer(history_app, name="history")

console = Console()


@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Show version and exit."),
):
    if version:
        console.print(f"giton {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


# --- top-level commands -----------------------------------------------------

@app.command()
def init(
    install_default_plugins: bool = typer.Option(
        True, "--with-defaults/--no-defaults",
        help="Also install the 3 default plugins.",
    ),
):
    """Install giton git hooks in the current repository."""
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
        "\n[dim]Tip: open the interactive shell with `giton shell`.[/dim]"
    )


@app.command()
def uninit():
    """Remove giton hooks from the current repository (restore backups)."""
    root = repo_root()
    if not root:
        console.print("[red]not inside a git repository[/red]")
        raise typer.Exit(1)
    removed = uninstall_hooks(root)
    console.print(f"[green]removed {len(removed)} giton hook(s)[/green]")


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
    """Launch the interactive giton shell."""
    giton_shell.run()


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
    """Run pre-commit policies + plugins."""
    out = run_trigger("pre-commit")
    if not out.ok:
        raise typer.Exit(1)


@hook_app.command("commit-msg")
def hook_commit_msg(
    message_file: Path = typer.Argument(
        ..., help="Path to .git/COMMIT_EDITMSG (passed by git).",
    ),
):
    """Validate the commit message before the commit completes.

    Git invokes this hook with the path to the message file as `$1`.
    On policy errors we exit non-zero so the commit is aborted; the
    user's message stays in the file so they can re-run `git commit`.
    """
    git_ctx = collect()
    if git_ctx is None:
        console.print("[yellow]giton: not inside a git repository[/yellow]")
        raise typer.Exit(0)
    try:
        raw = message_file.read_text()
    except OSError as e:
        console.print(f"[red]giton: cannot read {message_file}: {e}[/red]")
        raise typer.Exit(0)
    # strip git comment lines (`# ...`) and trailing whitespace
    lines = [ln for ln in raw.splitlines() if not ln.lstrip().startswith("#")]
    cleaned = "\n".join(lines).strip()
    subject, _, body = cleaned.partition("\n")
    git_ctx.last_commit_subject = subject.strip()
    git_ctx.last_commit_body = body.strip()
    cfg = repo_config.load(git_ctx.root)
    findings = policies.evaluate(git_ctx, cfg, "commit-msg")
    if not findings:
        return
    for f in findings:
        color = {"error": "red", "warn": "yellow", "info": "cyan"}.get(f.severity, "white")
        console.print(
            f"[{color}]{f.severity}[/{color}] [bold]{f.policy}[/bold]: {f.message}"
        )
    if cfg.fail_on_policy("commit-msg") and policies.has_errors(findings):
        console.print(
            "[dim]Tip: edit the message and re-run `git commit`, "
            "or `git commit --no-verify` to bypass.[/dim]"
        )
        raise typer.Exit(1)


@hook_app.command("post-commit")
def hook_post_commit():
    """Run post-commit policies + plugins (advisory, never blocks)."""
    run_trigger("post-commit")


@hook_app.command("pre-push")
def hook_pre_push():
    """Run pre-push policies + plugins."""
    out = run_trigger("pre-push")
    if not out.ok:
        raise typer.Exit(1)


# --- policy subcommands -----------------------------------------------------

@policy_app.command("check")
def policy_check(
    trigger: str = typer.Option(
        "pre-commit", "--trigger", "-t",
        help="Which trigger to evaluate (pre-commit, post-commit, pre-push).",
    ),
):
    """Run only the built-in policy engine for the given trigger."""
    git_ctx = collect()
    if git_ctx is None:
        console.print("[red]not inside a git repository[/red]")
        raise typer.Exit(1)
    cfg = repo_config.load(git_ctx.root)
    findings = policies.evaluate(git_ctx, cfg, trigger)
    if not findings:
        console.print("[green]✓ no policy findings[/green]")
        return
    for f in findings:
        color = {"error": "red", "warn": "yellow", "info": "cyan"}.get(f.severity, "white")
        loc = f" [dim]({f.location})[/dim]" if f.location else ""
        console.print(
            f"[{color}]{f.severity}[/{color}] [bold]{f.policy}[/bold]: {f.message}{loc}"
        )
    if cfg.fail_on_policy(trigger) and policies.has_errors(findings):
        raise typer.Exit(1)


@policy_app.command("init")
def policy_init(
    overwrite: bool = typer.Option(False, "--overwrite", help="Replace an existing config."),
):
    """Write a default `.giton/config.yaml` into the repo."""
    root = repo_root()
    if not root:
        console.print("[red]not inside a git repository[/red]")
        raise typer.Exit(1)
    path = repo_config.write_default(root, overwrite=overwrite)
    console.print(f"[green]✓ wrote {path.relative_to(root)}[/green]")


@policy_app.command("list")
def policy_list():
    """Show currently active policies in this repo."""
    root = repo_root()
    if not root:
        console.print("[red]not inside a git repository[/red]")
        raise typer.Exit(1)
    cfg = repo_config.load(root)
    src = cfg.path or "[dim](defaults — no .giton/config.yaml)[/dim]"
    console.print(f"config source: {src}")
    for name in policies.CHECKS:
        opts = cfg.policy(name)
        on = "[green]on [/green]" if opts.get("enabled", True) else "[dim]off[/dim]"
        console.print(f"  {on} {name}")


# --- fixup workflow ---------------------------------------------------------

@app.command()
def fixup(
    target: str = typer.Option(
        "HEAD", "--target", "-t",
        help="Commit (sha or ref) to point the fixup! at.",
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Don't prompt for confirmation.",
    ),
):
    """Create a `fixup!` commit from currently staged changes.

    Records a backup ref under `refs/giton/backup/fixup-<ts>` before
    running so the operation is recoverable.
    """
    root = repo_root()
    if not root:
        console.print("[red]not inside a git repository[/red]")
        raise typer.Exit(1)
    if not history.has_staged_changes(root):
        console.print(
            "[yellow]nothing staged — `git add` files first, "
            "then re-run `giton fixup`[/yellow]"
        )
        raise typer.Exit(1)
    target_sha = history._git(["rev-parse", target], root).stdout.strip()
    if not target_sha:
        console.print(f"[red]cannot resolve target: {target}[/red]")
        raise typer.Exit(1)
    target_subject = history._git(
        ["log", "-1", "--pretty=%s", target_sha], root
    ).stdout.strip()
    console.print(f"target: [bold]{target_sha[:12]}[/bold]  {target_subject}")
    if not yes and not interactive.confirm("Create fixup! commit?", default=True):
        console.print("[yellow]aborted[/yellow]")
        raise typer.Exit(0)
    backup = history.make_backup_ref(root, prefix="fixup")
    if backup:
        console.print(f"[dim]backup: {backup}[/dim]")
    res = history.create_fixup(root, target_sha)
    if res.stdout:
        console.print(res.stdout.rstrip())
    if not res.ok:
        console.print(f"[red]git commit --fixup failed: {res.stderr.strip()}[/red]")
        raise typer.Exit(res.returncode)
    console.print("[green]✓ fixup! commit created[/green]")


# --- history subcommands ----------------------------------------------------

@history_app.command("log")
def history_log(
    limit: int = typer.Option(20, "--limit", "-n", help="Max commits to show."),
    range_: str = typer.Option(
        "", "--range", "-r",
        help="Git range (default: <upstream>..HEAD if available).",
    ),
):
    """Show the commits eligible for the next push."""
    root = repo_root()
    if not root:
        console.print("[red]not inside a git repository[/red]")
        raise typer.Exit(1)
    rng = range_ or history.upstream_range(root) or ""
    rows = history.list_log(root, range_=rng or None, limit=limit)
    if not rows:
        console.print("[dim](no commits in range)[/dim]")
        return
    console.print(f"[bold]{rng or 'recent commits'}[/bold]")
    for sha, subject in rows:
        marker = "[yellow]fixup![/yellow]" if subject.startswith("fixup!") else " "
        console.print(f"  {sha[:12]}  {marker}  {subject}")


@history_app.command("clean")
def history_clean(
    base: str = typer.Option(
        "", "--base", "-b",
        help="Rebase base (default: tracked upstream).",
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Skip confirmation prompt.",
    ),
    interactive_rebase: bool = typer.Option(
        False, "--interactive", "-i",
        help="Open the editor instead of running headless.",
    ),
):
    """Run `git rebase -i --autosquash` safely with a backup ref.

    Default base is the tracked upstream. Records `refs/giton/backup/clean-<ts>`
    pointing at HEAD before rewriting history.
    """
    root = repo_root()
    if not root:
        console.print("[red]not inside a git repository[/red]")
        raise typer.Exit(1)
    if not base:
        rng = history.upstream_range(root)
        if not rng:
            console.print(
                "[red]no upstream tracked — pass --base <ref>[/red]"
            )
            raise typer.Exit(1)
        base = rng.split("..", 1)[0]
    rows = history.list_log(root, range_=f"{base}..HEAD")
    if not rows:
        console.print("[dim]nothing to rebase[/dim]")
        return
    console.print(f"[bold]rebasing {len(rows)} commit(s) on {base}[/bold]")
    for sha, subject in rows:
        marker = "[yellow]fixup![/yellow]" if subject.startswith("fixup!") else " "
        console.print(f"  {sha[:12]}  {marker}  {subject}")
    if not yes and not interactive.confirm(
        "Run autosquash now?", default=True
    ):
        console.print("[yellow]aborted[/yellow]")
        raise typer.Exit(0)
    backup = history.make_backup_ref(root, prefix="clean")
    if backup:
        console.print(f"[dim]backup: {backup}[/dim]")
    res = history.autosquash(root, base, interactive=interactive_rebase)
    if res.stdout:
        console.print(res.stdout.rstrip())
    if not res.ok:
        console.print(f"[red]rebase failed: {res.stderr.strip()}[/red]")
        console.print(
            f"[dim]recover with: git update-ref HEAD {backup} "
            "&& git reset --hard HEAD[/dim]"
        )
        raise typer.Exit(res.returncode)
    console.print("[green]✓ history cleaned[/green]")


if __name__ == "__main__":
    app()
