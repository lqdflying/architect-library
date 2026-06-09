# AGENTS.md — architect-library

Cross-editor guide for AI agents working **in this repository** (maintainers editing `skills/`, `agents/`, scripts, docs).

| Doc | Purpose |
|-----|---------|
| **This file** | Shared install contract, editor scope, anti-patterns |
| [docs/AGENT-SKILL-INSTALL.md](docs/AGENT-SKILL-INSTALL.md) | Full install procedure + verification commands |
| [docs/AGENTS.md](docs/AGENTS.md) | **Shipped custom agents catalog** (`code-review`, `security-auditor`) |
| [docs/MAINTAINING-SKILLS.md](docs/MAINTAINING-SKILLS.md) | Maintainer checklist for new skills/agents |

---

## Install library — follow this exactly

**Trigger phrases:** install library, patch library, refresh library, update library, install skills and agents, sync library, update architect library — or after you change `skills/` or `agents/` in this repo.

### 1. Detect editor — do not ask the user

| You are in | Install **only** to |
|------------|---------------------|
| **Cursor** | `~/.cursor/skills/`, `~/.cursor/agents/` |
| **VS Code Copilot** | `~/.copilot/skills/`, `~/.copilot/agents/` |
| **Claude Code** | `~/.claude/skills/`, `~/.claude/agents/` |

**Never** write to other editors’ home paths unless the user explicitly asks for all editors.

### 2. Runtimes (from repo root)

```bash
cd /path/to/architect-library
bash scripts/install_deps.sh
bash scripts/install_deps.sh office-system
npm install -g docx pptxgenjs
```

- `install_deps.sh` installs **Python/uv, Playwright, Office toolkit, PDF** — it does **not** install Node.js.
- If `npm` is missing: **report the error and stop** — do **not** install Node, nvm, or fnm unless the user explicitly asks.
- If `npm install` fails: skills/agents can still be installed; say runtime readiness is **incomplete** (no new docx-js / pptxgenjs generation).

### 3. Copy skills + agents — editor-scoped command

| Editor | Command |
|--------|---------|
| **Cursor** | `bash scripts/install_library.sh all cursor` |
| **VS Code Copilot** | `bash scripts/install_library.sh all copilot` |
| **Claude Code** | `bash scripts/install_library.sh all claude` |
| All editors (explicit user ask only) | `bash scripts/install_library.sh` |

**Do not** run bare `bash scripts/install_library.sh` by default — it uses `EDITOR=both` and installs to Cursor + Copilot + Claude.

Partial installs only when the user explicitly asks (still editor-scoped), e.g. `bash scripts/install_library.sh agents copilot`.

### 4. Tell the user

Reload the editor or open a **new agent chat**. If any runtime step failed, say which command failed — do not claim full readiness.

---

## Do not (common agent mistakes)

| Wrong | Right |
|-------|-------|
| `bash scripts/install_library.sh` with no editor arg | `all cursor` / `all copilot` / `all claude` |
| Install Node/nvm because `npm` failed | Report failure; install library copy anyway if appropriate |
| “`install_deps.sh` bootstraps Node” | Only `scripts/vendor_excalidraw.sh` bootstraps npm for **offline Excalidraw** — optional |
| Copy `skills/` into `repo/.cursor/skills/` | Source is `skills/`; install via `install_library.sh` |
| Ask which editor on “install library” | Infer from the environment you are running in |

---

## Library layout (source of truth)

- **Skills:** `skills/<name>/` → bundled in `SKILL_BUNDLE` in `scripts/install_library.sh`
- **Custom agents:** `agents/<name>/` → `AGENT_BUNDLE`; assembled from `cursor.header.md` / `copilot.header.md` / `claude.header.md` + `INSTRUCTIONS.md`
- **End-user skills/agents** live in the user’s home directory after install — not in this repo’s `.cursor/skills/` (except maintainer-only `.cursor/skills/absorb-reference-materials/`)

---

## Execution (installed library)

Artifact skills and custom agents have **done-when** rules in [docs/AGENT-SKILL-INSTALL.md](docs/AGENT-SKILL-INSTALL.md). PowerPoint deliveries require layout preview; artifact delivery claims require `verification-before-completion`.
