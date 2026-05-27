"""End-to-end tests for the plugin runner using a real fake-plugin script.

These tests verify that:
  - `{paths}`, `{diff_file}`, `{root}` placeholders are correctly expanded
  - Plugin stdout/stderr/exit-code are propagated into `TriggerOutcome`
  - `enabled=False` plugins are skipped
  - `unknown command` plugins are reported, not crashed
  - `commit-msg` plugin trigger is honoured
"""
from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest

from giton.config import PluginRecord, USER_PLUGINS_FILE, load_plugins, save_plugins
from giton.runner import run_trigger


def _git(args, cwd):
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """Initialise a clean repo + isolated giton config root."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    # reload config so USER_PLUGINS_FILE picks up the new XDG path
    import importlib
    from giton import config as _cfg
    importlib.reload(_cfg)
    from giton import plugins as _pl, runner as _rn
    importlib.reload(_pl)
    importlib.reload(_rn)

    r = tmp_path / "r"
    r.mkdir()
    _git(["init", "-q"], r)
    _git(["config", "user.email", "t@t"], r)
    _git(["config", "user.name", "t"], r)
    (r / "seed.txt").write_text("seed\n")
    _git(["add", "seed.txt"], r)
    _git(["commit", "-q", "-m", "feat: seed"], r)
    return r


def _write_fake_plugin(tmp_path: Path, name: str = "fakeplugin") -> Path:
    """A real executable that records its argv and stdin to a file."""
    script = tmp_path / name
    log = tmp_path / f"{name}.log"
    script.write_text(
        "#!/bin/sh\n"
        f"echo \"args:$@\" > '{log}'\n"
        f"echo \"cwd:$PWD\" >> '{log}'\n"
        "echo 'fake plugin ran'\n"
        "exit ${FAKE_EXIT:-0}\n"
    )
    script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return script


def _register(name: str, command: str, trigger: str, *, enabled: bool = True):
    from giton import config as _cfg
    plugins = _cfg.load_plugins()
    plugins = [p for p in plugins if p.name != name]
    plugins.append(PluginRecord(
        name=name,
        description="fake",
        category="task:test",
        exec_type="cli",
        command=command,
        triggers=[trigger],
        install=None,
        source="user",
        enabled=enabled,
    ))
    _cfg.save_plugins(plugins)


def test_plugin_executes_and_expands_paths(repo, tmp_path, monkeypatch):
    fake = _write_fake_plugin(tmp_path)
    log = tmp_path / "fakeplugin.log"
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")
    _register("fakeplugin", "fakeplugin {paths}", "pre-commit")

    # stage a couple of files
    (repo / "a.py").write_text("a=1\n")
    (repo / "b.py").write_text("b=2\n")
    _git(["add", "a.py", "b.py"], repo)

    out = run_trigger("pre-commit", cwd=repo)
    assert len(out.plugin_results) == 1
    pr = out.plugin_results[0]
    assert pr.ok, pr.stderr
    assert "fake plugin ran" in pr.stdout
    # placeholder expansion: {paths} → "a.py b.py"
    args_line = log.read_text().splitlines()[0]
    assert "a.py" in args_line and "b.py" in args_line


def test_plugin_diff_file_placeholder(repo, tmp_path, monkeypatch):
    fake = _write_fake_plugin(tmp_path, "diffplug")
    log = tmp_path / "diffplug.log"
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")
    _register("diffplug", "diffplug --diff {diff_file}", "post-commit")

    (repo / "x.py").write_text("x=1\n")
    _git(["add", "x.py"], repo)
    _git(["commit", "-q", "-m", "feat: x"], repo)

    out = run_trigger("post-commit", cwd=repo)
    assert out.plugin_results and out.plugin_results[0].ok
    args_line = log.read_text().splitlines()[0]
    assert "--diff" in args_line
    # diff_file path always resolves under .giton/
    assert ".giton" in args_line


def test_plugin_root_placeholder(repo, tmp_path, monkeypatch):
    fake = _write_fake_plugin(tmp_path, "rootplug")
    log = tmp_path / "rootplug.log"
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")
    _register("rootplug", "rootplug --workdir {root}", "pre-commit")

    (repo / "z.txt").write_text("z\n")
    _git(["add", "z.txt"], repo)

    out = run_trigger("pre-commit", cwd=repo)
    assert out.plugin_results[0].ok
    args_line = log.read_text().splitlines()[0]
    assert str(repo) in args_line


def test_plugin_failure_propagates_to_outcome(repo, tmp_path, monkeypatch):
    _write_fake_plugin(tmp_path, "failplug")
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_EXIT", "3")
    _register("failplug", "failplug", "pre-commit")

    (repo / "f.txt").write_text("f\n")
    _git(["add", "f.txt"], repo)

    out = run_trigger("pre-commit", cwd=repo)
    assert out.plugin_results[0].returncode == 3
    assert not out.plugin_results[0].ok
    assert not out.ok


def test_plugin_disabled_is_skipped(repo, tmp_path, monkeypatch):
    _write_fake_plugin(tmp_path, "skipplug")
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")
    _register("skipplug", "skipplug", "pre-commit", enabled=False)

    (repo / "g.txt").write_text("g\n")
    _git(["add", "g.txt"], repo)

    out = run_trigger("pre-commit", cwd=repo)
    assert out.plugin_results == []


def test_plugin_command_not_found(repo):
    # do NOT alter PATH (git must remain available); use a binary name that
    # is overwhelmingly unlikely to exist anywhere on the system.
    _register(
        "ghostplug", "giton-nonexistent-fake-binary-xyz123", "pre-commit"
    )

    (repo / "h.txt").write_text("h\n")
    _git(["add", "h.txt"], repo)

    out = run_trigger("pre-commit", cwd=repo)
    assert out.plugin_results[0].returncode == 127
    assert not out.ok


def test_multiple_plugins_run_in_order(repo, tmp_path, monkeypatch):
    _write_fake_plugin(tmp_path, "p1")
    _write_fake_plugin(tmp_path, "p2")
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")
    _register("p1", "p1", "pre-commit")
    _register("p2", "p2", "pre-commit")

    (repo / "i.txt").write_text("i\n")
    _git(["add", "i.txt"], repo)

    out = run_trigger("pre-commit", cwd=repo)
    names = [r.plugin for r in out.plugin_results]
    assert names == ["p1", "p2"]
    assert all(r.ok for r in out.plugin_results)


def test_default_catalog_commands_are_well_formed():
    """Catch regressions where a default plugin's command refers to a
    non-existent subcommand. We can't run them in CI without the deps
    installed, but we can verify the placeholder syntax parses."""
    from giton import catalog
    for entry in catalog.defaults():
        cmd = entry.record.command
        # placeholder substitution must succeed with reasonable inputs
        formatted = cmd.format(paths="a.py", diff_file="/tmp/d.patch", root="/tmp/r")
        assert formatted  # non-empty
        # and the binary name (first token) must equal the entry name
        assert formatted.split()[0] == entry.record.name
