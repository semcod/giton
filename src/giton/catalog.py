"""Built-in plugin catalog.

Defaults bundle three local-ecosystem plugins that are most useful in a
day-to-day commit -> push loop. Extra entries are grouped into categories
so the user can quickly install more via `giton plugin install <name>` or
`giton plugin add-category <category>`.
"""
from __future__ import annotations

from dataclasses import dataclass

from giton.config import PluginRecord


@dataclass(frozen=True)
class CatalogEntry:
    record: PluginRecord
    pip_local_path: str | None = None  # sibling repo path under semcod/


# --- Defaults: three plugins activated by `giton init` ---------------------
DEFAULT_PLUGIN_NAMES: tuple[str, ...] = ("pyqual", "vallm", "pretest")


def _entry(
    name: str,
    desc: str,
    *,
    category: str,
    triggers: list[str],
    command: str,
    pypi: str | None = None,
    local: str | None = None,
) -> CatalogEntry:
    return CatalogEntry(
        record=PluginRecord(
            name=name,
            description=desc,
            category=category,
            exec_type="cli",
            command=command,
            triggers=triggers,
            install=pypi or local,
            source="default",
        ),
        pip_local_path=local,
    )


CATALOG: dict[str, CatalogEntry] = {
    # --- Default plugins -------------------------------------------------
    "pyqual": _entry(
        "pyqual",
        "Python code quality checks (lint, types, complexity).",
        category="lang:python",
        triggers=["pre-commit"],
        command="pyqual check {paths}",
        pypi="pyqual",
        local="../pyqual",
    ),
    "vallm": _entry(
        "vallm",
        "Validate LLM-generated code/patches before they land in history.",
        category="task:validate",
        triggers=["post-commit"],
        command="vallm check --diff {diff_file}",
        pypi="vallm",
        local="../vallm",
    ),
    "pretest": _entry(
        "pretest",
        "Run / generate tests before push.",
        category="task:test",
        triggers=["pre-push"],
        command="pretest run",
        pypi="pretest",
        local="../pretest",
    ),

    # --- Quick-extend: language plugins ---------------------------------
    "domd": _entry(
        "domd",
        "Markdown / docs linter and fixer.",
        category="lang:markdown",
        triggers=["pre-commit"],
        command="domd lint {paths}",
        pypi="domd",
        local="../domd",
    ),
    "code2llm": _entry(
        "code2llm",
        "Pack the repo into LLM-ready context for AI plugins.",
        category="lang:any",
        triggers=["post-commit"],
        command="code2llm pack --staged",
        pypi="code2llm",
        local="../code2llm",
    ),

    # --- Quick-extend: task plugins -------------------------------------
    "prefact": _entry(
        "prefact",
        "AI refactoring suggestions as fixup! commits.",
        category="task:refactor",
        triggers=["post-commit"],
        command="prefact suggest --diff {diff_file}",
        pypi="prefact",
        local="../prefact",
    ),
    "redsl": _entry(
        "redsl",
        "Auto-fix lint/style issues and stage as fixup.",
        category="task:autofix",
        triggers=["pre-commit"],
        command="redsl autofix {paths}",
        pypi="redsl",
        local="../redsl",
    ),
    "pfix": _entry(
        "pfix",
        "Generic patch fixer — apply small AI-proposed patches.",
        category="task:fix",
        triggers=["post-commit"],
        command="pfix apply --diff {diff_file}",
        pypi="pfix",
        local="../pfix",
    ),
    "todocs": _entry(
        "todocs",
        "Generate / update docs from staged changes.",
        category="task:docs",
        triggers=["pre-push"],
        command="todocs sync --staged",
        pypi="todocs",
        local="../todocs",
    ),
    "prellm": _entry(
        "prellm",
        "Pre-LLM gate: redact secrets / shrink context before AI calls.",
        category="task:security",
        triggers=["pre-commit"],
        command="prellm scan {paths}",
        pypi="prellm",
        local="../prellm",
    ),

    # --- Quick-extend: integrations -------------------------------------
    "git-commit-mcp": _entry(
        "git-commit-mcp",
        "External MCP server for Conventional Commit messages.",
        category="integration:mcp",
        triggers=["pre-push"],
        command="git-commit-mcp-server --once",
        pypi="git-commit-mcp-server",
    ),
}


def list_categories() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for name, entry in CATALOG.items():
        out.setdefault(entry.record.category, []).append(name)
    for v in out.values():
        v.sort()
    return dict(sorted(out.items()))


def find(name: str) -> CatalogEntry | None:
    return CATALOG.get(name)


def defaults() -> list[CatalogEntry]:
    return [CATALOG[n] for n in DEFAULT_PLUGIN_NAMES]
