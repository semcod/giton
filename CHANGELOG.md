# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.5] - 2026-05-27

### Docs
- Update README.md

### Other
- Update .idea/misc.xml

## [0.1.4] - 2026-05-27

### Docs
- Update CHANGELOG.md
- Update README.md
- Update examples/advanced/README.md
- Update examples/basic/README.md
- Update examples/testing/README.md

### Test
- Update tests/test_history.py
- Update tests/test_policies.py

### Other
- Update VERSION
- Update examples/advanced/Dockerfile
- Update examples/advanced/logs/log.txt
- Update examples/advanced/main.py
- Update examples/basic/Dockerfile
- Update examples/basic/logs/log.txt
- Update examples/basic/main.py
- Update examples/testing/Dockerfile
- Update examples/testing/docker-compose.yml
- Update examples/testing/logs/log.txt
- ... and 5 more files

## [0.1.4] - 2026-05-27

### Added
- New `commit-msg` git hook: validates the message file before the
  commit is finalized. Aborts with a tip when policies fail; user's
  message is preserved so they can re-run `git commit`.
  Installed automatically by `giton init`.
- `giton fixup [--target SHA] [--yes]` — creates a `fixup!` commit
  from the staged index, recording a backup ref under
  `refs/giton/backup/fixup-<timestamp>` first.
- New `giton history` sub-app:
  - `history log [-n N] [-r RANGE]` — show commits eligible for push,
    highlighting `fixup!` entries.
  - `history clean [--base REF] [--yes] [-i]` — safe
    `git rebase -i --autosquash` with backup ref
    `refs/giton/backup/clean-<timestamp>` and headless edit by default
    (`GIT_SEQUENCE_EDITOR=true GIT_EDITOR=true`).
- New module `giton/history.py` with reusable primitives:
  `head_sha`, `make_backup_ref`, `list_log`, `upstream_range`,
  `create_fixup`, `has_staged_changes`, `autosquash`.
- Tests: `tests/test_history.py` (8 cases) covering hook installation,
  backup refs, fixup creation, autosquash, CLI fixup flow, and the
  `commit-msg` hook on both invalid and valid subjects.

### Changed
- `policies.conventional_commits` and `policies.no_wip_commits` now
  also fire on the `commit-msg` trigger.
- `repo_config` defaults gained a `commit-msg` entry with
  `fail_on_policy: true`.
- Fixed `examples/testing/test_giton_integration.py`: positional
  `policy check pre-commit` form replaced with `--trigger pre-commit`
  and the result is now asserted.

## [0.1.3] - 2026-05-27

### Added
- Built-in policy engine (`giton/policies.py`) with four checks:
  `conventional_commits`, `no_wip_commits`, `no_secrets`,
  `max_file_size`. Runs on every hook trigger, no plugins required.
- Per-repo configuration file `.giton/config.yaml` with per-policy
  options and per-trigger `fail_on_policy` switch (`giton/repo_config.py`).
- New CLI sub-app `giton policy` with `check`, `init`, `list` commands.
- Interactive helper `giton/interactive.py` (`confirm`, `choose`)
  honouring `GITON_NON_INTERACTIVE` and TTY detection.
- `runner.run_trigger` now returns a `TriggerOutcome` carrying both
  policy findings and plugin results; hooks fail when
  `fail_on_policy` and any error is present.
- Tests: `tests/test_policies.py` covers all checks, repo-config
  override semantics, and an end-to-end `run_trigger` flow.

### Changed
- `giton hook pre-commit` / `pre-push` now also evaluate built-in
  policies; `post-commit` runs them advisory by default.
- Shell REPL gained `policy list|check|init` commands.

## [0.1.2] - 2026-05-27

### Docs
- Update CHANGELOG.md
- Update README.md
- Update TODO.md

### Test
- Update tests/test_basic.py

### Other
- Update .gitignore
- Update .koru/event-store.jsonl
- Update .koru/events/observability.jsonl
- Update .koru/history.jsonl
- Update .koru/onboarding.json
- Update .koru/project.json
- Update .planfile/.koru/autonomous-state.json
- Update .planfile/.koru/autonomy-telemetry.json
- Update .planfile/.koru/event-store.jsonl
- Update .planfile/.koru/nfo-events.jsonl
- ... and 9 more files

## [0.1.1] - 2026-05-27

### Docs
- Update README.md

### Test
- Update tests/__init__.py
- Update tests/test_basic.py

### Other
- Update .env.example
- Update .idea/.gitignore
- Update .idea/giton.iml
- Update .idea/inspectionProfiles/Project_Default.xml
- Update .idea/inspectionProfiles/profiles_settings.xml
- Update .idea/modules.xml
- Update .idea/pyProjectModel.xml
- Update .idea/vcs.xml
- Update uv.lock

