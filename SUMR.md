# giton

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Dependencies](#dependencies)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `giton`
- **version**: `0.1.9`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, pyqual.yaml, goal.yaml, .env.example, project/(6 analysis files)

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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

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

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 37f 3815L | python:19,yaml:7,txt:3,shell:2,toml:2,yml:1 | 2026-05-27
# generated in 0.01s
# CC̅=3.9 | critical:2/98 | dups:0 | cycles:1

HEALTH[2]:
  🟡 CC    _cmd_policy CC=17 (limit:15)
  🟡 CC    dispatch CC=23 (limit:15)

REFACTOR[2]:
  1. split 2 high-CC methods  (CC>15)
  2. break 1 circular dependencies

PIPELINES[64]:
  [1] Src [main]: main → demonstrate_catalog
      PURITY: 100% pure
  [2] Src [main]: main → test_basic_giton_usage → collect → repo_root → ...(1 more)
      PURITY: 100% pure
  [3] Src [divide]: divide
      PURITY: 100% pure
  [4] Src [_xdg_config_home]: _xdg_config_home
      PURITY: 100% pure
  [5] Src [to_dict]: to_dict
      PURITY: 100% pure
  [6] Src [from_dict]: from_dict
      PURITY: 100% pure
  [7] Src [confirm]: confirm → is_tty
      PURITY: 100% pure
  [8] Src [choose]: choose → is_tty
      PURITY: 100% pure
  [9] Src [diff_file]: diff_file
      PURITY: 100% pure
  [10] Src [paths_arg]: paths_arg
      PURITY: 100% pure
  [11] Src [install]: install → hooks_dir
      PURITY: 100% pure
  [12] Src [uninstall]: uninstall → hooks_dir
      PURITY: 100% pure
  [13] Src [make_backup_ref]: make_backup_ref → head_sha → _git
      PURITY: 100% pure
  [14] Src [list_log]: list_log → _git
      PURITY: 100% pure
  [15] Src [upstream_range]: upstream_range → _git
      PURITY: 100% pure
  [16] Src [create_fixup]: create_fixup → _git
      PURITY: 100% pure
  [17] Src [has_staged_changes]: has_staged_changes → _git
      PURITY: 100% pure
  [18] Src [autosquash]: autosquash → _git
      PURITY: 100% pure
  [19] Src [policy]: policy
      PURITY: 100% pure
  [20] Src [hook]: hook
      PURITY: 100% pure
  [21] Src [fail_on_policy]: fail_on_policy
      PURITY: 100% pure
  [22] Src [load]: load → _deep_merge
      PURITY: 100% pure
  [23] Src [write_default]: write_default
      PURITY: 100% pure
  [24] Src [save_findings]: save_findings
      PURITY: 100% pure
  [25] Src [load_findings]: load_findings
      PURITY: 100% pure
  [26] Src [_root]: _root
      PURITY: 100% pure
  [27] Src [init]: init → repo_root → _run
      PURITY: 100% pure
  [28] Src [uninit]: uninit → repo_root → _run
      PURITY: 100% pure
  [29] Src [status]: status → collect → repo_root → _run
      PURITY: 100% pure
  [30] Src [shell]: shell
      PURITY: 100% pure
  [31] Src [doctor]: doctor → repo_root → _run
      PURITY: 100% pure
  [32] Src [plugin_list]: plugin_list
      PURITY: 100% pure
  [33] Src [plugin_catalog]: plugin_catalog
      PURITY: 100% pure
  [34] Src [plugin_install]: plugin_install
      PURITY: 100% pure
  [35] Src [plugin_install_defaults]: plugin_install_defaults
      PURITY: 100% pure
  [36] Src [plugin_install_category]: plugin_install_category
      PURITY: 100% pure
  [37] Src [plugin_remove]: plugin_remove
      PURITY: 100% pure
  [38] Src [hook_pre_commit]: hook_pre_commit → run_trigger → collect → repo_root → ...(1 more)
      PURITY: 100% pure
  [39] Src [hook_commit_msg]: hook_commit_msg → collect → repo_root → _run
      PURITY: 100% pure
  [40] Src [hook_post_commit]: hook_post_commit → run_trigger → collect → repo_root → ...(1 more)
      PURITY: 100% pure
  [41] Src [hook_pre_push]: hook_pre_push → run_trigger → collect → repo_root → ...(1 more)
      PURITY: 100% pure
  [42] Src [policy_check]: policy_check → collect → repo_root → _run
      PURITY: 100% pure
  [43] Src [policy_init]: policy_init → repo_root → _run
      PURITY: 100% pure
  [44] Src [policy_list]: policy_list → repo_root → _run
      PURITY: 100% pure
  [45] Src [policy_fix]: policy_fix → repo_root → _run
      PURITY: 100% pure
  [46] Src [fixup]: fixup → repo_root → _run
      PURITY: 100% pure
  [47] Src [history_log]: history_log → repo_root → _run
      PURITY: 100% pure
  [48] Src [history_clean]: history_clean → repo_root → _run
      PURITY: 100% pure
  [49] Src [install_defaults]: install_defaults → install_from_catalog → _pip_install
      PURITY: 100% pure
  [50] Src [install_category]: install_category → install_from_catalog → _pip_install
      PURITY: 100% pure

LAYERS:
  src/                            CC̄=4.0    ←in:0  →out:0
  │ cli                        447L  0C   23m  CC=12     ←0
  │ !! shell                      216L  0C    6m  CC=23     ←0
  │ catalog                    173L  1C    4m  CC=3      ←0
  │ policies                   171L  1C    6m  CC=10     ←0
  │ plugins                    143L  0C    8m  CC=10     ←0
  │ history                    140L  1C    8m  CC=4      ←0
  │ runner                     123L  2C    4m  CC=8      ←4
  │ repo_config                101L  1C    6m  CC=4      ←0
  │ config                      74L  1C    8m  CC=4      ←4
  │ fixups                      68L  0C    2m  CC=6      ←0
  │ context                     66L  1C    5m  CC=5      ←5
  │ interactive                 58L  0C    3m  CC=8      ←0
  │ hooks                       48L  0C    3m  CC=5      ←0
  │ store                       36L  0C    2m  CC=3      ←0
  │ __main__                     4L  0C    0m  CC=0.0    ←0
  │ __init__                     3L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=3.3    ←in:0  →out:0
  │ main                       156L  0C    5m  CC=9      ←0
  │ main                        67L  0C    2m  CC=8      ←0
  │ log.txt                     64L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  37L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  33L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  33L  0C    0m  CC=0.0    ←0
  │ example                     20L  0C    3m  CC=2      ←0
  │ log.txt                     17L  0C    0m  CC=0.0    ←0
  │ log.txt                     13L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              12L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml          11L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! planfile.yaml              526L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ koru.yaml                  133L  0C    0m  CC=0.0    ←0
  │ prefact.yaml                94L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              62L  0C    0m  CC=0.0    ←0
  │ pyqual.yaml                 61L  0C    0m  CC=0.0    ←0
  │ project.sh                  59L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │ generated-from-pytests.testql.toon.yaml    13L  0C    0m  CC=0.0    ←0
  │

COUPLING:
                             src.giton  examples.advanced     examples.basic
          src.giton                 ──                 ←6                 ←2  hub
  examples.advanced                  6                 ──                   
     examples.basic                  2                                    ──
  CYCLES: 1
  HUB: src.giton/ (fan-in=8)

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 3 groups | 18f 2094L | 2026-05-27

SUMMARY:
  files_scanned: 18
  total_lines:   2094
  dup_groups:    3
  dup_fragments: 8
  saved_lines:   17
  scan_ms:       2207

HOTSPOTS[1] (files with most duplication):
  src/giton/cli.py  dup=28L  groups=3  frags=8  (1.3%)

DUPLICATES[3] (ranked by impact):
  [c83a3afee3e88a5c]   STRU  shell  L=3 N=4 saved=9 sim=1.00
      src/giton/cli.py:105-107  (shell)
      src/giton/cli.py:124-126  (plugin_list)
      src/giton/cli.py:130-132  (plugin_catalog)
      src/giton/cli.py:142-144  (plugin_install_defaults)
  [53a68daa2f26aa3a]   STRU  hook_pre_commit  L=5 N=2 saved=5 sim=1.00
      src/giton/cli.py:163-167  (hook_pre_commit)
      src/giton/cli.py:222-226  (hook_pre_push)
  [b67a4e80d3d0d106]   STRU  plugin_install  L=3 N=2 saved=3 sim=1.00
      src/giton/cli.py:136-138  (plugin_install)
      src/giton/cli.py:155-157  (plugin_remove)

REFACTOR[3] (ranked by priority):
  [1] ○ extract_function   → src/giton/utils/shell.py
      WHY: 4 occurrences of 3-line block across 1 files — saves 9 lines
      FILES: src/giton/cli.py
  [2] ○ extract_function   → src/giton/utils/hook_pre_commit.py
      WHY: 2 occurrences of 5-line block across 1 files — saves 5 lines
      FILES: src/giton/cli.py
  [3] ○ extract_function   → src/giton/utils/plugin_install.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: src/giton/cli.py

QUICK_WINS[1] (low risk, high savings — do first):
  [1] extract_function   saved=9L  → src/giton/utils/shell.py
      FILES: cli.py

EFFORT_ESTIMATE (total ≈ 0.6h):
  easy   shell                               saved=9L  ~18min
  easy   hook_pre_commit                     saved=5L  ~10min
  easy   plugin_install                      saved=3L  ~6min

METRICS-TARGET:
  dup_groups:  3 → 0
  saved_lines: 17 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 88 func | 14f | 2026-05-27
# generated in 0.00s

NEXT[4] (ranked by impact):
  [1] !  SPLIT-FUNC      dispatch  CC=23  fan=16
      WHY: CC=23 exceeds 15
      EFFORT: ~1h  IMPACT: 368

  [2] !  SPLIT-FUNC      _cmd_policy  CC=17  fan=11
      WHY: CC=17 exceeds 15
      EFFORT: ~1h  IMPACT: 187

  [3] !! SPLIT           planfile.yaml
      WHY: 526L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0

  [4] !! SPLIT           goal.yaml
      WHY: 512L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[2]:
  ⚠ Splitting planfile.yaml may break 0 import paths
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          4.0 → ≤2.8
  max-CC:      23 → ≤11
  god-modules: 2 → 0
  high-CC(≥15): 2 → ≤1
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=3.9 → now CC̄=4.0
```

### Validation (`project/validation.toon.yaml`)

```toon markpact:analysis path=project/validation.toon.yaml
# vallm batch | 75f | 0✓ 45⚠ 0✗ | 2026-05-27

SUMMARY:
  scanned: 75  passed: 0 (0.0%)  warnings: 45  errors: 0  unsupported: 0

WARNINGS[45]{path,score}:
  src/giton/shell.py,0.74
    issues[2]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
      complexity.lizard_cc,warning,dispatch: CC=23 exceeds limit 15,132
  .koru/onboarding.json,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse JSON: Download error: Language 'JSON' not available for download. Available groups: [""all""]",
  .koru/project.json,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse JSON: Download error: Language 'JSON' not available for download. Available groups: [""all""]",
  .planfile/.koru/autonomous-state.json,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse JSON: Download error: Language 'JSON' not available for download. Available groups: [""all""]",
  .planfile/.koru/autonomy-telemetry.json,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse JSON: Download error: Language 'JSON' not available for download. Available groups: [""all""]",
  .planfile/.koru/serve-endpoint.json,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse JSON: Download error: Language 'JSON' not available for download. Available groups: [""all""]",
  .planfile/config.yaml,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse YAML: Download error: Language 'YAML' not available for download. Available groups: [""all""]",
  .planfile/sprints/current.yaml,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse YAML: Download error: Language 'YAML' not available for download. Available groups: [""all""]",
  .pyqual/runtime_errors.json,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse JSON: Download error: Language 'JSON' not available for download. Available groups: [""all""]",
  examples/advanced/main.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  examples/basic/main.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  examples/plugins/test_plugin_lifecycle.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  examples/testing/sample_project/pyproject.toml,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse TOML: Download error: Language 'TOML' not available for download. Available groups: [""all""]",
  examples/testing/sample_project/src/example.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  examples/testing/sample_project/tests/test_example.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  examples/testing/test_giton_integration.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  goal.yaml,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse YAML: Download error: Language 'YAML' not available for download. Available groups: [""all""]",
  koru.yaml,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse YAML: Download error: Language 'YAML' not available for download. Available groups: [""all""]",
  planfile.yaml,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse YAML: Download error: Language 'YAML' not available for download. Available groups: [""all""]",
  prefact.yaml,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse YAML: Download error: Language 'YAML' not available for download. Available groups: [""all""]",
  project.sh,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse BASH: Download error: Language 'BASH' not available for download. Available groups: [""all""]",
  project/calls.yaml,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse YAML: Download error: Language 'YAML' not available for download. Available groups: [""all""]",
  project/logic.pl,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PERL: Download error: Language 'PERL' not available for download. Available groups: [""all""]",
  project/planfile-tickets.yaml,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse YAML: Download error: Language 'YAML' not available for download. Available groups: [""all""]",
  pyproject.toml,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse TOML: Download error: Language 'TOML' not available for download. Available groups: [""all""]",
  pyqual.yaml,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse YAML: Download error: Language 'YAML' not available for download. Available groups: [""all""]",
  src/giton/__init__.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  src/giton/__main__.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  src/giton/catalog.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  src/giton/cli.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  src/giton/config.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  src/giton/context.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  src/giton/history.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  src/giton/hooks.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  src/giton/interactive.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  src/giton/plugins.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  src/giton/policies.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  src/giton/repo_config.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  src/giton/runner.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  tests/__init__.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  tests/test_basic.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  tests/test_history.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  tests/test_plugin_runner.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  tests/test_policies.py,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse PYTHON: Download error: Language 'PYTHON' not available for download. Available groups: [""all""]",
  tree.sh,0.78
    issues[1]{rule,severity,message,line}:
      syntax.unsupported,warning,"Could not parse BASH: Download error: Language 'BASH' not available for download. Available groups: [""all""]",
```

## Intent

Local AI layer for git: orchestrates policies & plugins between commit and push.
