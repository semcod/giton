"""
Advanced giton usage example.

This script demonstrates:
- Plugin management (add, remove, list)
- Custom policy configuration
- Hook installation/uninstallation
- Running multiple triggers
- Error handling and edge cases
"""

from pathlib import Path
from giton.context import collect, repo_root
from giton.runner import run_trigger
from giton.hooks import install as install_hooks, uninstall as uninstall_hooks
from giton.config import load_plugins, upsert_plugin, remove_plugin, PluginRecord
from giton import catalog
from rich.console import Console
from rich.table import Table

console = Console()


def demonstrate_plugin_management():
    """Show how to manage plugins programmatically."""
    console.print("\n[bold cyan]Plugin Management[/bold cyan]")
    
    # Load current plugins
    plugins = load_plugins()
    console.print(f"\nCurrent plugins: {len(plugins)}")
    
    # Display plugin table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="green")
    table.add_column("Triggers", style="yellow")
    table.add_column("Enabled", style="white")
    
    for plugin in plugins:
        table.add_row(
            plugin.name,
            plugin.category,
            ", ".join(plugin.triggers),
            "✓" if plugin.enabled else "✗"
        )
    console.print(table)
    
    # Add a custom plugin
    console.print("\nAdding custom plugin...")
    custom_plugin = PluginRecord(
        name="custom-linter",
        description="Custom linter example",
        category="lang:python",
        triggers=["pre-commit"],
        command="python -m py_compile {paths}",
        install=None,
        enabled=True,
        source="user"
    )
    upsert_plugin(custom_plugin)
    console.print("[green]✓ Custom plugin added[/green]")
    
    # Remove the custom plugin
    console.print("\nRemoving custom plugin...")
    remove_plugin("custom-linter")
    console.print("[green]✓ Custom plugin removed[/green]")


def demonstrate_catalog():
    """Show how to browse the built-in plugin catalog."""
    console.print("\n[bold cyan]Plugin Catalog[/bold cyan]")
    
    # List default plugins
    defaults = catalog.defaults()
    console.print(f"\nDefault plugins: {len(defaults)}")
    
    for entry in defaults:
        console.print(f"\n  [bold]{entry.record.name}[/bold]")
        console.print(f"    Category: {entry.record.category}")
        console.print(f"    Description: {entry.record.description}")
        console.print(f"    Triggers: {', '.join(entry.record.triggers)}")
    
    # List categories
    categories = catalog.list_categories()
    console.print(f"\nCategories: {list(categories.keys())}")


def demonstrate_hooks():
    """Show how to install/uninstall git hooks."""
    console.print("\n[bold cyan]Git Hooks Management[/bold cyan]")
    
    root = repo_root()
    if not root:
        console.print("[yellow]Not in a git repository, skipping hook demo[/yellow]")
        return
    
    # Install hooks
    console.print("\nInstalling git hooks...")
    try:
        installed = install_hooks(root)
        console.print(f"[green]✓ Installed {len(installed)} hooks:[/green]")
        for hook in installed:
            console.print(f"  - {hook.name}")
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        return


def demonstrate_trigger_sequence():
    """Run multiple triggers in sequence."""
    console.print("\n[bold cyan]Trigger Sequence[/bold cyan]")
    
    root = repo_root()
    if not root:
        console.print("[yellow]Not in a git repository, skipping trigger demo[/yellow]")
        return
    
    triggers = ["pre-commit", "post-commit", "pre-push"]
    
    for trigger in triggers:
        console.print(f"\nRunning [bold]{trigger}[/bold]...")
        outcome = run_trigger(trigger)
        
        if outcome.findings:
            console.print(f"  Findings: {len(outcome.findings)}")
            for f in outcome.findings:
                console.print(f"    - [{f.severity}] {f.message}")
        
        if outcome.plugin_results:
            console.print(f"  Plugins: {len(outcome.plugin_results)}")
            for r in outcome.plugin_results:
                status = "✓" if r.ok else "✗"
                console.print(f"    {status} {r.plugin}: {r.returncode}")
        
        console.print(f"  Outcome: {'[green]OK[/green]' if outcome.ok else '[red]FAILED[/red]'}")


def main():
    """Run all advanced examples."""
    console.print("[bold cyan]Advanced Giton Example[/bold cyan]")
    
    try:
        demonstrate_catalog()
        demonstrate_plugin_management()
        demonstrate_hooks()
        demonstrate_trigger_sequence()
        
        console.print("\n[bold green]All examples completed successfully![/bold green]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())


if __name__ == "__main__":
    main()
