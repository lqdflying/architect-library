# Color Palette & Brand Style

**This is the single source of truth for all colors and brand-specific styles.** To customize diagrams for your own brand, edit this file — everything else in the skill is universal.

Official service icons, and the F5, Palo Alto Networks, NGINX, Datadog, GitHub, and GitHub Actions marks, are an exception to diagram recoloring: retain their native SVG artwork and colors. Apply this palette to surrounding boundaries, text and connectors. See `azure-icons.md` for the offline Azure icon cache and usage terms. A node that is F5, Palo Alto Networks, NGINX, Datadog, GitHub, or GitHub Actions uses that product's cached icon and caption from `vendor-icons.md`.

---

## Shape Colors (Semantic)

Colors encode meaning, not decoration. Each semantic purpose has a fill/stroke pair.

| Semantic Purpose | Fill | Stroke |
|------------------|------|--------|
| Primary/Neutral | `#3b82f6` | `#1e3a5f` |
| Secondary | `#60a5fa` | `#1e3a5f` |
| Tertiary | `#93c5fd` | `#1e3a5f` |
| Start/Trigger | `#fed7aa` | `#c2410c` |
| End/Success | `#a7f3d0` | `#047857` |
| Warning/Reset | `#fee2e2` | `#dc2626` |
| Decision | `#fef3c7` | `#b45309` |
| AI/LLM | `#ddd6fe` | `#6d28d9` |
| Browser / admin client | `#93c5fd` | `#1e3a5f` |
| Sidebar ancillary panel | `#dbeafe` | `#1e3a5f` (use `strokeWidth: 1`) |
| Inactive/Disabled | `#dbeafe` | `#1e40af` (use dashed stroke) |
| Error | `#fecaca` | `#b91c1c` |

**Rule**: Always pair a darker stroke with a lighter fill for contrast.

---

## Text Colors (Hierarchy)

Use color on free-floating text to create visual hierarchy without containers.

| Level | Color | Use For |
|-------|-------|---------|
| Title | `#1e40af` | Section headings, major labels |
| Subtitle | `#3b82f6` | Subheadings, secondary labels |
| Body/Detail | `#64748b` | Descriptions, annotations, metadata |
| On light fills | `#374151` | Text inside light-colored shapes |
| On dark fills | `#ffffff` | Text inside dark-colored shapes |

---

## Evidence Artifact Colors

Used for code snippets, data examples, and other concrete evidence inside technical diagrams.

| Artifact | Background | Text Color |
|----------|-----------|------------|
| Code snippet | `#1e293b` | Syntax-colored (language-appropriate) |
| JSON/data example | `#1e293b` | `#22c55e` (green) |

---

## Architecture Route Colors

Choose a small set of colors by relationship type before routing. These defaults distinguish traffic families; use only the families present in the diagram and preserve an existing clear color key. Do not give every edge a different color or make all routes black or dark navy. The layered server pattern keeps its own arrow table in `layered-server-architecture.md`.

| Relationship | Route color | Line style |
|--------------|-------------|------------|
| User ingress | Blue `#3b82f6` | Solid |
| Deployment or administrative access | Orange `#c2410c` | Solid |
| Application-to-service or data access | Green `#047857` | Solid |
| Configuration, identity association or scope | Slate `#64748b` | Dashed |

Carry the family color along its route and use it for nearby protocol labels or matching service headings. Use darker blue `#1e40af` for small blue captions on white; keep long resource names and supporting detail neutral. Keep labels, arrowheads and solid/dashed distinctions so color is not the only cue. Include a compact legend when several families share the canvas.

Boundary colors describe ownership or grouping independently of route colors; make that distinction explicit when both are used. Keep official icons unchanged. Prefer colored routes and headings with restrained fills, not large saturated backgrounds. When refining an approved layout for color alone, preserve positions, waypoints, bindings and content except the color key.

## Default Stroke & Line Colors

| Element | Color |
|---------|-------|
| Architecture arrows | Use the relationship's route color above; a shared source may emit several traffic families |
| Other arrows | Use the stroke color of the source element's semantic purpose |
| Structural lines (dividers, trees, timelines) | Primary stroke (`#1e3a5f`) or Slate (`#64748b`) |
| Marker dots (fill + stroke) | Primary fill (`#3b82f6`) |

---

## Background

| Property | Value |
|----------|-------|
| Canvas background | `#ffffff` |
