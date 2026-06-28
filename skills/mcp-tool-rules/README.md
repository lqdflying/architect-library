# mcp-tool-rules

Scans enabled MCP servers, discovers tool schemas, and generates editor-specific documentation files so the AI agent always calls each tool with correct arguments.

This skill has two variants — one per supported editor:

| Variant | File | Output |
|---------|------|--------|
| Cursor | `SKILL.cursor.md` | `.cursor/rules/mcp-*.mdc` |
| VS Code Copilot | `SKILL.copilot.md` | `.github/instructions/mcp-*.instructions.md` |

The install script activates the correct variant as `SKILL.md` at the destination.

## Why

MCP tool calls can fail or produce unexpected results when the model guesses argument names, types, or required fields incorrectly. Cursor has a specific bug where `CallMcpTool` exposes `properties: []` for the `arguments` field. The generated files document every tool's parameters so the agent never guesses.

## Usage

**Cursor:**

```
/mcp-tool-rules
```

**VS Code Copilot:**

```
Generate MCP tool calling instructions for all my servers
```

Both variants walk through the same four phases:

1. **Discover servers** — reads editor-specific MCP config, shows a summary table
2. **Discover tools** — reads tool schemas from descriptor files, source code, docs, or user input
3. **Generate rules/instructions** — writes rule files (Cursor: `.mdc`, Copilot: `.instructions.md`)
4. **Validate** — reads back generated files, checks server names, parameter tables, and examples

## Dependencies

None. Uses only built-in editor tools and MCP filesystem access.
