---
name: powerpoint-presentation
description: Create, edit, and validate PowerPoint PPTX decks (slides, pitch decks, templates). Mandatory layout preview on every delivery — office_tools thumbnail grid + per-slide 150 DPI JPEGs (LibreOffice Impress + Poppler; install office-system). Architecture, executive, and general presentations. Validate PPTX; view preview images; fix overflow before finishing.
---

# PowerPoint Architecture Presentation Creator

Create and edit `.pptx` architecture presentations for executive reviews, solution walkthroughs, technical design reviews, migration plans, roadmap discussions, and architecture governance.

Use this skill when the user asks for a PowerPoint deck, PPTX file, architecture presentation, executive architecture deck, solution overview, template population, slide duplication, or visual review pack.

## Load First

Before authoring substantial content, read:

- `../_shared/architecture-document-principles.md`
- `references/pptx-guide.md`
- `references/layout-preview.md` — render preview images and verify layout before delivery

For PPTX tooling, use the shared toolkit:

```bash
python3 ../_shared/office-tools/office_tools.py --help
```

If the skill is installed in an editor skills folder, `_shared` should be a sibling of `powerpoint-presentation`.

## Setup

Run once from this skill folder (or use `bash scripts/install_deps.sh` from the repository root).

**Every PPTX delivery requires layout review** (rendered slide images). Install system deps on first use:

```bash
bash ../_shared/office-tools/install_deps.sh
bash ../_shared/office-tools/install_deps.sh --with-system
# or from repo root:
#   bash scripts/install_deps.sh office
#   bash scripts/install_deps.sh office-system
```

| Package | Needed for |
|---------|------------|
| Python (`install_deps.sh`) | `validate`, `extract`, unpack/pack |
| **LibreOffice Impress + Poppler** (`--with-system`) | **Mandatory layout preview** on every deck |
| **pptxgenjs** (npm) | Creating new decks from scratch |

Do not mark a PowerPoint task complete without running layout preview. If `soffice` or `pdftoppm` is missing, run `install_deps.sh --with-system` (may need sudo on Linux) and retry—not only note it in the reply.

For **new** decks (pptxgenjs workflow), from repo root:

```bash
bash scripts/install_deps.sh node
```

(`install_deps.sh all` includes this step. Do not use bare `npm install -g` before trying `install_deps.sh node` — it handles Cursor-server Node and npm bootstrap. Before running pptxgenjs generators manually: `source scripts/architect_env.sh` from repo root.)

## Without npm (no pptxgenjs)

There is **no** python-pptx greenfield fallback in this library (unlike Word’s python-docx path).

- **Cannot** use the New PPTX Workflow below for a deck built entirely from scratch.
- **Can:** populate or edit an **existing template** (unpack → analyze → edit XML → pack), use `slide`, `validate`, and **mandatory** `thumbnail` layout preview.
- Tell the user: new decks need `bash scripts/install_deps.sh node`, or provide a `.pptx` template to populate.

After `install_deps.sh`, prefer the uv environment for Office toolkit commands:

```bash
cd ../_shared/office-tools
uv run python3 office_tools.py --help
```

From this skill folder you can also use `python3 ../_shared/office-tools/office_tools.py` if dependencies are already on your PATH.

## Decision Workflow

First decide which path fits the request.

| Task | Primary tool |
|------|--------------|
| Create a new deck from scratch | `pptxgenjs` (requires `bash scripts/install_deps.sh node`) |
| New deck without npm | **Not supported** — user must supply a template or install Node |
| Populate or edit a template | Unpack, analyze, edit XML, pack (works without npm) |
| Inspect template placeholders | `office_tools.py analyze` |
| Layout preview (grid + per-slide JPEGs) | `office_tools.py thumbnail` |
| Duplicate or create slides | `office_tools.py slide` |
| Clean unused PPTX parts | `office_tools.py clean` |
| Extract text for review | `office_tools.py extract` |
| Validate output | `office_tools.py validate` |
| Convert PPTX to PDF/images | LibreOffice headless and Poppler |

Do not hand-edit a `.pptx` as a binary file. A PPTX is a ZIP package of XML parts. For existing decks and templates, unpack, edit XML, clean orphaned resources, repack, and validate.

## New PPTX Workflow

Use `pptxgenjs` for new decks.

