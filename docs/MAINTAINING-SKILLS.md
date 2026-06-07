# Maintaining skills, agents, and agent guidance

Use this checklist when adding or changing **skills**, **custom agents**, **workflow steps**, or **dependencies** in **architect-library**. Scripts and README alone are not enough—agents read `SKILL.md` frontmatter, **`.cursor/rules/`**, and `docs/AGENT-SKILL-INSTALL.md`.

**Reviewing external ref material (`tmp/skills/`, etc.)?** Read [`.cursor/skills/absorb-reference-materials/SKILL.md`](../.cursor/skills/absorb-reference-materials/SKILL.md) first — ship only high-value install targets, harden existing skills/agents, ignore the rest. That skill is **not** in `SKILL_BUNDLE`. After absorb: audit [README.md](../README.md) per [readme-after-absorb.md](../.cursor/skills/absorb-reference-materials/references/readme-after-absorb.md) (skills/agents tables, documentation map, repository layout).

## New skill folder

Create `skills/<skill-name>/` with at minimum:

- [ ] `SKILL.md` — YAML `name` + **`description`** (include completion criteria)
- [ ] `README.md` — human setup summary
- [ ] `references/` — guides agents load from “Load First” in `SKILL.md`

Update **agent guidance** (all that apply):

- [ ] [`.cursor/rules/`](../.cursor/rules/) — execution row, deps if needed
- [ ] [AGENT-SKILL-INSTALL.md](AGENT-SKILL-INSTALL.md) — skill table, execution rules
- [ ] [README.md](../README.md) — Skills table, documentation map
- [ ] [scripts/install_library.sh](../scripts/install_library.sh) — add to `SKILL_BUNDLE`
- [ ] Run `bash scripts/install_library.sh skills cursor` (global patch from Cursor)

If the skill uses Office tools:

- [ ] [office-tools/README.md](../skills/_shared/office-tools/README.md)
- [ ] [office-tools/office_tools.py](../skills/_shared/office-tools/office_tools.py)

## New custom agent

Create `agents/<agent-name>/` with:

- [ ] `README.md` — catalog entry (purpose, MCP, invocation)
- [ ] `INSTRUCTIONS.md` — shared prompt body (no YAML frontmatter)
- [ ] `cursor.header.md` — Cursor frontmatter
- [ ] `copilot.header.md` — Copilot frontmatter

Update **agent guidance**:

- [ ] [scripts/install_library.sh](../scripts/install_library.sh) — add to `AGENT_BUNDLE`
- [ ] [docs/AGENTS.md](AGENTS.md) — catalog row
- [ ] [README.md](../README.md) — Custom agents table
- [ ] `.cursor/rules/architect-library-execution.mdc` — completion row if applicable
- [ ] Optional deep dive: `docs/<AGENT-NAME>-AGENT.md`
- [ ] Run `bash scripts/install_library.sh agents cursor`

**Do not** add agents under `skills/` or to `SKILL_BUNDLE`.

## New workflow step (existing skill)

- [ ] `skills/<skill>/SKILL.md` — numbered workflow + delivery checklist
- [ ] `skills/<skill>/references/<topic>.md`
- [ ] `.cursor/rules/architect-library-execution.mdc` — execution row
- [ ] [AGENT-SKILL-INSTALL.md](AGENT-SKILL-INSTALL.md) if agents often skip the step

## New dependency (Python, system, or npm)

- [ ] [install_deps.sh](../scripts/install_deps.sh) and/or skill-specific installers
- [ ] `SKILL.md` Setup section
- [ ] [README.md](../README.md) Prerequisites table
- [ ] `.cursor/rules/architect-library-execution.mdc` — dependency matrix
- [ ] **`SKILL.md` `description`** if the dep blocks delivery

## New `office_tools.py` command

- [ ] Implement and register in [office_tools.py](../skills/_shared/office-tools/office_tools.py)
- [ ] [office-tools/README.md](../skills/_shared/office-tools/README.md)
- [ ] Consuming skill `SKILL.md`
- [ ] `.cursor/rules/architect-library-execution.mdc` if repo-wide

## Skill `description` field (auto-invocation)

Update `description` when completion rules change (PowerPoint layout preview, Excalidraw PNG review, etc.).

## PR self-check

1. Grep for `architect-doc` — zero stale hits in docs/rules/scripts.
2. Confirm `.cursor/rules/` and `AGENT-SKILL-INSTALL.md` agree on execution rules.
3. If skills or agents changed, run `bash scripts/install_library.sh all cursor` and verify.
