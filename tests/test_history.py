"""Tests for history operations: fixup + autosquash + commit-msg hook."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from giton import history
from giton.cli import app
from giton.hooks import install as install_hooks


def _git(args, cwd):
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "r"
    r.mkdir()
    _git(["init", "-q"], r)
    _git(["config", "user.email", "t@t"], r)
    _git(["config", "user.name", "t"], r)
    (r / "seed.txt").write_text("seed\n")
    _git(["add", "seed.txt"], r)
    _git(["commit", "-q", "-m", "chore: seed"], r)
    (r / "a.txt").write_text("one\n")
    _git(["add", "a.txt"], r)
    _git(["commit", "-q", "-m", "feat: initial"], r)
    return r


def test_install_hooks_includes_commit_msg(repo):
    written = install_hooks(repo)
    names = {p.name for p in written}
    assert "commit-msg" in names
    txt = (repo / ".git" / "hooks" / "commit-msg").read_text()
    assert "giton hook commit-msg" in txt


def test_make_backup_ref(repo):
    ref = history.make_backup_ref(repo, prefix="test")
    assert ref.startswith("refs/giton/backup/test-")
    sha = subprocess.run(
        ["git", "rev-parse", ref], cwd=repo, capture_output=True, text=True
    ).stdout.strip()
    assert sha == history.head_sha(repo)


def test_create_fixup_and_autosquash(repo):
    # add second commit
    (repo / "b.txt").write_text("b\n")
    _git(["add", "b.txt"], repo)
    _git(["commit", "-q", "-m", "feat: add b"], repo)
    head_before = history.head_sha(repo)

    # stage a fix
    (repo / "a.txt").write_text("one\nfix\n")
    _git(["add", "a.txt"], repo)
    assert history.has_staged_changes(repo)

    # fixup the *second* commit (`feat: add b`) so we can autosquash against
    # the first commit, which is a valid (non-root) base for `git rebase -i`.
    target_sha = subprocess.run(
        ["git", "rev-parse", "HEAD~1"], cwd=repo, capture_output=True, text=True
    ).stdout.strip()
    res = history.create_fixup(repo, target_sha)
    assert res.ok, res.stderr
    log = history.list_log(repo, limit=5)
    assert any(s.startswith("fixup!") for _, s in log)

    # base = parent of target = the initial commit (HEAD~2)
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD~2"], cwd=repo, capture_output=True, text=True
    ).stdout.strip()
    res = history.autosquash(repo, base_sha)
    assert res.ok, res.stderr
    log = history.list_log(repo, limit=10)
    assert not any(s.startswith("fixup!") for _, s in log)
    assert history.head_sha(repo) != head_before


def test_cli_fixup_requires_staged(repo, monkeypatch):
    monkeypatch.chdir(repo)
    runner = CliRunner()
    result = runner.invoke(app, ["fixup", "--yes"])
    assert result.exit_code == 1
    assert "nothing staged" in result.stdout.lower()


def test_cli_fixup_creates_commit(repo, monkeypatch):
    monkeypatch.chdir(repo)
    (repo / "a.txt").write_text("one\nadded\n")
    _git(["add", "a.txt"], repo)
    runner = CliRunner()
    result = runner.invoke(app, ["fixup", "--yes"])
    assert result.exit_code == 0, result.stdout
    log = history.list_log(repo, limit=5)
    assert any(s.startswith("fixup!") for _, s in log)


def test_commit_msg_hook_blocks_wip(repo, tmp_path, monkeypatch):
    monkeypatch.chdir(repo)
    msg_file = tmp_path / "msg"
    msg_file.write_text("wip junk\n# comment\n")
    runner = CliRunner()
    result = runner.invoke(app, ["hook", "commit-msg", str(msg_file)])
    assert result.exit_code == 1
    assert "no_wip_commits" in result.stdout


def test_commit_msg_hook_accepts_conventional(repo, tmp_path, monkeypatch):
    monkeypatch.chdir(repo)
    msg_file = tmp_path / "msg"
    msg_file.write_text("feat(api): add endpoint\n# comment\n")
    runner = CliRunner()
    result = runner.invoke(app, ["hook", "commit-msg", str(msg_file)])
    assert result.exit_code == 0


def test_history_log_command(repo, monkeypatch):
    monkeypatch.chdir(repo)
    (repo / "b.txt").write_text("b\n")
    _git(["add", "b.txt"], repo)
    _git(["commit", "-q", "-m", "feat: b"], repo)
    runner = CliRunner()
    result = runner.invoke(app, ["history", "log", "-n", "5"])
    assert result.exit_code == 0
    assert "feat: b" in result.stdout
