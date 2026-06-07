# verification-before-completion

Discipline skill: require fresh command output before any completion or success claim.

## Install

Ships with Architect Library:

```bash
bash scripts/install_library.sh skills cursor    # Cursor
bash scripts/install_library.sh skills copilot   # VS Code Copilot
```

## When to use

- Before saying a task is done, tests pass, or a deliverable is ready
- Before delivering Office artifacts (validate, thumbnail, recalc evidence required)
- After agent delegation — verify via diff and commands, not reports alone

## Provenance

Patterns adapted from [Superpowers](https://github.com/obra/superpowers) `verification-before-completion` (obra).
