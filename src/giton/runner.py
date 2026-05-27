"""Run plugins for a given hook trigger."""
from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console

from giton.config import PluginRecord, load_plugins
from giton.context import GitContext, collect
from giton import policies, repo_config

console = Console()


@dataclass
class PluginResult:
    plugin: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def _print_findings(findings: list[policies.Finding]) -> None:
    if not findings:
        return
    console.print("[bold]Policy findings:[/bold]")
    for f in findings:
        color = {"error": "red", "warn": "yellow", "info": "cyan"}.get(
            f.severity, "white"
        )
        loc = f" [dim]({f.location})[/dim]" if f.location else ""
        console.print(
            f"  [{color}]{f.severity}[/{color}] [bold]{f.policy}[/bold]: "
            f"{f.message}{loc}"
        )


def _format_command(cmd: str, ctx: GitContext) -> str:
    return cmd.format(
        paths=ctx.paths_arg(),
        diff_file=str(ctx.diff_file()),
        root=str(ctx.root),
    )


@dataclass
class TriggerOutcome:
    findings: list[policies.Finding]
    plugin_results: list[PluginResult]
    fail_on_policy: bool = True

    @property
    def ok(self) -> bool:
        if self.fail_on_policy and policies.has_errors(self.findings):
            return False
        return all(r.ok for r in self.plugin_results)


def run_trigger(trigger: str, cwd: Path | None = None) -> TriggerOutcome:
    ctx = collect(cwd)
    if ctx is None:
        console.print("[yellow]giton: not inside a git repository[/yellow]")
        return TriggerOutcome([], [])

    cfg = repo_config.load(ctx.root)
    findings = policies.evaluate(ctx, cfg, trigger)
    _print_findings(findings)

    plugins = [p for p in load_plugins() if p.enabled and trigger in p.triggers]
    if not plugins:
        if not findings:
            console.print(f"[dim]giton: no plugins or policies fired for {trigger}[/dim]")
        results: list[PluginResult] = []
    else:
        results = [_run_plugin(p, ctx) for p in plugins]

    return TriggerOutcome(
        findings=findings,
        plugin_results=results,
        fail_on_policy=cfg.fail_on_policy(trigger),
    )


def _run_plugin(plugin: PluginRecord, ctx: GitContext) -> PluginResult:
    if plugin.exec_type != "cli":
        console.print(
            f"[yellow]giton: exec_type '{plugin.exec_type}' not yet "
            f"implemented for plugin {plugin.name}[/yellow]"
        )
        return PluginResult(plugin.name, 0, "", "skipped")

    cmd_str = _format_command(plugin.command, ctx)
    console.print(f"[bold cyan]› {plugin.name}[/bold cyan] [dim]{cmd_str}[/dim]")
    try:
        proc = subprocess.run(
            shlex.split(cmd_str),
            cwd=ctx.root,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        console.print(
            f"[red]giton: plugin '{plugin.name}' not installed "
            f"(command: {cmd_str.split()[0]})[/red]"
        )
        return PluginResult(plugin.name, 127, "", "command not found")

    if proc.stdout:
        console.print(proc.stdout.rstrip())
    if proc.stderr:
        console.print(f"[dim]{proc.stderr.rstrip()}[/dim]")
    status = "[green]ok[/green]" if proc.returncode == 0 else f"[red]fail ({proc.returncode})[/red]"
    console.print(f"  → {status}")
    return PluginResult(plugin.name, proc.returncode, proc.stdout, proc.stderr)
