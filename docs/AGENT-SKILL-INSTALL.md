# Agent guide: install Architect Library (Cursor / Copilot)

Use this document when the user asks to install, update, or fix **skills**, **custom agents**, or **Cursor user-global rules** from the **architect-library** repository. Follow it literally; do not invent alternate paths.

**Cross-editor contract:** [AGENTS.md](../AGENTS.md) at the repo root — install trigger phrases, editor scope, and anti-patterns (both Cursor and Copilot should follow it).

**Editing this repository?** Cursor loads [`.cursor/rules/`](../.cursor/rules/) automatically (maintainer rules). Follow [MAINTAINING-SKILLS.md](MAINTAINING-SKILLS.md) whenever you add a skill, agent, user-global Cursor rule, workflow step, or dependency.

## User phrases (full readiness default)

When the user says any of these, run a **full global readiness install** (runtimes + skills + agents + Cursor user-global rules when you are in Cursor) for **the editor you are running in**:

- **install library** | install the library | patch library | refresh library | update library
- install skills and agents | sync library | update architect library
- patch | upgrade | install | refresh (skills or agents)

### Editor-scoped commands (default)

Run these runtime commands first:

```bash
bash scripts/install_deps.sh
bash scripts/install_deps.sh office-system
```

Then run the editor-scoped library command:

| You are in | Library command | Targets |
|------------|-----------------|---------|
| **Cursor** | `bash scripts/install_library.sh all cursor` | `~/.cursor/skills/`, `~/.cursor/agents/`, `~/.cursor/rules/` |
| **VS Code Copilot** | `bash scripts/install_library.sh all copilot` | `~/.copilot/skills/`, `~/.copilot/agents/` |
| **Claude Code** | `bash scripts/install_library.sh all claude` | `~/.claude/skills/`, `~/.claude/agents/` |

Do **not** ask which editor, scope, subset, or runtime set to install for these trigger phrases. Use the active editor default.

Do **not** install to other editors unless the user explicitly asks (e.g. "install for all editors" → `bash scripts/install_library.sh` with no `EDITOR` arg, which uses `both` = Cursor + Copilot + Claude).

Use **partial** installs (`skills`, `agents`, or `rules` only) **only** when the user explicitly asks — still scoped to your editor, e.g. `bash scripts/install_library.sh skills cursor` or `bash scripts/install_library.sh rules cursor`.

## What you are installing

Architect Library publishes **two libraries** plus **Cursor user-global rules**:

### Skill library (`skills/`)

| Folder | Type | Required |
|--------|------|----------|
| `excalidraw-diagram` | Cursor/Copilot skill | If diagrams are needed |
| `word-document` | Cursor/Copilot skill | If DOCX is needed |
| `powerpoint-presentation` | Cursor/Copilot skill | If PPTX is needed |
| `spreadsheet-document` | Cursor/Copilot skill | If XLSX/spreadsheet work is needed |
| `pdf-document` | Cursor/Copilot skill | If PDF work is needed |
| `verification-before-completion` | Cursor/Copilot skill | Evidence before completion claims; required by artifact skills at delivery |
| `newagentlink` | Cursor/Copilot skill | One-shot `/tmp/<topic>-newagentlink.md` for a new agent chat; not the review ledger |
| `api-and-interface-design` | Cursor/Copilot skill | API and module boundary design workflow |
| `github-markdown` | Cursor/Copilot skill | GitHub Flavored Markdown for READMEs, issues, PRs, discussions, wikis, and repo docs |
| `deprecation-and-migration` | Cursor/Copilot skill | Deprecation and migration planning workflow |
| `terraform-commit-review` | Cursor/Copilot skill | Terraform IaC commit-range review (correctness, security, destructive changes) |
| `terraform-apply-assistance` | Cursor/Copilot skill | Fix Terraform errors, review apply scope from commit hash through HEAD, create fix branches, review plan output for apply safety |
| `security-audit` | Cursor/Copilot skill | Deep multi-phase codebase security audit — parallel sub-agent hunting, adversarial validation, structured `findings.json` output |
| `mcp-tool-rules` | Cursor + Copilot (editor variants) | Scan MCP servers and generate rule/instruction files with correct tool arguments (`.mdc` for Cursor, `.instructions.md` for Copilot) |
| `context7-docs` | Cursor + Copilot (editor variants) | Fetch current library/framework documentation via Context7 MCP instead of training data; editor variants use correct MCP server name |
| `notion-mcp-ops` | Cursor + Copilot (editor variants) | Notion MCP CRUD and formatting; fetch-before-write; failure-mode avoidance; editor variants use correct MCP server name (`plugin-notion-workspace-notion` in Cursor, `notion` in Copilot) |
| `_shared` | Support files (not a standalone skill) | **Yes** whenever Word, PowerPoint, or spreadsheet skills are installed |

