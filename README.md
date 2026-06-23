# Architect Library

A **skill library** and **custom agent library** for Cursor and VS Code Copilot. Install once globally; use in any project.

**Skills** handle artifacts (Excalidraw, Word, PowerPoint, spreadsheets, PDFs) and architecture workflows (API design, deprecation/migration). **Custom agents** handle focused readonly tasks such as [code review](docs/CODE-REVIEW-AGENT.md) and [security audit](docs/SECURITY-AUDITOR-AGENT.md).

Compatible with [Cursor](https://cursor.com), [VS Code + GitHub Copilot](https://code.visualstudio.com/docs/copilot/customization/agent-skills), [Claude Code](https://docs.anthropic.com/en/docs/claude-code), and OpenCode.

**For coding agents:**

- Working **in this repo**: [`.cursor/rules/`](.cursor/rules/) (maintainer rules, not installed globally) and [docs/MAINTAINING-SKILLS.md](docs/MAINTAINING-SKILLS.md).
- **Installing** the full ready-to-use library: [docs/AGENT-SKILL-INSTALL.md](docs/AGENT-SKILL-INSTALL.md) — runtime dependencies + `bash scripts/install_library.sh all cursor` or `all copilot` (editor-scoped default).

**Full install means instructions + runtimes:** When an agent handles **install library**, it should install the runtime dependencies first, then copy skills and agents for the active editor. Manual installs should follow the same order below.

## First-time preparation (one-time per machine)

Run these steps **once** on each computer (or CI image) where you want rendering, Office XML tools, or offline Excalidraw. You do not repeat them for every project—only copy the skill folders per project or globally ([Installation](#installation)).

### Prerequisites

| Requirement | Needed for |
|-------------|------------|
| Python 3.11+ | Excalidraw renderer, Office toolkit (`uv` installs deps) |
| [uv](https://docs.astral.sh/uv/) | Installed automatically by `install_deps.sh` if missing |
| Node.js + npm | `bash scripts/install_deps.sh node` (or included in `install_deps.sh` `all`); offline Excalidraw vendor uses same npm bootstrap pattern |
| python-docx | Included in `bash scripts/install_deps.sh office` — Word fallback when npm/`docx` unavailable |
| sudo (Linux only) | Optional OS libraries for headless Chromium (`install_deps.sh`) and LibreOffice/Poppler (`office-system`) |
| LibreOffice + Poppler | **Optional** for Word-only / XML tooling; **required for every PowerPoint delivery** (mandatory layout preview). Also needed for DOCX/PPTX→PDF and `accept` tracked changes. Install once: `bash scripts/install_deps.sh office-system` |

**Artifact capability without npm:** Word new DOCX → python-docx; PowerPoint new deck → **not supported** (template/XML edit only). Run `bash scripts/runtime_readiness.sh` after install to see status.

### All-in-one (recommended)

From the repository root (after `git clone`):

```bash
cd architect-library   # or your clone path
bash scripts/install_deps.sh              # Excalidraw + Office + PDF + Node/npm (docx, pptxgenjs)
bash scripts/install_deps.sh office-system   # add LibreOffice Impress + Poppler (PPT layout preview, XLSX recalc, accept changes)
bash scripts/install_library.sh all cursor   # or: all copilot — skills + agents for your editor
```

**Is LibreOffice mandatory?** Not for creating `.docx` or building `.pptx` source (Node/python). **Yes for completing PowerPoint skill work**—every deck must go through layout preview (`thumbnail`), which needs LibreOffice Impress + Poppler. Word-only tasks can skip `office-system`. Install: `bash scripts/install_deps.sh office-system`.

Install only one runtime:

```bash
bash scripts/install_deps.sh excalidraw
bash scripts/install_deps.sh office
bash scripts/install_deps.sh office-system
bash scripts/install_deps.sh pdf              # pypdf, pdfplumber, reportlab (pdf-document skill)
```

### Excalidraw renderer (first-time)

Playwright + Chromium let the agent render `.excalidraw` files to PNG for visual QA. Included in `bash scripts/install_deps.sh`; to run alone:

```bash
cd skills/excalidraw-diagram/references
bash install_deps.sh
```

Manual equivalent:

```bash
cd skills/excalidraw-diagram/references
uv sync
uv run python -m playwright install chromium
```

**Online (default):** each render can load Excalidraw from `esm.sh` (network required).

**Offline / firewalled (first-time, requires Node.js):** build a local bundle once:

```bash
bash scripts/vendor_excalidraw.sh
```

Details: [`skills/excalidraw-diagram/README.md`](skills/excalidraw-diagram/README.md) → **Offline rendering**.

### Node.js (new DOCX / new PPTX decks)

Included in `bash scripts/install_deps.sh` (target `all` or `node`). Installs global `docx` and `pptxgenjs` under `$HOME/.npm-global` when Node is available.

```bash
bash scripts/install_deps.sh node   # re-run Node step only
bash scripts/runtime_readiness.sh   # summary: Node, npm globals, python-docx
source scripts/architect_env.sh     # manual agent shell: PATH + NODE_PATH for docx/pptxgenjs
```

`install_node.sh` writes `~/.config/architect-library/env.sh` and adds a hook to `~/.bashrc` so new login shells pick up `~/.npm-global/bin` and `NODE_PATH` automatically.

**Without npm:** Word → `bash scripts/install_deps.sh office` (python-docx). PowerPoint → edit/populate templates only; no greenfield deck.

Optional for PPTX icon workflows (see [`skills/powerpoint-presentation/README.md`](skills/powerpoint-presentation/README.md)):

```bash
npm install -g react-icons react react-dom sharp
```

### PDF tools (first-time)

For the `pdf-document` skill (included in `bash scripts/install_deps.sh all`):

```bash
bash scripts/install_deps.sh pdf
```

### Office tools (first-time)

Shared by Word, PowerPoint, and spreadsheet skills. Included in `bash scripts/install_deps.sh`; to run alone:

```bash
cd skills/_shared/office-tools
bash install_deps.sh
bash install_deps.sh --with-system   # LibreOffice + Poppler when needed
```

Verify:

```bash
cd skills/_shared/office-tools
uv run python3 office_tools.py --help
```

---

## Quick start (every project)

After [first-time preparation](#first-time-preparation-one-time-per-machine) (skip if you only need agent instructions with no PNG/Office tooling):

1. **Clone** (if you have not already)

   ```bash
   git clone https://github.com/lqdflying/architect-library.git
   cd architect-library
   ```

2. **Install library globally** — skills and custom agents (pick your editor):

   ```bash
   bash scripts/install_library.sh all cursor    # Cursor
   bash scripts/install_library.sh all copilot   # VS Code Copilot
   ```

   AI agents working in this repo: see [`AGENTS.md`](AGENTS.md). Full procedure: [`docs/AGENT-SKILL-INSTALL.md`](docs/AGENT-SKILL-INSTALL.md).

3. **Ask your agent** (skills load from their descriptions—no slash command required):

   > Create an Excalidraw diagram of our payment authorization flow.

See [Installation](#installation) for Copilot / Claude Code paths, or [docs/AGENT-SKILL-INSTALL.md](docs/AGENT-SKILL-INSTALL.md) for the full agent install procedure.

## Skills

| Skill | Use when |
|-------|----------|
| `excalidraw-diagram` | Create Excalidraw architecture diagrams, workflows, system maps, and concept visuals. |
| `word-document` | Create or edit DOCX architecture documents, HLDs, LLDs, ADRs, design docs, requirements, comments, and tracked changes. |
| `powerpoint-presentation` | Create or edit PPTX decks; **every delivery requires layout preview** (slide images via LibreOffice + Poppler). |
| `spreadsheet-document` | Create or edit `.xlsx`; formula recalc via `office_tools.py recalc` (LibreOffice). |
| `pdf-document` | Read, create, merge, split, and fill PDFs. |
| `verification-before-completion` | Fresh verification evidence before any completion or delivery claim. |
| `api-and-interface-design` | Design stable APIs and module boundaries — contract-first, error semantics, pagination, Hyrum's Law. |
| `deprecation-and-migration` | Deprecate and migrate systems safely — strangler pattern, migration guides, zero-usage removal. |
| `terraform-commit-review` | Review Terraform IaC changes across a git commit range — correctness, security/RBAC, destructive changes, naming, cross-phase consistency. |
| `_shared` | Shared principles and Office tooling for Word, PowerPoint, and spreadsheet skills. **Must** be a sibling of those skills. |

## Custom agents

| Agent | Use when |
|-------|----------|
| `code-review` | Read-only review of PRs, diffs, or modules; five-axis review; MCP and web verification. Cursor: `/code-review`. Copilot: agents dropdown. |
| `security-auditor` | Read-only security review — STRIDE, OWASP, LLM security, CVE checks. Cursor: `/security-auditor`. Copilot: agents dropdown. |

Catalog: [`docs/AGENTS.md`](docs/AGENTS.md). Deep dive: [`docs/CODE-REVIEW-AGENT.md`](docs/CODE-REVIEW-AGENT.md), [`docs/SECURITY-AUDITOR-AGENT.md`](docs/SECURITY-AUDITOR-AGENT.md).

## Documentation map

| Read this | When you need |
|-----------|----------------|
| [`AGENTS.md`](AGENTS.md) | **Agent (Cursor + Copilot):** install library contract, editor scope, anti-patterns |
| [`.cursor/`](.cursor/) | **Agent:** Cursor project rules and config (tracked in git) |
| [`docs/MAINTAINING-SKILLS.md`](docs/MAINTAINING-SKILLS.md) | **Maintainer/agent:** checklist when adding skills, steps, or dependencies |
| [`tmp/README.md`](tmp/README.md) | **Maintainer:** staging area for external ref skills/agents before absorption |
| [`.cursor/skills/absorb-reference-materials/SKILL.md`](.cursor/skills/absorb-reference-materials/SKILL.md) | **Maintainer:** triage `tmp/` ref material — ship, harden, or ignore (not in global install) |
| [`.cursor/skills/absorb-reference-materials/references/readme-after-absorb.md`](.cursor/skills/absorb-reference-materials/references/readme-after-absorb.md) | **Maintainer:** README audit checklist after each absorb session |
| [`docs/AGENT-SKILL-INSTALL.md`](docs/AGENT-SKILL-INSTALL.md) | **Agent:** install or refresh skills + custom agents (global) |
| [`docs/AGENTS.md`](docs/AGENTS.md) | Custom agent catalog |
| [`docs/CODE-REVIEW-AGENT.md`](docs/CODE-REVIEW-AGENT.md) | code-review agent usage |
| [`docs/SECURITY-AUDITOR-AGENT.md`](docs/SECURITY-AUDITOR-AGENT.md) | security-auditor agent usage |
| [`skills/api-and-interface-design/SKILL.md`](skills/api-and-interface-design/SKILL.md) | API and interface design workflow |
| [`skills/deprecation-and-migration/SKILL.md`](skills/deprecation-and-migration/SKILL.md) | Deprecation and migration workflow |
| [`skills/terraform-commit-review/SKILL.md`](skills/terraform-commit-review/SKILL.md) | Terraform commit-range review workflow |
| This README → [How to use](#how-to-use) | Using installed skills in Cursor, Copilot, or Claude Code chat |
| [`skills/excalidraw-diagram/SKILL.md`](skills/excalidraw-diagram/SKILL.md) | Diagram design rules and agent workflow |
| [`skills/excalidraw-diagram/README.md`](skills/excalidraw-diagram/README.md) | Render setup, offline bundle, PNG validation |
| [`skills/word-document/SKILL.md`](skills/word-document/SKILL.md) | DOCX agent workflow (new vs edit, comments, redlines) |
| [`skills/word-document/README.md`](skills/word-document/README.md) | Word skill setup and pointers |
| [`skills/word-document/references/docx-guide.md`](skills/word-document/references/docx-guide.md) | docx-js and XML editing patterns (explicit table theming) |
| [`skills/word-document/references/production-lessons.md`](skills/word-document/references/production-lessons.md) | Real-delivery lessons: one table style path, parallel tables, TOC, Word verify |
| [`skills/word-document/references/python-docx-patterns.md`](skills/word-document/references/python-docx-patterns.md) | python-docx: built-in `Medium Shading 1 Accent 1` + tblHeader, or explicit fills |
| [`skills/powerpoint-presentation/SKILL.md`](skills/powerpoint-presentation/SKILL.md) | PPTX agent workflow |
| [`skills/powerpoint-presentation/README.md`](skills/powerpoint-presentation/README.md) | PPT setup (including optional icon packages) |
| [`skills/powerpoint-presentation/references/pptx-guide.md`](skills/powerpoint-presentation/references/pptx-guide.md) | pptxgenjs and template editing |
| [`skills/powerpoint-presentation/references/layout-preview.md`](skills/powerpoint-presentation/references/layout-preview.md) | PPTX layout preview images (grid + per-slide JPEGs) |
| [`skills/spreadsheet-document/SKILL.md`](skills/spreadsheet-document/SKILL.md) | XLSX workflow and recalc |
| [`skills/pdf-document/SKILL.md`](skills/pdf-document/SKILL.md) | PDF workflows and form fill |
| [`skills/_shared/architecture-document-principles.md`](skills/_shared/architecture-document-principles.md) | Shared structure for architecture docs and decks |
| [`skills/_shared/office-tools/README.md`](skills/_shared/office-tools/README.md) | Full `office_tools.py` command reference and validation checks |

## Repository layout

```text
architect-library/
  README.md
  AGENTS.md                   # cross-editor agent guide (install library, scope law)
  tmp/                        # maintainer staging — external ref before absorption (see tmp/README.md)
  .cursor/
    rules/                    # maintainer rules (not installed globally)
    skills/
      absorb-reference-materials/   # maintainer skill — triage tmp/ ref (not in SKILL_BUNDLE)
  agents/                     # custom agent library (source)
    code-review/
    security-auditor/
  docs/
    AGENT-SKILL-INSTALL.md
    AGENTS.md
  scripts/
    install_library.sh        # skills + agents → global Cursor / Copilot
    install_deps.sh           # all | excalidraw | office | office-system | pdf
    vendor_excalidraw.sh
    vendor_excalidraw/
  skills/                     # skill library (source)
    excalidraw-diagram/
      SKILL.md
      README.md
      references/
        install_deps.sh
        render_excalidraw.py
        render_template.html
        vendor/                 # generated: excalidraw.bundle.mjs (gitignored, ~19MB)
    word-document/
      SKILL.md
      README.md
      references/docx-guide.md
    powerpoint-presentation/
      SKILL.md
      README.md
      references/pptx-guide.md
    spreadsheet-document/
      SKILL.md
      references/xlsx-guide.md
    pdf-document/
      SKILL.md
      references/pdf-guide.md
      scripts/
    verification-before-completion/
      SKILL.md
      README.md
    api-and-interface-design/
      SKILL.md
      README.md
    deprecation-and-migration/
      SKILL.md
      README.md
    terraform-commit-review/
      SKILL.md
      README.md
    _shared/
      architecture-document-principles.md
      office-tools/
        office_tools.py
        README.md
        install_deps.sh
```

## Installation

Clone the repository:

```bash
git clone git@github.com:lqdflying/architect-library.git
```

If you prefer HTTPS:

```bash
git clone https://github.com/lqdflying/architect-library.git
```

### Install library (recommended)

From the repo root — installs **runtime dependencies, skills, and custom agents** globally for **your editor**:

```bash
cd /path/to/architect-library
bash scripts/install_deps.sh
bash scripts/install_deps.sh office-system
bash scripts/install_library.sh all cursor    # Cursor
bash scripts/install_library.sh all copilot   # VS Code Copilot
bash scripts/install_library.sh all claude    # Claude Code
```

Install all editors at once (only if you use more than one):

```bash
bash scripts/install_library.sh
```

Partial installs (still editor-scoped):

```bash
bash scripts/install_library.sh skills cursor    # skills only, Cursor
bash scripts/install_library.sh agents copilot   # agents only, Copilot
bash scripts/install_library.sh all cursor project   # per-project copy
```

**Global targets:**

| Library | Cursor | Copilot | Claude Code |
|---------|--------|---------|-------------|
| Skills | `~/.cursor/skills/<name>/` | `~/.copilot/skills/<name>/` | `~/.claude/skills/<name>/` |
| Agents | `~/.cursor/agents/<name>.md` | `~/.copilot/agents/<name>.agent.md` | `~/.claude/agents/<name>.md` |

Reload Cursor, VS Code, or Claude Code after installation. Skills appear as slash commands (`/word-document`, etc.). Custom agents appear in the agent picker (`code-review`, `security-auditor`, `/code-review` on Cursor).

See [`docs/AGENT-SKILL-INSTALL.md`](docs/AGENT-SKILL-INSTALL.md) for verification steps and common mistakes.

## Office workflows (manual)

Render a diagram to PNG (after first-time Excalidraw setup):

```bash
cd skills/excalidraw-diagram/references
uv run python render_excalidraw.py path/to/diagram.excalidraw
```

From `skills/_shared/office-tools` (or use paths from an installed skill folder—see each `SKILL.md`):

```bash
# Edit existing DOCX
uv run python3 office_tools.py unpack input.docx unpacked/
# … edit XML under unpacked/word/ …
uv run python3 office_tools.py pack unpacked/ output.docx --original input.docx

# Validate only
uv run python3 office_tools.py validate output.docx --auto-repair

# PPTX template QA
uv run python3 office_tools.py analyze template.pptx
uv run python3 office_tools.py thumbnail deck.pptx /tmp/preview --cols 4
uv run python3 office_tools.py thumbnail deck.pptx /tmp/preview --per-slide /tmp/slides --dpi 150 --no-grid
```

Full command list: [`skills/_shared/office-tools/README.md`](skills/_shared/office-tools/README.md).

## How to use

Skills are **instructions for the coding agent**, not apps you launch yourself. This section assumes skills are [already installed](#installation). Not installed yet? See [Quick start](#quick-start-every-project) or [`docs/AGENT-SKILL-INSTALL.md`](docs/AGENT-SKILL-INSTALL.md).

| Skill folder | You get |
|--------------|---------|
| `excalidraw-diagram` | `.excalidraw` JSON + optional PNG visual check |
| `word-document` | `.docx` architecture documents (new or edited) |
| `powerpoint-presentation` | `.pptx` decks (new or edited) |
| `_shared` | Not invoked directly — support files for Word/PPT tooling |

Runtime setup ([first-time preparation](#first-time-preparation-one-time-per-machine)) is optional until you need PNG rendering, Office XML tools, or Node-based **new** DOCX/PPTX generation.

### Cursor

1. **Reload Cursor** — **Developer: Reload Window**, or quit and reopen Cursor, so it picks up any skill changes.
2. **New Agent chat** — start a fresh chat in **Agent** mode (do not continue an old thread opened before install).
3. **Run a slash command** — in the chat input, type `/` and pick the skill (clearest way to select which skill runs):

   | Slash command | Skill | Typical use |
   |---------------|-------|-------------|
   | `/excalidraw-diagram` | Excalidraw | Diagrams, workflows, system maps |
   | `/word-document` | Word | HLD, LLD, ADR, DOCX edit/validate |
   | `/powerpoint-presentation` | PowerPoint | Executive decks, migration/roadmap slides |

   `_shared` has no slash command — it is loaded automatically when Word or PowerPoint skills need Office tools.

4. **Add your request on the same line or next message** — for example:

   ```text
   /excalidraw-diagram Create a diagram of the payment authorization flow.
   ```

   ```text
   /word-document Create an HLD with risks, assumptions, and decision records.
   ```

5. **Attach files when needed** — for existing `.docx` / `.pptx`, @-mention or attach the file, then use the matching slash command:

   ```text
   /word-document Add review comments on the risks section in the attached DOCX.
   ```

   You can also skip the slash command and ask in plain language; Cursor may still auto-select a skill from the `description` in each `SKILL.md`, but slash commands are more explicit.

```text
Reload Cursor → new Agent chat → /skill-name + your task
       ↓
Agent follows that skill’s SKILL.md + references/
       ↓
Deliverable: .excalidraw / .docx / .pptx
```

### VS Code GitHub Copilot

Requires [GitHub Copilot](https://github.com/features/copilot) and [Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills) support in VS Code. Skills must already be under `~/.copilot/skills/` (global) or `.github/skills/` (workspace)—see [Installation → VS Code GitHub Copilot](#vs-code-github-copilot).

1. **Reload VS Code** — Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) → **Developer: Reload Window** (do this after every skill install or update).

2. **Open Copilot Chat** — open the **Chat** view (Copilot icon in the Activity Bar, or **GitHub Copilot: Open Chat** from the Command Palette). Use **Agent** mode when your VS Code build offers it (skills apply to agent-style requests).

3. **Slash command usage** — in the chat input, type `/`. VS Code shows available commands, including skills from installed `SKILL.md` files:

   | Slash command | Skill | Typical use |
   |---------------|-------|-------------|
   | `/excalidraw-diagram` | Excalidraw | Diagrams, workflows, system maps |
   | `/word-document` | Word | HLD, LLD, ADR, DOCX edit/validate |
   | `/powerpoint-presentation` | PowerPoint | Executive decks, migration/roadmap slides |

   Pick one command, then add your task on the **same message** (recommended):

   ```text
   /excalidraw-diagram Create a diagram of the payment authorization flow.
   ```

   ```text
   /word-document Create an HLD with risks, assumptions, and decision records.
   ```

   ```text
   /powerpoint-presentation Create a 10-slide executive deck for the migration plan.
   ```

   **Tips**

   - If `/excalidraw-diagram` (or others) does not appear, confirm skills are in `~/.copilot/skills/` or `.github/skills/`, reload VS Code, and start a **new** chat.
   - `_shared` has no slash command; Word and PowerPoint skills use it automatically for Office tooling.
   - You can send the slash command first, then your detailed request in a follow-up message—one combined line is usually clearer.

4. **Attach workspace files** — drag a `.docx` or `.pptx` into chat, use **Add context** / **#** file references (wording depends on VS Code version), then run the matching slash command:

   ```text
   /word-document Validate the attached DOCX and list any structural issues.
   ```

   ```text
   /powerpoint-presentation Analyze placeholder layout on the attached PPTX.
   ```

5. **Fallback** — describe the task without `/` if you prefer; Copilot may still match a skill by `description` in `SKILL.md`. Slash commands are the clearest way to force the right skill.

```text
Reload VS Code → Copilot Chat (Agent) → /skill-name + your task
       ↓
Copilot follows that skill’s SKILL.md + references/
       ↓
Deliverable: .excalidraw / .docx / .pptx
```

### Claude Code / OpenCode

1. **Start a new session** in the project where `.claude/skills/` is populated (or restart the CLI).
2. **Describe the task** — the agent loads skills from `SKILL.md` descriptions in that folder.

### Example prompts (with slash commands)

Use the same lines in **Cursor** or **VS Code Copilot Chat**:

**Excalidraw**

```text
/excalidraw-diagram Create a diagram showing the target-state payment authorization flow.
```

**Word**

```text
/word-document Create a Word HLD for this event-driven architecture with risks, assumptions, and decision records.
```

```text
/word-document Review the attached DOCX and add comments on the risks section.
```

**PowerPoint**

```text
/powerpoint-presentation Create an executive architecture review deck for the migration plan.
```

```text
/powerpoint-presentation Analyze the attached template’s placeholders and suggest a slide outline.
```

Attach `.docx` or `.pptx` files in chat when the task starts from an existing document.

Deeper workflows live in each skill’s `SKILL.md` (see [Documentation map](#documentation-map)).

## Customization

- Diagram colors: [`skills/excalidraw-diagram/references/color-palette.md`](skills/excalidraw-diagram/references/color-palette.md)
- Architecture writing principles: [`skills/_shared/architecture-document-principles.md`](skills/_shared/architecture-document-principles.md)
- DOCX patterns: [`skills/word-document/references/docx-guide.md`](skills/word-document/references/docx-guide.md)
- PPTX patterns: [`skills/powerpoint-presentation/references/pptx-guide.md`](skills/powerpoint-presentation/references/pptx-guide.md)

## Validation

Smoke checks after [first-time preparation](#first-time-preparation-one-time-per-machine):

```bash
cd skills/_shared/office-tools
uv run python3 office_tools.py --help
uv run python3 office_tools.py validate --help
uv run python3 office_tools.py analyze --help

cd ../../excalidraw-diagram/references
uv run python render_excalidraw.py --help
```

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| `playwright: command not found` during `install_deps.sh` | Use `uv run python -m playwright install chromium` (already what `install_deps.sh` runs after setup). |
| Excalidraw render times out / “Could not load library” | Online: allow `esm.sh`. Offline: run `bash scripts/vendor_excalidraw.sh`, then retry. |
| `process is not defined` after vendoring | Rebuild the bundle: `bash scripts/vendor_excalidraw.sh` (includes browser shims). |
| Office commands fail with import errors | Run from `skills/_shared/office-tools` with `uv run python3 office_tools.py …` after `bash install_deps.sh`. |
| `accept` or `thumbnail` fails | Install system deps: `bash scripts/install_deps.sh office-system`. Required before finishing any PowerPoint task. |
| Agent delivered PPTX without layout review | Reload `powerpoint-presentation` skill; agent must run `thumbnail` and view images per `layout-preview.md`. |
| Word/PPT skill can’t find tools | Ensure `_shared` is copied next to `word-document` and `powerpoint-presentation` in your skills folder. |
| Pack skipped redline checks | Pass `--original input.docx` to `pack`; without it, only structural validation runs (a warning is printed). |
