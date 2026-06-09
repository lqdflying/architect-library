# security-auditor agent

Read-only custom agent for security-focused code and configuration review.

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
| Cursor | Agent picker → **security-auditor**, or `/security-auditor audit the auth module` |
| Copilot | Agents dropdown → **security-auditor** |

## Behavior

1. Establish scope (diff, files, PR, commit, or `BASE_SHA`..`HEAD_SHA` range) using read-only git.
2. Map trust boundaries and apply STRIDE threat modeling.
3. Review input handling, auth, data protection, infrastructure, integrations, and LLM features (if present).
4. Report findings by severity (Critical / High / Medium / Low / Info) with file:line evidence.
5. Provide proof-of-concept notes for Critical/High issues.
6. Cross-check CVEs and advisories via MCP and web search.
7. Give a release verdict: **Safe to release?** Yes | No | With fixes.
8. Never edit source files.

Full prompt: [agents/security-auditor/INSTRUCTIONS.md](../agents/security-auditor/INSTRUCTIONS.md).

For general code quality (not security-focused), use **code-review** instead.

## Scope with git SHAs

When reviewing a change range, pass:

- `BASE_SHA` — start commit
- `HEAD_SHA` — end commit (usually `HEAD`)
- Brief description of the system or change under review

The agent runs `git diff BASE_SHA..HEAD_SHA` as primary scope.

## MCP (use what is enabled in the session)

| Server | Use for |
|--------|---------|
| user-tavily | CVEs, security advisories, OWASP guidance |
| user-context7 | Library security APIs |
| user-microsoftdocs | Microsoft / Azure security patterns |

Also use built-in **WebSearch** and **WebFetch** when MCP is unavailable.

## Enforcement

| Editor | Mechanism |
|--------|-----------|
| Cursor | `readonly: true` in assembled agent file |
| Copilot | `disallowedTools: edit`; `agents: []` |
| Claude Code | `permissionMode: plan`; `disallowedTools: Edit, Write, NotebookEdit, MultiEdit` |

## Maintainer source

```
agents/security-auditor/
  README.md
  INSTRUCTIONS.md
  cursor.header.md
  copilot.header.md
  claude.header.md
  references/security-checklist.md
```

After edits:

```bash
bash scripts/install_library.sh agents cursor    # or agents copilot
```
