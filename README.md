# Excalidraw Diagram Skill

A coding agent skill that generates beautiful and practical Excalidraw diagrams from natural language descriptions. Not just boxes-and-arrows - diagrams that **argue visually**.

Compatible with any coding agent that supports skills. For agents that read from `.claude/skills/` (like [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and OpenCode), just drop it in and go.

## What Makes This Different

- **Diagrams that argue, not display.** Every shape/group of shapes mirrors the concept it represents — fan-outs for one-to-many, timelines for sequences, convergence for aggregation. No uniform card grids.
- **Evidence artifacts.** As an example, technical diagrams include real code snippets and actual JSON payloads.
- **Built-in visual validation.** A Playwright-based render pipeline lets the agent see its own output, catch layout issues (overlapping text, misaligned arrows, unbalanced spacing), and fix them in a loop before delivering.
- **Brand-customizable.** All colors and brand styles live in a single file (`references/color-palette.md`). Swap it out and every diagram follows your palette.

## Installation

Clone or download this repo, then copy it into your project's `.claude/skills/` directory:

```bash
git clone https://github.com/coleam00/excalidraw-diagram-skill.git
cp -r excalidraw-diagram-skill .claude/skills/excalidraw-diagram
```

## Setup

The skill includes a render pipeline that lets the agent visually validate its diagrams. There are two ways to set it up:

**Option A: Ask your coding agent (easiest)**

Just tell your agent: *"Set up the Excalidraw diagram skill renderer by following the instructions in SKILL.md."* It will run the commands for you.

**Option B: Manual**

```bash
cd .claude/skills/excalidraw-diagram/references
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
cd .claude/skills/excalidraw-diagram/references
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
cd .claude/skills/excalidraw-diagram/references
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
cd .claude/skills/excalidraw-diagram/references
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
