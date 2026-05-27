"""
Basic giton usage example.

This script demonstrates how to use giton as a Python library to:
- Collect git context
- Run triggers (pre-commit, post-commit, pre-push)
- Handle policy findings and plugin results

Run with pytest for testing:
    pytest examples/basic/main.py -v
"""

from pathlib import Path
from giton.context import collect
from giton.runner import run_trigger
from rich.console import Console

console = Console()


def test_basic_giton_usage():
    """Test basic giton functionality."""
    console.print("[bold cyan]Basic Giton Example[/bold cyan]\n")

    # Collect git context from current directory
    console.print("1. Collecting git context...")
    ctx = collect()
    if ctx is None:
        console.print("[yellow]Warning: Not inside a git repository[/yellow]")
        return

    console.print(f"   Repository root: {ctx.root}")
    console.print(f"   Staged files: {len(ctx.staged_paths)}")
    console.print(f"   Staged diff size: {len(ctx.staged_diff)} bytes\n")

    # Run pre-commit trigger
    console.print("2. Running pre-commit trigger...")
    outcome = run_trigger("pre-commit")
    
    # Display policy findings
    if outcome.findings:
        console.print(f"\n   [yellow]Policy findings: {len(outcome.findings)}[/yellow]")
        for finding in outcome.findings:
            console.print(f"   - [{finding.severity}] {finding.policy}: {finding.message}")
    else:
        console.print("   [green]No policy findings[/green]")

    # Display plugin results
    if outcome.plugin_results:
        console.print(f"\n   Plugin results: {len(outcome.plugin_results)}")
        for result in outcome.plugin_results:
            status = "[green]✓[/green]" if result.ok else "[red]✗[/red]"
            console.print(f"   {status} {result.plugin}: exit code {result.returncode}")
    else:
        console.print("   [dim]No plugins executed[/dim]")

    # Overall outcome
    console.print(f"\n3. Overall outcome: {'[green]OK[/green]' if outcome.ok else '[red]FAILED[/red]'}")


def main():
    """Demonstrate basic giton usage."""
    test_basic_giton_usage()


if __name__ == "__main__":
    main()
