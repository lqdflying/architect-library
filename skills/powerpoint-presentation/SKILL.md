---
name: powerpoint-presentation
description: Create, edit, and validate PowerPoint PPTX architecture presentations, executive decks, solution overviews, technical design walkthroughs, roadmap decks, and template-based slides.
---

# PowerPoint Architecture Presentation Creator

Create and edit `.pptx` architecture presentations for executive reviews, solution walkthroughs, technical design reviews, migration plans, roadmap discussions, and architecture governance.

Use this skill when the user asks for a PowerPoint deck, PPTX file, architecture presentation, executive architecture deck, solution overview, template population, slide duplication, or visual review pack.

## Load First

Before authoring substantial content, read:

- `../_shared/architecture-document-principles.md`
- `references/pptx-guide.md`

For PPTX tooling, use the shared toolkit:

```bash
python3 ../_shared/office-tools/office_tools.py --help
```

If the skill is installed in an editor skills folder, `_shared` should be a sibling of `powerpoint-presentation`.

## Setup

Run once from this skill folder (or use `bash scripts/install_deps.sh office` from the repository root):

```bash
bash ../_shared/office-tools/install_deps.sh
```

For PDF/image conversion, PPTX thumbnails, and slide workflows that need LibreOffice or Poppler:

```bash
bash ../_shared/office-tools/install_deps.sh --with-system
```

For **new** decks (pptxgenjs workflow), install Node.js and pptxgenjs:

```bash
npm install -g pptxgenjs
```

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
| Create a new deck from scratch | `pptxgenjs` |
| Populate or edit a template | Unpack, analyze, edit XML, pack |
| Inspect template placeholders | `office_tools.py analyze` |
| Create thumbnail grid | `office_tools.py thumbnail` |
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

## Visual Validation

When LibreOffice and Poppler are available, create a thumbnail grid or PDF export to visually inspect the deck.

```bash
python3 ../_shared/office-tools/office_tools.py thumbnail output.pptx
```

Check for:

- Text clipping or overflow
- Misaligned titles, icons, and charts
- Broken images
- Hidden slides that should be visible
- Incorrect slide ordering
- Orphaned relationships or missing media

## Delivery Checklist

Before finishing:

1. Confirm the PPTX validates.
2. Generate thumbnails when available and inspect the result.
3. Extract text if you need to confirm narrative order.
4. Mention any skipped checks, such as missing LibreOffice or Poppler.
5. Keep unpacked working directories out of the final deliverable unless the user asks for them.
