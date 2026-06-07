# README.md after absorption

Run this audit **after every absorb session** that ships, hardens, or changes install surface. Skip only if you confirm zero user-visible catalog change (rare).

## When README must change

| Absorb activity | Update README |
|---------------|---------------|
| New skill in `SKILL_BUNDLE` | Skills table + repository layout tree |
| New agent in `AGENT_BUNDLE` | Custom agents table + layout |
| Hardened skill/agent (behavior users notice) | Skills/agents table blurb if completion rules changed |
| New maintainer path (`tmp/`, `.cursor/skills/…`) | Documentation map + layout (if not already documented) |
| Ignore-only session, no source edits | Usually **no** README change |

## Sections to check (in order)

1. **Skills table** (top catalog) — row per distributable skill; one-line purpose.
2. **Custom agents table** — row per agent; invocation hint.
3. **Documentation map** — links to new/changed `SKILL.md`, agent docs, `tmp/README.md` if relevant.
4. **Repository layout** (`text` tree) — folder under `skills/` or `agents/`; keep `verification-before-completion` and other bundle members in sync.
5. **Installation** — only if install commands or editor paths changed (usually unchanged).

## Do not

- Paste ref prose into README — one-line catalog entries only.
- Duplicate full execution rules (those live in `AGENT-SKILL-INSTALL.md` and `.cursor/rules/architect-library-execution.mdc`).
- Forget README when you updated `AGENT-SKILL-INSTALL.md` — both catalogs should agree.

## Quick grep

From repo root after edits:

```bash
grep -n 'verification-before-completion\|<new-skill-name>\|<new-agent-name>' README.md
```

If the new install target appears in `install_library.sh` but not in README skills/agents table → **fix before closing the absorb session**.
