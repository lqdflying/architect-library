# azure-iac-diagram

Agent skill that fixes the layout and style of the architecture diagram of an Azure IaC project, so every project diagram reads the same way: users and edge on the left, the compute VNet, the firewall, the private endpoint subnets, the project PaaS box on the right, a shared-platform band above, and an external-dependencies band and the Central AI service box below.

It builds on [`excalidraw-diagram`](../excalidraw-diagram/README.md). That skill owns the Excalidraw JSON, the official Azure and vendor icons, the validation rules, and the renderer. This skill adds only the design rules and does not copy any of those files.

## Setup

No runtime of its own. Rendering uses the Excalidraw renderer set up for `excalidraw-diagram`:

```bash
bash scripts/install_deps.sh excalidraw
```

Installed with the library for Cursor, VS Code Copilot, Claude Code, and Codex:

```bash
bash scripts/install_library.sh all cursor
bash scripts/install_library.sh all copilot
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | When to use, what it overrides in `excalidraw-diagram`, rules, workflow, delivery checklist |
| `references/layout-and-style.md` | Zone map and coordinates, row rhythm, style tokens, route key, routing, text templates |

## Change the house style

Edit `references/layout-and-style.md`. Keep the zone table, the style tokens, and the route key in that one file, and keep `SKILL.md` to rules and workflow. When a change replaces a rule of `excalidraw-diagram`, add it to the override table in `SKILL.md`.