1. Identify the audience and decision the deck needs to support.
2. Choose deck shape: executive summary, technical walkthrough, migration plan, options analysis, roadmap, or governance review.
3. Set layout explicitly, usually `LAYOUT_16x9` unless the user or template says otherwise.
4. Use coordinates in inches and keep a consistent grid.
5. Use real architecture terms, component names, constraints, and evidence.
6. Use diagrams, tables, timelines, sequence views, and option comparisons instead of text-heavy slides.
7. Generate the PPTX.
8. Validate the output:

```bash
python3 ../_shared/office-tools/office_tools.py validate output.pptx --auto-repair
```

9. **Layout preview (required on every deck):** render images, **view** them, fix layout issues—see `references/layout-preview.md`. Do not skip this step.

```bash
python3 ../_shared/office-tools/office_tools.py thumbnail output.pptx /tmp/deck-preview --cols 4
python3 ../_shared/office-tools/office_tools.py thumbnail output.pptx /tmp/deck-preview \
  --per-slide /tmp/deck-slides --dpi 150 --no-grid
```

View the grid for deck flow; open per-slide JPEGs to catch text overflow, overlap, and margin issues. Fix the generator or XML, then re-preview affected slides only. Repeat until the deck passes the layout checklist or the user explicitly waives visual QA.

## Template Editing Workflow

For an existing PPTX template, inspect before editing.

```bash
python3 ../_shared/office-tools/office_tools.py analyze template.pptx
python3 ../_shared/office-tools/office_tools.py thumbnail template.pptx
python3 ../_shared/office-tools/office_tools.py unpack template.pptx unpacked/
```

Then edit the relevant slides under `unpacked/ppt/slides/`, preserve relationships, and pack:

```bash
python3 ../_shared/office-tools/office_tools.py clean unpacked/
python3 ../_shared/office-tools/office_tools.py pack unpacked/ output.pptx --original template.pptx
```

After pack, run the same **layout preview** workflow as for new decks (steps 8–9 above).

Use template placeholders whenever possible. Do not guess placeholder names or coordinates if `analyze` can extract them.

## Slide Design Rules

Architecture decks should be clear enough to present and precise enough to review:

- Put the decision or takeaway in the slide title.
- Keep one major idea per slide.
- Use diagrams for system shape, ownership, sequence, and dependency.
- Use tables for option comparisons, risks, assumptions, milestones, and decisions.
- Use timelines for rollout and migration plans.
- Use real component names, interfaces, constraints, and metrics.
- Avoid generic clip art and decorative shapes that do not carry meaning.
- Keep executive slides concise and technical appendix slides detailed.

## Layout preview (visual validation)

**Required on every PPTX** before delivery—same standard as Excalidraw’s render-and-review loop. Full steps: `references/layout-preview.md`.

| Step | Command | Purpose |
|------|---------|---------|
| Overview | `thumbnail deck.pptx /tmp/preview --cols 4` | Labeled grid; order, hidden slides, repetition |
| Detail | `thumbnail deck.pptx /tmp/preview --per-slide /tmp/slides --dpi 150 --no-grid` | Per-slide JPEGs for overflow and alignment |

You cannot sign off on layout without viewing these images (or a user screenshot). XML validation alone is insufficient.

Check for: text clipping; misaligned titles/icons/charts; broken images; hidden slides; wrong order; elements closer than 0.3"; content inside 0.5" margins.

## Completion discipline

**REQUIRED SUB-SKILL:** Read `../verification-before-completion/SKILL.md` (or `verification-before-completion` when installed globally) before any completion claim.

| Excuse | Reality |
|--------|---------|
| ".pptx exists" | Not done — run thumbnail and view images |
| "Validated earlier" | Re-run validate + thumbnail in this message |
| "User seems in a hurry" | No exceptions — layout preview is mandatory |
| "XML looks fine" | XML ≠ rendered layout — view JPEGs |

## Delivery Checklist

Before finishing:

1. Confirm the PPTX validates (fresh command output in this message).
2. **Layout preview completed** — grid + per-slide JPEGs at 150 DPI; you viewed the images and fixed overflow/overlap (or the user explicitly waived visual QA in writing).
3. Extract text if you need to confirm narrative order.
4. If preview tools were unavailable, you ran `install_deps.sh --with-system` and retried; do not silently ship without layout review.
5. **Deliver only the `.pptx`** unless the user asked for preview images or generator scripts.
6. Keep preview JPEGs and unpacked working directories out of the deliverable folder (use `/tmp` or `.cursor/`).
7. Keep generator `.js` out of the deliverable folder unless the user wants a maintained regen script under `scripts/`.
