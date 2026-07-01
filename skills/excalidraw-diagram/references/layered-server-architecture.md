# Layered Server Architecture

Use this layout when diagramming **MCP servers**, API gateways, or multi-client backends with auth, admin, and a vertical request-to-storage flow.

**Canonical examples** (study before generating):

- `/home/opc/invmcp/Design/invmcp-architecture.excalidraw`
- `/home/opc/dbmcp/doc/architecture.excalidraw`

Colors come from `color-palette.md`. JSON templates in `element-templates.md`.

---

## When to Use

- Multiple external client types (AI/MCP, CLI/tooling, browser admin)
- Central server with route/tool layers, safety logic, and persistence
- Auth sidebar (OAuth, tokens, RBAC) and admin/management sidebar
- Real API names, tool names, or function names should appear (not placeholders)

For simple mental models or non-server concepts, use generic patterns in `visual-patterns.md` instead.

---

## Layout Map

```
                    [Title — Architecture]
              [one-line subtitle, gray, centered]

   (AI/MCP)          (Tool/LLM)              (Browser)
    ellipse            ellipse                 ellipse
       \                 |                      /
        \                |                     /
         ======== [Server bar — primary blue] ========
                        |
                  [Route Layer]  ← arrow label
         ┌─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┐
         │  /mcp    /api/*    /ansible/  ...  │  dashed boundary
         └─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘
           detail    detail     detail         ← 10px captions below
                        |
              [Variable Resolution / Safety]     ← red bar on spine
                        |
              [Store / Connection Manager]     ← blue bar
                        |
                    (PostgreSQL)               ← green ellipse(s)

[Auth Layer]                              [Admin & Management]
 dashed purple                           dashed navy boundary
 ┌ OAuth ─┐                              ┌ Admin SPA ─┐
 ├ Token ─┤                              ├ Admin API ─┤
 └ RBAC ──┘                              └ Policy DB ─┘

[Notifications]  [Data Model]             (left ancillary panels)
```

**Eye flow**: title → clients → server → spine (top to bottom) → sidebars for cross-cutting concerns.

---

## Build Order (Section-by-Section)

Build one section per edit pass. Use descriptive string IDs and namespace seeds by section (100xxx, 200xxx, …).

1. **Title block** — free-floating text only (no boxes)
2. **Client ellipses** — top band, spaced horizontally
3. **Server bar** — center, primary blue, white text
4. **Spine layers** — vertical stack below server: route boundary → critical/safety bar → store bar → database ellipse(s)
5. **Spine arrows** — between layers, with bound labels where layers need names
6. **Auth sidebar** — left: section title, dashed purple boundary, stacked auth boxes
7. **Admin sidebar** — right: section title, dashed navy boundary, stacked admin boxes
8. **Ancillary panels** — bottom-left: notifications, data model, debug (light blue panels)
9. **Cross-links** — server→auth, server→admin, clients→server, store→DB, secondary dashed flows

---

## Per-Zone Shape, Color, Size

| Zone | Shape | Fill / stroke | Typical size |
|------|-------|---------------|--------------|
| Title | free text | `#1e40af` | 28px |
| Subtitle | free text | `#64748b` | 14px |
| AI / MCP client | ellipse | AI/LLM (`#ddd6fe` / `#6d28d9`) | ~140×80 |
| Tool / Ansible / LLM client | ellipse | Start/Trigger (`#fed7aa` / `#c2410c`) | ~140×80 |
| Browser / admin client | ellipse | Tertiary (`#93c5fd` / `#1e3a5f`) | ~140×80 |
| Server, REST, store bars | rectangle, `roundness: {type: 3}` | Primary (`#3b82f6` / `#1e3a5f`) | ~380–400×55–60 |
| Route / tool boxes | rectangle | match client or primary semantic | ~125×70 |
| Secondary route tier | rectangle | Secondary (`#60a5fa`) or Tertiary (`#93c5fd`) | ~125×70 |
| Critical / safety / merge | rectangle bar | Warning/Reset (`#fee2e2` / `#dc2626`) | full spine width |
| RBAC / policy | rectangle | Decision (`#fef3c7` / `#b45309`) | ~220×42 |
| Auth inner boxes | rectangle | AI/LLM purple | ~220×42 |
| Database | ellipse | End/Success (`#a7f3d0` / `#047857`) | ~140–180×65–71 |
| Auth boundary | rectangle, dashed | purple stroke, transparent fill | ~260×180 |
| Route / admin boundary | rectangle, dashed | navy stroke, transparent fill | ~430–455×180–310 |
| Ancillary panel | rectangle, `strokeWidth: 1` | Sidebar ancillary (`#dbeafe` / `#1e3a5f`) | ~260×60–120 |
| Decision (2FA, etc.) | diamond | Decision amber | ~88×68 |
| Flow evidence artifact | rectangle | `#1e293b` fill, `#22c55e` text | variable |

