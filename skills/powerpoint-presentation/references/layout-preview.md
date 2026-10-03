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

## Microsoft PowerPoint compatibility

Three checks answer different questions:

| Check | What it establishes | What it does not establish |
|-------|---------------------|----------------------------|
| `office_tools.py validate` | Package/XML checks implemented by the validator pass | Microsoft PowerPoint accepts every construct |
| LibreOffice rendering + viewed images | Slides render and the inspected layout is usable | Windows PowerPoint opens without repair |
| Open the exact final file in Microsoft PowerPoint | That file opens without a repair prompt in the tested client | Compatibility with every Office version |

Run the native opening check when available. Otherwise report "Structural validation and rendered layout passed; Microsoft PowerPoint opening unverified." Do not describe a deck as PowerPoint-tested based on LibreOffice alone. A general Office runtime-readiness probe does not replace checking the delivered artifact.

### Recovery from a repair prompt

1. Preserve the failing original outside the deliverable folder. Record the generating library/version and the reported client error. Inspect ZIP integrity, XML, relationship targets, IDs, and missing content-type parts; fix a specific defect only when evidence supports it.
2. If the file still prompts for repair despite passing local checks, try a LibreOffice PowerPoint-format re-export into a separate temporary directory. This is a compatibility recovery, not proof of which original construct caused the failure.
3. Compare original and candidate: slide count/order, visible text, presenter-note bodies, editable shapes, and any images, charts, links, animations or other features present. Compare note bodies separately from generated slide-number/date placeholders. Re-export can change unsupported features; stop if required content or behavior is lost.
4. Run fresh validation and render a grid plus every candidate slide at 150 DPI. View the images. Replace the deliverable only after content and layout checks pass; keep the original backup. Verify the delivered bytes match the checked candidate.
5. Open the exact replacement in Microsoft PowerPoint, or ask the user to confirm when that client is unavailable. Until then say "re-exported and locally checked; native opening unverified," not "confirmed fixed." For a synced copy, ask the user to reopen the replacement rather than the earlier uploaded version.

Example Linux recovery. Run it from the `powerpoint-presentation` skill directory (`skills/powerpoint-presentation/` in this repo, or the installed `powerpoint-presentation` folder next to `_shared`). `input` is an existing absolute path:

```bash
input="/absolute/path/to/deck.pptx"
scratch=$(mktemp -d /tmp/pptx-recovery.XXXXXX)
mkdir -p "$scratch/original" "$scratch/export"
cp -- "$input" "$scratch/original/"
soffice "-env:UserInstallation=file://$scratch/profile" --headless \
  --convert-to 'pptx:Impress MS PowerPoint 2007 XML' \
  --outdir "$scratch/export" "$input"
candidate="$scratch/export/$(basename "$input")"
[[ -s "$candidate" ]] && \
  python3 ../_shared/office-tools/office_tools.py validate "$candidate" && \
  python3 ../_shared/office-tools/office_tools.py thumbnail "$candidate" \
    "$scratch/preview" --cols 4 --per-slide "$scratch/slides" --dpi 150
```

The command deliberately does not overwrite the input. A zero `soffice` exit code alone is insufficient: require a nonempty output and the content, layout and opening checks above. Do not routinely round-trip all decks or rasterize slides to conceal package errors; preserve editability and use recovery only when needed.

### Recorded lesson: PptxGenJS 4.0.1

In October 2026, two generated decks passed XML validation and LibreOffice previews after local corrections to notes-master element ordering and missing-part content-type entries. Windows PowerPoint still displayed "PowerPoint found a problem with content." Those corrections addressed validator findings but did not isolate the cause of the Windows failure. LibreOffice re-export using the filter above preserved all 26 slides, their visible text, presenter-note bodies and editable shape counts; fresh validation and visual checks passed. The user confirmed on 3 October that the replacements opened. Treat this as a confirmed recovery for those files, not a universal fix or evidence that every deck from that library version is invalid.

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
