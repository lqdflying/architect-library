# Triage examples — absorb reference materials

Extended record of the Superpowers `tmp/skills/` review (negotiated session). Use as calibration when scoring new ref batches.

## Shipped

### `verification-before-completion` → `skills/verification-before-completion/`

- Iron Law + gate function + rationalization table
- Artifact rows: PPT thumbnail viewed, XLSX recalc success, DOCX validate, PDF form scripts
- Cross-linked from `powerpoint-presentation`, `spreadsheet-document`, `word-document`
- Added to `SKILL_BUNDLE`

## Hardened (no new install)

### `code-reviewer.md` → `agents/code-review/INSTRUCTIONS.md`

- `BASE_SHA` / `HEAD_SHA` diff scope
- Strengths section
- Merge verdict: Yes | No | With fixes

### `spec-reviewer-prompt.md` (abbreviated) → same agent

- Requirements alignment when plan provided
- Missing/extra scope — no separate `spec-compliance-review` agent

### Artifact skills

- Rationalization tables (“file exists”, “validated earlier”)
- `REQUIRED SUB-SKILL: verification-before-completion`

## Ignored (left in `tmp/skills/`)

| Folder | Reason |
|--------|--------|
| `receiving-code-review` | Implementer etiquette; niche |
| `requesting-code-review` | Redundant after stronger `code-review` |
| `systematic-debugging` | Generic dev |
| `test-driven-development` | Generic dev |
| `writing-plans` | Implementation micro-plans; `word-document` covers ADR/HLD deliverables |
| `writing-skills` | Meta-authoring — not for distribution |
| `using-superpowers` | Meta-router |
| `brainstorming` | Heavy scripts; not artifact-aligned |
| `subagent-driven-development` | Orchestration chain not shipped |
| `executing-plans` | Depends on subagent-driven |
| `finishing-a-development-branch` | Git menu workflow |
| `using-git-worktrees` | Niche |
| `dispatching-parallel-agents` | Orchestration only |

## Install outcome

- **Before:** 5 skills + 1 agent in bundle
- **After:** 6 skills + 1 agent (`verification-before-completion` added; `code-review` enhanced)
- **Cursor readiness install:** runtime setup, then `bash scripts/install_library.sh all cursor` only

## Closing step (example)

**Remaining low-value (maintainer view):** all ignored folders listed above still under `tmp/skills/` — generic dev workflow, meta skills, orchestration without the full Superpowers chain.

**Ask user:**

1. **Replan** — another pass with different scope or folders  
2. **Clean `tmp/`** — delete ignored ref material  
3. **Keep for now** — leave as local reference