Word, PowerPoint, and spreadsheet skills reference Office tools via `../_shared/office-tools/`. If `_shared` is missing or not a **sibling** of those folders, paths break.

### Custom agent library (`agents/`)

| Agent | Purpose |
|-------|---------|
| `code-review` | Read-only code review with MCP and web verification |
| `security-auditor` | Read-only security review — STRIDE, OWASP, LLM security, CVE checks |

Agents install as single `.md` files (assembled from header + `INSTRUCTIONS.md`). See [AGENTS.md](AGENTS.md).

### Cursor user-global rules (`user-rules/cursor/`)

Cursor-only. Installed to `~/.cursor/rules/<name>.mdc` (not the Cursor Settings → Customize → Rules text box, and not this repo’s maintainer `.cursor/rules/`). One protocol: edit the repo file; the host file is an install copy. Install also removes leftover `code-review-handoff.mdc`.

| File | Purpose |
|------|---------|
| `review-handoff-reconciliation.mdc` | `/tmp/<topic>-handoff.md` ledger; dispositions FIX / DEFER / KEEP / DO NOT APPLY / FIXED / RECONCILED; reviewer writes, fixer validates and appends, loop until reconciled. Distinct from the `newagentlink` skill (`/tmp/<topic>-newagentlink.md`). |

**Source of truth:** `<repo>/skills/<name>/`, `<repo>/agents/<name>/`, and `<repo>/user-rules/cursor/<name>.mdc`  
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
| Cursor user-global rules only | `bash scripts/install_library.sh rules cursor` | n/a (Cursor-only) |
| Per project | `bash scripts/install_library.sh all cursor project` | `bash scripts/install_library.sh all copilot project` |
| All editors (explicit ask) | `bash scripts/install_library.sh` | same |

Prefer **global** unless the user explicitly wants project-local copies. Prefer **editor-scoped** unless the user explicitly wants all editors.

---

## Step 2: Patch / upgrade (agent default)

