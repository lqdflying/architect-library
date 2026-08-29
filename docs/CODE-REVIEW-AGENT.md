# code-review agent

Read-only custom agent for reviewing code with MCP and web cross-checks.

## Install

From the architect-library repo (scope to your editor):

```bash
bash scripts/install_library.sh agents cursor    # Cursor → ~/.cursor/agents/
bash scripts/install_library.sh agents copilot   # VS Code Copilot → ~/.copilot/agents/
```

Reload Cursor or VS Code after install.

## Invocation

| Editor | How |
|--------|-----|
| Cursor | Agent picker → **code-review**, or `/code-review review the PR diff` |
| Copilot | Agents dropdown → **code-review** |

## Behavior

1. Establish scope (diff, files, PR, commit, or `BASE_SHA`..`HEAD_SHA` range) using read-only git.
2. Review tests first — intent, coverage, and regression value.
3. When requirements or a plan are provided, check implementation alignment line by line.
4. Evaluate across five axes: correctness, readability, architecture, security, performance.
5. Trace logic through callers and callees before judging.
6. Report Strengths and Critical / Warning / Suggestion findings with file:line evidence.
7. Include a **Verification story** (tests reviewed, build checked, manual testing).
8. Cross-check technical claims via MCP and web search.
9. Give a merge verdict: **Ready to merge?** Yes | No | With fixes (approve when code health improves; block on Critical issues or clear regressions).
10. Never edit source files. For deep security review, recommend the **security-auditor** agent.
11. For commit/diff/PR/branch reviews, also **append** (never full-rewrite) findings to `/tmp/<topic>-handoff.md` per the Cursor user-global review-handoff protocol; source tree stays read-only.

Full prompt: [agents/code-review/INSTRUCTIONS.md](../agents/code-review/INSTRUCTIONS.md).

## Scope with git SHAs

When reviewing a task or commit range, pass:

- `BASE_SHA` — start commit (e.g. `origin/main` or task start)
- `HEAD_SHA` — end commit (usually `HEAD`)
- Brief description of what was built
- Requirements or plan text (optional but enables alignment check)

The agent runs `git diff BASE_SHA..HEAD_SHA` as primary scope.

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
| Copilot | `disallowedTools: edit`; `agents: []` (no subagent delegation) |
| Claude Code | `permissionMode: plan`; `disallowedTools: Edit, Write, NotebookEdit, MultiEdit` |

If the user asks for fixes, the agent reports only and suggests switching to the default implementation agent.

## Maintainer source

```
agents/code-review/
  README.md
  INSTRUCTIONS.md
  cursor.header.md
  copilot.header.md
  claude.header.md
```

After edits:

```bash
bash scripts/install_library.sh agents cursor    # or agents copilot
```
