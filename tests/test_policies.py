"""Tests for the built-in policy engine and repo config."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from giton import policies, repo_config
from giton.context import GitContext


def _ctx(root: Path, **kw) -> GitContext:
    return GitContext(root=root, **kw)


def test_conventional_commits_accepts_valid():
    cfg = repo_config.RepoConfig(raw=repo_config.DEFAULT_CONFIG)
    ctx = _ctx(Path("/tmp"), last_commit_subject="feat(api): add endpoint")
    assert policies.evaluate(ctx, cfg, "post-commit") == []


def test_conventional_commits_rejects_invalid():
    cfg = repo_config.RepoConfig(raw=repo_config.DEFAULT_CONFIG)
    ctx = _ctx(Path("/tmp"), last_commit_subject="just some change")
    findings = policies.evaluate(ctx, cfg, "post-commit")
    assert any(f.policy == "conventional_commits" and f.is_error for f in findings)


def test_no_wip_commits_blocks_wip():
    cfg = repo_config.RepoConfig(raw=repo_config.DEFAULT_CONFIG)
    ctx = _ctx(Path("/tmp"), last_commit_subject="wip: things")
    findings = policies.evaluate(ctx, cfg, "post-commit")
    assert any(f.policy == "no_wip_commits" and f.is_error for f in findings)


def test_no_secrets_detects_aws_key():
    cfg = repo_config.RepoConfig(raw=repo_config.DEFAULT_CONFIG)
    diff = "diff --git a/x b/x\n+++ b/x\n+AKIAABCDEFGHIJKLMNOP\n"
    ctx = _ctx(Path("/tmp"), staged_diff=diff)
    findings = policies.evaluate(ctx, cfg, "pre-commit")
    assert any(f.policy == "no_secrets" for f in findings)


def test_no_secrets_skips_non_added_lines():
    cfg = repo_config.RepoConfig(raw=repo_config.DEFAULT_CONFIG)
    diff = "diff --git a/x b/x\n-AKIAABCDEFGHIJKLMNOP\n"
    ctx = _ctx(Path("/tmp"), staged_diff=diff)
    findings = policies.evaluate(ctx, cfg, "pre-commit")
    assert not any(f.policy == "no_secrets" for f in findings)


def test_max_file_size_flags_big_file(tmp_path):
    cfg = repo_config.RepoConfig(raw=repo_config.DEFAULT_CONFIG)
    big = tmp_path / "big.bin"
    big.write_bytes(b"x" * (513 * 1024))
    ctx = _ctx(tmp_path, staged_paths=["big.bin"])
    findings = policies.evaluate(ctx, cfg, "pre-commit")
    assert any(f.policy == "max_file_size" for f in findings)


def test_repo_config_write_and_load(tmp_path):
    path = repo_config.write_default(tmp_path)
    assert path.exists()
    cfg = repo_config.load(tmp_path)
    assert cfg.path == path
    assert cfg.policy("conventional_commits").get("enabled") is True


def test_repo_config_user_override(tmp_path):
    cfg_path = tmp_path / ".giton" / "config.yaml"
    cfg_path.parent.mkdir(parents=True)
    cfg_path.write_text(
        "policies:\n"
        "  no_wip_commits:\n"
        "    enabled: false\n"
    )
    cfg = repo_config.load(tmp_path)
    assert cfg.policy("no_wip_commits").get("enabled") is False
    # other policies remain default-on
    assert cfg.policy("conventional_commits").get("enabled") is True


def test_runner_returns_outcome_with_findings(tmp_path, monkeypatch):
    """End-to-end: run_trigger collects policy findings."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    repo = tmp_path / "r"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    (repo / "a.txt").write_text("hi")
    subprocess.run(["git", "add", "a.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "wip junk"], cwd=repo, check=True)

    from giton.runner import run_trigger
    out = run_trigger("post-commit", cwd=repo)
    assert any(f.policy == "no_wip_commits" for f in out.findings)
