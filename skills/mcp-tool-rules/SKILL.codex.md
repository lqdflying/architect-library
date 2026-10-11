---
name: mcp-tool-rules
description: Codex only. Discover available MCP tool schemas and generate project references with an AGENTS.md trigger for Codex. Use when setting up MCP tool documentation or correcting calls with wrong or missing arguments.
---

# Generate MCP tool references for Codex

> **Codex only.** If you are not running in Codex, stop and use this editor's own `mcp-tool-rules` skill instead.

## Discover servers and tools

Inspect the session's available MCP tools first. When needed, inspect
`[mcp_servers.<name>]` in the active Codex home's `config.toml` (`$CODEX_HOME`,
default `~/.codex`) and trusted project `.codex/config.toml`. Plugins can provide
servers too; configuration entries alone do not establish that tools are active.

Present the discovered servers, their transport, and availability. Continue for
the servers covered by the user's request; ask only when the intended selection
is unclear. Do not change configuration, authenticate, or disclose credential
values as part of generating documentation.

Use exposed tool schemas as the source of truth. For local stdio servers whose
schemas are unavailable, inspect their tool definitions. Otherwise consult
official server documentation. If a schema cannot be established, report that
gap; do not invent tools, arguments, or required fields. Discover actual Codex
tool names instead of constructing a Cursor or Copilot prefix.

For each tool with arguments, record its name, purpose, fields, types,
required/optional status, defaults, enum values, and a schema-valid example.
Do not invoke a mutating tool just to test the example.

## Generate references and a trigger

Write plain Markdown in the current project's `.agents/mcp-tools/`:

- Up to 20 tools: `mcp-tools.md`.
- More than 20 tools: `mcp-<server-name>.md` per server. Use filename-safe server
  slugs, checking that distinct names do not produce the same filename.

Use headings for servers and tools, parameter tables, and JSON argument examples.
Label the discovery date and schema source. Keep credentials out of examples.
Back up an existing reference before replacing it.

Add or replace only this block in the project's `AGENTS.md`, listing the files
actually generated:

```markdown
<!-- BEGIN architect-library-mcp-tools -->
Before calling a documented MCP tool, read its reference in
`.agents/mcp-tools/mcp-tools.md`. Use the current session's tool schema if it
differs, and flag stale documentation. Never guess required arguments.
<!-- END architect-library-mcp-tools -->
```

Preserve every byte outside this block. Append it when absent; stop for repair
if markers are duplicated, unmatched, or reversed. Do not overwrite project
instructions. If a nonempty `AGENTS.override.md` hides the trigger, explain the
conflict before writing and ask where the user wants the trigger integrated.
The global library's instruction block uses different markers; leave it intact.

## Verify and report

Read back the references and trigger. Check names, parameter tables, and examples
against the discovered schemas, verify all trigger paths exist, and confirm
unrelated project instructions are preserved. Report generated and backup paths,
documented tool counts, and any unavailable schemas.
