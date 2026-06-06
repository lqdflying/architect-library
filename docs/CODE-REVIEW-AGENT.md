# code-review agent

Read-only custom agent for reviewing code with MCP and web cross-checks.

## Install

From the architect-skill repo (global default):

```bash
bash scripts/install_library.sh agents
```

Installs to:

- `~/.cursor/agents/code-review.md`
- `~/.copilot/agents/code-review.agent.md`

Reload Cursor or VS Code after install.

## Invocation

| Editor | How |
|--------|-----|
| Cursor | Agent picker → **code-review**, or `/code-review review the PR diff` |
| Copilot | Agents dropdown → **code-review** |

## Behavior

1. Establish scope (diff, files, PR, commit) using read-only git.
2. Trace logic through callers and callees before judging.
3. Report Critical / Warning / Suggestion findings with file:line evidence.
4. Cross-check technical claims via MCP and web search.
5. Never edit source files.

Full prompt: [agents/code-review/INSTRUCTIONS.md](../agents/code-review/INSTRUCTIONS.md).

## MCP (use what is enabled in the session)

| Server | Use for |
|--------|---------|
| user-context7 | Library/framework API verification |
| user-microsoftdocs | Microsoft / Azure documentation |
| user-dbmcp | SQL and schema correctness |
| user-tavily | Web search for advisories and best practices |

Also use built-in **WebSearch** and **WebFetch** when MCP is unavailable.

## Enforcement

| Editor | Mechanism |
|--------|-----------|
| Cursor | `readonly: true` in assembled agent file |
| Copilot | `disallowedTools: edit`; all other tools enabled |

If the user asks for fixes, the agent reports only and suggests switching to the default implementation agent.

## Maintainer source

```
agents/code-review/
  README.md
  INSTRUCTIONS.md
  cursor.header.md
  copilot.header.md
```

After edits, run `bash scripts/install_library.sh agents`.
