---
name: azure-iac-diagram
description: Draw or restyle the architecture diagram of an Azure IaC project repository in one fixed house layout, so every project diagram reads the same way. Use when asked for an architecture, infrastructure, environment, or design diagram of an Azure IaC or landing-zone project, or to make such a diagram match the other project diagrams. Builds on the excalidraw-diagram skill, which owns icons, JSON, bindings, and rendering; this skill fixes only the layout, style, and content rules. Done when the drawing shows one environment in the zone layout, uses the style tokens and route key of this skill, takes every name and address from the design or the IaC, marks every pending item in amber, and has passed the excalidraw-diagram validation and render loop with the PNG viewed.
---

# Azure IaC Diagram

One fixed layout and style for the architecture diagram of an Azure IaC project. A reader who knows one project diagram can read the next without a new key.

**REQUIRED BASE SKILL:** `excalidraw-diagram`. It owns the Excalidraw JSON, the official Azure and vendor icons, bindings, the collision pass, and the render and validation loop. Follow it for all of those. This skill adds the design the base skill leaves open.

## Load First

1. `references/layout-and-style.md` in this skill: zones, coordinates, style tokens, caption templates, route key.
2. From `excalidraw-diagram`: `references/azure-icons.md`, `references/vendor-icons.md`, `references/json-schema.md`, `references/element-templates.md`, `references/render-validate.md`, and `references/edit-existing.md` when the file already exists.

Do not load `visual-patterns.md` or `layered-server-architecture.md` from the base skill. The layout here is fixed.

## What This Skill Overrides In The Base Skill

| Base skill rule | Rule for this diagram |
|---|---|
| Pick a visual pattern per concept; avoid uniform rows | Use the zone layout in `references/layout-and-style.md`. Endpoint and service rows are uniform on purpose |
| Technical diagrams carry evidence artifacts | No callout boxes or summary strips, and one dark panel only: the call details in the Central AI service box. Elsewhere the names, CIDRs, ports, and settings in the captions are the evidence |
| Architecture route colors (blue ingress, green data access) | Use the route key in `references/layout-and-style.md`. Its legend goes on every drawing |
| Rounded rectangles | Boundaries and boxes have sharp corners. Only the user actor is an ellipse |

Everything else in the base skill still applies: official icons for every Azure service and every private endpoint, cached vendor icons, 16px minimum text, orthogonal routes, bound arrows, the collision pass, and the render loop.

## Rules

- **One environment per drawing.** Draw real names, subnets, and CIDRs for that environment. Do not draw `{env}` placeholders or a generic template. When the design covers several environments, draw the first one to be built and say in the subtitle how the others differ.
- **Draw only what the design states.** Every name, address, port, SKU, and setting comes from the design document, the IaC, or the network's published address plan. Do not invent one to fill a caption.
- **Pending is amber.** An undecided setting, an unallocated address or subnet, or a proposal that waits for approval is amber text, and an amber dashed arrow when a whole path is conditional. Write what is pending and who owns it. Do not draw a pending item as settled.
- **Ownership is containment.** A resource the project creates sits inside the compute region or the project PaaS box. A shared platform service sits in the shared-platform band. A system another team owns sits in the external band. Do not draw a platform or external resource inside a project boundary.
- **The central AI service is its own box.** When the project calls a shared AI gateway, draw the Central AI service box: the gateway's private endpoint, API Management, the shared Foundry account, and one panel with the gateway host and the header the caller sends. Do not reduce it to one icon in the external band, and never put a key value in the panel.
- **A private endpoint is in a subnet; its service is not.** The endpoint icon sits in its subnet box. The service icon sits in the PaaS box on the same row.
- **Leave out what the design does not have.** Drop an empty zone or band and close the gap. Do not keep an empty box for symmetry.
- **No second story.** No timeline, phase list, apply order, or role-assignment table on this drawing. Those belong in the design document or in a separate drawing.

## Workflow

1. **Inventory.** From the design and the IaC, list: the compute (cluster, node pools, web apps, VMs), each private endpoint with its subnet and address, each PaaS service with the settings that matter, the shared platform services the project uses, the external systems it reaches, and everything still pending.
2. **Place the zones.** Follow `references/layout-and-style.md`. Fix the endpoint rows first: they set the height of the PaaS box and the position of the external band.
3. **Write the JSON** as the base skill requires, one section at a time, with stable descriptive IDs. Group each icon with its caption.
4. **Embed icons** with the base skill's helpers. Every depicted endpoint gets its own Private Endpoints icon.
5. **Validate and render** with the base skill: binding and orthogonality checks, collision pass, render, view the PNG, crop and view the dense regions, fix, and repeat.
6. **Check against this skill**: the checklist below.
7. **Link the drawing** from the design document, PNG first and the `.excalidraw` source beside it.

Save both files beside the design: `design-docs/<project>-<env>-architecture.excalidraw` and `.png`. A drawing that serves a multi-environment design may be named `<project>-architecture`.

## Delivery Checklist

- [ ] One environment; no placeholder tokens in any label
- [ ] Every endpoint, service, subnet, and address on the drawing is in the inventory, and every inventory item is on the drawing or deliberately left to the design document
- [ ] Zones, row rhythm, and icon sizes match `references/layout-and-style.md`
- [ ] Style tokens match: fonts, colors, boundary strokes, sharp corners
- [ ] Route colors follow the key, and the legend lists only the families drawn
- [ ] Every pending item is amber and names what is pending
- [ ] A consumed central AI service is drawn as its own box with endpoint, API Management, Foundry account, and call panel
- [ ] Title and subtitle follow the templates
- [ ] Base skill validation passed: bindings reciprocal, routes orthogonal, no collisions, every icon visible in the viewed PNG
- [ ] The design document links the PNG and the source

Report in the reply any service that has no cached icon and was drawn as a labeled box.
