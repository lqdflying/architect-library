# Excalidraw JSON Schema

## Element Types

| Type | Use For |
|------|---------|
| `rectangle` | Processes, actions, components |
| `ellipse` | Entry/exit points, external systems |
| `diamond` | Decisions, conditionals |
| `arrow` | Connections between shapes |
| `text` | Labels inside shapes |
| `line` | Non-arrow connections |
| `frame` | Grouping containers |
| `image` | Official service icons and other embedded artwork |

## Common Properties

All elements share these:

| Property | Type | Description |
|----------|------|-------------|
| `id` | string | Unique identifier |
| `type` | string | Element type |
| `x`, `y` | number | Position in pixels |
| `width`, `height` | number | Size in pixels |
| `strokeColor` | string | Border color (hex) |
| `backgroundColor` | string | Fill color (hex or "transparent") |
| `fillStyle` | string | "solid", "hachure", "cross-hatch" |
| `strokeWidth` | number | 1, 2, or 4 |
| `strokeStyle` | string | "solid", "dashed", "dotted" |
| `roughness` | number | 0 (smooth), 1 (default), 2 (rough) |
| `opacity` | number | 0-100 |
| `seed` | number | Random seed for roughness |

## Text-Specific Properties

| Property | Description |
|----------|-------------|
| `text` | The display text |
| `originalText` | Same as text |
| `fontSize` | Size in pixels (16-20 recommended) |
| `fontFamily` | 3 for monospace (use this) |
| `textAlign` | "left", "center", "right" |
| `verticalAlign` | "top", "middle", "bottom" |
| `containerId` | ID of parent shape |

## Arrow-Specific Properties

| Property | Description |
|----------|-------------|
| `points` | Array of `[dx, dy]` **relative to the element's `x`,`y`**. Collision checks must use scene space (`x+dx`, `y+dy`). Negative `dy` occupies a band **above** the start shape. |
| `startBinding` | Connection to start shape |
| `endBinding` | Connection to end shape |
| `startArrowhead` | null, "arrow", "bar", "dot", "triangle" |
| `endArrowhead` | null, "arrow", "bar", "dot", "triangle" |

## Binding Format

```json
{
  "elementId": "shapeId",
  "focus": 0,
  "gap": 2
}
```

`elementId` must be another element, and that element must include this arrow in its `boundElements`:

```json
{ "id": "arrowId", "type": "arrow" }
```

The arrow's own `boundElements` lists a text label whose `containerId` is the arrow. It does not list the endpoint shapes. Omit one binding only when that end is intentionally open. Do not bind to text that already has a `containerId`; bind to the shape.

For architecture diagrams, use `angle: 0` and `roundness: null` on arrows with axis-aligned waypoints. Bind an icon relationship to the image element, not its nearby caption, and include the arrow in the image's `boundElements`.

## Image Assets

An image element uses `fileId`, `status: "saved"`, `scale: [1, 1]` and its normal position/dimensions. Keep service icons at `angle: 0` and preserve their aspect ratio. The top-level `files[fileId]` entry contains `id`, `mimeType`, `dataURL`, `created` and `lastRetrieved`. For official Azure SVGs, the MIME type is `image/svg+xml` and `dataURL` starts with `data:image/svg+xml;base64,`.

Use the offline search/embed helper in `azure-icons.md` to package original Azure artwork. For F5, Palo Alto Networks, NGINX, and Datadog, use the helper in `vendor-icons.md`. A remote image URL or local filesystem path is not a replacement for the embedded `files` entry. All image IDs must resolve before rendering.

## Rectangle Roundness

Add for rounded corners:
```json
"roundness": { "type": 3 }
```
