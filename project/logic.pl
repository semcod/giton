% ── Project Metadata ─────────────────────────────────────
project_metadata('gix', '0.1.5', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 29, 'less').
project_file('examples/advanced/main.py', 157, 'python').
project_file('examples/basic/main.py', 68, 'python').
project_file('examples/testing/sample_project/src/example.py', 21, 'python').
project_file('examples/testing/sample_project/tests/test_example.py', 31, 'python').
project_file('examples/testing/test_giton_integration.py', 179, 'python').
project_file('project.sh', 59, 'shell').
project_file('src/giton/__init__.py', 4, 'python').
project_file('src/giton/__main__.py', 5, 'python').
project_file('src/giton/catalog.py', 174, 'python').
project_file('src/giton/cli.py', 422, 'python').
project_file('src/giton/config.py', 75, 'python').
project_file('src/giton/context.py', 67, 'python').
project_file('src/giton/history.py', 141, 'python').
project_file('src/giton/hooks.py', 49, 'python').
project_file('src/giton/interactive.py', 59, 'python').
project_file('src/giton/plugins.py', 121, 'python').
project_file('src/giton/policies.py', 166, 'python').
project_file('src/giton/repo_config.py', 102, 'python').
project_file('src/giton/runner.py', 123, 'python').
project_file('src/giton/shell.py', 206, 'python').
project_file('tests/__init__.py', 1, 'python').
project_file('tests/test_basic.py', 86, 'python').
project_file('tests/test_history.py', 134, 'python').
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
python_function('src/giton/cli.py', 'hook_commit_msg', 1, 9, 17).
python_function('src/giton/cli.py', 'hook_post_commit', 0, 1, 2).
python_function('src/giton/cli.py', 'hook_pre_push', 0, 2, 3).
python_function('src/giton/cli.py', 'policy_check', 1, 7, 10).
python_function('src/giton/cli.py', 'policy_init', 1, 2, 7).
python_function('src/giton/cli.py', 'policy_list', 0, 5, 7).
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
python_function('src/giton/plugins.py', 'install_from_catalog', 1, 9, 8).
python_function('src/giton/plugins.py', 'install_defaults', 0, 2, 2).
python_function('src/giton/plugins.py', 'install_category', 1, 6, 3).
python_function('src/giton/plugins.py', 'uninstall', 1, 2, 2).
python_function('src/giton/plugins.py', 'show_table', 0, 5, 8).
python_function('src/giton/plugins.py', 'show_catalog', 0, 4, 8).
python_function('src/giton/policies.py', '_check_conventional_commits', 3, 10, 10).
python_function('src/giton/policies.py', '_check_no_wip', 3, 6, 4).
python_function('src/giton/policies.py', '_check_no_secrets', 3, 10, 8).
python_function('src/giton/policies.py', '_check_max_file_size', 3, 6, 5).
python_function('src/giton/policies.py', 'evaluate', 3, 4, 7).
python_function('src/giton/policies.py', 'has_errors', 1, 2, 1).
python_function('src/giton/repo_config.py', '_deep_merge', 2, 4, 5).
python_function('src/giton/repo_config.py', 'load', 1, 4, 5).
python_function('src/giton/repo_config.py', 'write_default', 1, 3, 4).
python_function('src/giton/runner.py', '_print_findings', 1, 4, 2).
python_function('src/giton/runner.py', '_format_command', 2, 1, 4).
python_function('src/giton/runner.py', 'run_trigger', 2, 8, 9).
python_function('src/giton/runner.py', '_run_plugin', 2, 6, 6).
python_function('src/giton/shell.py', '_set_enabled', 2, 5, 3).
python_function('src/giton/shell.py', '_cmd_status', 0, 4, 5).
python_function('src/giton/shell.py', '_cmd_policy', 1, 12, 8).
python_function('src/giton/shell.py', '_cmd_init', 0, 3, 4).
python_function('src/giton/shell.py', 'dispatch', 1, 23, 16).
python_function('src/giton/shell.py', 'run', 0, 5, 4).
python_function('tests/test_basic.py', 'isolated_xdg', 2, 1, 4).
python_function('tests/test_basic.py', 'test_catalog_has_three_defaults', 0, 4, 1).
python_function('tests/test_basic.py', 'test_catalog_categories_grouped', 0, 3, 3).
python_function('tests/test_basic.py', 'test_plugin_persistence', 2, 2, 7).
python_function('tests/test_basic.py', 'test_cli_help_runs', 0, 3, 2).
python_function('tests/test_basic.py', 'test_cli_plugin_catalog_runs', 0, 5, 2).
python_function('tests/test_basic.py', 'test_hook_install_in_temp_repo', 2, 6, 5).
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

