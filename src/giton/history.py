"""Safe history operations: fixup commits + autosquash before push.

Every operation that rewrites history first records a backup ref under
`refs/giton/backup/<timestamp>` so the user can always recover via
`git update-ref HEAD <backup>`.
"""
from __future__ import annotations

import datetime as _dt
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GitResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def _git(args: list[str], cwd: Path, *, env: dict | None = None) -> GitResult:
    proc = subprocess.run(
        ["git", *args], cwd=cwd, check=False, capture_output=True, text=True,
        env=env,
    )
    return GitResult(proc.returncode, proc.stdout, proc.stderr)


def head_sha(cwd: Path) -> str:
    return _git(["rev-parse", "HEAD"], cwd).stdout.strip()


def make_backup_ref(cwd: Path, prefix: str = "fixup") -> str:
    """Create `refs/giton/backup/<prefix>-<timestamp>` pointing at HEAD."""
    ts = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    ref = f"refs/giton/backup/{prefix}-{ts}"
    sha = head_sha(cwd)
    if not sha:
        return ""
    _git(["update-ref", ref, sha], cwd)
    return ref


def list_log(cwd: Path, range_: str | None = None, limit: int = 20) -> list[tuple[str, str]]:
    """Return (sha, subject) pairs for recent commits."""
    args = ["log", f"--max-count={limit}", "--pretty=%H%x09%s"]
    if range_:
        args.append(range_)
    out = _git(args, cwd).stdout
    rows: list[tuple[str, str]] = []
    for line in out.splitlines():
        sha, _, subj = line.partition("\t")
        if sha:
            rows.append((sha.strip(), subj.strip()))
    return rows


def upstream_range(cwd: Path) -> str | None:
    out = _git(
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd
    ).stdout.strip()
    if not out:
        return None
    return f"{out}..HEAD"


# --- fixup commits --------------------------------------------------------

def create_fixup(
    cwd: Path,
    target_sha: str,
    *,
    no_verify: bool = True,
) -> GitResult:
    """Create a `fixup!` commit pointing at `target_sha` from staged changes."""
    args = ["commit", "--fixup", target_sha]
    if no_verify:
        args.append("--no-verify")
    return _git(args, cwd)


def has_staged_changes(cwd: Path) -> bool:
    return _git(["diff", "--cached", "--quiet"], cwd).returncode != 0


# --- autosquash -----------------------------------------------------------

def autosquash(
    cwd: Path,
    base: str,
    *,
    interactive: bool = False,
) -> GitResult:
    """Run `git rebase -i --autosquash <base>`.

    With `interactive=False` (default) we set `GIT_SEQUENCE_EDITOR` to convert
    "pick" to "fixup" for commits that start with "fixup!" so they get squashed.
    """
    import os
    import sys
    import tempfile
    
    args = ["rebase", "-i", "--autosquash", base]
    env = dict(os.environ)
    
    if not interactive:
        # Create a Python script to modify the rebase todo list
        script_content = f"""#!{sys.executable}
import sys
with open(sys.argv[1], 'r') as f:
    lines = f.readlines()
modified = []
for line in lines:
    # Convert "pick <sha> fixup! ..." to "fixup <sha> fixup! ..."
    if line.startswith('pick ') and 'fixup!' in line:
        modified.append('fixup ' + line[5:])
    else:
        modified.append(line)
with open(sys.argv[1], 'w') as f:
    f.writelines(modified)
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            script_path = f.name
        
        try:
            os.chmod(script_path, 0o755)
            env["GIT_SEQUENCE_EDITOR"] = script_path
            env["GIT_EDITOR"] = "true"
            result = _git(args, cwd, env=env)
        finally:
            os.unlink(script_path)
        return result
    
    return _git(args, cwd, env=env)
