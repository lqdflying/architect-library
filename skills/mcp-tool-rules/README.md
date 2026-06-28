# mcp-tool-rules

Scans enabled MCP servers, discovers tool schemas, and generates `.cursor/rules/mcp-*.mdc` rule files that document the correct `CallMcpTool` arguments for each tool.

## Why

Cursor has a known bug where `CallMcpTool` exposes `properties: []` for the `arguments` field. Models that follow the schema strictly send empty `arguments: {}`, causing MCP calls to fail. The generated rule files teach the agent the correct arguments for every tool.

## Usage

In a Cursor agent chat:

```
/mcp-tool-rules
```

Or describe what you need:

```
Generate MCP tool calling rules for all my servers
```

The skill walks through four phases:

1. **Discover servers** — reads `.cursor/mcp.json` and `~/.cursor/mcp.json`, shows a summary table
2. **Discover tools** — reads tool schemas from MCP descriptor files, source code, docs, or user input
3. **Generate rules** — writes `.cursor/rules/mcp-tools.mdc` (or per-server files if >20 tools)
4. **Validate** — reads back generated files, checks server names, parameter tables, and examples

## Dependencies

None. Uses only Cursor's built-in tools (Read, Write, Glob) and MCP filesystem access.
