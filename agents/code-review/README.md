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

Install from the architect-library repo (scope to your editor):

```bash
bash scripts/install_library.sh agents cursor    # Cursor
bash scripts/install_library.sh agents copilot   # VS Code Copilot
```

Reviews tests first, evaluates across five axes (correctness, readability, architecture, security, performance), reports Strengths and Critical/Warning/Suggestion findings, includes a verification story, requirements alignment when a plan is provided, and a merge verdict (Yes / No / With fixes). Optional `BASE_SHA`..`HEAD_SHA` diff scope. For deep security review, use **security-auditor**.

## MCP (recommended)

Use whatever MCP servers are enabled in the user's session:

- **user-context7** — library docs
- **user-microsoftdocs** — Microsoft / Azure docs
- **user-dbmcp** — database schema and SQL
- **user-tavily** — web search

## Enforcement

- Cursor: `readonly: true` in assembled agent file
- Copilot: `disallowedTools: edit`; `agents: []` (no subagent delegation)
- Claude Code: `permissionMode: plan`; `disallowedTools: Edit, Write, NotebookEdit, MultiEdit`

See [docs/CODE-REVIEW-AGENT.md](../../docs/CODE-REVIEW-AGENT.md) for details.
