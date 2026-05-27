"""Per-repository config loaded from `.giton/config.yaml`.

The repo config defines policies, hook overrides and (optionally)
per-repo plugin selection. It is local-first: never committed unless the
user explicitly chooses to share it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_CONFIG_REL = ".giton/config.yaml"


DEFAULT_CONFIG: dict[str, Any] = {
    "policies": {
        # built-in checks; each entry: {enabled: bool, ...options}
        "conventional_commits": {
            "enabled": True,
            "types": [
                "feat", "fix", "docs", "style", "refactor", "perf",
                "test", "build", "ci", "chore", "revert",
            ],
            "max_subject_length": 72,
            "require_scope": False,
        },
        "no_wip_commits": {
            "enabled": True,
            "patterns": ["^wip", "^WIP", "^tmp", "^xxx", "^fixme"],
        },
        "no_secrets": {
            "enabled": True,
            # very small built-in set; user can extend
            "patterns": [
                r"AKIA[0-9A-Z]{16}",                 # AWS access key id
                r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
                r"(?i)api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{20,}['\"]",
                r"(?i)secret\s*[:=]\s*['\"][A-Za-z0-9_\-]{20,}['\"]",
            ],
        },
        "max_file_size": {
            "enabled": True,
            "kb": 512,
        },
    },
    "hooks": {
        "pre-commit": {"fail_on_policy": True},
        "commit-msg": {"fail_on_policy": True},
        "post-commit": {"fail_on_policy": False},
        "pre-push": {"fail_on_policy": True},
    },
}


@dataclass
class RepoConfig:
    raw: dict[str, Any] = field(default_factory=dict)
    path: Path | None = None

    def policy(self, name: str) -> dict[str, Any]:
        return self.raw.get("policies", {}).get(name, {}) or {}

    def hook(self, trigger: str) -> dict[str, Any]:
        return self.raw.get("hooks", {}).get(trigger, {}) or {}

    def fail_on_policy(self, trigger: str) -> bool:
        return bool(self.hook(trigger).get("fail_on_policy", True))


def _deep_merge(base: dict[str, Any], over: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load(repo_root: Path) -> RepoConfig:
    path = repo_root / REPO_CONFIG_REL
    if not path.exists():
        return RepoConfig(raw=DEFAULT_CONFIG, path=None)
    try:
        data = yaml.safe_load(path.read_text()) or {}
    except yaml.YAMLError:
        data = {}
    merged = _deep_merge(DEFAULT_CONFIG, data)
    return RepoConfig(raw=merged, path=path)


def write_default(repo_root: Path, *, overwrite: bool = False) -> Path:
    path = repo_root / REPO_CONFIG_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return path
    path.write_text(yaml.safe_dump(DEFAULT_CONFIG, sort_keys=False))
    return path