All shapes: `roughness: 0`, `opacity: 100`, `strokeWidth: 2` (except boundaries and ancillary: `strokeWidth: 1`).

---

## Three-Tier Labeling

Every major component gets up to three text layers:

| Tier | Placement | Font | Color | Content |
|------|-----------|------|-------|---------|
| 1 — Label | Inside shape (`containerId`) | 14–16px, `fontFamily: 3` | match shape stroke, or `#ffffff` on dark fills | Name + route or technology, e.g. `/mcp\nFastMCP` |
| 2 — Detail caption | Free-floating below shape | 10px, `fontFamily: 3` | `#64748b` | Bullet list of capabilities, endpoints, or behaviors |
| 3 — Function names | Inside red/critical bars or evidence artifacts | 14–16px (bars) or 9px (artifacts) | match bar stroke or `#22c55e` on dark | Real names: `validate_sql() · safe_identifier()` |

**Examples from reference diagrams:**

- Route detail: `inv_list_hosts`, `list_tables`, `query`, `describe_table`
- Safety bar: `validate_sql() · safe_identifier() · apply_pagination()`
- Merge bar: `effective_vars() · group_depths() · _merge_order()`
- Evidence artifact: `login/OAuth ok → mfa_required → POST /admin/api/login/2fa`

Use middle dot (`·`) to separate inline function lists. Use `\n` for multi-line detail captions.

**Rule**: detail captions are always **outside** the shape (`containerId: null`), positioned ~5–15px below the parent box.

---

## Arrows

| Arrow type | Color | Style | Label |
|------------|-------|-------|-------|
| Client → server | match client semantic (purple, orange, navy) | solid, `strokeWidth: 2` | optional bound label (e.g. "MCP Protocol", "Inventory Script") |
| Spine (layer to layer) | Primary stroke `#1e3a5f` | solid, vertical | **bound label** on arrow (`containerId` = arrow id), 16–20px, often `fontFamily: 5` |
| Store → database | End/Success green `#047857` | solid | usually unlabeled |
| Server → auth / admin | Primary stroke `#1e3a5f` | solid, elbowed | unlabeled |
| Config / hot-reload | `#64748b` | **dashed**, `strokeWidth: 1` | bound label if needed (e.g. "hot-reload") |

Bindings: `startBinding` / `endBinding` with `gap: 2`. Arrow color follows the **source** element's semantic color for client-origin flows.

---

## Section Titles

Free-floating text above dashed boundaries:

- Font: 16px, `#1e40af`, `fontFamily: 3`
- Examples: "Authentication Layer", "MCP Tool Layer", "Admin & Policy", "SQL Safety Guardrails"
- Ancillary panel labels: 13px, `#3b82f6`, left-aligned above light blue box

---

## Evidence Artifacts (Flows Inside Admin)

For authentication or request flows that need step-by-step detail:

1. Amber **diamond** for decision (`2FA\nenabled?`)
2. Dark rectangle (`#1e293b`) with green text (`#22c55e`, 9px, left-aligned)
3. Small gray callout for function names (`is_mfa_enabled()`, `verify_mfa_code()`)

Place inside or adjacent to the admin dashed boundary; connect with amber or navy arrows.

---

## Section Checklist

Before rendering, confirm each zone:

- [ ] Title uses em dash: `{Project} — Architecture`
- [ ] Subtitle is one sentence, centered, gray
- [ ] External actors are ellipses (not rectangles)
- [ ] Server bar is centered on spine with white label text
- [ ] Route/tool row sits inside a dashed navy boundary
- [ ] Each route box has a 10px gray detail caption below
- [ ] Critical/safety layer is red, full spine width, with real function names
- [ ] Database(s) are green ellipses at bottom
- [ ] Auth sidebar has purple dashed boundary
- [ ] Admin sidebar has navy dashed boundary
- [ ] Spine arrows between major layers have bound labels where layers are named
- [ ] Secondary config flows use dashed gray arrows
- [ ] No placeholder labels ("API", "Database") — use real names from the codebase

---

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Uniform card grid for all components | Vertical spine + sidebars |
| Rectangles for external clients | Ellipses at top |
| Single label per box | Label + detail caption (+ functions in critical bars) |
| Auth/admin boxes floating without boundary | Dashed grouping rectangle |
| Generic placeholder text | Research real tool names, routes, functions |
| All arrows same color | Color matches source semantic |
| Detail text inside small route boxes | Free-floating caption below shape |
| Skipping red safety/merge layer | Dedicated spine bar for guardrails or resolution logic |
