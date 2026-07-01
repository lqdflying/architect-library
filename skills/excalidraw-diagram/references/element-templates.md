# Element Templates

Copy-paste JSON templates for each Excalidraw element type. The `strokeColor` and `backgroundColor` values are placeholders — always pull actual colors from `color-palette.md` based on the element's semantic purpose.

## Free-Floating Text (no container)
```json
{
  "type": "text",
  "id": "label1",
  "x": 100, "y": 100,
  "width": 200, "height": 25,
  "text": "Section Title",
  "originalText": "Section Title",
  "fontSize": 20,
  "fontFamily": 3,
  "textAlign": "left",
  "verticalAlign": "top",
  "strokeColor": "<title color from palette>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 11111,
  "version": 1,
  "versionNonce": 22222,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": null,
  "lineHeight": 1.25
}
```

## Line (structural, not arrow)
```json
{
  "type": "line",
  "id": "line1",
  "x": 100, "y": 100,
  "width": 0, "height": 200,
  "strokeColor": "<structural line color from palette>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 44444,
  "version": 1,
  "versionNonce": 55555,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "points": [[0, 0], [0, 200]]
}
```

## Small Marker Dot
```json
{
  "type": "ellipse",
  "id": "dot1",
  "x": 94, "y": 94,
  "width": 12, "height": 12,
  "strokeColor": "<marker dot color from palette>",
  "backgroundColor": "<marker dot color from palette>",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 66666,
  "version": 1,
  "versionNonce": 77777,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false
}
```

## Rectangle
```json
{
  "type": "rectangle",
  "id": "elem1",
  "x": 100, "y": 100, "width": 180, "height": 90,
  "strokeColor": "<stroke from palette based on semantic purpose>",
  "backgroundColor": "<fill from palette based on semantic purpose>",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 12345,
  "version": 1,
  "versionNonce": 67890,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": [{"id": "text1", "type": "text"}],
  "link": null,
  "locked": false,
  "roundness": {"type": 3}
}
```

## Text (centered in shape)
```json
{
  "type": "text",
  "id": "text1",
  "x": 130, "y": 132,
  "width": 120, "height": 25,
  "text": "Process",
  "originalText": "Process",
  "fontSize": 16,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "<text color — match parent shape's stroke or use 'on light/dark fills' from palette>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 11111,
  "version": 1,
  "versionNonce": 22222,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": "elem1",
  "lineHeight": 1.25
}
```

