# Shape, Color, and Layout

Load before generating JSON. Colors come from `color-palette.md`.

## Shape Meaning

Choose shape based on what it represents—or use no shape at all:

| Concept Type | Shape | Why |
|--------------|-------|-----|
| Labels, descriptions, details | **none** (free-floating text) | Typography creates hierarchy |
| Section titles, annotations | **none** (free-floating text) | Font size/weight is enough |
| Markers on a timeline | small `ellipse` (10-20px) | Visual anchor, not container |
| Start, trigger, input | `ellipse` | Soft, origin-like |
| End, output, result | `ellipse` | Completion, destination |
| Decision, condition | `diamond` | Classic decision symbol |
| Process, action, step | `rectangle` | Contained action |
| Abstract state, context | overlapping `ellipse` | Fuzzy, cloud-like |
| Hierarchy node | lines + text (no boxes) | Structure through lines |

**Rule**: Default to no container. Add shapes only when they carry meaning. Aim for <30% of text elements to be inside containers.

## Server Architecture Shapes

For layered server diagrams (`layered-server-architecture.md`):

| Role | Shape | Notes |
|------|-------|-------|
| External actor (AI, tool, browser) | `ellipse` | Top band; color encodes client type |
| Internal layer (server, store, safety) | `rectangle` bar | Center spine; `roundness: {type: 3}` |
| Route / tool endpoint | `rectangle` | Inside dashed boundary; ~125×70 |
| Database | `ellipse` | Bottom of spine; green semantic |
| Section grouping | dashed `rectangle` | Transparent fill; auth=purple stroke, routes/admin=navy |
| Decision (2FA, policy gate) | `diamond` | Amber semantic |
| Flow evidence | dark `rectangle` | Terminal-style; green text inside |

**Detail captions** are always free-floating text below the parent shape (`containerId: null`), never inside route boxes.

### Architecture Font Scale

| Level | Size | Color | Use |
|-------|------|-------|-----|
| Diagram title | 28px | `#1e40af` | `{Name} — Architecture` |
| Section title | 16px | `#1e40af` | "Authentication Layer", "MCP Tool Layer" |
| Shape label | 14–16px | match shape or `#ffffff` on dark | Inside boxes/ellipses |
| Spine arrow label | 16–20px | `#1e1e1e`, often `fontFamily: 5` | Bound to vertical arrows |
| Detail caption | 10px | `#64748b` | Below route boxes, stores, auth |
| Evidence artifact | 9px | `#22c55e` on `#1e293b` | Flow sequences in admin |
| Ancillary panel label | 13px | `#3b82f6` | Above sidebar info boxes |

### Sidebar Panel Styling

Ancillary panels (notifications, data model, debug logging): light fill `#dbeafe`, stroke `#1e3a5f`, `strokeWidth: 1`. Label above box in `#3b82f6` at 13px.

## Color as Meaning

Colors encode information, not decoration. Every color choice should come from `color-palette.md` — the semantic shape colors, text hierarchy colors, and evidence artifact colors are all defined there.

**Key principles:**

- Each semantic purpose (start, end, decision, AI, error, etc.) has a specific fill/stroke pair
- Free-floating text uses color for hierarchy (titles, subtitles, details — each at a different level)
- Evidence artifacts (code snippets, JSON examples) use their own dark background + colored text scheme
- Always pair a darker stroke with a lighter fill for contrast

**Do not invent new colors.** If a concept doesn't fit an existing semantic category, use Primary/Neutral or Secondary.

## Modern Aesthetics

For clean, professional diagrams:

### Roughness

- `roughness: 0` — Clean, crisp edges. Use for modern/technical diagrams.
- `roughness: 1` — Hand-drawn, organic feel. Use for brainstorming/informal diagrams.

**Default to 0** for most professional use cases.

### Stroke Width

- `strokeWidth: 1` — Thin, elegant. Good for lines, dividers, subtle connections.
- `strokeWidth: 2` — Standard. Good for shapes and primary arrows.
- `strokeWidth: 3` — Bold. Use sparingly for emphasis (main flow line, key connections).

### Opacity

**Always use `opacity: 100` for all elements.** Use color, size, and stroke width to create hierarchy instead of transparency.

### Small Markers Instead of Shapes

Instead of full shapes, use small dots (10-20px ellipses) as:

- Timeline markers
- Bullet points
- Connection nodes
- Visual anchors for free-floating text

## Layout Principles

### Hierarchy Through Scale

- **Hero**: 300×150 - visual anchor, most important
- **Primary**: 180×90
- **Secondary**: 120×60
- **Small**: 60×40

### Whitespace = Importance

The most important element has the most empty space around it (200px+).

### Flow Direction

Guide the eye: typically left→right or top→bottom for sequences, radial for hub-and-spoke.

### Connections Required

Position alone doesn't show relationships. If A relates to B, there must be an arrow.

### Connected, Not Merely Touching

- Bind a node-to-node arrow with `startBinding` and `endBinding`. Add `{ "id": "<arrow id>", "type": "arrow" }` to each endpoint's `boundElements`. A coordinate that meets a box is not an attached connection. The arrow's own `boundElements` is for a label on the arrow, not for the endpoints.
- Bind to the shape. Do not bind to text that has a `containerId`. For an unboxed label, bind to that text or to a small marker, and align repeated markers in one column with the same gap. An open annotation or a timeline may leave an end unbound. A relationship arrow may not.
- For a small fan-out, draw one arrow per destination, bound at the source and at that destination. Overlapping first segments can look like one trunk. A separate unbound trunk with branch stubs comes apart when a node moves. Add a bus element only when the bus is a named object and each branch binds to an explicit junction on it.
- Use a short corridor, few bends, and arrowheads clear of dashed boundaries. A crossing must look different from a junction.
- Place each connector label beside the segment or target it explains. Wrap a long note there. Do not delete a relationship to simplify the drawing. Use a second view when one canvas cannot show it.

### One Diagram, One Main Story

Do not add a second timeline, ownership recap, or footer that repeats the architecture. Keep the labels and evidence the drawing needs to be read on its own. Shorten the canvas by omitting that repeat. Do not shrink type or squeeze gaps below the sizes in this file. Keep a timeline when the user asked for that sequence or the system actually has one.

### Multi-section posters (reflow, don't insert in place)

Inventory left, flow right, timeline below are **independent layers on one canvas**. Growing one layer is a **reflow of the occupied band**. Shift every element whose box intersects that band (or sits within the reserved gutter) — not only IDs that share a prefix. See `edit-existing.md`.

Arrow `points` that go up (`negative y`) occupy a band **above** the start shape. After a column grows, that band may be a new title. Re-route through a clear gap or below the spine; do not keep the old relative waypoints.

## Text Rules

**CRITICAL**: The JSON `text` property contains ONLY readable words.

```json
{
  "id": "myElement1",
  "text": "Start",
  "originalText": "Start"
}
```

Settings: `fontSize: 16`, `fontFamily: 3`, `textAlign: "center"`, `verticalAlign: "middle"`
