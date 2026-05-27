# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.10] - 2026-05-27

### Fixed
- Fix string-concat issues (ticket-f8e33603)
- Fix smart-return-type issues (ticket-5241a23f)
- Fix unused-imports issues (ticket-678976ed)
- Fix ai-boilerplate issues (ticket-f1340096)
- Fix smart-return-type issues (ticket-cf388d88)
- Fix unused-imports issues (ticket-ef62ed06)
- Fix ai-boilerplate issues (ticket-c9e99715)
- Fix smart-return-type issues (ticket-25895170)
- Fix llm-hallucinations issues (ticket-d5864acf)
- Fix ai-boilerplate issues (ticket-22c7a20b)

## [0.1.10] - 2026-05-27

### Fixed
- Fix ai-boilerplate issues (ticket-520cc8b0)
- Fix unused-imports issues (ticket-d9ba49df)
- Fix smart-return-type issues (ticket-a078f21e)
- Fix unused-imports issues (ticket-6bb663ef)
- Fix magic-numbers issues (ticket-670a4fff)
- Fix ai-boilerplate issues (ticket-7b75c64a)
- Fix unused-imports issues (ticket-7f7595f5)
- Fix unused-imports issues (ticket-7836e6dc)
- Fix magic-numbers issues (ticket-364cdbb4)
- Fix unused-imports issues (ticket-3df4999d)
- Fix string-concat issues (ticket-ddefd20d)
- Fix unused-imports issues (ticket-37e354ce)
- Fix string-concat issues (ticket-0959072c)
- Fix unused-imports issues (ticket-cbff985c)
- Fix unused-imports issues (ticket-d9544d1d)
- Fix magic-numbers issues (ticket-01a9b257)
- Fix unused-imports issues (ticket-bf9e08bd)
- Fix unused-imports issues (ticket-dc102598)
- Fix magic-numbers issues (ticket-0afc68c7)
- Fix smart-return-type issues (ticket-a5264d97)
- Fix unused-imports issues (ticket-97fe62d8)
- Fix string-concat issues (ticket-07df1cf8)
- Fix unused-imports issues (ticket-9135e71a)
- Fix unused-imports issues (ticket-580c65b2)
- Fix magic-numbers issues (ticket-f6e8663e)
- Fix smart-return-type issues (ticket-b5dc313c)
- Fix unused-imports issues (ticket-e85782ed)
- Fix smart-return-type issues (ticket-bbf11608)
- Fix unused-imports issues (ticket-61cab342)

## [Unreleased]

## [0.1.8] - 2026-05-27

### Docs
- Update README.md
- Update examples/plugins/README.md

### Test
- Update tests/test_plugin_runner.py

### Other
- Update examples/plugins/test_plugin_lifecycle.py

## [0.1.7] - 2026-05-27

### Docs
- Update README.md

## [0.1.6] - 2026-05-27

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update project/README.md
- Update project/context.md

### Test
- Update testql-scenarios/generated-cli-tests.testql.toon.yaml
- Update testql-scenarios/generated-from-pytests.testql.toon.yaml

### Other
- Update .code2llm_cache/Dockerfile_1779904106733599983_1063.pkl
- Update .code2llm_cache/Dockerfile_1779904204018542516_855.pkl
- Update .code2llm_cache/Dockerfile_1779904222125718170_858.pkl
- Update .code2llm_cache/__init___1779904484527861301_88.pkl
- Update .code2llm_cache/__main___1779903461855440523_64.pkl
- Update .code2llm_cache/catalog_1779903467942497517_4931.pkl
- Update .code2llm_cache/cli_1779904308177553774_14209.pkl
- Update .code2llm_cache/config_1779903467956497648_2190.pkl
- Update .code2llm_cache/context_1779903467968497760_1979.pkl
- Update .code2llm_cache/docker-compose_1779904015273715995_275.pkl
- ... and 43 more files

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

