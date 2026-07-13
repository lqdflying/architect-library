# Agent guide: install Architect Library (Cursor / Copilot)

Use this document when the user asks to install, update, or fix **skills** or **custom agents** from the **architect-library** repository. Follow it literally; do not invent alternate paths.

**Cross-editor contract:** [AGENTS.md](../AGENTS.md) at the repo root — install trigger phrases, editor scope, and anti-patterns (both Cursor and Copilot should follow it).

**Editing this repository?** Cursor loads [`.cursor/rules/`](../.cursor/rules/) automatically. Follow [MAINTAINING-SKILLS.md](MAINTAINING-SKILLS.md) whenever you add a skill, agent, workflow step, or dependency.

## User phrases (full readiness default)

When the user says any of these, run a **full global readiness install** (runtimes + skills + agents) for **the editor you are running in**:

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
| **Cursor** | `bash scripts/install_library.sh all cursor` | `~/.cursor/skills/`, `~/.cursor/agents/` |
| **VS Code Copilot** | `bash scripts/install_library.sh all copilot` | `~/.copilot/skills/`, `~/.copilot/agents/` |
| **Claude Code** | `bash scripts/install_library.sh all claude` | `~/.claude/skills/`, `~/.claude/agents/` |

Do **not** ask which editor, scope, subset, or runtime set to install for these trigger phrases. Use the active editor default.

Do **not** install to other editors unless the user explicitly asks (e.g. "install for all editors" → `bash scripts/install_library.sh` with no `EDITOR` arg, which uses `both` = Cursor + Copilot + Claude).

Use **partial** installs (`skills` or `agents` only) **only** when the user explicitly asks — still scoped to your editor, e.g. `bash scripts/install_library.sh skills cursor`.

## What you are installing

Architect Library publishes **two libraries**:

### Skill library (`skills/`)

| Folder | Type | Required |
|--------|------|----------|
| `excalidraw-diagram` | Cursor/Copilot skill | If diagrams are needed |
| `word-document` | Cursor/Copilot skill | If DOCX is needed |
| `powerpoint-presentation` | Cursor/Copilot skill | If PPTX is needed |
| `spreadsheet-document` | Cursor/Copilot skill | If XLSX/spreadsheet work is needed |
| `pdf-document` | Cursor/Copilot skill | If PDF work is needed |
| `verification-before-completion` | Cursor/Copilot skill | Evidence before completion claims; required by artifact skills at delivery |
| `api-and-interface-design` | Cursor/Copilot skill | API and module boundary design workflow |
| `deprecation-and-migration` | Cursor/Copilot skill | Deprecation and migration planning workflow |
| `terraform-commit-review` | Cursor/Copilot skill | Terraform IaC commit-range review (correctness, security, destructive changes) |
| `terraform-apply-assistance` | Cursor/Copilot skill | Fix Terraform errors, review apply scope from commit hash through HEAD, create fix branches, review plan output for apply safety |
| `security-audit` | Cursor/Copilot skill | Deep multi-phase codebase security audit — parallel sub-agent hunting, adversarial validation, structured `findings.json` output |
| `mcp-tool-rules` | Cursor + Copilot (editor variants) | Scan MCP servers and generate rule/instruction files with correct tool arguments (`.mdc` for Cursor, `.instructions.md` for Copilot) |
| `_shared` | Support files (not a standalone skill) | **Yes** whenever Word, PowerPoint, or spreadsheet skills are installed |

Word, PowerPoint, and spreadsheet skills reference Office tools via `../_shared/office-tools/`. If `_shared` is missing or not a **sibling** of those folders, paths break.

### Custom agent library (`agents/`)

| Agent | Purpose |
|-------|---------|
| `code-review` | Read-only code review with MCP and web verification |
| `security-auditor` | Read-only security review — STRIDE, OWASP, LLM security, CVE checks |

Agents install as single `.md` files (assembled from header + `INSTRUCTIONS.md`). See [AGENTS.md](AGENTS.md).

**Source of truth:** `<repo>/skills/<name>/` and `<repo>/agents/<name>/`  
**Do not** copy into `<repo>/.cursor/skills/` or `<repo>/.cursor/agents/` — use `install_library.sh`.

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
| Per project | `bash scripts/install_library.sh all cursor project` | `bash scripts/install_library.sh all copilot project` |
| All editors (explicit ask) | `bash scripts/install_library.sh` | same |

