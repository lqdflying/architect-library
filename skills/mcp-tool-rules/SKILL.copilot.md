---
name: mcp-tool-rules
description: "Scan all enabled MCP servers, discover tool schemas, and generate .instructions.md files that document correct tool arguments. Use when: setting up MCP tools, adding new MCP servers, or MCP calls fail with wrong/missing arguments in VS Code Copilot."
---

# Generate MCP Tool Instruction Files (VS Code Copilot)

## Context

MCP tool calls can fail or produce unexpected results when the model guesses argument names,
types, or required fields incorrectly. This skill generates instruction files that document
the correct arguments for each tool, so VS Code Copilot always has an accurate reference.

## Execution

### Phase 1: Discover MCP servers

Read MCP config files in this order:
1. `.vscode/mcp.json` (project-level)
2. VS Code user `settings.json` — look for the `mcp.servers` or `mcp` section
   - Linux: `~/.config/Code/User/settings.json`
   - macOS: `~/Library/Application Support/Code/User/settings.json`
   - Remote/server: `~/.vscode-server/data/User/settings.json`

Extract every server entry. Present a summary table to the user:

| Server Name | Type | Status |
|-------------|------|--------|
| ...         | ...  | ...    |

Wait for user confirmation before proceeding.

### Phase 2: Discover tools per server

First, check the server type from config. If the entry has a `command` field, it is a local stdio server. If it has a `url` field, it is a remote HTTP/SSE server.

For each server, try these methods in order until one succeeds:

1. **Source code inspection** (stdio servers only): If the server is local, read its tool definition files — look for `tool()` decorators, `inputSchema`, Zod schemas, or Pydantic models. Skip this for remote HTTP/SSE servers.
2. **Documentation**: Check the server repo's README or official docs for tool specs.
3. **User input**: Ask the user to paste tool info from the VS Code MCP panel (Output > MCP log, or the tool list shown in chat).

For each tool, capture:
- Tool name
- Description
- Every input field: name, type, required/optional, default, allowed values
- Skip tools with zero arguments (they need no documentation)

### Phase 3: Generate instruction files

Generated files go into the project's `.github/instructions/` directory.

**Existing files:** If target `.instructions.md` files already exist, create a backup with `.bak` extension before overwriting. Report both the backup path and the new file path in the Phase 4 summary.

**Decision: single file or split**
- Total tools across all servers <= 20: single file `.github/instructions/mcp-tools.instructions.md`
- Total tools > 20: split into `.github/instructions/mcp-<server-name>.instructions.md` per server

**File template (single file):**

```markdown
---
description: "MCP tool arguments — reference when calling any MCP tool"
---

# MCP Tool Calling Reference

Always include all required arguments when calling MCP tools.
Do not guess argument names or types — use the documented parameters below.
If unsure about a required argument value, ask the user.

---

## Server: "<server-name-1>"

### tool_name_a
One-line description.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| ...   | ...  | ...      | ...     | ...         |

Example:
```json
{ "field1": "value1", "field2": 42 }
```

### tool_name_b
...

## Server: "<server-name-2>"
...
```

**File template (split, per server):**

```markdown
---
description: "MCP tool arguments for <server-name> — reference when calling any <server-name> tool"
---

# MCP Tools: <server-name>

Always include all required arguments when calling MCP tools.
Do not guess argument names or types — use the documented parameters below.

### tool_name_a
...
```

### Phase 4: Validate

After generating, perform these checks:
1. Read back every generated `.instructions.md` file
2. Verify every server name exactly matches the name in MCP config (case-sensitive)
3. Verify every tool has both a parameter table and an example call
4. Verify frontmatter is valid YAML with a `description` field
5. Report results to user:
   - Files generated (paths)
   - Total servers / tools documented
   - Any tools skipped (zero-arg) or servers that failed discovery

## Rules

- Server names in documentation MUST exactly match MCP config names — copy verbatim, do not rename
- One example per tool minimum, covering the most common use case
- For enum fields, list all allowed values in the Description column
- Do NOT fabricate parameter names — if discovery fails and user cannot provide info, skip that tool and note it in the report
- Do NOT include tools that require zero arguments
- Keep each generated file under 300 lines
- Do NOT add `applyTo` in frontmatter — the `description` field is sufficient for contextual activation
- Generated files are project-scoped (`.github/instructions/`), not user-global
