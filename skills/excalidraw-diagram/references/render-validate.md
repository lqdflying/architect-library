# Render & Validate (MANDATORY)

You cannot judge a diagram from JSON alone. After generating or editing the Excalidraw JSON, you MUST render it to PNG, view the image, and fix what you see — in a loop until it's right. This is a core part of the workflow, not a final check.

## How to Render

```bash
cd <installed-skills-root>/excalidraw-diagram/references && uv run python render_excalidraw.py <path-to-file.excalidraw>
```

This outputs a PNG next to the `.excalidraw` file. Then use the **Read tool** on the PNG to actually view it.

## The Loop

After generating the initial JSON, run this cycle:

**1. Render & View** — Run the render script, then Read the PNG.

**2. Audit against your original vision** — Before looking for bugs, compare the rendered result to what you designed in Steps 1-4. Ask:

- Does the visual structure match the conceptual structure you planned?
- Does each section use the pattern you intended (fan-out, convergence, timeline, etc.)?
- Does the eye flow through the diagram in the order you designed?
- Is the visual hierarchy correct — hero elements dominant, supporting elements smaller?
- For technical diagrams: are the evidence artifacts (code snippets, data examples) readable and properly placed?

**3. Check for visual defects:**

- Text clipped by or overflowing its container
- Text or shapes overlapping other elements
- Arrows crossing through elements instead of routing around them
- Arrows landing on the wrong element or pointing into empty space
- Labels floating ambiguously (not clearly anchored to what they describe)
- Uneven spacing between elements that should be evenly spaced
- Sections with too much whitespace next to sections that are too cramped
- Text too small to read at the rendered size
- Overall composition feels lopsided or unbalanced

**4. Fix** — Edit the JSON to address everything you found. Common fixes:

- Widen containers when text is clipped
- Adjust `x`/`y` coordinates to fix spacing and alignment
- Add intermediate waypoints to arrow `points` arrays to route around elements
- Reposition labels closer to the element they describe
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
3. **No overlapping elements**: Shapes and text don't overlap unintentionally
4. **Even spacing**: Similar elements have consistent spacing
5. **Arrows land correctly**: Arrows connect to intended elements without crossing others
6. **Readable at export size**: Text is legible in the rendered PNG
7. **Balanced composition**: No large empty voids or overcrowded regions

## Layered Server Architecture Checks

When the diagram follows `layered-server-architecture.md`, also confirm:

1. **Vertical spine**: Eye can trace server → routes → safety → store → DB without crossing confusion
2. **Detail captions**: Every route/tool box has a 10px gray caption below with real names
3. **Dashed boundaries**: Auth region (purple) and admin/route region (navy) are visibly grouped
4. **Client color coding**: Purple = AI/MCP, orange = external tool, blue = browser/admin client
5. **Red critical layer**: Safety, merge, or guardrail bar stands out on the spine with function names
