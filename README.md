# giton


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.2-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.41-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-3.0h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.4093 (6 commits)
- 👤 **Human dev:** ~$300 (3.0h @ $100/h, 30min dedup)

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

## Proposed direction for `gix`

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

## Quick start

```bash
giton init                # install git hooks + 3 default plugins
giton shell               # interactive REPL
giton plugin catalog      # browse all available plugins
giton plugin install domd # install a specific extension
giton plugin install-category lang:python   # install everything for a language
```

### Default plugins

The 3 plugins activated by `gix init` cover the most common
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

### Plugin contract

A plugin is any executable command (CLI). The catalog entry declares its
trigger, category, install target (PyPI/local path) and command template.
The runner expands `{paths}`, `{diff_file}` and `{root}` placeholders
with the current git context before invocation.

Future exec types (`mcp`, `rest`) will share the same JSON in/out
contract: input = git context + policy findings, output = list of
proposed actions (patches, fixup commits, warnings).


## License

Licensed under Apache-2.0.
