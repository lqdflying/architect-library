# notion-mcp-ops

Operational reference for Notion MCP — fetch-before-write, CRUD patterns, formatting rules, and failure-mode avoidance.

## Install

Installed as part of the Architect Library:

```bash
bash scripts/install_library.sh all cursor    # Cursor
bash scripts/install_library.sh all copilot   # VS Code Copilot
```

This is an **editor-variant skill** — the install script selects the correct `SKILL.md` variant for your editor (Cursor uses server `plugin-notion-workspace-notion`; Copilot uses `notion`).

## Prerequisites

The Notion MCP server must be enabled:

- **Cursor**: Enable the Notion workspace plugin in Settings → MCP.
- **VS Code Copilot**: Enable the Notion plugin; server is typically `notion` in `.vscode/mcp.json`.

No additional runtime dependencies.

## Relationship to Notion plugin skills

The Notion plugin ships task-specific skills (`create-page`, `search`, `tasks-build`, etc.). This skill is the **operational layer** — when to fetch before write, how to format callouts/tables, and how to avoid silent `update_content` failures. Use both: plugin skills for workflows, this skill for reliable MCP operations.

## When to use

- Any Notion page create/read/update via MCP
- Formatting callouts, tables, toggles, code blocks in Notion content
- Debugging updates that appear to succeed but change nothing
- Multi-step edits (section renumbering, restructures, cross-references)

## Provenance

Adapted from `tmp/notion-mcp-ops.skill` with API corrections for current Notion MCP (`new_str` on `replace_content`, `insert_content`, schema-driven property names, editor-variant MCP invocation).
