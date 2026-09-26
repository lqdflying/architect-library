# review-handoff

Review and fix protocol with a living ledger at `/tmp/<topic>-handoff.md`.
Reviewer and fixer rounds append to the same file until no **FIX** item
remains (**RECONCILED**).

Loaded on demand. Only the skill `name` and `description` stay in context
until a turn reviews, audits, or fixes from a handoff. A short always-on
trigger keeps that load reliable:

| Editor | Trigger (always on) | Skill (on demand) |
|--------|---------------------|-------------------|
| Cursor | `~/.cursor/rules/review-handoff-reconciliation.mdc` | `~/.cursor/skills/review-handoff/SKILL.md` |
| VS Code Copilot | `review-handoff` fragment in `~/.copilot/copilot-instructions.md` | `~/.copilot/skills/review-handoff/SKILL.md` |

Installed for Cursor and Copilot only (listed in `EDITOR_VARIANT_SKILLS`).
Claude Code does not get this skill.

This is **not** the `newagentlink` one-shot snapshot
(`/tmp/<topic>-newagentlink.md`).

## Install

Ships with Architect Library:

```bash
bash scripts/install_library.sh all cursor    # Cursor
bash scripts/install_library.sh all copilot   # VS Code Copilot
```

The trigger needs the skill, so install both (`all`), not `rules` alone.

## When it loads

- Review, audit, check, or find issues in a commit, diff, branch, file, or PR
- Verify another model's or agent's work
- Fix, triage, or reconcile from a `/tmp/*-handoff.md` file or pasted review feedback
