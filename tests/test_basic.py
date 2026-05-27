"""Smoke tests for gix."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from gix import catalog
from gix.cli import app
from gix.config import (
    PluginRecord,
    USER_PLUGINS_FILE,
    load_plugins,
    save_plugins,
    upsert_plugin,
)
from gix.hooks import install as install_hooks


@pytest.fixture(autouse=True)
def isolated_xdg(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    # reload module-level path
    import importlib
    from gix import config
    importlib.reload(config)
    # also reload anything that imported these
    from gix import plugins, catalog as cat, runner
    importlib.reload(plugins)
    yield


def test_catalog_has_three_defaults():
    assert len(catalog.DEFAULT_PLUGIN_NAMES) == 3
    for name in catalog.DEFAULT_PLUGIN_NAMES:
        assert name in catalog.CATALOG


def test_catalog_categories_grouped():
    cats = catalog.list_categories()
    assert any(c.startswith("lang:") for c in cats)
    assert any(c.startswith("task:") for c in cats)


def test_plugin_persistence(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    import importlib
    from gix import config
    importlib.reload(config)
    rec = PluginRecord(name="demo", command="echo hello", triggers=["pre-commit"])
    config.upsert_plugin(rec)
    loaded = config.load_plugins()
    assert any(p.name == "demo" for p in loaded)


def test_cli_help_runs():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "gix" in result.stdout


def test_cli_plugin_catalog_runs():
    runner = CliRunner()
    result = runner.invoke(app, ["plugin", "catalog"])
    assert result.exit_code == 0
    assert "pyqual" in result.stdout
    assert "vallm" in result.stdout
    assert "pretest" in result.stdout


def test_hook_install_in_temp_repo(tmp_path, monkeypatch):
    # init bare repo
    repo = tmp_path / "r"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    written = install_hooks(repo)
    names = {p.name for p in written}
    assert {"pre-commit", "post-commit", "pre-push"} <= names
    for p in written:
        assert os.access(p, os.X_OK)
        assert "gix hook" in p.read_text()
