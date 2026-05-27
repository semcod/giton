# giton

Local AI layer for git: orchestrates policies & plugins between commit and push.

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Code Analysis](#code-analysis)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `giton`
- **version**: `0.1.9`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, pyqual.yaml, goal.yaml, .env.example, project/(3 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: giton;
  version: 0.1.9;
}

dependencies {
  runtime: "typer>=0.12, rich>=13.7, PyYAML>=6.0";
  dev: "pytest>=8.0, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="giton"] {

}

deploy {
  target: docker;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  python_version: >=3.10;
}
```

## Interfaces

### CLI Entry Points

- `giton`

### testql Scenarios

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m gix
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m gix --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m gix --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m gix --help" 10000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, ${api_url:-http://localhost:8101}
  timeout_ms, 10000

# Converted 3 assertions from pytest
ASSERT[3]{field, operator, expected}:
  hello(), ==, "world"
  policy_result.returncode, ==, 0
  test_result.returncode, ==, 0
```

## Quality Pipeline (`pyqual.yaml`)

```yaml markpact:pyqual path=pyqual.yaml
pipeline:
  name: quality-loop

  # Quickstart: replace all of this with a single profile line:
  #   profile: python-minimal   # analyze → validate → lint → fix → test
  #   profile: python-publish   # + git-push and make-publish
  #   profile: python-secure    # + pip-audit, bandit, detect-secrets
  #   profile: python           # standard (needs manual stage config)
  #   profile: ci               # CI-only, no fix
  # See: pyqual profiles

  # Quality gates — pipeline iterates until ALL pass
  metrics:
    cc_max: 15           # cyclomatic complexity per function
    vallm_pass_min: 90   # vallm validation pass rate (%)
    coverage_min: 80     # test coverage (%)

  # Pipeline stages — use 'tool:' for built-in presets or 'run:' for custom commands
  # See all presets: pyqual tools
  # when: any_stage_fail    — run only when a prior stage in this iteration failed
  # when: metrics_fail      — run only when quality gates are not yet passing
  # when: first_iteration   — run only on iteration 1 (skip re-runs after fix)
  # when: after_fix         — run only after the fix stage ran in this iteration
  stages:
    - name: analyze
      tool: code2llm-filtered   # uses sensible exclude defaults

    - name: validate
      tool: vallm-filtered      # uses sensible exclude defaults

    - name: prefact
      tool: prefact
      optional: true
      when: any_stage_fail
      timeout: 900

    - name: fix
      tool: llx-fix
      optional: true
      when: any_stage_fail
      timeout: 1800

    - name: test
      tool: pytest

    - name: push
      tool: git-push            # built-in: git add + commit + push
      optional: true
      timeout: 120

  # Loop behavior
  loop:
    max_iterations: 3
    on_fail: report      # report | create_ticket | block
    ticket_backends:     # backends to sync when on_fail = create_ticket
      - markdown        # TODO.md (default)
      # - github        # GitHub Issues (requires GITHUB_TOKEN)

  # Environment (optional)
  env:
    LLM_MODEL: openrouter/qwen/qwen3-coder-next
```

## Configuration

```yaml
project:
  name: giton
  version: 0.1.9
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
typer>=0.12
rich>=13.7
PyYAML>=6.0
```

### Development

```text markpact:deps python scope=dev
pytest>=8.0
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Deployment

```bash markpact:run
pip install giton

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `*(not set)*` | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model (default: openrouter/qwen/qwen3-coder-next) |
| `PFIX_AUTO_APPLY` | `true` | true = apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | true = auto pip/uv install |
| `PFIX_AUTO_RESTART` | `false` | true = os.execv restart after fix |
| `PFIX_MAX_RETRIES` | `3` |  |
| `PFIX_DRY_RUN` | `false` |  |
| `PFIX_ENABLED` | `true` |  |
| `PFIX_GIT_COMMIT` | `false` | true = auto-commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | false = disable .pfix_backups/ directory |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`gix`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `venv/lib/python3.13/site-packages/cryptography/__init__.py:__version__`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# gix | 31f 3164L | python:28,shell:2,less:1 | 2026-05-27
# stats: 152 func | 8 cls | 31 mod | CC̄=3.6 | critical:6 | cycles:0
# alerts[5]: CC dispatch=23; CC _cmd_policy=17; CC history_clean=12; CC install_from_catalog=10; CC _check_conventional_commits=10
# hotspots[5]: hook_commit_msg fan=18; dispatch fan=16; test_register_run_and_unregister fan=15; history_clean fan=15; fixup fan=12
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[31]:
  app.doql.less,29
  examples/advanced/main.py,157
  examples/basic/main.py,68
  examples/plugins/test_plugin_lifecycle.py,117
  examples/testing/sample_project/src/example.py,21
  examples/testing/sample_project/tests/test_example.py,31
  examples/testing/test_giton_integration.py,179
  project.sh,59
  src/giton/__init__.py,4
  src/giton/__main__.py,5
  src/giton/catalog.py,174
  src/giton/cli.py,448
  src/giton/config.py,75
  src/giton/context.py,67
  src/giton/fixups.py,69
  src/giton/history.py,141
  src/giton/hooks.py,49
  src/giton/interactive.py,59
  src/giton/plugins.py,144
  src/giton/policies.py,172
  src/giton/repo_config.py,102
  src/giton/runner.py,124
  src/giton/shell.py,217
  src/giton/store.py,37
  tests/__init__.py,1
  tests/test_basic.py,86
  tests/test_fixups.py,85
  tests/test_history.py,134
  tests/test_plugin_runner.py,209
  tests/test_policies.py,99
  tree.sh,2
D:
  examples/advanced/main.py:
    e: demonstrate_plugin_management,demonstrate_catalog,demonstrate_hooks,demonstrate_trigger_sequence,main
    demonstrate_plugin_management()
    demonstrate_catalog()
    demonstrate_hooks()
    demonstrate_trigger_sequence()
    main()
  examples/basic/main.py:
    e: test_basic_giton_usage,main
    test_basic_giton_usage()
    main()
  examples/plugins/test_plugin_lifecycle.py:
    e: _git,isolated_repo,test_register_run_and_unregister,test_default_catalog_pyqual_command_is_valid
    _git(args;cwd)
    isolated_repo(tmp_path;monkeypatch)
    test_register_run_and_unregister(isolated_repo;tmp_path;monkeypatch)
    test_default_catalog_pyqual_command_is_valid()
  examples/testing/sample_project/src/example.py:
    e: add,multiply,divide
    add(a;b)
    multiply(a;b)
    divide(a;b)
  examples/testing/sample_project/tests/test_example.py:
    e: test_add,test_multiply,test_divide,test_divide_by_zero
    test_add()
    test_multiply()
    test_divide()
    test_divide_by_zero()
  examples/testing/test_giton_integration.py:
    e: temp_repo,test_giton_installation,test_giton_policy_check,test_giton_policy_init,test_giton_plugin_list,test_sample_project_tests,test_giton_with_pytest_integration
    temp_repo()
    test_giton_installation()
    test_giton_policy_check(temp_repo)
    test_giton_policy_init(temp_repo)
    test_giton_plugin_list()
    test_sample_project_tests()
    test_giton_with_pytest_integration(temp_repo)
  src/giton/__init__.py:
  src/giton/__main__.py:
  src/giton/catalog.py:
    e: _entry,list_categories,find,defaults,CatalogEntry
    CatalogEntry:
    _entry(name;desc)
    list_categories()
    find(name)
    defaults()
  src/giton/cli.py:
    e: _root,init,uninit,status,shell,doctor,plugin_list,plugin_catalog,plugin_install,plugin_install_defaults,plugin_install_category,plugin_remove,hook_pre_commit,hook_commit_msg,hook_post_commit,hook_pre_push,policy_check,policy_init,policy_list,policy_fix,fixup,history_log,history_clean
    _root(ctx;version)
    init(install_default_plugins)
    uninit()
    status()
    shell()
    doctor()
    plugin_list()
    plugin_catalog()
    plugin_install(name)
    plugin_install_defaults()
    plugin_install_category(category)
    plugin_remove(name)
    hook_pre_commit()
    hook_commit_msg(message_file)
    hook_post_commit()
    hook_pre_push()
    policy_check(trigger)
    policy_init(overwrite)
    policy_list()
    policy_fix(yes)
    fixup(target;yes)
    history_log(limit;range_)
    history_clean(base;yes;interactive_rebase)
  src/giton/config.py:
    e: _xdg_config_home,ensure_user_dirs,load_plugins,save_plugins,upsert_plugin,remove_plugin,PluginRecord
    PluginRecord: to_dict(0),from_dict(2)
    _xdg_config_home()
    ensure_user_dirs()
    load_plugins()
    save_plugins(plugins)
    upsert_plugin(plugin)
    remove_plugin(name)
  src/giton/context.py:
    e: _run,repo_root,collect,GitContext
    GitContext: diff_file(0),paths_arg(0)
    _run(cmd;cwd)
    repo_root(cwd)
    collect(cwd)
  src/giton/fixups.py:
    e: apply_fix,apply_all
    apply_fix(finding;cwd)
    apply_all(findings;cwd)
  src/giton/history.py:
    e: _git,head_sha,make_backup_ref,list_log,upstream_range,create_fixup,has_staged_changes,autosquash,GitResult
    GitResult: ok(0)
    _git(args;cwd)
    head_sha(cwd)
    make_backup_ref(cwd;prefix)
    list_log(cwd;range_;limit)
    upstream_range(cwd)
    create_fixup(cwd;target_sha)
    has_staged_changes(cwd)
    autosquash(cwd;base)
  src/giton/hooks.py:
    e: hooks_dir,install,uninstall
    hooks_dir(repo_root)
    install(repo_root)
    uninstall(repo_root)
  src/giton/interactive.py:
    e: is_tty,confirm,choose
    is_tty()
    confirm(question)
    choose(question;options)
  src/giton/plugins.py:
    e: _pip_install,_init_plugin,install_from_catalog,install_defaults,install_category,uninstall,show_table,show_catalog
    _pip_install(target)
    _init_plugin(name)
    install_from_catalog(name)
    install_defaults()
    install_category(category)
    uninstall(name)
    show_table()
    show_catalog()
  src/giton/policies.py:
    e: _check_conventional_commits,_check_no_wip,_check_no_secrets,_check_max_file_size,evaluate,has_errors,Finding
    Finding: is_error(0)
    _check_conventional_commits(ctx;opts;trigger)
    _check_no_wip(ctx;opts;trigger)
    _check_no_secrets(ctx;opts;trigger)
    _check_max_file_size(ctx;opts;trigger)
    evaluate(ctx;repo_cfg;trigger)
    has_errors(findings)
  src/giton/repo_config.py:
    e: _deep_merge,load,write_default,RepoConfig
    RepoConfig: policy(1),hook(1),fail_on_policy(1)
    _deep_merge(base;over)
    load(repo_root)
    write_default(repo_root)
  src/giton/runner.py:
    e: _print_findings,_format_command,run_trigger,_run_plugin,PluginResult,TriggerOutcome
    PluginResult: ok(0)
    TriggerOutcome: ok(0)
    _print_findings(findings)
    _format_command(cmd;ctx)
    run_trigger(trigger;cwd)
    _run_plugin(plugin;ctx)
  src/giton/shell.py:
    e: _set_enabled,_cmd_status,_cmd_policy,_cmd_init,dispatch,run
    _set_enabled(name;value)
    _cmd_status()
    _cmd_policy(args)
    _cmd_init()
    dispatch(line)
    run()
  src/giton/store.py:
    e: save_findings,load_findings
    save_findings(findings;repo_root)
    load_findings(repo_root)
  tests/__init__.py:
  tests/test_basic.py:
    e: isolated_xdg,test_catalog_has_three_defaults,test_catalog_categories_grouped,test_plugin_persistence,test_cli_help_runs,test_cli_plugin_catalog_runs,test_hook_install_in_temp_repo
    isolated_xdg(tmp_path;monkeypatch)
    test_catalog_has_three_defaults()
    test_catalog_categories_grouped()
    test_plugin_persistence(tmp_path;monkeypatch)
    test_cli_help_runs()
    test_cli_plugin_catalog_runs()
    test_hook_install_in_temp_repo(tmp_path;monkeypatch)
  tests/test_fixups.py:
    e: _ctx,test_conventional_commits_includes_fix,test_no_wip_commits_includes_fix,test_store_roundtrip,test_apply_fix_runs_command,test_apply_all_counts,test_apply_fix_in_real_repo
    _ctx(root)
    test_conventional_commits_includes_fix()
    test_no_wip_commits_includes_fix()
    test_store_roundtrip(tmp_path)
    test_apply_fix_runs_command(tmp_path)
    test_apply_all_counts(tmp_path)
    test_apply_fix_in_real_repo(tmp_path)
  tests/test_history.py:
    e: _git,repo,test_install_hooks_includes_commit_msg,test_make_backup_ref,test_create_fixup_and_autosquash,test_cli_fixup_requires_staged,test_cli_fixup_creates_commit,test_commit_msg_hook_blocks_wip,test_commit_msg_hook_accepts_conventional,test_history_log_command
    _git(args;cwd)
    repo(tmp_path)
    test_install_hooks_includes_commit_msg(repo)
    test_make_backup_ref(repo)
    test_create_fixup_and_autosquash(repo)
    test_cli_fixup_requires_staged(repo;monkeypatch)
    test_cli_fixup_creates_commit(repo;monkeypatch)
    test_commit_msg_hook_blocks_wip(repo;tmp_path;monkeypatch)
    test_commit_msg_hook_accepts_conventional(repo;tmp_path;monkeypatch)
    test_history_log_command(repo;monkeypatch)
  tests/test_plugin_runner.py:
    e: _git,repo,_write_fake_plugin,_register,test_plugin_executes_and_expands_paths,test_plugin_diff_file_placeholder,test_plugin_root_placeholder,test_plugin_failure_propagates_to_outcome,test_plugin_disabled_is_skipped,test_plugin_command_not_found,test_multiple_plugins_run_in_order,test_default_catalog_commands_are_well_formed
    _git(args;cwd)
    repo(tmp_path;monkeypatch)
    _write_fake_plugin(tmp_path;name)
    _register(name;command;trigger)
    test_plugin_executes_and_expands_paths(repo;tmp_path;monkeypatch)
    test_plugin_diff_file_placeholder(repo;tmp_path;monkeypatch)
    test_plugin_root_placeholder(repo;tmp_path;monkeypatch)
    test_plugin_failure_propagates_to_outcome(repo;tmp_path;monkeypatch)
    test_plugin_disabled_is_skipped(repo;tmp_path;monkeypatch)
    test_plugin_command_not_found(repo)
    test_multiple_plugins_run_in_order(repo;tmp_path;monkeypatch)
    test_default_catalog_commands_are_well_formed()
  tests/test_policies.py:
    e: _ctx,test_conventional_commits_accepts_valid,test_conventional_commits_rejects_invalid,test_no_wip_commits_blocks_wip,test_no_secrets_detects_aws_key,test_no_secrets_skips_non_added_lines,test_max_file_size_flags_big_file,test_repo_config_write_and_load,test_repo_config_user_override,test_runner_returns_outcome_with_findings
    _ctx(root)
    test_conventional_commits_accepts_valid()
    test_conventional_commits_rejects_invalid()
    test_no_wip_commits_blocks_wip()
    test_no_secrets_detects_aws_key()
    test_no_secrets_skips_non_added_lines()
    test_max_file_size_flags_big_file(tmp_path)
    test_repo_config_write_and_load(tmp_path)
    test_repo_config_user_override(tmp_path)
    test_runner_returns_outcome_with_findings(tmp_path;monkeypatch)
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('gix', '0.1.9', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 29, 'less').
project_file('examples/advanced/main.py', 157, 'python').
project_file('examples/basic/main.py', 68, 'python').
project_file('examples/plugins/test_plugin_lifecycle.py', 117, 'python').
project_file('examples/testing/sample_project/src/example.py', 21, 'python').
project_file('examples/testing/sample_project/tests/test_example.py', 31, 'python').
project_file('examples/testing/test_giton_integration.py', 179, 'python').
project_file('project.sh', 59, 'shell').
project_file('src/giton/__init__.py', 4, 'python').
project_file('src/giton/__main__.py', 5, 'python').
project_file('src/giton/catalog.py', 174, 'python').
project_file('src/giton/cli.py', 448, 'python').
project_file('src/giton/config.py', 75, 'python').
project_file('src/giton/context.py', 67, 'python').
project_file('src/giton/fixups.py', 69, 'python').
project_file('src/giton/history.py', 141, 'python').
project_file('src/giton/hooks.py', 49, 'python').
project_file('src/giton/interactive.py', 59, 'python').
project_file('src/giton/plugins.py', 144, 'python').
project_file('src/giton/policies.py', 172, 'python').
project_file('src/giton/repo_config.py', 102, 'python').
project_file('src/giton/runner.py', 124, 'python').
project_file('src/giton/shell.py', 217, 'python').
project_file('src/giton/store.py', 37, 'python').
project_file('tests/__init__.py', 1, 'python').
project_file('tests/test_basic.py', 86, 'python').
project_file('tests/test_fixups.py', 85, 'python').
project_file('tests/test_history.py', 134, 'python').
project_file('tests/test_plugin_runner.py', 209, 'python').
project_file('tests/test_policies.py', 99, 'python').
project_file('tree.sh', 2, 'shell').

% ── Python Functions ─────────────────────────────────────
python_function('examples/advanced/main.py', 'demonstrate_plugin_management', 0, 3, 10).
python_function('examples/advanced/main.py', 'demonstrate_catalog', 0, 2, 7).
python_function('examples/advanced/main.py', 'demonstrate_hooks', 0, 4, 4).
python_function('examples/advanced/main.py', 'demonstrate_trigger_sequence', 0, 9, 4).
python_function('examples/advanced/main.py', 'main', 0, 2, 6).
python_function('examples/basic/main.py', 'test_basic_giton_usage', 0, 8, 4).
python_function('examples/basic/main.py', 'main', 0, 1, 1).
python_function('examples/plugins/test_plugin_lifecycle.py', '_git', 2, 1, 1).
python_function('examples/plugins/test_plugin_lifecycle.py', 'isolated_repo', 2, 1, 6).
python_function('examples/plugins/test_plugin_lifecycle.py', 'test_register_run_and_unregister', 3, 9, 15).
python_function('examples/plugins/test_plugin_lifecycle.py', 'test_default_catalog_pyqual_command_is_valid', 0, 5, 3).
python_function('examples/testing/sample_project/src/example.py', 'add', 2, 1, 0).
python_function('examples/testing/sample_project/src/example.py', 'multiply', 2, 1, 0).
python_function('examples/testing/sample_project/src/example.py', 'divide', 2, 2, 1).
python_function('examples/testing/sample_project/tests/test_example.py', 'test_add', 0, 3, 1).
python_function('examples/testing/sample_project/tests/test_example.py', 'test_multiply', 0, 3, 1).
python_function('examples/testing/sample_project/tests/test_example.py', 'test_divide', 0, 3, 1).
python_function('examples/testing/sample_project/tests/test_example.py', 'test_divide_by_zero', 0, 1, 2).
python_function('examples/testing/test_giton_integration.py', 'temp_repo', 0, 1, 3).
python_function('examples/testing/test_giton_integration.py', 'test_giton_installation', 0, 2, 1).
python_function('examples/testing/test_giton_integration.py', 'test_giton_policy_check', 1, 2, 2).
python_function('examples/testing/test_giton_integration.py', 'test_giton_policy_init', 1, 3, 2).
python_function('examples/testing/test_giton_integration.py', 'test_giton_plugin_list', 0, 2, 1).
python_function('examples/testing/test_giton_integration.py', 'test_sample_project_tests', 0, 3, 5).
python_function('examples/testing/test_giton_integration.py', 'test_giton_with_pytest_integration', 1, 3, 5).
python_function('src/giton/catalog.py', '_entry', 2, 2, 2).
python_function('src/giton/catalog.py', 'list_categories', 0, 3, 7).
python_function('src/giton/catalog.py', 'find', 1, 1, 1).
python_function('src/giton/catalog.py', 'defaults', 0, 2, 0).
python_function('src/giton/cli.py', '_root', 2, 3, 6).
python_function('src/giton/cli.py', 'init', 1, 4, 8).
python_function('src/giton/cli.py', 'uninit', 0, 2, 6).
python_function('src/giton/cli.py', 'status', 0, 4, 5).
python_function('src/giton/cli.py', 'shell', 0, 1, 2).
python_function('src/giton/cli.py', 'doctor', 0, 3, 5).
python_function('src/giton/cli.py', 'plugin_list', 0, 1, 2).
python_function('src/giton/cli.py', 'plugin_catalog', 0, 1, 2).
python_function('src/giton/cli.py', 'plugin_install', 1, 1, 2).
python_function('src/giton/cli.py', 'plugin_install_defaults', 0, 1, 2).
python_function('src/giton/cli.py', 'plugin_install_category', 1, 1, 3).
python_function('src/giton/cli.py', 'plugin_remove', 1, 1, 2).
python_function('src/giton/cli.py', 'hook_pre_commit', 0, 2, 3).
python_function('src/giton/cli.py', 'hook_commit_msg', 1, 9, 18).
python_function('src/giton/cli.py', 'hook_post_commit', 0, 1, 2).
python_function('src/giton/cli.py', 'hook_pre_push', 0, 2, 3).
python_function('src/giton/cli.py', 'policy_check', 1, 7, 11).
python_function('src/giton/cli.py', 'policy_init', 1, 2, 7).
python_function('src/giton/cli.py', 'policy_list', 0, 5, 7).
python_function('src/giton/cli.py', 'policy_fix', 1, 6, 7).
python_function('src/giton/cli.py', 'fixup', 2, 9, 12).
python_function('src/giton/cli.py', 'history_log', 2, 9, 8).
python_function('src/giton/cli.py', 'history_clean', 3, 12, 15).
python_function('src/giton/config.py', '_xdg_config_home', 0, 2, 3).
python_function('src/giton/config.py', 'ensure_user_dirs', 0, 1, 1).
python_function('src/giton/config.py', 'load_plugins', 0, 4, 6).
python_function('src/giton/config.py', 'save_plugins', 1, 2, 4).
python_function('src/giton/config.py', 'upsert_plugin', 1, 3, 3).
python_function('src/giton/config.py', 'remove_plugin', 1, 4, 3).
python_function('src/giton/context.py', '_run', 2, 1, 1).
python_function('src/giton/context.py', 'repo_root', 1, 2, 3).
python_function('src/giton/context.py', 'collect', 1, 5, 5).
python_function('src/giton/fixups.py', 'apply_fix', 2, 6, 4).
python_function('src/giton/fixups.py', 'apply_all', 2, 6, 3).
python_function('src/giton/history.py', '_git', 2, 1, 2).
python_function('src/giton/history.py', 'head_sha', 1, 1, 2).
python_function('src/giton/history.py', 'make_backup_ref', 2, 2, 4).
python_function('src/giton/history.py', 'list_log', 3, 4, 5).
python_function('src/giton/history.py', 'upstream_range', 1, 2, 2).
python_function('src/giton/history.py', 'create_fixup', 2, 2, 2).
python_function('src/giton/history.py', 'has_staged_changes', 1, 1, 1).
python_function('src/giton/history.py', 'autosquash', 2, 2, 6).
python_function('src/giton/hooks.py', 'hooks_dir', 1, 1, 0).
python_function('src/giton/hooks.py', 'install', 1, 5, 10).
python_function('src/giton/hooks.py', 'uninstall', 1, 5, 7).
python_function('src/giton/interactive.py', 'is_tty', 0, 3, 2).
python_function('src/giton/interactive.py', 'confirm', 1, 5, 5).
python_function('src/giton/interactive.py', 'choose', 2, 8, 7).
python_function('src/giton/plugins.py', '_pip_install', 1, 1, 3).
python_function('src/giton/plugins.py', '_init_plugin', 1, 3, 3).
python_function('src/giton/plugins.py', 'install_from_catalog', 1, 10, 9).
python_function('src/giton/plugins.py', 'install_defaults', 0, 2, 2).
python_function('src/giton/plugins.py', 'install_category', 1, 6, 3).
python_function('src/giton/plugins.py', 'uninstall', 1, 2, 2).
python_function('src/giton/plugins.py', 'show_table', 0, 5, 8).
python_function('src/giton/plugins.py', 'show_catalog', 0, 4, 8).
python_function('src/giton/policies.py', '_check_conventional_commits', 3, 10, 10).
python_function('src/giton/policies.py', '_check_no_wip', 3, 7, 5).
python_function('src/giton/policies.py', '_check_no_secrets', 3, 10, 8).
python_function('src/giton/policies.py', '_check_max_file_size', 3, 6, 5).
python_function('src/giton/policies.py', 'evaluate', 3, 4, 7).
python_function('src/giton/policies.py', 'has_errors', 1, 2, 1).
python_function('src/giton/repo_config.py', '_deep_merge', 2, 4, 5).
python_function('src/giton/repo_config.py', 'load', 1, 4, 5).
python_function('src/giton/repo_config.py', 'write_default', 1, 3, 4).
python_function('src/giton/runner.py', '_print_findings', 1, 4, 2).
python_function('src/giton/runner.py', '_format_command', 2, 1, 4).
python_function('src/giton/runner.py', 'run_trigger', 2, 8, 10).
python_function('src/giton/runner.py', '_run_plugin', 2, 6, 6).
python_function('src/giton/shell.py', '_set_enabled', 2, 5, 3).
python_function('src/giton/shell.py', '_cmd_status', 0, 4, 5).
python_function('src/giton/shell.py', '_cmd_policy', 1, 17, 10).
python_function('src/giton/shell.py', '_cmd_init', 0, 3, 4).
python_function('src/giton/shell.py', 'dispatch', 1, 23, 16).
python_function('src/giton/shell.py', 'run', 0, 5, 4).
python_function('src/giton/store.py', 'save_findings', 2, 2, 3).
python_function('src/giton/store.py', 'load_findings', 1, 3, 4).
python_function('tests/test_basic.py', 'isolated_xdg', 2, 1, 4).
python_function('tests/test_basic.py', 'test_catalog_has_three_defaults', 0, 4, 1).
python_function('tests/test_basic.py', 'test_catalog_categories_grouped', 0, 3, 3).
python_function('tests/test_basic.py', 'test_plugin_persistence', 2, 2, 7).
python_function('tests/test_basic.py', 'test_cli_help_runs', 0, 3, 2).
python_function('tests/test_basic.py', 'test_cli_plugin_catalog_runs', 0, 5, 2).
python_function('tests/test_basic.py', 'test_hook_install_in_temp_repo', 2, 6, 5).
python_function('tests/test_fixups.py', '_ctx', 1, 1, 1).
python_function('tests/test_fixups.py', 'test_conventional_commits_includes_fix', 0, 6, 5).
python_function('tests/test_fixups.py', 'test_no_wip_commits_includes_fix', 0, 6, 5).
python_function('tests/test_fixups.py', 'test_store_roundtrip', 1, 4, 4).
python_function('tests/test_fixups.py', 'test_apply_fix_runs_command', 1, 3, 3).
python_function('tests/test_fixups.py', 'test_apply_all_counts', 1, 3, 2).
python_function('tests/test_fixups.py', 'test_apply_fix_in_real_repo', 1, 7, 9).
python_function('tests/test_history.py', '_git', 2, 1, 1).
python_function('tests/test_history.py', 'repo', 1, 1, 3).
python_function('tests/test_history.py', 'test_install_hooks_includes_commit_msg', 1, 4, 2).
python_function('tests/test_history.py', 'test_make_backup_ref', 1, 3, 5).
python_function('tests/test_history.py', 'test_create_fixup_and_autosquash', 1, 7, 11).
python_function('tests/test_history.py', 'test_cli_fixup_requires_staged', 2, 3, 4).
python_function('tests/test_history.py', 'test_cli_fixup_creates_commit', 2, 3, 8).
python_function('tests/test_history.py', 'test_commit_msg_hook_blocks_wip', 3, 3, 5).
python_function('tests/test_history.py', 'test_commit_msg_hook_accepts_conventional', 3, 2, 5).
python_function('tests/test_history.py', 'test_history_log_command', 2, 3, 5).
python_function('tests/test_plugin_runner.py', '_git', 2, 1, 1).
python_function('tests/test_plugin_runner.py', 'repo', 2, 1, 6).
python_function('tests/test_plugin_runner.py', '_write_fake_plugin', 2, 1, 3).
python_function('tests/test_plugin_runner.py', '_register', 3, 3, 4).
python_function('tests/test_plugin_runner.py', 'test_plugin_executes_and_expands_paths', 3, 5, 9).
python_function('tests/test_plugin_runner.py', 'test_plugin_diff_file_placeholder', 3, 4, 8).
python_function('tests/test_plugin_runner.py', 'test_plugin_root_placeholder', 3, 3, 9).
python_function('tests/test_plugin_runner.py', 'test_plugin_failure_propagates_to_outcome', 3, 4, 6).
python_function('tests/test_plugin_runner.py', 'test_plugin_disabled_is_skipped', 3, 2, 6).
python_function('tests/test_plugin_runner.py', 'test_plugin_command_not_found', 1, 3, 4).
python_function('tests/test_plugin_runner.py', 'test_multiple_plugins_run_in_order', 3, 4, 7).
python_function('tests/test_plugin_runner.py', 'test_default_catalog_commands_are_well_formed', 0, 4, 3).
python_function('tests/test_policies.py', '_ctx', 1, 1, 1).
python_function('tests/test_policies.py', 'test_conventional_commits_accepts_valid', 0, 2, 4).
python_function('tests/test_policies.py', 'test_conventional_commits_rejects_invalid', 0, 2, 5).
python_function('tests/test_policies.py', 'test_no_wip_commits_blocks_wip', 0, 2, 5).
python_function('tests/test_policies.py', 'test_no_secrets_detects_aws_key', 0, 2, 5).
python_function('tests/test_policies.py', 'test_no_secrets_skips_non_added_lines', 0, 2, 5).
python_function('tests/test_policies.py', 'test_max_file_size_flags_big_file', 1, 2, 5).
python_function('tests/test_policies.py', 'test_repo_config_write_and_load', 1, 4, 5).
python_function('tests/test_policies.py', 'test_repo_config_user_override', 1, 3, 5).
python_function('tests/test_policies.py', 'test_runner_returns_outcome_with_findings', 2, 2, 7).

% ── Python Classes ───────────────────────────────────────
python_class('src/giton/catalog.py', 'CatalogEntry').
python_class('src/giton/config.py', 'PluginRecord').
python_method('PluginRecord', 'to_dict', 0, 1, 1).
python_method('PluginRecord', 'from_dict', 2, 3, 2).
python_class('src/giton/context.py', 'GitContext').
python_method('GitContext', 'diff_file', 0, 1, 2).
python_method('GitContext', 'paths_arg', 0, 2, 1).
python_class('src/giton/history.py', 'GitResult').
python_method('GitResult', 'ok', 0, 1, 0).
python_class('src/giton/policies.py', 'Finding').
python_method('Finding', 'is_error', 0, 1, 0).
python_class('src/giton/repo_config.py', 'RepoConfig').
python_method('RepoConfig', 'policy', 1, 2, 1).
python_method('RepoConfig', 'hook', 1, 2, 1).
python_method('RepoConfig', 'fail_on_policy', 1, 1, 3).
python_class('src/giton/runner.py', 'PluginResult').
python_method('PluginResult', 'ok', 0, 4, 0).
python_class('src/giton/runner.py', 'TriggerOutcome').
python_method('TriggerOutcome', 'ok', 0, 4, 2).

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────
env_variable('OPENROUTER_API_KEY', '*(not set)*', 'Required: OpenRouter API key (https://openrouter.ai/keys)').
env_variable('LLM_MODEL', 'openrouter/qwen/qwen3-coder-next', 'Model (default: openrouter/qwen/qwen3-coder-next)').
env_variable('PFIX_AUTO_APPLY', 'true', 'true = apply fixes without asking').
env_variable('PFIX_AUTO_INSTALL_DEPS', 'true', 'true = auto pip/uv install').
env_variable('PFIX_AUTO_RESTART', 'false', 'true = os.execv restart after fix').
env_variable('PFIX_MAX_RETRIES', '3', '').
env_variable('PFIX_DRY_RUN', 'false', '').
env_variable('PFIX_ENABLED', 'true', '').
env_variable('PFIX_GIT_COMMIT', 'false', 'true = auto-commit fixes').
env_variable('PFIX_GIT_PREFIX', 'pfix:', 'commit message prefix').
env_variable('PFIX_CREATE_BACKUPS', 'false', 'false = disable .pfix_backups/ directory').

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('generated-cli-tests.testql.toon.yaml', 'cli').
testql_scenario('generated-from-pytests.testql.toon.yaml', 'integration').

% ── Semantic Facts from SUMD.md ──────────────────────────
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/generated-cli-tests.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-from-pytests.testql.toon.yaml', 'testql').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('cli', 'argparse').
sumd_interface('cli', '').
```

## Call Graph

*65 nodes · 66 edges · 13 modules · CC̄=3.9*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `history_clean` *(in src.giton.cli)* | 12 ⚠ | 0 | 30 | **30** |
| `fixup` *(in src.giton.cli)* | 9 | 0 | 28 | **28** |
| `dispatch` *(in src.giton.shell)* | 23 ⚠ | 1 | 25 | **26** |
| `hook_commit_msg` *(in src.giton.cli)* | 9 | 0 | 25 | **25** |
| `test_basic_giton_usage` *(in examples.basic.main)* | 8 | 1 | 20 | **21** |
| `_cmd_policy` *(in src.giton.shell)* | 17 ⚠ | 1 | 20 | **21** |
| `collect` *(in src.giton.context)* | 5 | 7 | 13 | **20** |
| `demonstrate_plugin_management` *(in examples.advanced.main)* | 3 | 1 | 19 | **20** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/gix
# generated in 0.03s
# nodes: 65 | edges: 66 | modules: 13
# CC̄=3.9

HUBS[20]:
  src.giton.cli.history_clean
    CC=12  in:0  out:30  total:30
  src.giton.cli.fixup
    CC=9  in:0  out:28  total:28
  src.giton.shell.dispatch
    CC=23  in:1  out:25  total:26
  src.giton.cli.hook_commit_msg
    CC=9  in:0  out:25  total:25
  examples.basic.main.test_basic_giton_usage
    CC=8  in:1  out:20  total:21
  src.giton.shell._cmd_policy
    CC=17  in:1  out:20  total:21
  src.giton.context.collect
    CC=5  in:7  out:13  total:20
  examples.advanced.main.demonstrate_plugin_management
    CC=3  in:1  out:19  total:20
  src.giton.runner.run_trigger
    CC=8  in:6  out:12  total:18
  src.giton.context.repo_root
    CC=2  in:13  out:3  total:16
  src.giton.runner._run_plugin
    CC=6  in:1  out:15  total:16
  src.giton.plugins.install_from_catalog
    CC=10  in:2  out:13  total:15
  examples.advanced.main.demonstrate_catalog
    CC=2  in:1  out:13  total:14
  src.giton.cli.policy_check
    CC=7  in:0  out:14  total:14
  src.giton.plugins.show_table
    CC=5  in:0  out:13  total:13
  examples.advanced.main.demonstrate_trigger_sequence
    CC=9  in:1  out:12  total:13
  src.giton.cli.history_log
    CC=9  in:0  out:12  total:12
  src.giton.cli.init
    CC=4  in:0  out:12  total:12
  src.giton.hooks.install
    CC=5  in:0  out:12  total:12
  src.giton.config.load_plugins
    CC=4  in:6  out:6  total:12

MODULES:
  examples.advanced.main  [5 funcs]
    demonstrate_catalog  CC=2  out:13
    demonstrate_hooks  CC=4  out:9
    demonstrate_plugin_management  CC=3  out:19
    demonstrate_trigger_sequence  CC=9  out:12
    main  CC=2  out:9
  examples.basic.main  [2 funcs]
    main  CC=1  out:1
    test_basic_giton_usage  CC=8  out:20
  src.giton.cli  [15 funcs]
    doctor  CC=3  out:6
    fixup  CC=9  out:28
    history_clean  CC=12  out:30
    history_log  CC=9  out:12
    hook_commit_msg  CC=9  out:25
    hook_post_commit  CC=1  out:2
    hook_pre_commit  CC=2  out:3
    hook_pre_push  CC=2  out:3
    init  CC=4  out:12
    policy_check  CC=7  out:14
  src.giton.config  [5 funcs]
    ensure_user_dirs  CC=1  out:1
    load_plugins  CC=4  out:6
    remove_plugin  CC=4  out:4
    save_plugins  CC=2  out:4
    upsert_plugin  CC=3  out:3
  src.giton.context  [3 funcs]
    _run  CC=1  out:1
    collect  CC=5  out:13
    repo_root  CC=2  out:3
  src.giton.fixups  [2 funcs]
    apply_all  CC=6  out:3
    apply_fix  CC=6  out:5
  src.giton.history  [8 funcs]
    _git  CC=1  out:2
    autosquash  CC=2  out:7
    create_fixup  CC=2  out:2
    has_staged_changes  CC=1  out:1
    head_sha  CC=1  out:2
    list_log  CC=4  out:7
    make_backup_ref  CC=2  out:4
    upstream_range  CC=2  out:2
  src.giton.hooks  [3 funcs]
    hooks_dir  CC=1  out:0
    install  CC=5  out:12
    uninstall  CC=5  out:8
  src.giton.interactive  [3 funcs]
    choose  CC=8  out:10
    confirm  CC=5  out:5
    is_tty  CC=3  out:3
  src.giton.plugins  [7 funcs]
    _init_plugin  CC=3  out:5
    _pip_install  CC=1  out:3
    install_category  CC=6  out:3
    install_defaults  CC=2  out:2
    install_from_catalog  CC=10  out:13
    show_table  CC=5  out:13
    uninstall  CC=2  out:3
  src.giton.repo_config  [2 funcs]
    _deep_merge  CC=4  out:6
    load  CC=4  out:6
  src.giton.runner  [4 funcs]
    _format_command  CC=1  out:5
    _print_findings  CC=4  out:3
    _run_plugin  CC=6  out:15
    run_trigger  CC=8  out:12
  src.giton.shell  [6 funcs]
    _cmd_init  CC=3  out:6
    _cmd_policy  CC=17  out:20
    _cmd_status  CC=4  out:6
    _set_enabled  CC=5  out:4
    dispatch  CC=23  out:25
    run  CC=5  out:7

EDGES:
  examples.advanced.main.demonstrate_plugin_management → src.giton.config.load_plugins
  examples.advanced.main.demonstrate_hooks → src.giton.context.repo_root
  examples.advanced.main.demonstrate_trigger_sequence → src.giton.context.repo_root
  examples.advanced.main.demonstrate_trigger_sequence → src.giton.runner.run_trigger
  examples.advanced.main.main → examples.advanced.main.demonstrate_catalog
  examples.advanced.main.main → examples.advanced.main.demonstrate_plugin_management
  examples.advanced.main.main → examples.advanced.main.demonstrate_hooks
  examples.advanced.main.main → examples.advanced.main.demonstrate_trigger_sequence
  examples.basic.main.test_basic_giton_usage → src.giton.context.collect
  examples.basic.main.test_basic_giton_usage → src.giton.runner.run_trigger
  examples.basic.main.main → examples.basic.main.test_basic_giton_usage
  src.giton.config.load_plugins → src.giton.config.ensure_user_dirs
  src.giton.config.save_plugins → src.giton.config.ensure_user_dirs
  src.giton.config.upsert_plugin → src.giton.config.load_plugins
  src.giton.config.upsert_plugin → src.giton.config.save_plugins
  src.giton.config.remove_plugin → src.giton.config.load_plugins
  src.giton.config.remove_plugin → src.giton.config.save_plugins
  src.giton.interactive.confirm → src.giton.interactive.is_tty
  src.giton.interactive.choose → src.giton.interactive.is_tty
  src.giton.context.repo_root → src.giton.context._run
  src.giton.context.collect → src.giton.context.repo_root
  src.giton.context.collect → src.giton.context._run
  src.giton.hooks.install → src.giton.hooks.hooks_dir
  src.giton.hooks.uninstall → src.giton.hooks.hooks_dir
  src.giton.history.head_sha → src.giton.history._git
  src.giton.history.make_backup_ref → src.giton.history.head_sha
  src.giton.history.make_backup_ref → src.giton.history._git
  src.giton.history.list_log → src.giton.history._git
  src.giton.history.upstream_range → src.giton.history._git
  src.giton.history.create_fixup → src.giton.history._git
  src.giton.history.has_staged_changes → src.giton.history._git
  src.giton.history.autosquash → src.giton.history._git
  src.giton.repo_config.load → src.giton.repo_config._deep_merge
  src.giton.cli.init → src.giton.context.repo_root
  src.giton.cli.uninit → src.giton.context.repo_root
  src.giton.cli.status → src.giton.context.collect
  src.giton.cli.doctor → src.giton.context.repo_root
  src.giton.cli.hook_pre_commit → src.giton.runner.run_trigger
  src.giton.cli.hook_commit_msg → src.giton.context.collect
  src.giton.cli.hook_post_commit → src.giton.runner.run_trigger
  src.giton.cli.hook_pre_push → src.giton.runner.run_trigger
  src.giton.cli.policy_check → src.giton.context.collect
  src.giton.cli.policy_init → src.giton.context.repo_root
  src.giton.cli.policy_list → src.giton.context.repo_root
  src.giton.cli.policy_fix → src.giton.context.repo_root
  src.giton.cli.fixup → src.giton.context.repo_root
  src.giton.cli.history_log → src.giton.context.repo_root
  src.giton.cli.history_clean → src.giton.context.repo_root
  src.giton.plugins.install_from_catalog → src.giton.plugins._pip_install
  src.giton.plugins.install_from_catalog → src.giton.config.upsert_plugin
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**

## Intent

Local AI layer for git: orchestrates policies & plugins between commit and push.