## Arrow
```json
{
  "type": "arrow",
  "id": "arrow1",
  "x": 282, "y": 145, "width": 118, "height": 0,
  "strokeColor": "<arrow color — typically matches source element's stroke from palette>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 33333,
  "version": 1,
  "versionNonce": 44444,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "points": [[0, 0], [118, 0]],
  "startBinding": {"elementId": "elem1", "focus": 0, "gap": 2},
  "endBinding": {"elementId": "elem2", "focus": 0, "gap": 2},
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

For curves: use 3+ points in `points` array.

---

## Layered Server Architecture Templates

Use with colors from `color-palette.md`. See `layered-server-architecture.md` for layout rules.

### Title + Subtitle (free-floating)
```json
{
  "type": "text",
  "id": "title",
  "x": 380, "y": -29,
  "width": 460, "height": 35,
  "text": "Project — Architecture",
  "originalText": "Project — Architecture",
  "fontSize": 28,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "top",
  "strokeColor": "#1e40af",
  "backgroundColor": "transparent",
  "roughness": 0,
  "opacity": 100,
  "containerId": null,
  "lineHeight": 1.25
}
```
```json
{
  "type": "text",
  "id": "subtitle",
  "x": 350, "y": 9,
  "width": 520, "height": 20,
  "text": "One-line description of what the system does",
  "originalText": "One-line description of what the system does",
  "fontSize": 14,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "top",
  "strokeColor": "#64748b",
  "backgroundColor": "transparent",
  "roughness": 0,
  "opacity": 100,
  "containerId": null,
  "lineHeight": 1.25
}
```

### Client Ellipse (external actor)
```json
{
  "type": "ellipse",
  "id": "client_ai",
  "x": 100, "y": 50,
  "width": 140, "height": 80,
  "strokeColor": "#6d28d9",
  "backgroundColor": "#ddd6fe",
  "strokeWidth": 2,
  "roughness": 0,
  "opacity": 100,
  "boundElements": [{"id": "client_ai_text", "type": "text"}, {"id": "arrow_ai_to_server", "type": "arrow"}],
  "roundness": null
}
```
```json
{
  "type": "text",
  "id": "client_ai_text",
  "text": "AI Agents\n(MCP)",
  "originalText": "AI Agents\n(MCP)",
  "fontSize": 16,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "#6d28d9",
  "containerId": "client_ai",
  "lineHeight": 1.25
}
```

### Server Spine Bar
```json
{
  "type": "rectangle",
  "id": "server_rect",
  "x": 390, "y": 220,
  "width": 380, "height": 60,
  "strokeColor": "#1e3a5f",
  "backgroundColor": "#3b82f6",
  "strokeWidth": 2,
  "roughness": 0,
  "opacity": 100,
  "roundness": {"type": 3},
  "boundElements": [{"id": "server_text", "type": "text"}]
}
```
```json
{
  "type": "text",
  "id": "server_text",
  "text": "FastMCP Server (server.py)",
  "originalText": "FastMCP Server (server.py)",
  "fontSize": 18,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "#ffffff",
  "containerId": "server_rect",
  "lineHeight": 1.25
}
```

### Route Box + Detail Caption
```json
{
  "type": "rectangle",
  "id": "route_mcp",
  "x": 378, "y": 350,
  "width": 125, "height": 75,
  "strokeColor": "#6d28d9",
  "backgroundColor": "#ddd6fe",
  "strokeWidth": 2,
  "roughness": 0,
  "opacity": 100,
  "roundness": {"type": 3},
  "boundElements": [{"id": "route_mcp_text", "type": "text"}]
}
```
```json
{
  "type": "text",
  "id": "route_mcp_text",
  "text": "/mcp\nFastMCP",
  "originalText": "/mcp\nFastMCP",
  "fontSize": 16,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "#6d28d9",
  "containerId": "route_mcp",
  "lineHeight": 1.25
}
```
```json
{
  "type": "text",
  "id": "route_mcp_detail",
  "text": "list_connections\nlist_tables\nquery\ndescribe_table",
  "originalText": "list_connections\nlist_tables\nquery\ndescribe_table",
  "fontSize": 10,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "top",
  "strokeColor": "#64748b",
  "containerId": null,
  "lineHeight": 1.25
}
```

### Dashed Section Boundary
```json
{
  "type": "rectangle",
  "id": "route_boundary",
  "x": 360, "y": 335,
  "width": 430, "height": 180,
  "strokeColor": "#1e3a5f",
  "backgroundColor": "transparent",
  "strokeWidth": 1,
  "strokeStyle": "dashed",
  "roughness": 0,
  "opacity": 100,
  "roundness": {"type": 3}
}
```

### Arrow with Bound Label (spine layer)
```json
{
  "type": "arrow",
  "id": "arrow_server_to_tools",
  "strokeColor": "#1e3a5f",
  "strokeWidth": 2,
  "roughness": 0,
  "opacity": 100,
  "points": [[0, 0], [0, 50]],
  "startBinding": {"elementId": "server_rect", "focus": 0, "gap": 2},
  "endBinding": null,
  "endArrowhead": "arrow",
  "boundElements": [{"type": "text", "id": "arrow_server_label"}]
}
```
```json
{
  "type": "text",
  "id": "arrow_server_label",
  "text": "Route Layer",
  "originalText": "Route Layer",
  "fontSize": 20,
  "fontFamily": 5,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "#1e1e1e",
  "containerId": "arrow_server_to_tools",
  "lineHeight": 1.25
}
```

### Dashed Secondary Arrow (config / hot-reload)
```json
{
  "type": "arrow",
  "id": "arrow_config_flow",
  "strokeColor": "#64748b",
  "strokeWidth": 1,
  "strokeStyle": "dashed",
  "roughness": 0,
  "opacity": 100,
  "points": [[0, 0], [-200, 117]],
  "startBinding": {"elementId": "config_label", "focus": 0, "gap": 10},
  "endBinding": {"elementId": "conn_mgr_rect", "focus": 0.7, "gap": 5},
  "endArrowhead": "arrow"
}
```

### Evidence Flow Artifact (terminal style)
```json
{
  "type": "rectangle",
  "id": "flow_artifact_rect",
  "x": 1170, "y": 404,
  "width": 190, "height": 112,
  "strokeColor": "#1e293b",
  "backgroundColor": "#1e293b",
  "strokeWidth": 1,
  "roughness": 0,
  "opacity": 100,
  "roundness": {"type": 3},
  "boundElements": [{"id": "flow_artifact_text", "type": "text"}]
}
```
```json
{
  "type": "text",
  "id": "flow_artifact_text",
  "text": "login/OAuth ok\n-> mfa_required\nPOST /admin/api/login/2fa\n-> login + csrf_token",
  "originalText": "login/OAuth ok\n-> mfa_required\nPOST /admin/api/login/2fa\n-> login + csrf_token",
  "fontSize": 9,
  "fontFamily": 3,
  "textAlign": "left",
  "verticalAlign": "top",
  "strokeColor": "#22c55e",
  "containerId": "flow_artifact_rect",
  "lineHeight": 1.25
}
```

### Database Ellipse
```json
{
  "type": "ellipse",
  "id": "postgres_db",
  "x": 449, "y": 860,
  "width": 180, "height": 65,
  "strokeColor": "#047857",
  "backgroundColor": "#a7f3d0",
  "strokeWidth": 2,
  "roughness": 0,
  "opacity": 100,
  "boundElements": [{"id": "postgres_text", "type": "text"}, {"id": "arrow_store_to_db", "type": "arrow"}]
}
```
```json
{
  "type": "text",
  "id": "postgres_text",
  "text": "PostgreSQL\n16",
  "originalText": "PostgreSQL 16",
  "fontSize": 16,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "#047857",
  "containerId": "postgres_db",
  "lineHeight": 1.25
}
```
