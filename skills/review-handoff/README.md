# review-handoff

Review and fix protocol with a living ledger at `/tmp/<topic>-handoff.md`.
Reviewer and fixer rounds append to the same file until no **FIX** item
remains (**RECONCILED**). After each append, `scripts/purge_handoff.py`
moves closed rounds into `/tmp/<topic>-handoff-archive.md`. The active
file keeps the header, open items, and the two newest rounds.

Loaded on demand. Only the skill `name` and `description` stay in context
until a turn reviews, audits, or fixes from a handoff. A short always-on
trigger keeps that load reliable:

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

- Review, audit, check, or find issues in a commit, diff, branch, file, or PR
- Verify another model's or agent's work
- Fix, triage, or reconcile from a `/tmp/*-handoff.md` file or pasted review feedback

## Codex

Install with `bash scripts/install_library.sh all codex`. Skills live under
`~/.agents/skills/` globally or `.agents/skills/` in a project.
The generated Codex user-rule fragment triggers the same shared ledger protocol.
Read-only Codex custom agents return a labeled ledger round to the parent.
The parent appends it and purges closed rounds. Ordinary Codex sessions with
write access do both directly.
