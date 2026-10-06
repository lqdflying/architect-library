# Editing an existing diagram (collision pass)

Load this file when the task is **changing an existing `.excalidraw`**, not only when creating one.

The render-view-fix loop in `render-validate.md` is still mandatory. Run **this pass before the first PNG** so a grown column cannot land on a neighbor that does not share an ID prefix.

This is layout QA. It is not a diagram generator. Do not use it to synthesize a whole poster.

## Learning from manual edits

When asked to compare a user's drawing with an earlier generated version:

1. Read the current file from disk and compare elements by stable ID. Ignore JSON indentation, element ordering, version nonces and editor defaults. Text width/height recalculation alone is not evidence that the user prefers different typography. Unsaved editor changes may not yet be present on disk.
2. Render both snapshots at the same font and scale into temporary files. Do not overwrite the user's source or its published preview merely to compare them. Inspect both the overview and changed connector regions.
3. Measure drawing changes such as endpoint attachment, reciprocal bindings, route bends, marker alignment, label proximity and exported frame size. Separate these observations from content edits, deleted relationships and remaining imperfections. A manual revision is evidence, not a rule to imitate every detail.
4. Re-read the target immediately before an authorized edit. If it changed during comparison, refresh the affected evidence; do not restore the older snapshot. Preserve the user's coordinates and waypoints when a binding-only repair is sufficient.
5. Record only transferable drawing lessons in the skill. Do not generalize a shorter canvas into a mandate to remove required relationships, or a partially improved binding count into an acceptable final result. Every intended node-to-node arrow needs both bindings and reciprocal endpoint references.

## Why ID-prefix shifts fail

A multi-section poster (inventory tree on the left, process flow on the right, timeline below) is **independent layers on one canvas**. Growing one layer is a **reflow of the occupied band**, not an in-place insert.

Example: adding leaves to a left-column tree increases that column's height. Shifting only `inv_*` IDs leaves a title at the same `x` whose id is `ph_title`. The grown identity text then overlaps the title.

**The collision set is geometric.** Do not shift only IDs that share a prefix.

## Reserved gutters

| Situation | Minimum gap |
|-----------|-------------|
| Stacked free-text blocks (title / identity / next section) | 40px |
| Sibling boxes with overlapping `y` | 24px |
| Polyline or dashed arrow vs unrelated text | 20px |

## Before inserting or growing

1. Compute an axis-aligned box per element: `x`, `y`, `width`, `height`.
2. For arrows and lines, use the union of `points` in **scene** space (`element.x + px`, `element.y + py`), not the element's `width`/`height` alone.
3. Define the **grown region**: the column or row you are extending (after the insert).
4. Find every other element whose box **intersects** that region or sits within a reserved gutter of it.
5. Push those elements by the growth delta (`Δh` down, `Δw` right). Exclude only elements that must stay (for example a label that is part of the grown block itself).
6. Bound arrows move with their start/end shapes. Then **rebuild waypoints** so the path does not cross the new labels.

### Growing a tree (add leaves)

- Extend the trunk `height` and `points` to the last leaf.
- Push **everything whose `y` is at or below that last leaf**, including sections to the right that share that `y` band if their `x` ranges overlap the column (or sit within the gutter).
- Then push the next stacked section so the gutter to the grown block stays ≥ 40px.

Helper for a simple horizontal band:

```bash
cd <installed-skills-root>/excalidraw-diagram/references
uv run python shift_region.py diagram.excalidraw --below 1075 --dy 108 --exclude inv_identity
```

`--below Y` moves elements with `y >= Y`. Use `--dry-run` first and read the printed IDs. If a neighbor below the insert is missing from that list, the threshold is wrong — fix `Y`, do not add a one-off ID list.

### Widening a box

- Check the new right edge against every element with overlapping `y`.
- Do not grow into a sibling. Move the sibling, wrap text, or keep the old width.
- After a width change, re-check the 24px sibling gutter.

### Arrow waypoints after a column grows

Arrow `points` that go **up** (`negative y`) occupy a band **above** the start shape. After a column grows, that band may now hold a title. Re-route (through a clear gap, or below the spine). Do not keep the old relative waypoints.

## JSON rewrite

When a script rewrites the file, use `json.dumps(..., indent=2, ensure_ascii=False)` so unicode (em dash, arrows) is not turned into `\u2014`. Re-read the file from disk after the write if the editor has the diagram open.

## Then render

Crop the grown region from the view-safe PNG and Read those crops. The renderer keeps each full export at or below 29,000 vision patches (APIs reject above 30,000). Full-page PNG summaries miss local overlap. See `render-validate.md`.
