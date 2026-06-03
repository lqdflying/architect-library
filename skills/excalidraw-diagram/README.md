# Excalidraw Diagram Skill

Create Excalidraw architecture diagrams that argue visually instead of merely displaying boxes and arrows.

## Use When

- The user asks for an Excalidraw file or architecture diagram.
- A Word document or PowerPoint deck needs a supporting system diagram.
- A workflow, dependency, decision, sequence, or concept needs a visual explanation.

## Setup

From this skill folder:

```bash
cd references
bash install_deps.sh
```

`install_deps.sh` installs uv (if needed), Python dependencies via `uv sync`, and Chromium for Playwright. On Linux it may use sudo only to install OS libraries required by headless Chromium.

Manual setup (equivalent):

```bash
cd references
uv sync
uv run python -m playwright install chromium
```

## Offline rendering

By default each render loads `@excalidraw/excalidraw@0.17.6` from `esm.sh`, which requires network access at render time.

For offline or firewalled environments, build a self-contained vendor bundle once:

```bash
# From repository root
bash scripts/vendor_excalidraw.sh
```

This writes `references/vendor/excalidraw.bundle.mjs`, which `render_template.html` loads before falling back to the CDN.

The render script serves `references/` over loopback HTTP so the bundle can be imported (browsers block `import()` from `file://` URLs). When the bundle is present, external CDN requests are not used.

Re-run the script when upgrading the pinned Excalidraw version in `scripts/vendor_excalidraw.sh`.

## Render

```bash
cd references
uv run python render_excalidraw.py <path-to-file.excalidraw>
```

The renderer writes a PNG next to the `.excalidraw` file. Inspect the PNG and iterate until the diagram is readable, balanced, and accurate.

## Key References

- `SKILL.md` - design methodology and workflow
- `references/color-palette.md` - single source of truth for colors
- `references/element-templates.md` - reusable Excalidraw JSON templates
- `references/json-schema.md` - Excalidraw file format reference
