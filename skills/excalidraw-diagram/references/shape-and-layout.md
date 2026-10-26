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
| Route / tool endpoint | `rectangle` | Inside dashed boundary; ~168×70 |
| Database | `ellipse` | Bottom of spine; green semantic. An Azure database uses its official icon (`azure-icons.md`) |
| Section grouping | dashed `rectangle` | Transparent fill; auth=purple stroke, routes/admin=navy |
| Decision (2FA, policy gate) | `diamond` | Amber semantic |
| Flow evidence | dark `rectangle` | Terminal-style; green text inside |

On an Azure diagram, a zone that is an Azure service, such as a database, cache, storage account, Key Vault or Entra ID, uses its official icon and caption from `azure-icons.md` instead of the shape in this table. Keep the zone's position in the layout and its connector colors. A database that is not an Azure service stays a green ellipse. A node that is F5, Palo Alto Networks, NGINX, Datadog, GitHub, or GitHub Actions uses that product's cached icon and caption from `vendor-icons.md`. A generic load balancer, firewall, proxy, monitoring service, source host, or workflow runner keeps the shape in this table.

**Detail captions** are free-floating text outside the parent shape (`containerId: null`). Place them above, below, left or right to keep connectors clear; below is not mandatory. Keep each caption closer to its own icon than to a neighboring icon, and group the icon and caption so they move together.

### Architecture Font Scale

| Level | Size | Color | Use |
|-------|------|-------|-----|
| Diagram title | 28–36px | `#1e40af` | `{Name} — Architecture` |
| Section title | 18–20px | `#1e40af` | "Authentication Layer", "MCP Tool Layer" |
| Shape label | 16–18px | match shape or `#ffffff` on dark | Inside boxes/ellipses |
| Spine arrow label | 16–20px | `#1e1e1e`, often `fontFamily: 5` | Bound to vertical arrows |
| Detail caption | 16px | `#64748b` | Beside route boxes, stores or auth; choose the clearest side |
| Evidence artifact | 16px | `#22c55e` on `#1e293b` | Short flow sequences or examples |
| Ancillary panel label | 16px | `#3b82f6` | Above sidebar info boxes |

Use 16px as the default minimum for architecture text, including endpoint names, subnet labels and notes. An explicit user-specified scale may override it; otherwise shorten or wrap the text, expand the occupied region, or move inventory detail to the companion document. Never shrink labels to fit a fixed box. Check readability at the intended viewing size: a large export or readable close-up does not prove that the overview is legible.

### Sidebar Panel Styling

Ancillary panels (notifications, data model, debug logging): light fill `#dbeafe`, stroke `#1e3a5f`, `strokeWidth: 1`. Label above box in `#3b82f6` at 16px.

## Color as Meaning

Colors encode information, not decoration. Every color choice should come from `color-palette.md` — the semantic shape colors, text hierarchy colors, and evidence artifact colors are all defined there.

**Key principles:**

- Each semantic purpose (start, end, decision, AI, error, etc.) has a specific fill/stroke pair
- Free-floating text uses color for hierarchy (titles, subtitles, details — each at a different level)
- Evidence artifacts (code snippets, JSON examples) use their own dark background + colored text scheme
- Always pair a darker stroke with a lighter fill for contrast
- In architecture diagrams, give each major traffic family a consistent route color from `color-palette.md`. Carry it through its ports and connector captions; keep configuration links visually secondary and dashed. Do not make every route black or the same dark navy.

**Do not invent new colors.** If a concept doesn't fit an existing semantic category, use Primary/Neutral or Secondary.

Official service icons, and the F5, Palo Alto Networks, NGINX, Datadog, GitHub, and GitHub Actions marks, retain their original artwork and colors. Use the palette for the diagram's boundaries, labels and connectors. Do not recolor those icons to match the palette. See `azure-icons.md` and `vendor-icons.md`.

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

Use whitespace to separate semantic groups and keep captions and routes clear. Do not reserve a fixed large halo around a service node. When removing content leaves an empty band, compact the affected sections together using `edit-existing.md` without shrinking text or deleting required relationships.

### Flow Direction

Guide the eye: typically left→right or top→bottom for sequences, radial for hub-and-spoke.

### Repeated Icon And Label Rows

- Choose one label alignment per repeated column. For labels beside icons, default to a shared left edge and `textAlign: "left"`; equal `x` values do not align visible text when some labels are centered.
- Align icon centers in one column. Vertically center each label block on its icon, including wrapped labels: `label.y + label.height / 2 = icon.y + icon.height / 2`. Use measured text height after changing wording or font size.
- Use a consistent center-to-center row interval, large enough for the tallest label and the required gutters. Choose the interval for the content, not a fixed project-specific value. Separate semantic groups explicitly when their spacing differs.
- Move connected service nodes and rebuild routes when rows move. Group each icon with its caption, then check the rendered text edges and centers; non-overlap alone is not alignment.

### Connections Required

Position alone doesn't show relationships. If A relates to B, there must be an arrow.

### Connected, Not Merely Touching

