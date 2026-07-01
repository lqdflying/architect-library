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
