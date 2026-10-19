"""Interactive `giton shell` REPL.

Lightweight, dependency-free (uses builtin `input`). Provides shortcuts for
the most common operations: managing plugins, running hooks, inspecting
the current repo. Type `help` to see commands.
"""
from __future__ import annotations

import shlex
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from giton import catalog, fixups, plugins as plug, policies, repo_config, store
from giton.context import collect, repo_root
from giton.hooks import install as install_hooks
from giton.runner import run_trigger

console = Console()

BANNER = """[bold cyan]giton[/bold cyan] interactive shell — local AI layer for git
type [bold]help[/bold] for commands, [bold]exit[/bold] to quit
"""

HELP = """\
[bold]Plugins[/bold]
  ls                       list registered plugins
  catalog                  show available plugins + categories
  install <name>           install a plugin from the catalog
  install-defaults         install the 3 default plugins (pyqual, vallm, testless)
  install-category <cat>   install all plugins of a category (e.g. lang:python)
  remove <name>            unregister a plugin
  enable <name> / disable <name>

[bold]Repo / hooks[/bold]
  init                     install git hooks in the current repo
  status                   show repo + staged-files summary
  hook <pre-commit|post-commit|pre-push>
                           run policies + plugins for that trigger

[bold]Policy[/bold]
  policy list              show active built-in policies
  policy check [trigger]   evaluate built-in policies (default: pre-commit)
  policy fix               apply auto-fixes from the last check
  policy init              write default .giton/config.yaml

[bold]Misc[/bold]
  help                     show this help
  exit / quit              leave the shell
"""


def _set_enabled(name: str, value: bool) -> None:
    from giton.config import load_plugins, save_plugins
    plugins = load_plugins()
    found = False
    for p in plugins:
        if p.name == name:
            p.enabled = value
            found = True
    if found:
        save_plugins(plugins)
        console.print(f"[green]{'enabled' if value else 'disabled'} {name}[/green]")
    else:
        console.print(f"[yellow]plugin '{name}' not registered[/yellow]")


def _cmd_status() -> None:
    ctx = collect()
    if not ctx:
        console.print("[yellow]not inside a git repo[/yellow]")
        return
    console.print(
        Panel.fit(
            f"[bold]repo[/bold]   {ctx.root}\n"
            f"[bold]last[/bold]   {ctx.last_commit_subject or '(no commits yet)'}\n"
            f"[bold]staged[/bold] {len(ctx.staged_paths)} file(s)"
            + ("\n  " + "\n  ".join(ctx.staged_paths) if ctx.staged_paths else ""),
            title="giton status",
        )
    )


def _policy_list(cfg) -> None:
    src = cfg.path or "(defaults)"
    console.print(f"config source: {src}")
    for name in policies.CHECKS:
        opts = cfg.policy(name)
        on = "[green]on [/green]" if opts.get("enabled", True) else "[dim]off[/dim]"
        console.print(f"  {on} {name}")


def _policy_check(ctx, cfg, args: list[str]) -> None:
    trigger = args[1] if len(args) > 1 else "pre-commit"
    findings = policies.evaluate(ctx, cfg, trigger)
    if not findings:
        console.print("[green]✓ no policy findings[/green]")
        return
    for f in findings:
        color = {"error": "red", "warn": "yellow", "info": "cyan"}.get(f.severity, "white")
        console.print(f"  [{color}]{f.severity}[/{color}] {f.policy}: {f.message}")


def _policy_fix(ctx) -> None:
    findings = store.load_findings(ctx.root)
    if not findings:
        console.print("[dim]no saved findings — run `policy check` first[/dim]")
        return
    applied, total = fixups.apply_all(findings, ctx.root, yes=False)
    if applied == total and total:
        console.print(f"[green]✓ applied {applied}/{total} fix(es)[/green]")
    elif total:
        console.print(f"[yellow]applied {applied}/{total} fix(es)[/yellow]")


