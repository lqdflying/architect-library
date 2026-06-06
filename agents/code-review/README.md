# code-review

Read-only code review custom agent for Cursor and Copilot.

## When to use

- Review a PR, branch diff, or specific files
- Trace logic and find bugs, security issues, or convention drift
- Verify API usage, SQL, or framework behavior via MCP and web search

## Invocation

| Editor | How |
|--------|-----|
| Cursor | Agent picker → **code-review**, or `/code-review review this diff` |
| Copilot | Agents dropdown → **code-review** |

Requires global install: `bash scripts/install_library.sh agents` from the architect-library repo.

## MCP (recommended)

Use whatever MCP servers are enabled in the user's session:

- **user-context7** — library docs
- **user-microsoftdocs** — Microsoft / Azure docs
- **user-dbmcp** — database schema and SQL
- **user-tavily** — web search

## Enforcement

- Cursor: `readonly: true` in assembled agent file
- Copilot: `disallowedTools: edit`

See [docs/CODE-REVIEW-AGENT.md](../../docs/CODE-REVIEW-AGENT.md) for details.