When the user says **install library** or any phrase in [User phrases](#user-phrases-full-readiness-default) — or you changed `skills/`, `agents/`, or `user-rules/` — **run this** from the repo root (replace `cursor` with `copilot` or `claude` if that is your editor):

```bash
REPO=/path/to/architect-library
cd "$REPO"
bash scripts/install_deps.sh
bash scripts/install_deps.sh office-system
bash scripts/install_library.sh all cursor
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

| Library | Cursor | Copilot | Claude (optional) |
|---------|--------|---------|-------------------|
| Skills | `~/.cursor/skills/<name>/` | `~/.copilot/skills/<name>/` | `~/.claude/skills/<name>/` |
| Agents | `~/.cursor/agents/<name>.md` | `~/.copilot/agents/<name>.agent.md` | `~/.claude/agents/<name>.md` |
| User-global rules | `~/.cursor/rules/<name>.mdc` | — | — |

### Per project (only when asked)

| Library | Cursor | Copilot |
|---------|--------|---------|
| Skills | `.cursor/skills/<name>/` | `.github/skills/<name>/` |
| Agents | `.cursor/agents/<name>.md` | `.github/agents/<name>.agent.md` |
| User-global rules | `.cursor/rules/<name>.mdc` | — |

Project-scope from the **architect-library** clone (repo root or any subdirectory) skips user-global rules so they are not copied into maintainer `.cursor/rules/` or a nested `.cursor/rules/` under the clone.

---

## Runtime capability (artifact skills)

See [AGENTS.md](../AGENTS.md) § Runtime capability matrix. Summary:

| Without npm | Word | PowerPoint |
|-------------|------|------------|
| New artifact from scratch | python-docx (`install_deps.sh office`) | **Not supported** — template/XML only |
| Edit, validate, preview | `office_tools` | `office_tools` + `office-system` for `thumbnail` |

`bash scripts/runtime_readiness.sh` prints Node, npm globals, and python-docx status after `install_deps.sh`.

## Step 4: Verify installation

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
test -f ~/.cursor/agents/code-review.md && echo "OK: cursor agents"
grep -q 'readonly: true' ~/.cursor/agents/code-review.md && echo "OK: code-review"
test -f ~/.cursor/agents/security-auditor.md && echo "OK: security-auditor"
grep -q 'readonly: true' ~/.cursor/agents/security-auditor.md && echo "OK: security-auditor readonly"
test -f ~/.cursor/rules/review-handoff-reconciliation.mdc && echo "OK: cursor user-global rules"
grep -q 'alwaysApply: true' ~/.cursor/rules/review-handoff-reconciliation.mdc && echo "OK: review-handoff alwaysApply"
test ! -f ~/.cursor/rules/code-review-handoff.mdc && echo "OK: legacy code-review-handoff.mdc absent"
cmp -s /path/to/architect-library/user-rules/cursor/review-handoff-reconciliation.mdc ~/.cursor/rules/review-handoff-reconciliation.mdc && echo "OK: host rule matches repo source"
find ~/.cursor/skills -maxdepth 2 -name .git -type d   # expect no output
cd /path/to/architect-library/skills/_shared/office-tools && uv run python3 office_tools.py --help >/dev/null && echo "OK: office tools"
command -v soffice >/dev/null && command -v pdftoppm >/dev/null && echo "OK: office-system"
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
command -v soffice >/dev/null && command -v pdftoppm >/dev/null && echo "OK: office-system"
source /path/to/architect-library/scripts/architect_env.sh
command -v npm >/dev/null && echo "OK: npm CLI" || echo "WARN: npm CLI missing"
test -d ~/.npm-global/lib/node_modules/docx && test -d ~/.npm-global/lib/node_modules/pptxgenjs && echo "OK: docx/pptxgenjs on disk"
cd /path/to/architect-library/skills/_shared/office-tools && uv run python3 -c "import docx" && echo "OK: python-docx"
bash /path/to/architect-library/scripts/runtime_readiness.sh
```

The install script runs **library** checks automatically for the `EDITOR` you pass. npm/python-docx/LibreOffice are artifact runtimes — use the commands above or `runtime_readiness.sh`.

---

## Step 5: Reload the editor

- **Cursor:** new agent chat or reload window (skills, agents, and user-global rules reload).
- **VS Code:** reload window.

---

## Agent execution rules (skills)

| Skill | Before marking the task complete |
|-------|----------------------------------|
| **excalidraw-diagram** | Render `.excalidraw` → PNG, **view** the image, fix in a loop |
| **word-document** | Validate DOCX; explicit table styling; deliver `.docx` only |
| **powerpoint-presentation** | Validate PPTX; **`thumbnail` every deck**; **view** images; `office-system` if missing |
| **spreadsheet-document** | Deliver `.xlsx`; `recalc` until zero formula errors if formulas used |
| **pdf-document** | Deliver `.pdf`; form fills per `references/forms.md` |
| **verification-before-completion** | Fresh verification command output in same message before any completion/success claim |
| **newagentlink** | `/tmp/<topic>-newagentlink.md` written once this turn; one-shot banner present; live git gathered; chat returns path + starter prompt only; never writes `/tmp/<topic>-handoff.md` |
| **api-and-interface-design** | Contract before implementation; consistent errors; boundary validation; list pagination; deprecation cross-check when changing public interfaces |
| **github-markdown** | Render context identified; valid GFM syntax; context-limited features avoided (e.g. no footnotes in wikis); relative in-repo links where applicable; delivery checklist in `SKILL.md` satisfied |
| **deprecation-and-migration** | Replacement before deprecation; migration guide; zero-usage verified before removal |
| **terraform-commit-review** | Commit range established; all changed files read; provider docs verified via MCP; 7-section checklist applied; structured report with intent summary, per-phase table, issues, vendor comments, source URLs, and execution summary |
| **terraform-apply-assistance** | Apply scope established (commit hash through HEAD or inferred); error/plan triaged; focused branch created; diagnosis via MCP; smallest edit applied; local validation run; **paused for user review** — no commit/push unless user instructs; plan evaluated with rubric; recap/runbook requests honor phase scope exclusions; risks re-raised every iteration; execution summary with apply decision, global/common/phase-specific env prerequisites, per-phase `## Phase N` command blocks, and post-apply checks |
| **security-audit** | All 6 phases completed (Recon → Hunt → Validate → Report → Structured output → Independent verification); `findings.json` validates against schema (`validate-findings.cjs`); `REPORT.md` and `FINDINGS-DETAIL.md` reconciled with `findings.json`; output directory contains all artifacts |
| **mcp-tool-rules** | MCP config read; servers presented and confirmed; tools discovered per server; editor-appropriate files generated (Cursor: `.mdc` rules, Copilot: `.instructions.md`) with parameter tables and example calls; files validated (server names, tables, examples, frontmatter); report delivered |
| **context7-docs** | Library/framework docs fetched via Context7 MCP; version-specific library ID selected when applicable; query decomposed to one topic per call; source cited in response; fallback to web search or Microsoft Learn when Context7 lacks the library |
| **notion-mcp-ops** | Notion MCP server discovered with correct editor server name; fetch before write on updates; anchors from fetched content; formatting rules applied (`<callout>`, HTML tables); post-update verify fetch for structural edits; property names from fetched schema |

**PowerPoint is not done** when the `.pptx` exists — only after layout preview (or user waives).

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
| Library copy (Copilot) | `bash scripts/install_library.sh all copilot` |
| Library copy (all editors) | `bash scripts/install_library.sh` |
| Core runtimes | `bash scripts/install_deps.sh` |
| LibreOffice + Poppler (PPT) | `bash scripts/install_deps.sh office-system` |
| Offline Excalidraw | `bash scripts/vendor_excalidraw.sh` |
| New DOCX / PPTX via Node | `bash scripts/install_deps.sh node` (included in `install_deps.sh all`) |
| Word fallback (no npm) | `bash scripts/install_deps.sh office` (python-docx in uv env) |
| Readiness summary | `bash scripts/runtime_readiness.sh` |
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
| Leave `~/.cursor/skills/handoff` or `~/.cursor/commands/handoff.md` after install | Old continuation skill/command collides with `newagentlink` — install must delete both and install `~/.cursor/commands/newagentlink.md` |
| Install to all editors from one agent | Pollutes unused paths — scope to your editor |
| Edit `agents/` without running install | Global agents stale |
| Edit `user-rules/` without running install | `~/.cursor/rules/` stale |
| Add agents to `skills/` bundle | Wrong library — use `AGENT_BUNDLE` in `install_library.sh` |
| Deliver PPTX without `thumbnail` | Violates powerpoint-presentation completion rules |

---

## Quick reference

Full human guide: [README.md](../README.md). Agent catalog: [AGENTS.md](AGENTS.md).
