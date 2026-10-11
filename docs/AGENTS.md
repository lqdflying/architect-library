# Custom agents catalog

> **Repo agent guide (install library, editor scope):** [AGENTS.md](../AGENTS.md) at repository root.

Architect Library ships a **custom agent library** under `agents/`. Install globally with `bash scripts/install_library.sh agents cursor` or `agents copilot` (editor-scoped). Use `all codex` for the Codex agents plus their review-handoff skill and user instructions; `agents codex` refreshes only agents.

| Agent | Purpose | Invocation |
|-------|---------|--------------|
| [code-review](../agents/code-review/) | Read-only code review with MCP and web verification | Cursor: `/code-review` or agent picker. Copilot: agents dropdown. Codex: ask to use the agent by name |
| [security-auditor](../agents/security-auditor/) | Read-only security review — STRIDE, OWASP, LLM security, CVE checks | Cursor: `/security-auditor` or agent picker. Copilot: agents dropdown. Codex: ask to use the agent by name |

## Install targets (global default)

| Editor | Path |
|--------|------|
| Cursor | `~/.cursor/agents/<name>.md` |
| Copilot | `~/.copilot/agents/<name>.agent.md` |
| Claude Code | `~/.claude/agents/<name>.md` |
| Codex | `${CODEX_HOME:-$HOME/.codex}/agents/<name>.toml` |

Agents are assembled at install from `cursor.header.md` / `copilot.header.md` / `claude.header.md` + `INSTRUCTIONS.md`.

Codex agents combine `codex.json` metadata, the shared `INSTRUCTIONS.md`, and `agents/codex-review.md`. They inherit the model and request a read-only sandbox. Parent live sandbox and approval overrides take precedence over this default. Their instructions prohibit writes and require returning ledger entries to the parent for append-only recording; those instructions provide no sandbox enforcement in a writable parent session. Project installation writes `.codex/agents/` without changing `config.toml`. See the [Codex custom-agent format](https://learn.chatgpt.com/docs/agent-configuration/subagents).

## Adding an agent

See [MAINTAINING-SKILLS.md](MAINTAINING-SKILLS.md) → **New custom agent**.
