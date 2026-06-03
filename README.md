# Architect Document Skills

A multi-skill repository for creating architecture artifacts with coding agents. The skill set covers visual architecture diagrams, Word architecture documents, and PowerPoint architecture presentations.

The original Excalidraw diagram skill is preserved under `skills/excalidraw-diagram/`. Word and PowerPoint skills have been added around the Office draft guides and shared DOCX/PPTX tooling.

Compatible with [Cursor](https://cursor.com), [VS Code + GitHub Copilot](https://code.visualstudio.com/docs/copilot/customization/agent-skills), [Claude Code](https://docs.anthropic.com/en/docs/claude-code), and OpenCode.

**For coding agents:**

- Working **in this repo**: [`.cursor/`](.cursor/) (project Cursor config and rules, tracked in git) and [docs/MAINTAINING-SKILLS.md](docs/MAINTAINING-SKILLS.md) (when adding skills, steps, or deps—update rules + docs, not only README/scripts).
- **Installing** skills in Cursor/Copilot: [docs/AGENT-SKILL-INSTALL.md](docs/AGENT-SKILL-INSTALL.md) (four folders, `_shared` sibling, execution rules for Excalidraw PNG review, Word tables, **mandatory PPT layout preview**).

**Instructions vs runtime:** Skill `SKILL.md` files load as soon as they are copied into your editor. **Completing** a task still needs runtimes: Excalidraw → Playwright; Word (new DOCX) → optional npm `docx`; **PowerPoint → `office-system` (LibreOffice + Poppler) on every deck** for layout preview, plus npm `pptxgenjs` for new decks. See [First-time preparation](#first-time-preparation-one-time-per-machine).

## First-time preparation (one-time per machine)

Run these steps **once** on each computer (or CI image) where you want rendering, Office XML tools, or offline Excalidraw. You do not repeat them for every project—only copy the skill folders per project or globally ([Installation](#installation)).

### Prerequisites

| Requirement | Needed for |
|-------------|------------|
| Python 3.11+ | Excalidraw renderer, Office toolkit (`uv` installs deps) |
| [uv](https://docs.astral.sh/uv/) | Installed automatically by `install_deps.sh` if missing |
| Node.js + npm | `npm install -g docx` / `pptxgenjs`; `scripts/vendor_excalidraw.sh` (bootstraps npm if absent) |
| sudo (Linux only) | Optional OS libraries for headless Chromium (`install_deps.sh`) and LibreOffice/Poppler (`office-system`) |
| LibreOffice + Poppler | **Optional** for Word-only / XML tooling; **required for every PowerPoint delivery** (mandatory layout preview). Also needed for DOCX/PPTX→PDF and `accept` tracked changes. Install once: `bash scripts/install_deps.sh office-system` |

### All-in-one (recommended)

From the repository root (after `git clone`):

```bash
cd architect-doc-skill   # or your clone path
bash scripts/install_deps.sh              # Excalidraw + Office Python deps (no LibreOffice)
bash scripts/install_deps.sh office-system   # add LibreOffice Impress + Poppler (PPT layout preview, PDF, accept changes)
```

**Is LibreOffice mandatory?** Not for creating `.docx` or building `.pptx` source (Node/python). **Yes for completing PowerPoint skill work**—every deck must go through layout preview (`thumbnail`), which needs LibreOffice Impress + Poppler. Word-only tasks can skip `office-system`. Install: `bash scripts/install_deps.sh office-system`.

Install only one runtime:

```bash
bash scripts/install_deps.sh excalidraw
bash scripts/install_deps.sh office
bash scripts/install_deps.sh office-system
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

### Node.js (first-time, for new DOCX / PPTX only)

Not installed by `install_deps.sh`:

```bash
npm install -g docx        # Word — new DOCX via docx-js
npm install -g pptxgenjs   # PowerPoint — new PPTX decks
```

Optional for PPTX icon workflows (see [`skills/powerpoint-presentation/README.md`](skills/powerpoint-presentation/README.md)):

```bash
npm install -g react-icons react react-dom sharp
```

### Office tools (first-time)

Shared by Word and PowerPoint skills. Included in `bash scripts/install_deps.sh`; to run alone:

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
   git clone https://github.com/lqdflying/architect-doc-skill.git
   cd architect-doc-skill
   ```

2. **Install skills into your editor** — **Agents:** read and follow [`docs/AGENT-SKILL-INSTALL.md`](docs/AGENT-SKILL-INSTALL.md) in this repo (do not improvise paths). **Humans (Cursor global example):**

   ```bash
   mkdir -p ~/.cursor/skills
   cp -r skills/excalidraw-diagram ~/.cursor/skills/
   cp -r skills/word-document ~/.cursor/skills/
   cp -r skills/powerpoint-presentation ~/.cursor/skills/
   cp -r skills/_shared ~/.cursor/skills/
   ```

3. **Ask your agent** (skills load from their descriptions—no slash command required):

   > Create an Excalidraw diagram of our payment authorization flow.

See [Installation](#installation) for Copilot / Claude Code paths, or [docs/AGENT-SKILL-INSTALL.md](docs/AGENT-SKILL-INSTALL.md) for the full agent install procedure.

## Skills

| Skill | Use when |
|-------|----------|
| `excalidraw-diagram` | Create Excalidraw architecture diagrams, workflows, system maps, and concept visuals. |
| `word-document` | Create or edit DOCX architecture documents, HLDs, LLDs, ADRs, design docs, requirements, comments, and tracked changes. |
| `powerpoint-presentation` | Create or edit PPTX decks; **every delivery requires layout preview** (slide images via LibreOffice + Poppler). |
| `_shared` | Shared principles and Office tooling used by the Word and PowerPoint skills. **Must** be installed as a sibling of the other skills. |

## Documentation map

| Read this | When you need |
|-----------|----------------|
| [`.cursor/`](.cursor/) | **Agent:** Cursor project rules and config (tracked in git) |
| [`docs/MAINTAINING-SKILLS.md`](docs/MAINTAINING-SKILLS.md) | **Maintainer/agent:** checklist when adding skills, steps, or dependencies |
| [`docs/AGENT-SKILL-INSTALL.md`](docs/AGENT-SKILL-INSTALL.md) | **Agent:** install or refresh skills in Cursor / Copilot / Claude Code |
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
| [`skills/_shared/architecture-document-principles.md`](skills/_shared/architecture-document-principles.md) | Shared structure for architecture docs and decks |
| [`skills/_shared/office-tools/README.md`](skills/_shared/office-tools/README.md) | Full `office_tools.py` command reference and validation checks |

## Repository layout

```text
architect-doc-skill/
  README.md
  docs/
    AGENT-SKILL-INSTALL.md   # agent procedure for Cursor / Copilot install
  scripts/
    install_deps.sh           # all | excalidraw | office | office-system
    vendor_excalidraw.sh      # build offline Excalidraw bundle (Node.js)
    vendor_excalidraw/        # esbuild vendor project (not the bundle itself)
  skills/
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
git clone git@github.com:lqdflying/architect-doc-skill.git
```

If you prefer HTTPS:

```bash
git clone https://github.com/lqdflying/architect-doc-skill.git
```

### VS Code GitHub Copilot

Install globally for all workspaces:

```bash
cd /path/to/architect-doc-skill
mkdir -p ~/.copilot/skills
cp -r skills/excalidraw-diagram ~/.copilot/skills/
cp -r skills/word-document ~/.copilot/skills/
cp -r skills/powerpoint-presentation ~/.copilot/skills/
cp -r skills/_shared ~/.copilot/skills/
```

Install per workspace from your project root:

```bash
mkdir -p .github/skills
cp -r /path/to/architect-doc-skill/skills/excalidraw-diagram .github/skills/
cp -r /path/to/architect-doc-skill/skills/word-document .github/skills/
cp -r /path/to/architect-doc-skill/skills/powerpoint-presentation .github/skills/
cp -r /path/to/architect-doc-skill/skills/_shared .github/skills/
```

Reload VS Code after installation. The skills are available as slash commands such as `/excalidraw-diagram`, `/word-document`, and `/powerpoint-presentation`, and may also load automatically when the request matches their descriptions.

### Cursor

Install globally:

```bash
cd /path/to/architect-doc-skill
mkdir -p ~/.cursor/skills
cp -r skills/excalidraw-diagram ~/.cursor/skills/
cp -r skills/word-document ~/.cursor/skills/
cp -r skills/powerpoint-presentation ~/.cursor/skills/
cp -r skills/_shared ~/.cursor/skills/
```

Install per project:

```bash
mkdir -p .cursor/skills
cp -r /path/to/architect-doc-skill/skills/excalidraw-diagram .cursor/skills/
cp -r /path/to/architect-doc-skill/skills/word-document .cursor/skills/
cp -r /path/to/architect-doc-skill/skills/powerpoint-presentation .cursor/skills/
cp -r /path/to/architect-doc-skill/skills/_shared .cursor/skills/
```

### Claude Code / OpenCode

Install into a project:

```bash
cd /path/to/architect-doc-skill
mkdir -p .claude/skills
cp -r skills/excalidraw-diagram .claude/skills/
cp -r skills/word-document .claude/skills/
cp -r skills/powerpoint-presentation .claude/skills/
cp -r skills/_shared .claude/skills/
```

Keep `_shared` as a sibling of the other skill folders. The Word and PowerPoint skills reference shared Office tools through `../_shared/office-tools/`.

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
