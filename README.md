# gix

`gix` is a local AI layer for Git that works between `commit` and `push`.
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

```bash
# 1) initialize hooks in the repository
gix init

# 2) user makes a normal commit
git add -p
git commit -m "update stuff"

# 3) gix detects issues and proposes a fixup commit
gix hook post-commit

# 4) before push, gix suggests history cleanup
gix hook pre-push
```

Example interaction:

```text
gix: Found 2 issues (null-check, commit message policy).
gix: Apply patch and add commit "fixup! ..."? [Y/n]
```

## MVP plan

- MVP 1: hooks + policy engine + interactive CLI
- MVP 2: patching + fixup workflow + pre-push autosquash
- MVP 3: stable plugin API and MCP/REST/CLI/gRPC integrations
