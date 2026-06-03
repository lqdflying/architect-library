# PPTX layout preview (required on every delivery)

You cannot judge slide layout from PPTX XML or pptxgenjs source alone. **Every** time you generate or pack a deck, render preview images, **view** them, and fix layout issues before handing off the `.pptx`—the same bar as Excalidraw’s PNG review loop.

Skipping layout review is not allowed unless the user explicitly waives visual QA.

## Prerequisites (install once per machine)

```bash
bash ../_shared/office-tools/install_deps.sh --with-system
# repo root: bash scripts/install_deps.sh office-system
```

Needs **LibreOffice Impress** (`soffice`), **Poppler** (`pdftoppm`), and **Pillow**. On RHEL/Oracle Linux, `libreoffice-impress` is required (included by `--with-system` on dnf/yum).

If `thumbnail` fails with “soffice not found” or “source file could not be loaded”, install system deps and retry before delivering.

## Workflow (after every validate)

```bash
# 1. Structural validation
python3 ../_shared/office-tools/office_tools.py validate output.pptx --auto-repair

# 2a. Deck overview — labeled grid (slide1.xml, …)
python3 ../_shared/office-tools/office_tools.py thumbnail output.pptx /tmp/deck-preview --cols 4

# 2b. Layout detail — one JPEG per slide at 150 DPI
python3 ../_shared/office-tools/office_tools.py thumbnail output.pptx /tmp/deck-preview \
  --per-slide /tmp/deck-slides --dpi 150 --no-grid
```

Use `/tmp` or `.cursor/` for previews—not the user’s deliverable folder unless they asked for images.

**You must open or inspect these images** (agent vision, user screenshot, or attach in chat). XML validation alone does not count as layout review.

## Content QA (before or with visual review)

Assume problems exist until ruled out.

```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|TODO|\[insert|this.*(page|slide).*layout"
```

Also run `office_tools.py extract` or pandoc if markitdown is not installed. Fix placeholder text before sign-off.

## What to inspect

**Grid (2a):** slide order, hidden slides, overall rhythm, repeated layouts, missing slides.

**Per-slide (2b):** text clipping; tables/diagrams inside margins (≥ 0.5"); no overlapping shapes; consistent titles; broken images; contrast.

Use a **second reviewer or subagent** on the JPEGs when possible — authors often miss defects they introduced in source.

## Fix cycle

1. Generate or pack → validate → thumbnail grid + per-slide export → **view images**.
2. Fix coordinates, fonts, or content in pptxgenjs source or unpacked XML.
3. Re-validate and re-preview affected slides.
4. One fix pass is usually enough; stop unless new overflow/overlap/order defects appear.

## Template decks

Preview the template before populating:

```bash
python3 ../_shared/office-tools/office_tools.py analyze template.pptx
python3 ../_shared/office-tools/office_tools.py thumbnail template.pptx /tmp/template-preview --cols 4
```

After pack, run the full preview workflow again on the output deck.

## If system deps cannot be installed

1. Run `bash scripts/install_deps.sh office-system` (or ask the user to approve sudo).
2. If still blocked (no sudo, air-gapped host), **stop** and tell the user: PowerPoint delivery requires LibreOffice Impress + Poppler for mandatory layout review; offer to proceed only if they waive visual QA or will review the deck in PowerPoint themselves.

Do not treat “optional LibreOffice” as permission to skip preview on every deck.

## Manual fallback

```bash
libreoffice --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

Produces `slide-01.jpg`, `slide-02.jpg`, … — still required viewing before delivery.
