# giton


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.8-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.96-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-3.4h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.9599 (11 commits)
- 👤 **Human dev:** ~$339 (3.4h @ $100/h, 30min dedup)

Generated on 2026-05-27 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

`giton` is a local AI layer for Git that works between `commit` and `push`.
It helps standardize commits, propose safe code fixes, and orchestrate external tools via plugins.

## Does something like this already exist?

Partially: there are tools for AI commit messages, git hooks, and commit-history rewriting.
What is still missing is one local operator that:

- interacts with the user right after commit,
- proposes code fixes as additional commits (`fixup!`),
- cleans up history before `push`,
- integrates plugins via MCP/REST/CLI/gRPC.

## Proposed direction for `giton`

1. **Local-first with safe defaults**
   - AI proposes changes, user approves them.
   - Prefer `fixup!` commits over automatic history rewriting.

2. **Git hook layer**
   - `pre-commit`: policy validation and quick fixes.
   - `post-commit`: inspect the fresh commit and propose follow-up patches.
   - `pre-push`: standardize history (`autosquash`, commit naming, final checks).

3. **Plugin architecture**
   - Shared input/output contract (JSON schema).
   - Plugin adapters: MCP, REST, CLI shell, gRPC/protobuf.

## MVP usage example

After `giton init`, hooks are installed and run automatically from Git lifecycle events.
The commands below show equivalent manual execution for demonstration/debugging.

```bash
# 1) initialize hooks in the repository
giton init

# 2) user makes a normal commit
git add -p
git commit -m "update stuff"

# 3) equivalent manual run: post-commit hook logic
giton hook post-commit

# 4) equivalent manual run: pre-push hook logic
giton hook pre-push
```

Example interaction:

```text
giton: Found 2 issues (example: null check, commit message policy).
giton: Apply patch and add commit "fixup! ..."? [Y/n]
```

## MVP plan

- MVP 1: hooks + policy engine + interactive CLI
- MVP 2: patching + fixup workflow + pre-push autosquash
- MVP 3: stable plugin API and MCP/REST/CLI/gRPC integrations

## Install

```bash
pip install giton
```

## Development

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd gix

# Install in development mode
pip install -e .[dev]
```

### Dependencies

**Runtime:**
- `typer>=0.12`
- `rich>=13.7`
- `PyYAML>=6.0`

**Development:**
- `pytest>=8.0`
- `goal>=2.1.0`
- `costs>=0.1.20`
- `pfix>=0.1.60`

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_history.py

# Run with coverage
pytest --cov=src/giton
```

### Environment Variables