- Bind a node-to-node arrow with `startBinding` and `endBinding`. Add `{ "id": "<arrow id>", "type": "arrow" }` to each endpoint's `boundElements`. A coordinate that meets a box is not an attached connection. The arrow's own `boundElements` is for a label on the arrow, not for the endpoints.
- Bind to the shape. Do not bind to text that has a `containerId`. For an unboxed label, bind to that text or to a small marker, and align repeated markers in one column with the same gap. An open annotation or a timeline may leave an end unbound. A relationship arrow may not.
- For a small fan-out, draw one arrow per destination, bound at the source and at that destination. Overlapping first segments can look like one trunk. A separate unbound trunk with branch stubs comes apart when a node moves. Add a bus element only when the bus is a named object and each branch binds to an explicit junction on it.
- Use a short corridor, few bends, and arrowheads clear of dashed boundaries. A crossing must look different from a junction.
- Place each connector label beside the segment or target it explains. Move port and protocol labels with a rerouted line; do not leave them beside the old route or add bends merely to reach an old label position. Wrap a long note there. Do not delete a relationship to simplify the drawing. Use a second view when one canvas cannot show it.

### Routing Before Decoration

- Arrange regions around the dominant relationships before routing individual edges. Do not place an unrelated system boundary between a source and its main destinations: lines crossing it can imply traversal or membership. A shared hub usually belongs near the center of its connected peers; the test is the resulting routes, not geometric symmetry.
- Reserve different corridors for different connection families, such as network peerings, service access and diagnostics. Let a clearly separated secondary route be longer when that makes the primary flow easier to trace. Optimize for semantic clarity and fewer crossings first, then bends and length; shortest total wire length is not the goal.
- Avoid crossings when another placement or route can remove them. Move a source closer to its destinations, reorder peer nodes, or reserve a separate connector lane before adding detours. Check each retained relationship: fewer arrows after an edit can mean reduced scope rather than better routing.
- Prefer orthogonal routing for architecture diagrams: use clean L-shaped or stepped folds between offset nodes and separate lanes for fan-out paths. Keep already aligned horizontal or vertical links straight. A fold that organizes the overall flow is useful even when a diagonal would avoid collisions; do not require a direct-line trial or straighten a route merely to reduce its bend count.
- Choose attachment sides, lanes and labels together. Use enough bends to make the path easy to trace, without zigzags, tiny doglegs or perimeter-length detours. Align a tiny endpoint offset when that preserves the layout. For folded routes, consecutive scene-space points share x or y; set `angle: 0` and `roundness: null`. Use a diagonal only for an explicit user preference or a layout whose meaning depends on it, such as a radial relationship.
- Keep parallel routes separated. Do not run connectors through unrelated icons, labels or container headings. Choose the connection side and caption side together: the side occupied by incoming or outgoing arrows should stay clear, so a caption above an icon can free its lower connection point. Keep repeated subgraphs aligned so the reader can compare them.
- For unavoidable crossings, make continuation distinct from connection. Junctions need an explicit node or marker; an ordinary crossing is not a junction. Do not merge independent routes into an unlabeled shared trunk to hide crossings.
- Preserve both endpoint bindings and reciprocal `boundElements` when rerouting. Check the complete route in scene coordinates after moving any connected node; endpoint attachment alone does not keep intermediate segments clear. Preserve user-approved routing, route colors and layout unless the requested change or a specific collision or misleading relationship requires an adjustment.

Do not turn a successful arrangement into a universal top/bottom rule. A control plane can sit above, below or beside compute; place it where its links stay clear of unrelated network relationships. For orthogonal routes, allow at most 0.5 px of scene-space tolerance for editor rounding and snap newly authored bends to shared axes. Judge the whole route family at overview size: both folded and aligned straight links must be easy to follow.

### One Diagram, One Main Story

Do not add a second timeline, ownership recap, or footer that repeats the architecture. Keep the labels and evidence the drawing needs to be read on its own. Shorten the canvas by omitting that repeat. Do not shrink type or squeeze gaps below the sizes in this file. Keep a timeline when the user asked for that sequence or the system actually has one.

Containment communicates ownership or network membership. Put an externally owned service outside the relevant project or resource-group boundary and show only the consumer-facing relationship the design needs. For a feasible but unimplemented integration, label the path as planned or pending; documented support is not evidence of approval, provisioning or working connectivity. Keep detailed external prerequisites in the companion design instead of inventing a subnet or resource inventory.

### Multi-section posters (reflow, don't insert in place)

Inventory left, flow right, timeline below are **independent layers on one canvas**. Growing one layer is a **reflow of the occupied band**. Shift every element whose box intersects that band (or sits within the reserved gutter) — not only IDs that share a prefix. See `edit-existing.md`.

Arrow `points` that go up (`negative y`) occupy a band **above** the start shape. After a column grows, that band may be a new title. Re-route through a clear gap or below the spine; do not keep the old relative waypoints.

## Text Rules

**CRITICAL**: The JSON `text` property contains ONLY readable words.

When improving an existing diagram, preserve technical meaning, ownership and pending decisions, not unclear wording. Replace unexplained abbreviations with service names, shorten descriptions and remove redundant inventory text. Keep identifiers that distinguish real resources; do not invent approval or runtime certainty. Make deliberate wording edits consistent in `text` and `originalText`, while retaining intentional display wrapping.

```json
{
  "id": "myElement1",
  "text": "Start",
  "originalText": "Start"
}
```

Settings: `fontSize: 16`, `fontFamily: 3`, `textAlign: "center"`, `verticalAlign: "middle"`
