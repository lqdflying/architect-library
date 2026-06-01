# Excalidraw Diagram Skill

A coding agent skill that generates beautiful and practical Excalidraw diagrams from natural language descriptions. Not just boxes-and-arrows - diagrams that **argue visually**.

Compatible with [Cursor](https://cursor.com), [VS Code + GitHub Copilot](https://code.visualstudio.com/docs/copilot/customization/agent-skills), [Claude Code](https://docs.anthropic.com/en/docs/claude-code), and OpenCode. Pick the install path for your editor below.

## What Makes This Different

- **Diagrams that argue, not display.** Every shape/group of shapes mirrors the concept it represents — fan-outs for one-to-many, timelines for sequences, convergence for aggregation. No uniform card grids.
- **Evidence artifacts.** As an example, technical diagrams include real code snippets and actual JSON payloads.
- **Built-in visual validation.** A Playwright-based render pipeline lets the agent see its own output, catch layout issues (overlapping text, misaligned arrows, unbalanced spacing), and fix them in a loop before delivering.
- **Brand-customizable.** All colors and brand styles live in a single file (`references/color-palette.md`). Swap it out and every diagram follows your palette.

## Installation

### Cursor

Cursor loads skills from a folder containing `SKILL.md` (with YAML frontmatter). Install **globally** (all projects on this machine) or **per project** (committed with your repo).

**Global install (recommended):**

```bash
git clone https://github.com/coleam00/excalidraw-diagram-skill.git
mkdir -p ~/.cursor/skills
cp -r excalidraw-diagram-skill ~/.cursor/skills/excalidraw-diagram
```

**Per-project install:**

```bash
git clone https://github.com/coleam00/excalidraw-diagram-skill.git
mkdir -p .cursor/skills
cp -r excalidraw-diagram-skill .cursor/skills/excalidraw-diagram
```

**Using the skill:** Open any project in Cursor and ask for a diagram in chat, for example:

> Create an Excalidraw diagram of our authentication flow.

The agent picks up the skill from its `description` in `SKILL.md` — no mode picker required. Relative paths like `references/color-palette.md` work as-is; do **not** copy `~/.cursor/skills-cursor/` (that directory is reserved for Cursor built-in skills).

| Scope | Skill location |
|-------|----------------|
| Global (all projects) | `~/.cursor/skills/excalidraw-diagram/` |
| Single project | `.cursor/skills/excalidraw-diagram/` |

**Live updates from a dev checkout:** If you are editing this repo locally, symlink instead of copy so changes apply immediately:

```bash
ln -sf /path/to/excalidraw-diagram-skill ~/.cursor/skills/excalidraw-diagram
```

### VS Code (GitHub Copilot Agent Skill)

VS Code uses [Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills) — folders with a `SKILL.md` file that define reusable capabilities. Skills resolve relative paths from the `SKILL.md` location, so no path rewriting is needed. Install **globally** (all workspaces) or **per-workspace**.

**Global install (recommended):**

```bash
git clone https://github.com/coleam00/excalidraw-diagram-skill.git
mkdir -p ~/.copilot/skills/excalidraw-diagram
cp excalidraw-diagram-skill/SKILL.md ~/.copilot/skills/excalidraw-diagram/
cp -r excalidraw-diagram-skill/references ~/.copilot/skills/excalidraw-diagram/
```

**Per-workspace install** (run from your project root):

```bash
git clone https://github.com/coleam00/excalidraw-diagram-skill.git
mkdir -p .github/skills
cp -r excalidraw-diagram-skill .github/skills/excalidraw-diagram
```

Note: The skill directory name must match the `name` field in `SKILL.md` frontmatter (`excalidraw-diagram`).

**Using the skill:** After installation, reload VS Code (`Ctrl+Shift+P` → "Developer: Reload Window"). The skill is available as:
- A **slash command**: type `/excalidraw-diagram` in chat
- **Automatically loaded** when the agent detects a relevant request (e.g., "create a diagram")

| Scope | Skill location |
|-------|----------------|
| Global (all workspaces) | `~/.copilot/skills/excalidraw-diagram/` |
| Workspace | `.github/skills/excalidraw-diagram/` |

### Claude Code / OpenCode

Clone or download this repo, then copy it into your project's `.claude/skills/` directory:

```bash
git clone https://github.com/coleam00/excalidraw-diagram-skill.git
cp -r excalidraw-diagram-skill .claude/skills/excalidraw-diagram
```

## Setup

The skill includes a render pipeline that lets the agent visually validate its diagrams. There are two ways to set it up:

**Option A: Ask your coding agent (easiest)**

Just tell your agent: *"Set up the Excalidraw diagram skill renderer."* It will run the install script for you.

**Option B: Manual**

Run the install script from your `references` folder (pick the path that matches your install):

```bash
# Cursor (global):
cd ~/.cursor/skills/excalidraw-diagram/references
bash install_deps.sh

# Cursor (project):
cd .cursor/skills/excalidraw-diagram/references
bash install_deps.sh

# VS Code Copilot (global):
cd ~/.copilot/skills/excalidraw-diagram/references
bash install_deps.sh

# VS Code Copilot (workspace):
cd .github/skills/excalidraw-diagram/references
bash install_deps.sh

# Claude Code / OpenCode:
cd .claude/skills/excalidraw-diagram/references
bash install_deps.sh
```

Or manually install just the Python deps:

```bash
cd <path-to-references>
uv sync
uv run playwright install chromium
```

### System prerequisites

The render pipeline requires:
- **Python >= 3.11** (uv will auto-download one if your system Python is older)
- **[uv](https://docs.astral.sh/uv/)** — Python package manager
- **curl** — for installing uv and optional offline vendoring
- **System libraries** for headless Chromium (atk, nss, pango, etc.)

**The included helper script installs everything in one step** (uv + system libs + Python deps + Chromium):
```bash
cd <path-to-references>   # see paths in Option B above
bash install_deps.sh
```

Or install manually:

**uv** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Chromium system libraries — Debian / Ubuntu:**
```bash
sudo apt-get install -y libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1 \
  libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 libasound2 libnss3
```

**Chromium system libraries — RHEL / Oracle Linux / Rocky / Alma (dnf):**
```bash
sudo dnf install -y atk at-spi2-atk cups-libs libXcomposite libXdamage \
  libXrandr mesa-libgbm pango alsa-lib nss
```

**Then install Python deps and Chromium:**
```bash
cd <path-to-references>
uv sync
uv run playwright install chromium
```

If you're on a desktop Linux with a browser already installed, the system libraries are almost certainly present and you can skip that step.

### Network requirements

The render pipeline reaches the network in two places:

- **Setup:** `playwright install chromium` downloads the headless browser from `cdn.playwright.dev`.
- **Render time:** the browser loads the Excalidraw library (pinned to `0.17.6`) from `esm.sh` each time it renders.

In offline, proxied, or firewalled environments these hosts may be blocked. If `esm.sh` is unreachable, the renderer prints a clear error instead of hanging.

### Optional: vendor Excalidraw for offline rendering

To render without hitting `esm.sh` on every run, download the pinned library once into a local `vendor/` folder. The renderer prefers this local copy and falls back to the CDN only if it's missing:

```bash
cd <path-to-references>
mkdir -p vendor
curl -L "https://esm.sh/@excalidraw/excalidraw@0.17.6?bundle" -o vendor/excalidraw.js
```

`vendor/` is gitignored, so it stays local to your checkout.

## Usage

Ask your coding agent to create a diagram:

> "Create an Excalidraw diagram showing how the AG-UI protocol streams events from an AI agent to a frontend UI"

The skill handles the rest — concept mapping, layout, JSON generation, rendering, and visual validation.

## Customize Colors

Edit `references/color-palette.md` to match your brand. Everything else in the skill is universal design methodology.

## File Structure

```
excalidraw-diagram/
  SKILL.md                          # Design methodology + workflow
  references/
    color-palette.md                # Brand colors (edit this to customize)
    element-templates.md            # JSON templates for each element type
    json-schema.md                  # Excalidraw JSON format reference
    install_deps.sh                 # Install system libs for headless Chromium
    render_excalidraw.py            # Render .excalidraw to PNG
    render_template.html            # Browser template for rendering
    pyproject.toml                  # Python dependencies (playwright)
```
