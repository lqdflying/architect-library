# Agent guide: install Architect Library (Cursor / Copilot)

Use this document when the user asks to install, update, or fix **skills** or **custom agents** from the **architect-library** repository. Follow it literally; do not invent alternate paths.

**Editing this repository?** Cursor loads [`.cursor/rules/`](../.cursor/rules/) automatically. Follow [MAINTAINING-SKILLS.md](MAINTAINING-SKILLS.md) whenever you add a skill, agent, workflow step, or dependency.

## User phrases (full install default)

When the user says any of these, run the **full global install** (`bash scripts/install_library.sh` with no args — skills + agents):

- **install library** | install the library | patch library | refresh library | update library
- install skills and agents | sync library | update architect library
- patch | upgrade | install | refresh (skills or agents)

Use **partial** installs (`skills` or `agents` only) **only** when the user explicitly asks.

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
| `_shared` | Support files (not a standalone skill) | **Yes** whenever Word, PowerPoint, or spreadsheet skills are installed |

Word, PowerPoint, and spreadsheet skills reference Office tools via `../_shared/office-tools/`. If `_shared` is missing or not a **sibling** of those folders, paths break.

### Custom agent library (`agents/`)

| Agent | Purpose |
|-------|---------|
| `code-review` | Read-only code review with MCP and web verification |

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

| User intent | Command |
|-------------|---------|
| Global (default) | `bash scripts/install_library.sh` |
| Skills only | `bash scripts/install_library.sh skills` |
| Agents only | `bash scripts/install_library.sh agents` |
| Per project | `bash scripts/install_library.sh all both project` from user's project root |

Prefer **global** unless the user explicitly wants project-local copies.

---

## Step 2: Patch / upgrade (agent default)

When the user says **install library** or any phrase in [User phrases](#user-phrases-full-install-default) — or you changed `skills/` or `agents/` — **run this** from the repo root:

```bash
REPO=/path/to/architect-library
cd "$REPO"
bash scripts/install_library.sh
```

| Action | Result |
|--------|--------|
| **New** skill | Added under `~/.cursor/skills/`, `~/.copilot/skills/` |
| **Existing** skill | Folder replaced (full refresh) |
| **New** agent | Assembled to `~/.cursor/agents/`, `~/.copilot/agents/` |
| **Existing** agent | File replaced |

Repo rule: [`.cursor/rules/architect-library-patch.mdc`](../.cursor/rules/architect-library-patch.mdc).

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

## Step 4: Verify installation

```bash
test -f ~/.cursor/skills/_shared/office-tools/office_tools.py && echo "OK: cursor skills"
test -f ~/.copilot/skills/word-document/SKILL.md && echo "OK: copilot skills"
test -f ~/.cursor/agents/code-review.md && echo "OK: cursor agents"
test -f ~/.copilot/agents/code-review.agent.md && echo "OK: copilot agents"
grep -q 'readonly: true' ~/.cursor/agents/code-review.md && echo "OK: code-review"
find ~/.cursor/skills -maxdepth 2 -name .git -type d   # expect no output
```

The install script runs similar checks automatically.

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

**PowerPoint is not done** when the `.pptx` exists — only after layout preview (or user waives).

## Custom agent execution (agents)

| Agent | Done when |
|-------|-----------|
| **code-review** | Scope set; logic traced; findings with evidence; MCP/web verification table; **no edits** |

See [CODE-REVIEW-AGENT.md](CODE-REVIEW-AGENT.md).

---

## First-time machine setup (separate from library copy)

| Task | Command (from repo root) |
|------|---------------------------|
| Library copy | `bash scripts/install_library.sh` |
| Runtimes | `bash scripts/install_deps.sh` |
| LibreOffice + Poppler (PPT) | `bash scripts/install_deps.sh office-system` |
| Offline Excalidraw | `bash scripts/vendor_excalidraw.sh` |
| New DOCX / PPTX via Node | `npm install -g docx` / `pptxgenjs` |

Do not run `install_deps.sh` inside `~/.cursor/skills/` — run from the **repository clone**.

---

## Common mistakes

| Mistake | Why it fails |
|---------|----------------|
| Copy only one skill folder | Word/PPT break; missing `_shared` |
| Omit `_shared` | `../_shared/office-tools/` paths break |
| Copy repo into `~/.cursor/skills/` | Wrong layout |
| Edit `agents/` without running install | Global agents stale |
| Add agents to `skills/` bundle | Wrong library — use `AGENT_BUNDLE` in `install_library.sh` |
| Deliver PPTX without `thumbnail` | Violates powerpoint-presentation completion rules |

---

## Quick reference

Full human guide: [README.md](../README.md). Agent catalog: [AGENTS.md](AGENTS.md).
