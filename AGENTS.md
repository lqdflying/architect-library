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
bash scripts/install_deps.sh              # Python, Excalidraw, Office, PDF, Node attempt
bash scripts/install_deps.sh office-system
```

- `install_deps.sh` (target `all`) runs **`install_node.sh`**: finds Node (PATH, Cursor-server bundle, or `sudo dnf`/`apt`), bootstraps npm if needed, installs global `docx` and `pptxgenjs` under `$HOME/.npm-global`.
- **`install_node.sh` writes** `~/.config/architect-library/env.sh` (idempotent PATH/`NODE_PATH`, optional `NODE_BIN`) and a bootstrapped **`npm` shim** at `~/.npm-global/bin/npm` when system npm is missing. Adds a guarded hook to `~/.bashrc` / `~/.profile`. **`install_deps.sh`**, **`install_library.sh`**, and **`runtime_readiness.sh`** source `scripts/architect_env.sh` automatically — no manual `export` needed inside those scripts.
- Before **manual** Node/docx-js/pptxgenjs work in an agent shell (outside install scripts): `source /path/to/architect-library/scripts/architect_env.sh`
- Re-run only Node step: `bash scripts/install_deps.sh node`
- If Node still unavailable after the script tries: **do not** improvisationally install nvm/fnm unless the user asks — report incomplete runtime; still run `install_library.sh` (skills/agents work without Node).
- If `npm` global install fails: skills/agents can still be installed; say runtime readiness is **incomplete** for Node-based generation. After install, `bash scripts/runtime_readiness.sh` summarizes what artifact work is still possible.
- **Library installed** ≠ **all artifact runtimes ready**. Skills/agents copy without Node; Word may still deliver via python-docx; new PPT decks need pptxgenjs or a user-supplied template.

### Runtime capability matrix (artifact skills)

| Capability | npm (`docx` / `pptxgenjs`) | Python (`office_tools` + `uv sync`) | Word `python-docx` fallback |
|------------|----------------------------|----------------------------------------|-----------------------------|
| New Word DOCX | docx-js (primary) | — | yes — `bash scripts/install_deps.sh office` |
| New PPT deck from scratch | pptxgenjs only | — | **not in library** |
| Edit template / unpack-pack | + validate | yes | — |
| PPT layout preview (`thumbnail`) | after `.pptx` exists | LibreOffice Impress + Poppler (`office-system`) | same |

**Without npm:** Word → python-docx per `word-document` skill; PowerPoint → template/XML path only (no greenfield deck); layout preview still mandatory when delivering `.pptx`.

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

Reload the editor or open a **new agent chat**. If any runtime step failed, say which command failed — do not claim full readiness. Run `bash scripts/runtime_readiness.sh` when Node/npm failed so the user knows Word (python-docx) vs PPT (template-only) options.

---

## Do not (common agent mistakes)

| Wrong | Right |
|-------|-------|
| `bash scripts/install_library.sh` with no editor arg | `all cursor` / `all copilot` / `all claude` |
| Install nvm/fnm because `npm` failed | Run `bash scripts/install_deps.sh node` first; only install nvm if user asks |
| Run bare `npm install -g` before `install_deps.sh node` | Use `bash scripts/install_deps.sh` or `install_deps.sh node` — it handles Cursor-server Node + npm bootstrap |
| Say pptxgenjs works via python-docx | **Wrong** — PPT new decks need pptxgenjs or template/XML; Word only has python-docx fallback |
| Manual Node without sourcing env | `source scripts/architect_env.sh` so `NODE_PATH` finds `docx` / `pptxgenjs` under `~/.npm-global` |
| Copy `skills/` into `repo/.cursor/skills/` | Source is `skills/`; install via `install_library.sh` |
| Global install over Cursor Remote SSH | Use `bash scripts/install_library.sh all cursor project` in the open remote workspace — global `~/.cursor/skills/` often missing from Customize |
| Ask which editor on “install library” | Infer from the environment you are running in |

---

## Library layout (source of truth)

- **Skills:** `skills/<name>/` → bundled in `SKILL_BUNDLE` in `scripts/install_library.sh`
- **Custom agents:** `agents/<name>/` → `AGENT_BUNDLE`; assembled from `cursor.header.md` / `copilot.header.md` / `claude.header.md` + `INSTRUCTIONS.md`
- **End-user skills/agents** live in the user’s home directory after install — not in this repo’s `.cursor/skills/` (except maintainer-only `.cursor/skills/absorb-reference-materials/`)

---

## Execution (installed library)

Artifact skills and custom agents have **done-when** rules in [docs/AGENT-SKILL-INSTALL.md](docs/AGENT-SKILL-INSTALL.md). PowerPoint deliveries require layout preview; artifact delivery claims require `verification-before-completion`.
