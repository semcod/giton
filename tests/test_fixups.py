"""Tests for the auto-fixup layer."""
from __future__ import annotations

import subprocess
from pathlib import Path

from giton import policies, repo_config, store
from giton.context import GitContext
from giton.fixups import apply_all, apply_fix


def _ctx(root: Path, **kw) -> GitContext:
    return GitContext(root=root, **kw)


def test_conventional_commits_includes_fix():
    cfg = repo_config.RepoConfig(raw=repo_config.DEFAULT_CONFIG)
    ctx = _ctx(Path("/tmp"), last_commit_subject="just some change")
    findings = policies.evaluate(ctx, cfg, "post-commit")
    f = next((f for f in findings if f.policy == "conventional_commits"), None)
    assert f is not None
    assert f.fix is not None
    assert 'git commit --amend -m "chore: just some change"' == f.fix


def test_no_wip_commits_includes_fix():
    cfg = repo_config.RepoConfig(raw=repo_config.DEFAULT_CONFIG)
    ctx = _ctx(Path("/tmp"), last_commit_subject="wip: things")
    findings = policies.evaluate(ctx, cfg, "post-commit")
    f = next((f for f in findings if f.policy == "no_wip_commits"), None)
    assert f is not None
    assert f.fix is not None
    assert f.fix == 'git commit --amend -m ": things"'


def test_store_roundtrip(tmp_path):
    findings = [
        policies.Finding("x", "error", "msg", "loc", fix='echo hello'),
        policies.Finding("y", "warn", "msg2"),
    ]
    store.save_findings(findings, tmp_path)
    loaded = store.load_findings(tmp_path)
    assert len(loaded) == 2
    assert loaded[0].fix == 'echo hello'
    assert loaded[1].fix is None


def test_apply_fix_runs_command(tmp_path):
    marker = tmp_path / "marker.txt"
    f = policies.Finding("test", "error", "msg", fix=f'touch "{marker}"')
    assert apply_fix(f, tmp_path, yes=True)
    assert marker.exists()


def test_apply_all_counts(tmp_path):
    f1 = policies.Finding("a", "error", "msg", fix='true')
    f2 = policies.Finding("b", "error", "msg2")  # no fix
    applied, total = apply_all([f1, f2], tmp_path, yes=True)
    assert applied == 1
    assert total == 1


def test_apply_fix_in_real_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    (repo / "a.txt").write_text("hi")
    subprocess.run(["git", "add", "a.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "wip: bad"], cwd=repo, check=True)

    cfg = repo_config.RepoConfig(raw=repo_config.DEFAULT_CONFIG)
    ctx = _ctx(repo, last_commit_subject="wip: bad")
    findings = policies.evaluate(ctx, cfg, "post-commit")
    f = next((f for f in findings if f.policy == "no_wip_commits" and f.fix), None)
    assert f is not None
    assert apply_fix(f, repo, yes=True)

    out = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        cwd=repo, capture_output=True, text=True, check=True,
    )
    assert out.stdout.strip() == ": bad"
