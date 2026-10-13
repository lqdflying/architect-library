# Agent guide: install Architect Library (Cursor / Copilot / Codex / Claude Code)

Use this document when the user asks to install, update, or fix **skills**, **custom agents**, or **user instructions** from the **architect-library** repository. Follow it literally; do not invent alternate paths.

**Cross-editor contract:** [AGENTS.md](../AGENTS.md) at the repo root — install trigger phrases, editor scope, and anti-patterns (all supported editors should follow it).

**Editing this repository?** Cursor loads [`.cursor/rules/`](../.cursor/rules/) automatically (maintainer rules). Follow [MAINTAINING-SKILLS.md](MAINTAINING-SKILLS.md) whenever you add a skill, agent, user-global Cursor rule, workflow step, or dependency.

## User phrases (full readiness default)

When the user says any of these, run a **full global readiness install** (runtimes + skills + agents + Cursor user-global rules + the Copilot always-on instruction) for **Cursor and VS Code Copilot**:

- **install library** | install the library | patch library | refresh library | update library
- install skills and agents | sync library | update architect library
- patch | upgrade | install | refresh (skills or agents)

### Editor-scoped commands (default)

Run these runtime commands first:

```bash
bash scripts/install_deps.sh
bash scripts/install_deps.sh office-system
```

Then run both library commands:

| Target | Library command | Paths |
|------------|-----------------|---------|
| **Cursor** | `bash scripts/install_library.sh all cursor` | `~/.cursor/skills/`, `~/.cursor/agents/`, `~/.cursor/rules/` |
| **VS Code Copilot** | `bash scripts/install_library.sh all copilot` | `~/.copilot/skills/`, `~/.copilot/agents/`, `~/.copilot/copilot-instructions.md` |
| **Claude Code** (only when the user asks) | `bash scripts/install_library.sh all claude` | `~/.claude/skills/`, `~/.claude/agents/`, `~/.claude/rules/` |
| **Codex** (only when the user asks) | `bash scripts/install_library.sh all codex` | `~/.agents/skills/`, `${CODEX_HOME:-$HOME/.codex}/agents/`, `${CODEX_HOME:-$HOME/.codex}/AGENTS.md` |

Do **not** ask which editor, scope, subset, or runtime set to install for these trigger phrases. Install Cursor and VS Code Copilot.

Codex and Claude are opt-in. If the user names one editor, install only that editor. An explicit all-editor request uses `bash scripts/install_library.sh all all`. The legacy `both` selector (also the bare command default) still means Cursor + Copilot + Claude, without Codex.

Use **partial** installs (`skills`, `agents`, or `rules` only) **only** when the user explicitly asks — still for both Cursor and Copilot, for example `bash scripts/install_library.sh skills cursor` and `bash scripts/install_library.sh skills copilot`.

## What you are installing

Architect Library publishes **two libraries** plus **Cursor user-global rules**:

### Skill library (`skills/`)

| Folder | Type | Required |
|--------|------|----------|
| `excalidraw-diagram` | Shared skill | If diagrams are needed |
| `word-document` | Shared skill | If DOCX is needed |
| `powerpoint-presentation` | Shared skill | If PPTX is needed |
| `spreadsheet-document` | Shared skill | If XLSX/spreadsheet work is needed |
| `pdf-document` | Shared skill | If PDF work is needed |
| `verification-before-completion` | Shared skill | Evidence before completion claims; required by artifact skills at delivery |
| `newagentlink` | Shared skill | One-shot `/tmp/<topic>-newagentlink.md` for a new agent chat; not the review ledger |
| `review-handoff` | Shared skill (on demand) | Review and fix ledger protocol at `/tmp/<topic>-handoff.md`; read when the always-on `review-handoff` trigger fires |
| `api-and-interface-design` | Shared skill | API and module boundary design workflow |
| `github-markdown` | Shared skill | GitHub Flavored Markdown for READMEs, issues, PRs, discussions, wikis, and repo docs |
| `deprecation-and-migration` | Shared skill | Deprecation and migration planning workflow |
| `terraform-commit-review` | Shared skill | Terraform IaC commit-range review (correctness, security, destructive changes) |
| `terraform-apply-assistance` | Shared skill | Fix Terraform errors, review apply scope from commit hash through HEAD, stay on the current working branch, review plan output for apply safety |
| `security-audit` | Shared skill | Deep multi-phase codebase security audit — parallel sub-agent hunting, adversarial validation, structured `findings.json` output |
| `mcp-tool-rules` | Cursor + Copilot + Codex (editor variants) | Scan MCP servers and generate rule/instruction files with correct tool arguments (`.mdc` for Cursor, `.instructions.md` for Copilot, `.agents/mcp-tools/` references plus a project `AGENTS.md` trigger for Codex) |
| `context7-docs` | Cursor + Copilot + Codex (editor variants) | Fetch current library/framework documentation via Context7 MCP instead of training data; editor variants use correct MCP server name |
| `notion-mcp-ops` | Cursor + Copilot + Codex (editor variants) | Notion MCP CRUD and formatting; fetch-before-write; failure-mode avoidance; editor variants use correct MCP server name (`plugin-notion-workspace-notion` in Cursor, `notion` in Copilot; Codex discovers the available tool names) |
| `_shared` | Support files (not a standalone skill) | **Yes** whenever Word, PowerPoint, or spreadsheet skills are installed |

