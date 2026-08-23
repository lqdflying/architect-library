# newagentlink

One-shot continuation snapshot so a **new** agent can continue work without
the old transcript. The new agent reads `/tmp/<topic>-newagentlink.md` once
on the first turn, then ignores it.

This is **not** the review ledger (`/tmp/<topic>-handoff.md` from
`review-handoff-reconciliation`). Invoke with `/newagentlink`.

On Cursor, install also copies `cursor.command.md` to
`~/.cursor/commands/newagentlink.md` and removes leftover `/handoff`
(`~/.cursor/skills/handoff` and `~/.cursor/commands/handoff.md`).

## Install

Ships with Architect Library:

```bash
bash scripts/install_library.sh skills cursor    # Cursor
bash scripts/install_library.sh skills copilot   # VS Code Copilot
```

## When to use

- Context is too large and a new agent chat should continue the live task
- User asks for a new-agent brief or continuation file
- User types `/newagentlink`

Do **not** use this skill for code review findings. That protocol appends
`/tmp/<topic>-handoff.md`.

## Provenance

Adapted from the user-global `handoff` skill; renamed so it cannot collide
with the review-handoff ledger.