def _policy_init(ctx) -> None:
    path = repo_config.write_default(ctx.root)
    console.print(f"[green]✓ wrote {path}[/green]")


def _cmd_policy(args: list[str]) -> None:
    sub = args[0] if args else "list"
    ctx = collect()
    if not ctx:
        console.print("[red]not inside a git repository[/red]")
        return
    cfg = repo_config.load(ctx.root)
    if sub == "list":
        _policy_list(cfg)
    elif sub == "check":
        _policy_check(ctx, cfg, args)
    elif sub == "fix":
        _policy_fix(ctx)
    elif sub == "init":
        _policy_init(ctx)
    else:
        console.print("[yellow]usage: policy <list|check [trigger]|fix|init>[/yellow]")


def _cmd_init() -> None:
    root = repo_root()
    if not root:
        console.print("[red]not inside a git repository[/red]")
        return
    written = install_hooks(root)
    console.print(f"[green]installed {len(written)} hook(s) in {root}/.git/hooks[/green]")
    for w in written:
        console.print(f"  • {w.name}")


def _cmd_install(args: list[str]) -> None:
    if not args:
        console.print("[yellow]usage: install <name>[/yellow]")
    else:
        plug.install_from_catalog(args[0])


def _cmd_install_category(args: list[str]) -> None:
    if not args:
        console.print("[yellow]usage: install-category <category>[/yellow]")
        console.print("Categories: " + ", ".join(catalog.list_categories()))
    else:
        plug.install_category(args[0])


def _cmd_remove(args: list[str]) -> None:
    if not args:
        console.print("[yellow]usage: remove <name>[/yellow]")
    else:
        plug.uninstall(args[0])


def _cmd_enable(args: list[str]) -> None:
    if not args:
        console.print("[yellow]usage: enable <name>[/yellow]")
    else:
        _set_enabled(args[0], True)


def _cmd_disable(args: list[str]) -> None:
    if not args:
        console.print("[yellow]usage: disable <name>[/yellow]")
    else:
        _set_enabled(args[0], False)


def _cmd_hook(args: list[str]) -> None:
    if not args or args[0] not in {"pre-commit", "post-commit", "pre-push"}:
        console.print("[yellow]usage: hook <pre-commit|post-commit|pre-push>[/yellow]")
    else:
        run_trigger(args[0])


COMMANDS = {
    "ls", "catalog", "install", "install-defaults", "install-category",
    "remove", "enable", "disable", "init", "status", "hook",
    "help", "exit", "quit",
}

HANDLERS = {
    "help": lambda _args: console.print(HELP),
    "ls": lambda _args: plug.show_table(),
    "catalog": lambda _args: plug.show_catalog(),
    "install": _cmd_install,
    "install-defaults": lambda _args: plug.install_defaults(),
    "install-category": _cmd_install_category,
    "remove": _cmd_remove,
    "enable": _cmd_enable,
    "disable": _cmd_disable,
    "init": lambda _args: _cmd_init(),
    "status": lambda _args: _cmd_status(),
    "hook": _cmd_hook,
    "policy": _cmd_policy,
}


def dispatch(line: str) -> bool:
    """Return False if the shell should exit."""
    line = line.strip()
    if not line:
        return True
    parts = shlex.split(line)
    cmd, args = parts[0], parts[1:]

    if cmd in {"exit", "quit"}:
        return False
    handler = HANDLERS.get(cmd)
    if handler:
        handler(args)
    else:
        console.print(f"[red]unknown command: {cmd}[/red] — try 'help'")
    return True


def run() -> None:
    console.print(Panel(BANNER, border_style="cyan"))
    while True:
        try:
            line = input("giton> ")
        except (EOFError, KeyboardInterrupt):
            console.print()
            break
        try:
            if not dispatch(line):
                break
        except Exception as e:  # pragma: no cover - defensive
            console.print(f"[red]error:[/red] {e}")
    console.print("[dim]bye.[/dim]")
