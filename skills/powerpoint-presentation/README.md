# PowerPoint Presentation Skill

Create, edit, and validate Microsoft PowerPoint architecture presentations.

## Use When

- The user asks for a `.pptx` file.
- The artifact is an executive deck, solution overview, technical walkthrough, migration plan, roadmap, or architecture review pack.
- The task requires template analysis, slide duplication, thumbnails, text extraction, or PPTX validation.

## Setup

Install Office Python deps **and** system deps (layout preview is required on every deck):

```bash
cd ../_shared/office-tools
bash install_deps.sh
bash install_deps.sh --with-system
# or from repo root: bash scripts/install_deps.sh office-system
```

For creating PPTX files from scratch, install the Node package used by the guide:

```bash
npm install -g pptxgenjs
```

Optional icon generation support:

```bash
npm install -g react-icons react react-dom sharp
```

## References

- `SKILL.md` - agent workflow
- `references/pptx-guide.md` - PPTX creation, template editing, and visual QA details
- `references/layout-preview.md` - render grid + per-slide JPEGs to test layout before delivery
- `../_shared/office-tools/` - validation, unpack, pack, thumbnail, slide, cleanup, and extraction tools
