# Review handoff and reconciliation

Applies in every VS Code Copilot chat.

Before acting, read the `review-handoff` skill at `~/.copilot/skills/review-handoff/SKILL.md` when this turn does any of these:

- Reviews, audits, checks, or finds issues in a commit, diff, branch, file, or PR, or verifies another model's or agent's work.
- Fixes, triages, or reconciles findings from a `/tmp/<topic>-handoff.md` ledger or pasted review feedback.

That skill owns the append-only ledger at `/tmp/<topic>-handoff.md`, the reviewer and fixer roles, and the dispositions. Until you have read it, a review turn changes nothing in the repository under review, and an existing handoff file is never overwritten or truncated.
