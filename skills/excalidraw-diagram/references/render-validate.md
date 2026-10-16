# Render & Validate (MANDATORY)

You cannot judge a diagram from JSON alone. After generating or editing the Excalidraw JSON, you MUST render it to PNG, view the image, and fix what you see — in a loop until it's right. This is a core part of the workflow, not a final check.

**Editing an existing file:** run the geometric collision pass in `edit-existing.md` **before** this loop. Then crop the grown region and Read those PNGs. A full-page PNG summary often misses a local overlap.

## Connector Integrity Before Export

A zero-collision PNG does not prove a relationship is attached. For every arrow that claims a node-to-node relationship, check the JSON:

- `startBinding.elementId` and `endBinding.elementId` exist and are not deleted. An id that merely exists in the file is not enough.
- Each of those elements includes `{ "id": "<arrow id>", "type": "arrow" }` in its `boundElements`.
- The arrow's own `boundElements` lists only a text label on the arrow. Do not put the endpoint shapes there.
- Bind to the shape. If label text has a `containerId`, do not bind the arrow to that text. For an unboxed label, bind to the text element or to a small marker that is the real endpoint.
- Verify what each endpoint represents, not only that its binding exists. Rebinding a group-wide relationship to one child's caption changes its meaning even when the arrow count and reciprocal references still pass. Preserve the intended source and destination when simplifying routes.

An intentionally open end (annotation, timeline tick, decorative line) may omit that binding. Do not use that exception for a relationship the diagram claims.

The headless renderer cannot move elements. The check above is the required gate. If an interactive editor is already open, you may move one connected node on a disposable copy and confirm the connector follows. Never run that test on the user's original file.

For architecture routes, check the direct path before judging bends. A clear two-point connector is valid even when diagonal or slightly offset; do not add folds to make it pass an orthogonality check. For deliberately orthogonal multi-segment routes, consecutive scene-space points share x or y (allow at most 0.5 px for editor rounding), `angle` is zero and `roundness` is null. Examine connector-to-connector intersections as well as connector-to-text collisions. Remove avoidable crossings by adjusting placement or lanes; count neither shared endpoint attachment nor an explicit junction as an accidental crossing. A low crossing count is not success if required relationships were removed.

## Alignment And Readability Before Export

A zero-collision result proves neither alignment nor readability. Check these separately using `shape-and-layout.md`:

- For repeated icon-and-label rows, assert a common visible text edge, consistent `textAlign`, aligned icon centers, vertically centered label blocks and consistent row intervals within each group. Equal text `x` values alone are insufficient when alignment modes differ. Recheck the measured text after wrapping or resizing.
- Check architecture text against the default 16px minimum or the user's explicit scale. Inspect both the intended overview size and detail crops. Rewrite, wrap or reflow small text instead of relying on a higher-resolution PNG or a close-up to make it readable.
- Inspect each connector bend. Remove a bend when a straight segment reads just as clearly, and update its bindings. Keep a bend that makes the route clearer (examples in `shape-and-layout.md`). Passing an orthogonal-segment check does not justify an unnecessary elbow. Do not replace a user's already simplified direct route with an elbow, and do not keep a route that collides or states the wrong relationship.
- Match depicted Azure services and private endpoints to their individual icon nodes. Valid `fileId` values only prove that existing images resolve; they do not detect a missing icon represented by text alone.

## How to Render

```bash
cd <installed-skills-root>/excalidraw-diagram/references && uv run python render_excalidraw.py <path-to-file.excalidraw>
```

This outputs a PNG next to the `.excalidraw` file. Then use the **Read tool** on that PNG to actually view it.

### View-safe PNG size

Vision APIs reject an image above 30,000 patches. Patches are `ceil(width / 32) × ceil(height / 32)`, counted after their own resize rules, and an over-limit image is not shrunk for you. The render script keeps the PNG at or below 29,000 patches. Read that file.

`--scale` (default 2) is only a request. The script lowers it when the full image would exceed the budget, and it prints `capped PNG` on stderr when it does. Do not raise `--scale` to beat the cap. Do not Read a screenshot from another tool, and do not stitch crops into one image before Read. A crop of the capped PNG is smaller, so it is safe to Read. When a label is too small in the overview, crop that region from this PNG and Read the crop.

## The Loop

After generating the initial JSON, run this cycle:

**1. Render & View** — Run the render script, then Read the PNG. Also crop the changed region (widened box, repeated rows, identity/title stack, arrow band) and Read **those** crops. Recompute crop bounds after reflow so the image includes the whole changed region. Full-page descriptions miss local alignment and overlap.

**2. Audit against your original vision** — Before looking for bugs, compare the rendered result to what you designed in Steps 1-4. Ask:

- Does the visual structure match the conceptual structure you planned?
- Does each section use the pattern you intended (fan-out, convergence, timeline, etc.)?
- Does the eye flow through the diagram in the order you designed?
- Is the visual hierarchy correct — hero elements dominant, supporting elements smaller?
- For technical diagrams: are the evidence artifacts (code snippets, data examples) readable and properly placed?
- Does the exported frame still give the main architecture room to read, or does an extra timeline or footer shrink it?

