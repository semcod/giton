"""User and repository config for giton."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _xdg_config_home() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")


USER_CONFIG_DIR = _xdg_config_home() / "giton"
USER_PLUGINS_FILE = USER_CONFIG_DIR / "plugins.json"
REPO_CONFIG_PATH = ".giton/config.yaml"


@dataclass
class PluginRecord:
    name: str
    description: str = ""
    category: str = "task"  # "lang" | "task" | "integration"
    exec_type: str = "cli"  # "cli" | "mcp" | "rest"
    command: str = ""        # shell command template, e.g. "pyqual check {paths}"
    triggers: list[str] = field(default_factory=lambda: ["pre-commit"])
    install: str | None = None  # pip target (PyPI name, VCS URL, or local path)
    enabled: bool = True
    source: str = "user"     # "default" | "user"

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "PluginRecord":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def ensure_user_dirs() -> None:
    USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_plugins() -> list[PluginRecord]:
    ensure_user_dirs()
    if not USER_PLUGINS_FILE.exists():
        return []
    try:
        raw = json.loads(USER_PLUGINS_FILE.read_text())
    except json.JSONDecodeError:
        return []
    return [PluginRecord.from_dict(p) for p in raw.get("plugins", [])]


def save_plugins(plugins: list[PluginRecord]) -> None:
    ensure_user_dirs()
    payload = {"plugins": [p.to_dict() for p in plugins]}
    USER_PLUGINS_FILE.write_text(json.dumps(payload, indent=2))


def upsert_plugin(plugin: PluginRecord) -> None:
    plugins = load_plugins()
    plugins = [p for p in plugins if p.name != plugin.name]
    plugins.append(plugin)
    save_plugins(plugins)


def remove_plugin(name: str) -> bool:
    plugins = load_plugins()
    new = [p for p in plugins if p.name != name]
    if len(new) == len(plugins):
        return False
    save_plugins(new)
    return True
