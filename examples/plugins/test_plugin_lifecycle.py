"""End-to-end example: register a custom plugin, run it, observe the result.

Run with:
    pytest examples/plugins/test_plugin_lifecycle.py -v
"""
from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest


def _git(args, cwd):
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )


@pytest.fixture
def isolated_repo(tmp_path, monkeypatch):
    """A fresh git repo + isolated XDG_CONFIG_HOME so we don't touch
    the real user's giton plugins."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    import importlib
    from giton import config as _cfg
    importlib.reload(_cfg)
    from giton import plugins as _pl, runner as _rn
    importlib.reload(_pl)
    importlib.reload(_rn)

    repo = tmp_path / "repo"
    repo.mkdir()
    _git(["init", "-q"], repo)
    _git(["config", "user.email", "demo@example.com"], repo)
    _git(["config", "user.name", "demo"], repo)
    (repo / "README.md").write_text("# demo\n")
    _git(["add", "README.md"], repo)
    _git(["commit", "-q", "-m", "chore: seed"], repo)
    return repo


def test_register_run_and_unregister(isolated_repo, tmp_path, monkeypatch):
    # 1) build a fake plugin executable that records its argv to a log
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    plugin = bin_dir / "my_lint"
    log = tmp_path / "my_lint.log"
    plugin.write_text(
        "#!/bin/sh\n"
        f"echo \"argv:$@\" > '{log}'\n"
        "echo 'my_lint: ok'\n"
        "exit 0\n"
    )
    plugin.chmod(plugin.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")

    # 2) register it as a giton plugin firing on pre-commit
    from giton.config import PluginRecord, upsert_plugin, load_plugins, remove_plugin
    upsert_plugin(PluginRecord(
        name="my_lint",
        description="example plugin",
        category="lang:python",
        exec_type="cli",
        command="my_lint {paths}",
        triggers=["pre-commit"],
        install=None,
        source="user",
        enabled=True,
    ))
    assert any(p.name == "my_lint" for p in load_plugins())

    # 3) stage a python file and fire the pre-commit trigger
    (isolated_repo / "module.py").write_text("def f():\n    return 42\n")
    _git(["add", "module.py"], isolated_repo)

    from giton.runner import run_trigger
    outcome = run_trigger("pre-commit", cwd=isolated_repo)

    # 4) the plugin must have actually run
    assert len(outcome.plugin_results) == 1
    pr = outcome.plugin_results[0]
    assert pr.plugin == "my_lint"
    assert pr.ok, pr.stderr
    assert "my_lint: ok" in pr.stdout

    # 5) {paths} placeholder must have been expanded to the staged file
    argv_line = log.read_text().strip()
    assert "module.py" in argv_line, argv_line

    # 6) unregister cleanly
    assert remove_plugin("my_lint")
    assert not any(p.name == "my_lint" for p in load_plugins())


def test_default_catalog_pyqual_command_is_valid():
    """Smoke-test the catalog metadata for the three default plugins."""
    from giton import catalog

    expected = {"pyqual", "vallm", "pretest"}
    actual = {e.record.name for e in catalog.defaults()}
    assert expected == actual

    for entry in catalog.defaults():
        cmd = entry.record.command
        # every default command must declare which binary to invoke and
        # the binary name must equal the plugin name
        first_token = cmd.split()[0]
        assert first_token == entry.record.name, (
            f"plugin {entry.record.name!r} command starts with "
            f"{first_token!r}; commands should always invoke their own binary"
        )
        # placeholders must format cleanly with reasonable values
        cmd.format(paths="a.py", diff_file="/tmp/d.patch", root="/tmp/r")