**3. Check for visual defects:**

- Text clipped by or overflowing its container
- Text or shapes overlapping other elements (fail if two non-connected boxes overlap, or a dashed/polyline arrow crosses a label it is not bound to)
- JSON rewritten with `ensure_ascii=True` (em dashes become `\u2014` — rewrite with `ensure_ascii=False`)
- Arrows crossing through elements instead of routing around them
- Preventable connector crossings, unnecessary folds, rounded multi-segment routing or perimeter-length detours; a clear diagonal connector is not a defect
- Arrows landing on the wrong element or pointing into empty space
- A relationship that only meets a shape in the PNG, or a trunk line that is not bound to the nodes it appears to join
- Labels floating ambiguously (not clearly anchored to what they describe)
- Uneven spacing between elements that should be evenly spaced
- Sections with too much whitespace next to sections that are too cramped
- Text too small to read at the rendered size
- Font substitution changing caption widths or apparent spacing. Compare revisions with the same loaded font and export scale; an icon-only render with fallback text is not layout evidence.
- Overall composition feels lopsided or unbalanced

**4. Fix** — Edit the JSON to address everything you found. Common fixes:

- Widen containers when text is clipped
- Adjust `x`/`y` coordinates to fix spacing and alignment
- Remove unnecessary waypoints first. Add one when the folded route reads more clearly than the straight one, using the fewest bends. For a small endpoint offset, align the attachment points instead of folding. Do not replace a user's already simplified direct route with an elbow, and do not keep a route that collides or states the wrong relationship.
- Reposition labels closer to the element they describe; use above, below or beside the icon to free the route
- Resize elements to rebalance visual weight across sections

**5. Re-render & re-view** — Run the render script again and Read the new PNG.

**6. Repeat** — Keep cycling until the diagram passes both the vision check (Step 2) and the defect check (Step 3). Typically takes 2-4 iterations. Don't stop after one pass just because there are no critical bugs — if the composition could be better, improve it.

## When to Stop

The loop is done when:

- The rendered diagram matches the conceptual design from your planning steps
- No text is clipped, overlapping, or unreadable
- Arrows route cleanly and connect to the right elements
- Spacing is consistent and the composition is balanced
- You'd be comfortable showing it to someone without caveats

## First-Time Setup

If the render script hasn't been set up yet:

```bash
cd <installed-skills-root>/excalidraw-diagram/references
bash install_deps.sh
```

`install_deps.sh` installs uv (if needed), Python dependencies, Chromium for Playwright, and on Linux may prompt for sudo only when installing OS libraries required by headless Chromium.

Rendering reaches the network twice by default: setup downloads Chromium from `cdn.playwright.dev`, and each render loads the pinned Excalidraw library from `esm.sh`. In offline or firewalled environments, build the local vendor bundle once (see `README.md` → **Offline rendering**). If the library cannot be loaded, the render script prints a clear error rather than hanging.

## Visual Validation Checklist

After rendering, confirm:

1. **Rendered to PNG**: Diagram has been rendered and visually inspected
2. **No text overflow**: All text fits within its container
3. **No overlapping elements**: Geometric (AABB + scene-space arrow points) and cropped PNG of the grown region; shapes and text don't overlap unintentionally
4. **Alignment and spacing**: Repeated labels share a visible text edge and alignment mode; icon and label centers match; comparable rows use consistent intervals, verified numerically and in the close-up
5. **Arrows land correctly**: Node-to-node arrows have both bindings and a matching `boundElements` entry on each endpoint. Each fan-out destination has its own bound arrow
6. **Readable at viewing size**: Architecture text meets the default 16px minimum or explicit user scale, and is legible at the intended overview size as well as in detail crops; unclear wording is rewritten
7. **Balanced composition**: No large empty voids or overcrowded regions
8. **Routing**: Direct connectors when clear, including diagonals. No unnecessary folds: each retained bend makes its route clearer than a straight segment, and each route uses the fewest bends it needs. No preventable crossings or ambiguous junctions
9. **Icon captions**: Clear association with the intended icon and no interference with connector lanes; above-icon placement is valid
10. **Service artwork**: Every depicted Azure service and private endpoint has its own cached official icon node (or a labeled box where the cache has none, reported in the reply), checked against the design inventory. F5, Palo Alto Networks, NGINX, Datadog, GitHub, and GitHub Actions nodes use the cached SVG for that product (`vendor-icons.md`). Icons render without distortion; every image element's `fileId` resolves to embedded `files` data

## Layered Server Architecture Checks

When the diagram follows `layered-server-architecture.md`, also confirm:

1. **Vertical spine**: Eye can trace server → routes → safety → store → DB without crossing confusion
2. **Detail captions**: Every route/tool box has a nearby gray caption with real names on a side that keeps routes clear
3. **Dashed boundaries**: Auth region (purple) and admin/route region (navy) are visibly grouped
4. **Client color coding**: Purple = AI/MCP, orange = external tool, blue = browser/admin client
5. **Red critical layer**: Safety, merge, or guardrail bar stands out on the spine with function names
