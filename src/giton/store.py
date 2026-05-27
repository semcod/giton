"""Persist findings so they can be inspected or fixed later."""
from __future__ import annotations

import json
from pathlib import Path

from giton import policies

LAST_CHECK_NAME = ".giton/last_check.json"


def save_findings(findings: list[policies.Finding], repo_root: Path) -> Path:
    """Write the list of findings as JSON so `policy fix` can read them."""
    path = repo_root / LAST_CHECK_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "policy": f.policy,
            "severity": f.severity,
            "message": f.message,
            "location": f.location,
            "fix": f.fix,
        }
        for f in findings
    ]
    path.write_text(json.dumps(data, indent=2))
    return path


def load_findings(repo_root: Path) -> list[policies.Finding]:
    """Load previously saved findings."""
    path = repo_root / LAST_CHECK_NAME
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return [policies.Finding(**item) for item in data]
