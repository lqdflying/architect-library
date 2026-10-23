# review-handoff

Review and fix protocol with a living ledger at `/tmp/<topic>-handoff.md`.
Reviewer and fixer rounds append to the same file until no **FIX** item
remains (**RECONCILED**). After each append, `scripts/purge_handoff.py`
moves closed rounds into `/tmp/<topic>-handoff-archive.md`. The active
file keeps the header, open items, and the two newest rounds.

Loaded on demand. Only the skill `name` and `description` stay in context
until the user explicitly asks for a code review or points at a handoff to fix.
A short always-on trigger keeps that load reliable:

| Editor | Trigger (always on) | Skill (on demand) |
|--------|---------------------|-------------------|
| Cursor | `~/.cursor/rules/review-handoff-reconciliation.mdc` | `~/.cursor/skills/review-handoff/SKILL.md` |
| VS Code Copilot | `review-handoff` fragment in `~/.copilot/copilot-instructions.md` | `~/.copilot/skills/review-handoff/SKILL.md` |
| Codex | `review-handoff` fragment in the active Codex home’s `AGENTS.md` | `~/.agents/skills/review-handoff/SKILL.md` |
| Claude Code | `~/.claude/rules/review-handoff.md` | `~/.claude/skills/review-handoff/SKILL.md` |

Installed for all four editors (listed in `SKILL_BUNDLE`).

This is **not** the `newagentlink` one-shot snapshot
(`/tmp/<topic>-newagentlink.md`).

## Install

Ships with Architect Library:

```bash
bash scripts/install_library.sh all cursor    # Cursor
bash scripts/install_library.sh all copilot   # VS Code Copilot
bash scripts/install_library.sh all claude    # Claude Code (opt-in)
```

The trigger needs the skill, so install both (`all`), not `rules` alone.

## When it loads

Only when the user explicitly asks for one of these:

- A code review of a commit, diff, branch, file, or PR (the user invoking the code-review or security-auditor agent counts)
- A fix, triage, or reconciliation that points at a `/tmp/*-handoff.md` file, or pastes that review and asks to fix it

Other tasks do not load it and do not get a ledger.

## Codex

Install with `bash scripts/install_library.sh all codex`. Skills live under
`~/.agents/skills/` globally or `.agents/skills/` in a project.
The generated Codex user-rule fragment triggers the same shared ledger protocol.
Read-only Codex custom agents return a labeled ledger round to the parent.
The parent appends it and purges closed rounds. Ordinary Codex sessions with
write access do both directly.