Create a `.env` file in the project root (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | *(not set)* | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model to use for AI operations |
| `PFIX_AUTO_APPLY` | `true` | Automatically apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | Automatically pip/uv install dependencies |
| `PFIX_AUTO_RESTART` | `false` | Restart process after fix using os.execv |
| `PFIX_MAX_RETRIES` | `3` | Maximum retry attempts |
| `PFIX_DRY_RUN` | `false` | Run in dry-run mode without making changes |
| `PFIX_ENABLED` | `true` | Enable automatic fixing |
| `PFIX_GIT_COMMIT` | `false` | Automatically commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | Commit message prefix for fixes |
| `PFIX_CREATE_BACKUPS` | `false` | Create backups in `.pfix_backups/` directory |

### Project Structure

```
gix/
├── src/giton/           # Main source code
│   ├── __init__.py      # Package initialization
│   ├── __main__.py      # Entry point for `python -m giton`
│   ├── catalog.py       # Plugin catalog management
│   ├── cli.py           # Command-line interface (Typer)
│   ├── config.py        # User plugin configuration
│   ├── context.py       # Git context collection
│   ├── history.py       # Safe history operations (fixup, autosquash)
│   ├── hooks.py         # Git hook installation
│   ├── interactive.py   # Interactive prompts
│   ├── plugins.py       # Plugin installation/management
│   ├── policies.py      # Built-in policy engine
│   ├── repo_config.py   # Repository configuration
│   ├── runner.py        # Plugin execution runner
│   └── shell.py         # Interactive REPL shell
├── tests/               # Test suite
│   ├── test_basic.py    # Basic functionality tests
│   ├── test_history.py  # History operations tests
│   └── test_policies.py # Policy engine tests
├── examples/            # Usage examples
│   ├── basic/           # Basic library usage
│   ├── advanced/        # Advanced features demo
│   └── testing/         # CI/CD integration example
├── pyproject.toml       # Project configuration
├── README.md            # This file
├── SUMD.md              # System documentation (SUMD)
├── TODO.md              # Auto-generated TODO list
└── CHANGELOG.md         # Version history
```

## Quick start

```bash
giton init                # install git hooks + 3 default plugins
giton shell               # interactive REPL
giton plugin catalog      # browse all available plugins
giton plugin install domd # install a specific extension
giton plugin install-category lang:python   # install everything for a language
```

### Default plugins

The 3 plugins activated by `giton init` cover the most common
day-to-day needs in a `commit → push` loop:

| name      | category        | trigger      | role                                       |
| --------- | --------------- | ------------ | ------------------------------------------ |
| `pyqual`  | `lang:python`   | `pre-commit` | Python lint / type / complexity checks      |
| `vallm`   | `task:validate` | `post-commit`| Validate AI-generated code/patches          |
| `pretest` | `task:test`     | `pre-push`   | Run / generate tests before push            |

### Quick-extend categories

Each plugin in the catalog is tagged with a category, so you can install
groups at once:

- **languages:** `lang:python`, `lang:markdown`, `lang:any`
- **tasks:** `task:validate`, `task:test`, `task:refactor`,
  `task:autofix`, `task:fix`, `task:docs`, `task:security`
- **integrations:** `integration:mcp`

```bash
giton plugin install-category task:autofix
```

### Interactive shell

```text
$ giton shell
giton> help
giton> install-defaults
giton> hook pre-commit
giton> catalog
giton> install prefact
```

### Built-in policies

`giton` ships with a small zero-dependency policy engine that runs on
every hook trigger — even before any plugin is installed:

- **`conventional_commits`** — subject must match
  `type(scope)?: subject` and stay within `max_subject_length`.
- **`no_wip_commits`** — blocks subjects matching `wip`, `tmp`, `xxx`, `fixme`.
- **`no_secrets`** — scans staged additions for AWS keys, private-key
  headers and `api_key=`/`secret=` patterns.
- **`max_file_size`** — rejects staged files larger than `kb` (default 512 KB).

Inspect or customize them per repo:

```bash
giton policy list                    # show active policies
giton policy check -t pre-commit     # evaluate without running plugins
giton policy init                    # write .giton/config.yaml
```

`.giton/config.yaml` is a deep-merge over the defaults — disable a
single check or tweak `max_subject_length` without restating everything:

```yaml
policies:
  no_wip_commits:
    enabled: false
  conventional_commits:
    max_subject_length: 100
hooks:
  post-commit:
    fail_on_policy: true   # turn advisory checks into blocking
```

### Plugin contract

A plugin is any executable command (CLI). The catalog entry declares its
trigger, category, install target (PyPI/local path) and command template.
The runner expands `{paths}`, `{diff_file}` and `{root}` placeholders
with the current git context before invocation.

Future exec types (`mcp`, `rest`) will share the same JSON in/out
contract: input = git context + policy findings, output = list of
proposed actions (patches, fixup commits, warnings).

## Examples

The `examples/` directory contains working demonstrations of giton:

- **[examples/basic](examples/basic/)** - Basic usage example showing how to use giton as a Python library to collect git context, run triggers, and handle policy findings and plugin results. Can be run directly or with pytest.

- **[examples/advanced](examples/advanced/)** - Advanced usage example demonstrating plugin management (add, remove, list), custom policy configuration, hook installation/uninstallation, and running multiple triggers in sequence.

- **[examples/testing](examples/testing/)** - Testing example with pytest integration and Docker support. Shows how to integrate giton into CI/CD pipelines with containerized testing environments. Includes Dockerfile and docker-compose.yml for easy setup.

### Running examples with Docker

All examples include Dockerfiles for containerized execution:

```bash
# Basic example
docker build -f examples/basic/Dockerfile -t giton-example-basic .
docker run --rm -v $(pwd)/examples/basic/logs:/app/logs giton-example-basic

# Advanced example
docker build -f examples/advanced/Dockerfile -t giton-example-advanced .
docker run --rm -v $(pwd)/examples/advanced/logs:/app/logs giton-example-advanced

# Testing example
docker build -f examples/testing/Dockerfile -t giton-test .
docker run --rm -v $(pwd)/examples/testing/logs:/app/logs giton-test
```

See each example's README.md for detailed usage instructions.


## License

Licensed under Apache-2.0.