Prefer **global** unless the user explicitly wants project-local copies. Prefer **editor-scoped** unless the user explicitly wants all editors.

---

## Step 2: Patch / upgrade (agent default)

When the user says **install library** or any phrase in [User phrases](#user-phrases-full-readiness-default) — or you changed `skills/` or `agents/` — **run this** from the repo root (replace `cursor` with `copilot` or `claude` if that is your editor):

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

Repo rule (Cursor): [`.cursor/rules/architect-library-patch.mdc`](../.cursor/rules/architect-library-patch.mdc).  
Copilot rule: [`.github/instructions/update-library.instructions.md`](../.github/instructions/update-library.instructions.md).

---

## Step 3: Global install targets

| Library | Cursor | Copilot | Claude (optional) |
|---------|--------|---------|-------------------|
| Skills | `~/.cursor/skills/<name>/` | `~/.copilot/skills/<name>/` | `~/.claude/skills/<name>/` |
| Agents | `~/.cursor/agents/<name>.md` | `~/.copilot/agents/<name>.agent.md` | `~/.claude/agents/<name>.md` |

### Per project (only when asked)

| Library | Cursor | Copilot |
|---------|--------|---------|
| Skills | `.cursor/skills/<name>/` | `.github/skills/<name>/` |
| Agents | `.cursor/agents/<name>.md` | `.github/agents/<name>.agent.md` |

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
test -f ~/.cursor/skills/api-and-interface-design/SKILL.md && echo "OK: api skill"
test -f ~/.cursor/skills/deprecation-and-migration/SKILL.md && echo "OK: deprecation skill"
test -f ~/.cursor/skills/security-audit/SKILL.md && echo "OK: security-audit skill"
test -f ~/.cursor/agents/code-review.md && echo "OK: cursor agents"
grep -q 'readonly: true' ~/.cursor/agents/code-review.md && echo "OK: code-review"
test -f ~/.cursor/agents/security-auditor.md && echo "OK: security-auditor"
grep -q 'readonly: true' ~/.cursor/agents/security-auditor.md && echo "OK: security-auditor readonly"
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
test -f ~/.copilot/skills/api-and-interface-design/SKILL.md && echo "OK: api skill"
test -f ~/.copilot/skills/deprecation-and-migration/SKILL.md && echo "OK: deprecation skill"
test -f ~/.copilot/skills/security-audit/SKILL.md && echo "OK: security-audit skill"
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

- **Cursor:** new agent chat or reload window (skills + agents reload).
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
| **api-and-interface-design** | Contract before implementation; consistent errors; boundary validation; list pagination; deprecation cross-check when changing public interfaces |
| **deprecation-and-migration** | Replacement before deprecation; migration guide; zero-usage verified before removal |
| **terraform-commit-review** | Commit range established; all changed files read; provider docs verified via MCP; 7-section checklist applied; structured report with intent summary, per-phase table, issues, vendor comments, source URLs, and execution summary |
| **terraform-apply-assistance** | Apply scope established (commit hash through HEAD or inferred); error/plan triaged; focused branch created; diagnosis via MCP; smallest edit applied; local validation run; **paused for user review** — no commit/push unless user instructs; plan evaluated with rubric; risks re-raised every iteration; execution summary with apply decision, global/common/phase-specific env prerequisites, per-phase `## Phase N` command blocks, and post-apply checks |
| **security-audit** | All 6 phases completed (Recon → Hunt → Validate → Report → Structured output → Independent verification); `findings.json` validates against schema (`validate-findings.cjs`); `REPORT.md` and `FINDINGS-DETAIL.md` reconciled with `findings.json`; output directory contains all artifacts |
| **mcp-tool-rules** | MCP config read; servers presented and confirmed; tools discovered per server; editor-appropriate files generated (Cursor: `.mdc` rules, Copilot: `.instructions.md`) with parameter tables and example calls; files validated (server names, tables, examples, frontmatter); report delivered |

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
| Install to all editors from one agent | Pollutes unused paths — scope to your editor |
| Edit `agents/` without running install | Global agents stale |
| Add agents to `skills/` bundle | Wrong library — use `AGENT_BUNDLE` in `install_library.sh` |
| Deliver PPTX without `thumbnail` | Violates powerpoint-presentation completion rules |

---

## Quick reference

Full human guide: [README.md](../README.md). Agent catalog: [AGENTS.md](AGENTS.md).
