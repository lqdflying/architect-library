## Codex execution and review handoff

This section specializes the shared instructions for Codex. It takes precedence
over the shared prompt's permission to append to `/tmp` or use shell as an edit
tool workaround.

- Remain read-only, including `/tmp`. Do not request broader write permissions.
- Load the available `review-handoff` skill from its discovered location
  (`~/.agents/skills/review-handoff/SKILL.md` for a global install, or the project's
  `.agents/skills/review-handoff/SKILL.md`).
- Read the existing ledger when provided. Return a proposed ledger path and a
  complete labeled round for the parent agent to record using the skill's
  append-only protocol. Do not claim the ledger was written.
- The parent creates or appends the ledger and reports its path. If the parent
  cannot write it, report that limitation; do not bypass the sandbox.
- Keep the shared review report and evidence requirements. Discover actual MCP
  tools available in the session instead of assuming editor-specific tool names.
