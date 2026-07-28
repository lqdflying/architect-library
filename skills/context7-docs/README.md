# context7-docs

Fetch current library, framework, SDK, API, and CLI documentation via the Context7 MCP server. Replaces training-data guesswork with live documentation lookups.

## Install

Installed as part of the Architect Library:

```bash
bash scripts/install_library.sh all cursor    # Cursor
bash scripts/install_library.sh all copilot   # VS Code Copilot
```

This is an **editor-variant skill** — the install script selects the correct `SKILL.md` variant for your editor (Cursor uses `user-context7` server name; Copilot uses `context7`).

## Prerequisites

The Context7 MCP server must be enabled in your editor:

- **Cursor**: Context7 is available as a built-in plugin (`context7-plugin`). Enable it in Settings > MCP.
- **VS Code Copilot**: Add the Context7 server to `.vscode/mcp.json` or VS Code user settings. See [Context7 documentation](https://context7.com) for setup.

No additional runtime dependencies are required.

## When to use

- Library or framework API questions
- Setup and configuration guidance
- Version migration help
- Library-specific debugging
- CLI tool usage
- Terraform provider documentation lookups

## Provenance

Refined from the Cursor-bundled `context7-mcp` plugin skill. Adds editor-variant MCP naming, rate-limit awareness, query decomposition guidance, fallback strategy, and cross-editor compatibility.
