---
name: mcp-tool-rules
description: "Scan all enabled MCP servers, discover tool schemas, and generate mdc rule files that document the correct CallMcpTool arguments. Use when: setting up MCP tools, adding new MCP servers, or MCP calls fail with missing arguments."
---

# Generate MCP Tool Calling Rules

## Context

Cursor has a known bug: `CallMcpTool` schema exposes `properties: []` for the `arguments` field.
Models that strictly follow schema send empty `arguments: {}`, causing MCP calls to fail.
This skill generates rule files that document the correct arguments for each tool.

## Execution

### Phase 1: Discover MCP servers

Read MCP config files in this order:
1. `.cursor/mcp.json` (project-level)
2. `~/.cursor/mcp.json` (user-level)

Extract every server entry. Present a summary table to the user:

| Server Name | Type | Status |
|-------------|------|--------|
| ...         | ...  | ...    |

Wait for user confirmation before proceeding.

### Phase 2: Discover tools per server

First, check the server type from `mcp.json`. If the entry has a `command` field, it is a local stdio server. If it has a `url` field, it is a remote HTTP/SSE server.

For each server, try these methods in order until one succeeds:

1. **MCP descriptor files** (preferred): Read JSON tool descriptors from the Cursor MCP cache at `~/.cursor/projects/<project-slug>/mcps/<server-name>/tools/*.json`. Each file contains the tool name, description, and full `arguments` JSON Schema. Works for both stdio and HTTP servers that Cursor has connected to.
2. **Source code inspection** (stdio servers only): If the server is local, read its tool definition files — look for `tool()` decorators, `inputSchema`, Zod schemas, or Pydantic models. Skip this for remote HTTP/SSE servers.
3. **Documentation**: Check the server repo's README or official docs for tool specs.
4. **User input**: Ask the user to paste tool info from Cursor Settings > MCP > [server] > Tools.

For each tool, capture:
- Tool name
- Description
- Every input field: name, type, required/optional, default, allowed values
- Skip tools with zero arguments (they are not affected by the bug)

### Phase 3: Generate rule files

Generated rules go into the project's `.cursor/rules/` directory.

**Existing files:** If target `.mdc` files already exist, create a backup with `.bak` extension before overwriting. Report both the backup path and the new file path in the Phase 4 summary.

**Decision: single file or split**
- Total tools across all servers <= 20: single file `.cursor/rules/mcp-tools.mdc`
- Total tools > 20: split into `.cursor/rules/mcp-<server-name>.mdc` per server

**File template (single file):**

```markdown
---
description: Fix Cursor CallMcpTool schema bug — always include arguments when calling any MCP tool
alwaysApply: true
---

# MCP Tool Calling Rules

ALWAYS include the `arguments` field when calling CallMcpTool.
The tool schema shown to you may omit it — this is a known Cursor bug.
NEVER send empty arguments `{}`.
If unsure about required arguments, ask the user.

Correct pattern:
CallMcpTool({ server: "<server>", toolName: "<tool>", arguments: { <params> } })

---

## Server: "<server-name-1>"

### tool_name_a
One-line description.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| ...   | ...  | ...      | ...     | ...         |

Example:
CallMcpTool({ server: "<server-name-1>", toolName: "tool_name_a", arguments: { field1: "value1" } })

### tool_name_b
...

## Server: "<server-name-2>"
...
```

**File template (split, per server):**

```markdown
---
description: "MCP tool arguments for <server-name> — use when calling any <server-name> tool"
alwaysApply: false
---

# MCP Tools: <server-name>

ALWAYS include `arguments` in CallMcpTool calls. NEVER send empty `{}`.

### tool_name_a
...
```

### Phase 4: Validate

After generating, perform these checks:
1. Read back every generated `.mdc` file
2. Verify every `server` value exactly matches the name in MCP config (case-sensitive)
3. Verify every tool has both a parameter table and an example call
4. Verify frontmatter is valid YAML with correct fields
5. Report results to user:
   - Files generated (paths)
   - Total servers / tools documented
   - Any tools skipped (zero-arg) or servers that failed discovery

## Rules

- `server` field values MUST exactly match MCP config names — copy verbatim, do not rename
- One example call per tool minimum, cover the most common use case
- For enum fields, list all allowed values in the Description column
- Do NOT fabricate parameter names — if discovery fails and user cannot provide info, skip that tool and note it in the report
- Do NOT include tools that require zero arguments
- Keep each generated file under 300 lines
