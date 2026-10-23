# Review handoff and reconciliation

Applies in every VS Code Copilot chat.

Write a handoff only when the user explicitly asks for one of these:

- A code review of a commit, diff, branch, file, or PR. The user invoking the code-review or security-auditor agent is that request.
- A fix, triage, or reconciliation that points at a `/tmp/<topic>-handoff.md` ledger, or pastes that review and asks to fix it.

Do not write a handoff on any other turn. Implementation, questions, planning, refactors, installs, and checking your own work do not get a ledger. Do not start one because code changed, or because an earlier turn in the chat was a review.

When one of those two cases applies, read the `review-handoff` skill at `~/.copilot/skills/review-handoff/SKILL.md` before acting. That skill owns the ledger at `/tmp/<topic>-handoff.md`, including the purge of closed rounds, the reviewer and fixer roles, and the dispositions. Until you have read it, do not change the repository under review and do not rewrite an existing handoff file.
