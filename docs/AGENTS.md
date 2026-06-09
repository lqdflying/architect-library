# Custom agents catalog

> **Repo agent guide (install library, editor scope):** [AGENTS.md](../AGENTS.md) at repository root.

Architect Library ships a **custom agent library** under `agents/`. Install globally with `bash scripts/install_library.sh agents cursor` or `agents copilot` (editor-scoped).

| Agent | Purpose | Invocation |
|-------|---------|--------------|
| [code-review](../agents/code-review/) | Read-only code review with MCP and web verification | Cursor: `/code-review` or agent picker. Copilot: agents dropdown |
| [security-auditor](../agents/security-auditor/) | Read-only security review — STRIDE, OWASP, LLM security, CVE checks | Cursor: `/security-auditor` or agent picker. Copilot: agents dropdown |

## Install targets (global default)

| Editor | Path |
|--------|------|
| Cursor | `~/.cursor/agents/<name>.md` |
| Copilot | `~/.copilot/agents/<name>.agent.md` |
| Claude Code | `~/.claude/agents/<name>.md` |

Agents are assembled at install from `cursor.header.md` / `copilot.header.md` / `claude.header.md` + `INSTRUCTIONS.md`.

## Adding an agent

See [MAINTAINING-SKILLS.md](MAINTAINING-SKILLS.md) → **New custom agent**.
