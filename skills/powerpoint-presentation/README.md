# PowerPoint Presentation Skill

Create, edit, and validate Microsoft PowerPoint architecture presentations.

## Use When

- The user asks for a `.pptx` file.
- The artifact is an executive deck, solution overview, technical walkthrough, migration plan, roadmap, or architecture review pack.
- The task requires template analysis, slide duplication, thumbnails, text extraction, or PPTX validation.

## Setup

### Installed skill layout (`~/.cursor/skills/` or `~/.copilot/skills/`)

Office Python toolkit and **mandatory** layout-preview system deps:

```bash
cd ../_shared/office-tools
bash install_deps.sh
bash install_deps.sh --with-system
```

### Repository clone (Node / full runtime install)

From the **architect-library repo root** (not from the installed skill folder):

```bash
cd /path/to/architect-library
bash scripts/install_deps.sh node
bash scripts/install_deps.sh office-system   # LibreOffice + Poppler for thumbnail preview
source scripts/architect_env.sh              # before manual pptxgenjs generators in a shell
```

New PPTX decks from scratch need **pptxgenjs** (no python greenfield fallback). Without Node, use template/XML editing only.

Optional icon generation (after `source scripts/architect_env.sh` so `npm` is on PATH):

```bash
npm install -g react-icons react react-dom sharp
```

## References

- `SKILL.md` - agent workflow
- `references/pptx-guide.md` - PPTX creation, template editing, and visual QA details
- `references/layout-preview.md` - render grid + per-slide JPEGs to test layout before delivery
- `../_shared/office-tools/` - validation, unpack, pack, thumbnail, slide, cleanup, and extraction tools
