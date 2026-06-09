# security-auditor

Read-only security review custom agent for Cursor and Copilot.

## When to use

- Security-focused review of a PR, diff, file, or system component
- Threat modeling (STRIDE) and trust-boundary analysis
- OWASP Top 10 and LLM Application security checks
- CVE and dependency advisory verification

## Invocation

| Editor | How |
|--------|-----|
| Cursor | Agent picker → **security-auditor**, or `/security-auditor audit auth.ts` |
| Copilot | Agents dropdown → **security-auditor** |

Install from the architect-library repo (scope to your editor):

```bash
bash scripts/install_library.sh agents cursor    # Cursor
bash scripts/install_library.sh agents copilot   # VS Code Copilot
```

Reports Critical/High/Medium/Low findings with file:line evidence, proof-of-concept notes for serious issues, and a release verdict (Yes / No / With fixes). Optional `BASE_SHA`..`HEAD_SHA` diff scope.

For general code quality review, use **code-review** instead.

## MCP (recommended)

- **user-tavily** / **WebSearch** — CVEs and advisories
- **user-context7** — library security APIs
- **user-microsoftdocs** — Azure / .NET security patterns

## Enforcement

- Cursor: `readonly: true` in assembled agent file
- Copilot: `disallowedTools: edit`; `agents: []`
- Claude Code: `permissionMode: plan`; `disallowedTools: Edit, Write, NotebookEdit, MultiEdit`

See [docs/SECURITY-AUDITOR-AGENT.md](../../docs/SECURITY-AUDITOR-AGENT.md) for details.