Word, PowerPoint, and spreadsheet skills reference Office tools via `../_shared/office-tools/`. If `_shared` is missing or not a **sibling** of those folders, paths break.

### Custom agent library (`agents/`)

| Agent | Purpose |
|-------|---------|
| `code-review` | Read-only code review with MCP and web verification |
| `security-auditor` | Read-only security review — STRIDE, OWASP, LLM security, CVE checks |

Agents install as single `.md` files (assembled from header + `INSTRUCTIONS.md`), or `.toml` for Codex (`codex.json` metadata + shared instructions + `agents/codex-review.md`). See [AGENTS.md](AGENTS.md).

### Cursor user-global rules (`user-rules/cursor/`)

Installed to `~/.cursor/rules/<name>.mdc` (not the Cursor Settings → Customize → Rules text box, and not this repo’s maintainer `.cursor/rules/`). One protocol: edit the repo file; the host file is an install copy. Install also removes leftover `code-review-handoff.mdc` and `response-and-edit-scope.mdc`.

| File | Purpose |
|------|---------|
| `review-handoff-reconciliation.mdc` | Always-on trigger (about 1 KB): on review, audit, or fix-from-ledger turns, read the `review-handoff` skill first. The protocol (`/tmp/<topic>-handoff.md` ledger, FIX / DEFER / KEEP / DO NOT APPLY / FIXED / RECONCILED, **append-only**) lives in `skills/review-handoff/SKILL.md` and loads on demand. Distinct from the `newagentlink` skill (`/tmp/<topic>-newagentlink.md`). |
| `response-style.mdc` | Short replies (result first; a vague objective stops the work; a worse approach is named and the shorter path is used; excess complexity in the task's own work is deleted rather than defended; Changes, Verify, Open Items only on file-changing turns and only when they have content; one conclusion; no step narration, pasted logs, or AI filler). Matching Copilot fragment: `user-rules/copilot/response-style.md`. |
| `edit-scope.mdc` | Writes stay in the current repo. Auto-read is allowed everywhere. The diff is the minimum that meets the request, and work that a simpler means already settles is not done again. `/tmp`, `~/.cursor/`, and `~/.copilot/` may be written when this request or an installed protocol requires that write. Matching Copilot fragment: `user-rules/copilot/edit-scope.md`. |
| `branch-strategy.mdc` | One working branch at a time (the branch already checked out). Before the first write, `git status --short --branch` decides the branch, including when a session note says the directory is not a git repo. No edit, commit, or push on `main`. No switch off a branch that still has unmerged commits or uncommitted files. A new branch only from `main`, when the current branch is `main` or the user asks, named from branch names already used in that repository without asking the user for the name. Mixed topics on one branch are expected. Pause before `git commit` or `git push`. Matching Copilot fragment: `user-rules/copilot/branch-strategy.md`. |
| `docs-lookup.mdc` | Code documentation uses Microsoft Learn or Context7 MCP first. Native web search and fetch run only when no documentation MCP applies, the call fails, or the result has nothing usable. Matching Copilot fragment: `user-rules/copilot/docs-lookup.md`. |
| `temp-validators.mdc` | Intermediate status and validator scripts go under `/tmp` and are not added to the current code repository. Matching Copilot fragment: `user-rules/copilot/temp-validators.md`. |

### Copilot always-on instruction (`user-rules/copilot/`)

Global Copilot install concatenates `response-style.md`, `edit-scope.md`, `branch-strategy.md`, `review-handoff.md`, `docs-lookup.md`, and `temp-validators.md` into `~/.copilot/copilot-instructions.md`. That path is the personal always-on file for Copilot Agent Host chats. Fragments have no `alwaysApply` frontmatter. They are generated from `user-rules/cursor/` by `bash scripts/sync_copilot_rules.sh`; do not hand-edit them. Install verify fails when they drift from the Cursor sources. Project-scope install does not write `.github/copilot-instructions.md`.

### Codex user instructions (`user-rules/codex/`)

The same six user-rule groups are generated from the canonical Cursor sources
with `bash scripts/sync_codex_rules.sh`. Do not hand-edit the Codex fragments.
The transformation drops Cursor frontmatter, changes the scope wording to Codex,
uses `~/.agents/skills/` for skills, and adapts the allowed instruction paths to
`~/.agents/` and the active Codex home (`$CODEX_HOME`, default `~/.codex`). Policy
intent remains shared with Cursor and Copilot. `--check` fails on drift.

Global installation places the fragments in `AGENTS.md` in the active Codex home,
between `<!-- BEGIN architect-library -->` and `<!-- END architect-library -->`.
Reinstallation replaces only that block and preserves personal text outside it.
Unmatched/duplicate markers, instruction-file symlinks, and a nonempty global
`AGENTS.override.md` fail preflight before any library files are copied. Resolve
the reported conflict and rerun; the installer never removes the override.
A `rules codex` refresh requires the installed `review-handoff` skill; on a fresh
machine use `all codex` or install `skills codex` first.

Codex installation uses Python 3 standard-library helpers and needs no Node
runtime for copying. It does not install Codex, change `config.toml`, configure
MCP servers, or authenticate. Project scope installs skills and agents only;
it does not write `AGENTS.md` or global instructions. User skills stay under
`~/.agents/skills/` even with a custom `CODEX_HOME`.

Cursor and VS Code Copilot also load `~/.agents/skills/` and project
`.agents/skills/`, so after a Codex install they list the library skills twice.
Shared skills are identical copies. The Codex variants of `mcp-tool-rules`,
`context7-docs`, and `notion-mcp-ops` are marked Codex only, so other editors
use their own copy.

See official documentation for [skill discovery and invocation metadata](https://learn.chatgpt.com/docs/build-skills),
[AGENTS.md precedence](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents), and
[Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

### Claude Code user rules (`user-rules/claude/`)

The same six user-rule groups are generated from the Cursor sources with
`bash scripts/sync_claude_rules.sh`. Do not hand-edit them. The transformation
drops Cursor frontmatter, changes the scope wording to Claude Code, uses
`~/.claude/skills/` for skills, and allows writes to `~/.claude/` instead of
`~/.cursor/` and `~/.copilot/`. `--check` fails on drift.

Global installation copies each fragment to `~/.claude/rules/<name>.md`. Claude
Code loads user-level rules without `paths` frontmatter in every project
([memory docs](https://code.claude.com/docs/en/memory)). The installer replaces
only its six files and never edits `~/.claude/CLAUDE.md`, so keep personal
instructions there and do not repeat the library rules in it. A `rules claude`
refresh requires the installed `review-handoff` skill; on a fresh machine use
`all claude`. Project scope does not write `.claude/rules/`.

**Source of truth:** `<repo>/skills/<name>/`, `<repo>/agents/<name>/`, `<repo>/user-rules/cursor/<name>.mdc`, and `<repo>/user-rules/copilot/{response-style,edit-scope,branch-strategy,review-handoff,docs-lookup,temp-validators}.md`  
**Do not** copy into `<repo>/.cursor/skills/`, `<repo>/.cursor/agents/`, or `<repo>/.cursor/rules/` — use `install_library.sh`.

---

## Step 0: Locate the repository root

```bash
REPO=/path/to/architect-library
cd "$REPO"
```

```bash
test -f "$REPO/skills/excalidraw-diagram/SKILL.md" && \
test -f "$REPO/skills/word-document/SKILL.md" && \
test -f "$REPO/agents/code-review/INSTRUCTIONS.md" && \
test -f "$REPO/user-rules/cursor/review-handoff-reconciliation.mdc" && \
test -f "$REPO/user-rules/cursor/response-style.mdc" && \
test -f "$REPO/user-rules/cursor/edit-scope.mdc" && \
test -f "$REPO/user-rules/cursor/branch-strategy.mdc" && \
test -f "$REPO/user-rules/cursor/docs-lookup.mdc" && \
test -f "$REPO/user-rules/cursor/temp-validators.mdc" && \
test -f "$REPO/user-rules/copilot/response-style.md" && \
test -f "$REPO/user-rules/copilot/edit-scope.md" && \
test -f "$REPO/user-rules/copilot/branch-strategy.md" && \
test -f "$REPO/user-rules/copilot/review-handoff.md" && \
test -f "$REPO/user-rules/copilot/docs-lookup.md" && \
test -f "$REPO/user-rules/copilot/temp-validators.md" && \
test -f "$REPO/skills/review-handoff/SKILL.md" && \
bash "$REPO/scripts/sync_copilot_rules.sh" --check && \
test -f "$REPO/scripts/install_library.sh" && \
test -f "$REPO/skills/_shared/office-tools/office_tools.py" && \
echo "OK: repo layout valid"
```

---

## Step 1: Choose install scope

| User intent | Cursor | VS Code Copilot |
|-------------|--------|-----------------|
| Global full install (default) | `bash scripts/install_library.sh all cursor` | `bash scripts/install_library.sh all copilot` |
| Skills only | `bash scripts/install_library.sh skills cursor` | `bash scripts/install_library.sh skills copilot` |
| Agents only | `bash scripts/install_library.sh agents cursor` | `bash scripts/install_library.sh agents copilot` |
| User-global rules only | `bash scripts/install_library.sh rules cursor` | `bash scripts/install_library.sh rules copilot` |
| Per project | `bash scripts/install_library.sh all cursor project` | `bash scripts/install_library.sh all copilot project` |
| All editors (explicit ask) | `bash scripts/install_library.sh all all` | same |

Prefer **global** unless the user explicitly wants project-local copies. The default pair is Cursor and VS Code Copilot. Add Codex or Claude only when requested. For Codex, use the same `all`, `skills`, `agents`, or `rules` selector with `codex`; project scope supports skills and agents only.

---

## Step 2: Patch / upgrade (agent default)

When the user says **install library** or any phrase in [User phrases](#user-phrases-full-readiness-default) — or you changed `skills/`, `agents/`, or `user-rules/` — **run this** from the repo root:

```bash
REPO=/path/to/architect-library
cd "$REPO"
bash scripts/install_deps.sh
bash scripts/install_deps.sh office-system
bash scripts/install_library.sh all cursor
bash scripts/install_library.sh all copilot
```

If a runtime command fails because of missing permissions, sudo, network, or npm, report the exact failing command and error. Run `bash scripts/runtime_readiness.sh` and state partial capability per [AGENTS.md](../AGENTS.md) — **library copy can succeed without Node**; Word may still work via python-docx; new PPT decks need pptxgenjs or a user template.

| Action | Result (Cursor example) |
|--------|-------------------------|
| **New** skill | Added under `~/.cursor/skills/` |
| **Existing** skill | Folder replaced (full refresh) |
| **New** agent | Assembled to `~/.cursor/agents/` |
| **Existing** agent | File replaced |
| **New** user-global rule | Added under `~/.cursor/rules/` |
| **Existing** user-global rule | File replaced |
| **Legacy** user-global rule (`code-review-handoff.mdc`) | Removed from dest so two `alwaysApply` protocols cannot load |
| **Legacy** skill (`handoff`) | Removed from dest; replaced by `newagentlink` |
| **Legacy** Cursor command (`~/.cursor/commands/handoff.md`) | Removed; replaced by `~/.cursor/commands/newagentlink.md` |

Repo rule (Cursor): [`.cursor/rules/architect-library-patch.mdc`](../.cursor/rules/architect-library-patch.mdc).  
Copilot rule: [`.github/instructions/update-library.instructions.md`](../.github/instructions/update-library.instructions.md).

---

## Step 3: Global install targets

| Library | Cursor | Copilot | Claude (optional) | Codex (optional) |
|---------|--------|---------|-------------------|------------------|
| Skills | `~/.cursor/skills/<name>/` | `~/.copilot/skills/<name>/` | `~/.claude/skills/<name>/` | `~/.agents/skills/<name>/` |
| Agents | `~/.cursor/agents/<name>.md` | `~/.copilot/agents/<name>.agent.md` | `~/.claude/agents/<name>.md` | `${CODEX_HOME:-$HOME/.codex}/agents/<name>.toml` |
| User-global rules | `~/.cursor/rules/<name>.mdc` | `~/.copilot/copilot-instructions.md` | `~/.claude/rules/<name>.md` | `${CODEX_HOME:-$HOME/.codex}/AGENTS.md` |

### Per project (only when asked)

| Library | Cursor | Copilot | Codex |
|---------|--------|---------|-------|
| Skills | `.cursor/skills/<name>/` | `.github/skills/<name>/` | `.agents/skills/<name>/` |
| Agents | `.cursor/agents/<name>.md` | `.github/agents/<name>.agent.md` | `.codex/agents/<name>.toml` |
| User-global rules | `.cursor/rules/<name>.mdc` | — (global file only; project install does not write `.github/copilot-instructions.md`) | — (project `AGENTS.md` untouched) |

Project-scope from the **architect-library** clone (repo root or any subdirectory) skips user-global rules so they are not copied into maintainer `.cursor/rules/` or a nested `.cursor/rules/` under the clone.

---

## Runtime capability (artifact skills)

See [AGENTS.md](../AGENTS.md) § Runtime capability matrix. Summary:

| Without npm | Word | PowerPoint |
|-------------|------|------------|
| New artifact from scratch | python-docx (`install_deps.sh office`) | **Not supported** — template/XML only |
| Edit, validate, preview | `office_tools` | `office_tools` + `office-system` for `thumbnail` |

`bash scripts/runtime_readiness.sh` reports Node/npm packages and tests offline schema compilation, generated DOCX validation, DOCX/PPTX generation, and PDF/PNG previews. `bash scripts/runtime_readiness.sh --require-office` returns nonzero if an Office check fails. `office-system` runs this required gate and propagates failure; library copying remains independent. DOCX conversion requires Writer, PPTX conversion requires Impress, and previews require Poppler. Calc and spreadsheet recalculation are not checked.

## Step 4: Verify installation

**Codex:** the installer verifies all bundled skills, editor variants, agent
content, instruction fragments, and the managed block. For a standalone refresh:

```bash
bash scripts/sync_codex_rules.sh --check
bash scripts/install_library.sh all codex
```

Start a fresh Codex session and confirm `$word-document`, `$newagentlink`, and
the other library skills are discoverable. Ask which instruction sources are
active and confirm the six user-rule groups. Confirm the custom agents
`code-review` and `security-auditor` are available. Read-only agents return a
ledger round to the parent; the parent records it with `review-handoff`.
If runtime discovery cannot be checked, report that separately from file-copy
verification. Project overrides and configured disabled skills may change what
loads; the installer does not rewrite those user settings.

Maintainer regression checks (Python 3.11+ for the test runner):

```bash
python3 -m unittest discover -s scripts -p 'test_install_library.py'
bash -n scripts/install_library.sh scripts/sync_codex_rules.sh scripts/sync_claude_rules.sh
bash scripts/sync_copilot_rules.sh --check
bash scripts/sync_codex_rules.sh --check
bash scripts/sync_claude_rules.sh --check
```

**Library copy** (required) — skills and agents paths. **Artifact runtimes** (optional for install, required for delivery) — npm globals, python-docx, LibreOffice.

**Cursor:**

```bash
test -f ~/.cursor/skills/_shared/office-tools/office_tools.py && echo "OK: cursor skills"
test -f ~/.cursor/skills/word-document/SKILL.md && echo "OK: cursor skills"
test -f ~/.cursor/skills/verification-before-completion/SKILL.md && echo "OK: verification skill"
test -f ~/.cursor/skills/newagentlink/SKILL.md && echo "OK: newagentlink skill"
grep -q 'disable-model-invocation: true' ~/.cursor/skills/newagentlink/SKILL.md && echo "OK: newagentlink disable-model-invocation"
test ! -d ~/.cursor/skills/handoff && echo "OK: legacy handoff skill absent"
test ! -f ~/.cursor/commands/handoff.md && echo "OK: leftover commands/handoff.md absent"
test -f ~/.cursor/commands/newagentlink.md && echo "OK: newagentlink Cursor command"
cmp -s /path/to/architect-library/skills/newagentlink/cursor.command.md ~/.cursor/commands/newagentlink.md && echo "OK: command matches repo source"
test -f ~/.cursor/skills/api-and-interface-design/SKILL.md && echo "OK: api skill"
test -f ~/.cursor/skills/github-markdown/SKILL.md && echo "OK: github-markdown skill"
test -f ~/.cursor/skills/deprecation-and-migration/SKILL.md && echo "OK: deprecation skill"
test -f ~/.cursor/skills/security-audit/SKILL.md && echo "OK: security-audit skill"
test -f ~/.cursor/skills/mcp-tool-rules/SKILL.md && echo "OK: mcp-tool-rules variant"
test -f ~/.cursor/skills/context7-docs/SKILL.md && echo "OK: context7-docs variant"
test -f ~/.cursor/skills/notion-mcp-ops/SKILL.md && echo "OK: notion-mcp-ops variant"
test -f ~/.cursor/skills/review-handoff/SKILL.md && echo "OK: review-handoff skill (trigger target)"
test -f ~/.cursor/agents/code-review.md && echo "OK: cursor agents"
grep -q 'readonly: true' ~/.cursor/agents/code-review.md && echo "OK: code-review"
test -f ~/.cursor/agents/security-auditor.md && echo "OK: security-auditor"
grep -q 'readonly: true' ~/.cursor/agents/security-auditor.md && echo "OK: security-auditor readonly"
test -f ~/.cursor/rules/review-handoff-reconciliation.mdc && echo "OK: cursor user-global rules"
grep -q 'alwaysApply: true' ~/.cursor/rules/review-handoff-reconciliation.mdc && echo "OK: review-handoff alwaysApply"
test -f ~/.cursor/rules/response-style.mdc && echo "OK: response-style"
grep -q 'alwaysApply: true' ~/.cursor/rules/response-style.mdc && echo "OK: response-style alwaysApply"
test -f ~/.cursor/rules/edit-scope.mdc && echo "OK: edit-scope"
grep -q 'alwaysApply: true' ~/.cursor/rules/edit-scope.mdc && echo "OK: edit-scope alwaysApply"
test -f ~/.cursor/rules/branch-strategy.mdc && echo "OK: branch-strategy"
grep -q 'alwaysApply: true' ~/.cursor/rules/branch-strategy.mdc && echo "OK: branch-strategy alwaysApply"
test -f ~/.cursor/rules/docs-lookup.mdc && echo "OK: docs-lookup"
grep -q 'alwaysApply: true' ~/.cursor/rules/docs-lookup.mdc && echo "OK: docs-lookup alwaysApply"
test -f ~/.cursor/rules/temp-validators.mdc && echo "OK: temp-validators"
grep -q 'alwaysApply: true' ~/.cursor/rules/temp-validators.mdc && echo "OK: temp-validators alwaysApply"
test ! -f ~/.cursor/rules/code-review-handoff.mdc && echo "OK: legacy code-review-handoff.mdc absent"
test ! -f ~/.cursor/rules/response-and-edit-scope.mdc && echo "OK: legacy response-and-edit-scope.mdc absent"
cmp -s /path/to/architect-library/user-rules/cursor/review-handoff-reconciliation.mdc ~/.cursor/rules/review-handoff-reconciliation.mdc && echo "OK: host rule matches repo source"
cmp -s /path/to/architect-library/user-rules/cursor/response-style.mdc ~/.cursor/rules/response-style.mdc && echo "OK: response-style matches repo source"
cmp -s /path/to/architect-library/user-rules/cursor/edit-scope.mdc ~/.cursor/rules/edit-scope.mdc && echo "OK: edit-scope matches repo source"
cmp -s /path/to/architect-library/user-rules/cursor/branch-strategy.mdc ~/.cursor/rules/branch-strategy.mdc && echo "OK: branch-strategy matches repo source"
cmp -s /path/to/architect-library/user-rules/cursor/docs-lookup.mdc ~/.cursor/rules/docs-lookup.mdc && echo "OK: docs-lookup matches repo source"
cmp -s /path/to/architect-library/user-rules/cursor/temp-validators.mdc ~/.cursor/rules/temp-validators.mdc && echo "OK: temp-validators matches repo source"
test -f ~/.copilot/copilot-instructions.md && echo "OK: copilot always-on instruction"
test -f ~/.copilot/skills/review-handoff/SKILL.md && echo "OK: copilot review-handoff skill (trigger target)"
grep -q 'Applies in every VS Code Copilot chat.' ~/.copilot/copilot-instructions.md && echo "OK: copilot handoff opening"
grep -q '/tmp/<topic>-handoff.md' ~/.copilot/copilot-instructions.md && echo "OK: copilot handoff ledger path"
grep -q '# Response style' ~/.copilot/copilot-instructions.md && echo "OK: copilot response style"
grep -q '# Edit scope' ~/.copilot/copilot-instructions.md && echo "OK: copilot edit scope"
grep -q '# Branch strategy' ~/.copilot/copilot-instructions.md && echo "OK: copilot branch strategy"
grep -q '# Review handoff' ~/.copilot/copilot-instructions.md && echo "OK: copilot review handoff"
grep -q '# Docs lookup' ~/.copilot/copilot-instructions.md && echo "OK: copilot docs lookup"
grep -q '# Temporary validators' ~/.copilot/copilot-instructions.md && echo "OK: copilot temporary validators"
! grep -q 'alwaysApply' ~/.copilot/copilot-instructions.md && echo "OK: copilot file has no alwaysApply"
cmp -s <(printf '%s\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s\n' "$(cat /path/to/architect-library/user-rules/copilot/response-style.md)" "$(cat /path/to/architect-library/user-rules/copilot/edit-scope.md)" "$(cat /path/to/architect-library/user-rules/copilot/branch-strategy.md)" "$(cat /path/to/architect-library/user-rules/copilot/review-handoff.md)" "$(cat /path/to/architect-library/user-rules/copilot/docs-lookup.md)" "$(cat /path/to/architect-library/user-rules/copilot/temp-validators.md)") ~/.copilot/copilot-instructions.md && echo "OK: copilot instruction matches fragments"
find ~/.cursor/skills -maxdepth 2 -name .git -type d   # expect no output
cd /path/to/architect-library/skills/_shared/office-tools && uv run python3 office_tools.py --help >/dev/null && echo "OK: office tools"
bash /path/to/architect-library/scripts/runtime_readiness.sh --require-office
source /path/to/architect-library/scripts/architect_env.sh
command -v npm >/dev/null && echo "OK: npm CLI" || echo "WARN: npm CLI missing"
test -d ~/.npm-global/lib/node_modules/docx && test -d ~/.npm-global/lib/node_modules/pptxgenjs && echo "OK: docx/pptxgenjs on disk"
cd /path/to/architect-library/skills/_shared/office-tools && uv run python3 -c "import docx" && echo "OK: python-docx"
bash /path/to/architect-library/scripts/runtime_readiness.sh
```

**VS Code Copilot:**

```bash
test -f ~/.copilot/skills/_shared/office-tools/office_tools.py && echo "OK: copilot skills"
test -f ~/.copilot/skills/word-document/SKILL.md && echo "OK: copilot skills"
test -f ~/.copilot/skills/verification-before-completion/SKILL.md && echo "OK: verification skill"
test -f ~/.copilot/skills/newagentlink/SKILL.md && echo "OK: newagentlink skill"
test ! -d ~/.copilot/skills/handoff && echo "OK: legacy handoff skill absent"
test -f ~/.copilot/skills/api-and-interface-design/SKILL.md && echo "OK: api skill"
test -f ~/.copilot/skills/github-markdown/SKILL.md && echo "OK: github-markdown skill"
test -f ~/.copilot/skills/deprecation-and-migration/SKILL.md && echo "OK: deprecation skill"
test -f ~/.copilot/skills/security-audit/SKILL.md && echo "OK: security-audit skill"
test -f ~/.copilot/skills/mcp-tool-rules/SKILL.md && echo "OK: mcp-tool-rules variant"
test -f ~/.copilot/skills/context7-docs/SKILL.md && echo "OK: context7-docs variant"
test -f ~/.copilot/skills/notion-mcp-ops/SKILL.md && echo "OK: notion-mcp-ops variant"
test -f ~/.copilot/agents/code-review.agent.md && echo "OK: copilot agents"
test -f ~/.copilot/agents/security-auditor.agent.md && echo "OK: security-auditor"
grep -q 'disallowedTools: edit' ~/.copilot/agents/security-auditor.agent.md && echo "OK: security-auditor readonly"
cd /path/to/architect-library/skills/_shared/office-tools && uv run python3 office_tools.py --help >/dev/null && echo "OK: office tools"
bash /path/to/architect-library/scripts/runtime_readiness.sh --require-office
source /path/to/architect-library/scripts/architect_env.sh
command -v npm >/dev/null && echo "OK: npm CLI" || echo "WARN: npm CLI missing"
test -d ~/.npm-global/lib/node_modules/docx && test -d ~/.npm-global/lib/node_modules/pptxgenjs && echo "OK: docx/pptxgenjs on disk"
cd /path/to/architect-library/skills/_shared/office-tools && uv run python3 -c "import docx" && echo "OK: python-docx"
bash /path/to/architect-library/scripts/runtime_readiness.sh
```

The install script runs **library** checks automatically for the `EDITOR` you pass. Claim DOCX/PPTX runtime readiness only after the `--require-office` gate passes. Checks use temporary documents and isolated LibreOffice profiles, require readable nonempty PDFs and PNGs, and do not treat exit 0 without output as success.

---

## Step 5: Reload the editor

- **Codex:** start a fresh session; skills use `$skill-name`, and `$newagentlink` is explicit-only.
- **Cursor:** new agent chat or reload window (skills, agents, and user-global rules reload).
- **VS Code:** reload window.

---

## Agent execution rules (skills)

| Skill | Before marking the task complete |
|-------|----------------------------------|
| **excalidraw-diagram** | Check both bindings and reciprocal endpoint references for node-to-node arrows. Architecture routes use a direct connector when clear, including a diagonal. Keep a bend only to avoid an obstacle, separate routes, or clarify a fan-out; those bends stay horizontal/vertical. No preventable crossings. Check readable text (default minimum 16px), visible label alignment and equal row spacing separately from collisions, per `shape-and-layout.md` and `render-validate.md`. Every depicted Azure service and private endpoint has its own official icon node; when the cache has none, use a labeled box and report it. F5, Palo Alto Networks, NGINX, Datadog, GitHub, and GitHub Actions use cached Simple Icons SVGs. Render `.excalidraw` → PNG under the 30,000-patch vision cap; **view** the overview and changed-region crops, fix layout. Existing files: geometric collision pass before first PNG (`edit-existing.md`) |
| **word-document** | Validate DOCX; explicit table styling; deliver `.docx` only |
| **powerpoint-presentation** | Validate PPTX; **`thumbnail` every deck**; **view** images; `office-system` if missing; test native PowerPoint opening when available, otherwise report it unverified; follow repair-prompt recovery in the skill |
| **spreadsheet-document** | Deliver `.xlsx`; formulas LibreOffice can evaluate (no `XLOOKUP`/`XMATCH`/`SORT`/`FILTER`/`UNIQUE`/`SEQUENCE`); `recalc` until JSON `status: success` if formulas used; external-link refusal fails the recalc until values are preserved or `--force` |
| **pdf-document** | Deliver `.pdf`; form fills per `references/forms.md` |
| **verification-before-completion** | Fresh verification command output in same message before any completion/success claim |
| **newagentlink** | `/tmp/<topic>-newagentlink.md` written once this turn; one-shot banner present; live git gathered; chat returns path + starter prompt only; never writes `/tmp/<topic>-handoff.md` |
| **api-and-interface-design** | Contract before implementation; consistent errors; boundary validation; list pagination; deprecation cross-check when changing public interfaces |
| **github-markdown** | Render context identified; valid GFM syntax; context-limited features avoided (e.g. no footnotes in wikis); relative in-repo links where applicable; delivery checklist in `SKILL.md` satisfied |
| **deprecation-and-migration** | Replacement before deprecation; migration guide; zero-usage verified before removal |
| **terraform-commit-review** | Commit range established; all changed files read; provider docs verified via MCP; 7-section checklist applied; structured report with intent summary, per-phase table, issues, vendor comments, source URLs, and execution summary |
| **terraform-apply-assistance** | Apply scope established (commit hash through HEAD or inferred); error/plan triaged; stayed on the current working branch (new branch only when the current branch is `main`, or the user asks); diagnosis via MCP; smallest edit applied; local validation run; **paused for user review** — no commit/push unless user instructs; plan evaluated with rubric; recap/runbook requests honor phase scope exclusions; risks re-raised every iteration; execution summary with apply decision, global/common/phase-specific env prerequisites, per-phase `## Phase N` command blocks, and post-apply checks |
| **security-audit** | All 6 phases completed (Recon → Hunt → Validate → Report → Structured output → Independent verification); `findings.json` validates against schema (`validate-findings.cjs`); `REPORT.md` and `FINDINGS-DETAIL.md` reconciled with `findings.json`; output directory contains all artifacts |
| **mcp-tool-rules** | MCP config read; servers presented and confirmed; tools discovered per server; editor-appropriate files generated (Cursor: `.mdc` rules, Copilot: `.instructions.md`, Codex: `.agents/mcp-tools/` references plus a managed project `AGENTS.md` trigger) with parameter tables and example calls; files validated (server names, tables, examples, frontmatter); report delivered |
| **context7-docs** | Library/framework docs fetched via Context7 MCP; version-specific library ID selected when applicable; query decomposed to one topic per call; source cited in response; fallback to web search or Microsoft Learn when Context7 lacks the library |
| **notion-mcp-ops** | Notion MCP server discovered with correct editor server name; fetch before write on updates; anchors from fetched content; formatting rules applied (`<callout>`, HTML tables); post-update verify fetch for structural edits; property names from fetched schema |

**PowerPoint is not done** when the `.pptx` exists — only after layout preview (or user waives).

Structural validation, rendered layout, and native PowerPoint opening are separate checks. LibreOffice rendering and the Office runtime-readiness gate do not prove that Microsoft PowerPoint accepts a delivered file. After a repair prompt, preserve the original, compare content and presenter notes, validate and preview any replacement, and obtain native-opening confirmation when possible. See [the recovery workflow](../skills/powerpoint-presentation/references/layout-preview.md#microsoft-powerpoint-compatibility).

## Custom agent execution (agents)

| Agent | Done when |
|-------|-----------|
| **code-review** | Scope set (SHA range when provided); tests reviewed first; five-axis review; requirements alignment when plan supplied; logic traced; Strengths + findings with evidence; verification story; MCP/web verification table; merge verdict; **no edits** |
| **security-auditor** | Scope set; trust boundaries + STRIDE; findings by severity with evidence; PoC for Critical/High; release verdict; **no edits** |

See [CODE-REVIEW-AGENT.md](CODE-REVIEW-AGENT.md) and [SECURITY-AUDITOR-AGENT.md](SECURITY-AUDITOR-AGENT.md).

---

## Runtime command reference

| Task | Command (from repo root) |
|------|---------------------------|
| Library copy (Cursor) | `bash scripts/install_library.sh all cursor` |
| Cursor user-global rules only | `bash scripts/install_library.sh rules cursor` |
| Copilot always-on instruction only | `bash scripts/install_library.sh rules copilot` |
| Library copy (Copilot) | `bash scripts/install_library.sh all copilot` |
| Library copy (Codex) | `bash scripts/install_library.sh all codex` |
| Codex user instructions only | `bash scripts/install_library.sh rules codex` |
| Library copy (all editors) | `bash scripts/install_library.sh all all` |
| Core runtimes | `bash scripts/install_deps.sh` |
| LibreOffice Writer + Impress + Calc + Poppler | `bash scripts/install_deps.sh office-system` |
| Offline Excalidraw | `bash scripts/vendor_excalidraw.sh` |
| New DOCX / PPTX via Node | `bash scripts/install_deps.sh node` (included in `install_deps.sh all`) |
| Word fallback (no npm) | `bash scripts/install_deps.sh office` (python-docx in uv env) |
| Readiness summary | `bash scripts/runtime_readiness.sh` |
| Required DOCX/PPTX readiness gate | `bash scripts/runtime_readiness.sh --require-office` |
| Shell env (manual Node) | `source /path/to/architect-library/scripts/architect_env.sh` |
| Persistent env file | `~/.config/architect-library/env.sh` (written by `install_node.sh`; hooked from `~/.bashrc`) |

Install scripts source `architect_env.sh` automatically. Agents doing docx-js/pptxgenjs **outside** those scripts must source it first so `NODE_PATH` includes `~/.npm-global/lib/node_modules`.

Do not run `install_deps.sh` inside `~/.cursor/skills/` — run from the **repository clone**.

---

## Common mistakes

| Mistake | Why it fails |
|---------|----------------|
| Copy only one skill folder | Word/PPT break; missing `_shared` |
| Omit `_shared` | `../_shared/office-tools/` paths break |
| Copy repo into `~/.cursor/skills/` | Wrong layout |
| Copy `user-rules/` into `repo/.cursor/rules/` | Maintainer rules and user-global rules are different sources |
| Leave `~/.cursor/rules/code-review-handoff.mdc` after install | Two `alwaysApply` review protocols load — install must delete the legacy name |
| Leave `~/.cursor/rules/response-and-edit-scope.mdc` after install | Old combined rule overlaps `response-style.mdc` and `edit-scope.mdc` — install must delete the legacy name |
| Leave `~/.cursor/skills/handoff` or `~/.cursor/commands/handoff.md` after install | Old continuation skill/command collides with `newagentlink` — install must delete both and install `~/.cursor/commands/newagentlink.md` |
| Install Claude without being asked | Default is Cursor and VS Code Copilot; bare `install_library.sh` also installs Claude |
| Edit `agents/` without running install | Global agents stale |
| Edit `user-rules/` without running install | `~/.cursor/rules/` and `~/.copilot/copilot-instructions.md` stale |
| Add agents to `skills/` bundle | Wrong library — use `AGENT_BUNDLE` in `install_library.sh` |
| Deliver PPTX without `thumbnail` | Violates powerpoint-presentation completion rules |

---

## Quick reference

Full human guide: [README.md](../README.md). Agent catalog: [AGENTS.md](AGENTS.md).
