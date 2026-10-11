# code-review

Read-only code review custom agent for Cursor, Copilot, Claude Code, and Codex.

## When to use

- Review a PR, branch diff, or specific files
- Trace logic and find bugs, security issues, or convention drift
- Verify API usage, SQL, or framework behavior via MCP and web search

## Invocation

| Editor | How |
|--------|-----|
| Cursor | Agent picker → **code-review**, or `/code-review review this diff` |
| Copilot | Agents dropdown → **code-review** |
| Codex | Ask Codex to use the `code-review` custom agent |

Install from the architect-library repo (scope to your editor):

```bash
bash scripts/install_library.sh agents cursor    # Cursor
bash scripts/install_library.sh agents copilot   # VS Code Copilot
bash scripts/install_library.sh all codex        # agents plus review-handoff skill and instructions
bash scripts/install_library.sh agents codex     # refresh agents only
```

Reviews tests first, evaluates across five axes (correctness, readability, architecture, security, performance), reports Strengths and Critical/Warning/Suggestion findings, includes a verification story, requirements alignment when a plan is provided, and a merge verdict (Yes / No / With fixes). Optional `BASE_SHA`..`HEAD_SHA` diff scope. For deep security review, use **security-auditor**.

## MCP (recommended)

Use whatever MCP servers are enabled in the user's session:

- **user-context7** — library docs
- **user-microsoftdocs** — Microsoft / Azure docs
- **user-dbmcp** — database schema and SQL
- **user-tavily** — web search

Codex discovers the actual MCP tool names in the session; the aliases above are examples.

## Enforcement

- Codex: generated TOML requests `sandbox_mode = "read-only"`; no model override. Parent live sandbox and approval overrides take precedence over this default. Instructions prohibit writes and require returning ledger rounds to the parent. In a writable parent session, those instructions provide no sandbox enforcement. See [Codex sandbox controls](https://learn.chatgpt.com/docs/agent-configuration/subagents#approvals-and-sandbox-controls).
- Cursor: `readonly: true` in assembled agent file
- Copilot: `disallowedTools: edit`; `agents: []` (no subagent delegation)
- Claude Code: `permissionMode: plan`; `disallowedTools: Edit, Write, NotebookEdit, MultiEdit`

See [docs/CODE-REVIEW-AGENT.md](../../docs/CODE-REVIEW-AGENT.md) for details.
