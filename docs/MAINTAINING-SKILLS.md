# Maintaining skills and agent guidance

Use this checklist when adding or changing **skills**, **workflow steps**, or **dependencies** in architect-doc-skill. Scripts and README alone are not enough—agents read `SKILL.md` frontmatter, **`.cursor/`** (project rules), and `docs/AGENT-SKILL-INSTALL.md`.

## New skill folder

Create `skills/<skill-name>/` with at minimum:

- [ ] `SKILL.md` — YAML `name` + **`description`** (include completion criteria: e.g. visual QA, required deps)
- [ ] `README.md` — human setup summary
- [ ] `references/` — guides agents load from “Load First” in `SKILL.md`

Update **agent guidance** (all that apply):

- [ ] [`.cursor/`](../.cursor/) — update `rules/*.mdc` (layout, execution, deps); add project Cursor config here if needed
- [ ] [AGENT-SKILL-INSTALL.md](AGENT-SKILL-INSTALL.md) — “What you are installing” table, execution rules, common mistakes
- [ ] [README.md](../README.md) — Skills table, documentation map, first-time preparation, example prompts if relevant
- [ ] [architecture-document-principles.md](../skills/_shared/architecture-document-principles.md) — cross-skill rules
- [ ] [scripts/install_deps.sh](../scripts/install_deps.sh) — new install target if the skill needs a runtime
- [ ] Add a new `.mdc` rule only if the skill needs always-on guidance beyond the two core rules

If the skill uses Office tools:

- [ ] [office-tools/README.md](../skills/_shared/office-tools/README.md) — command table
- [ ] [office-tools/office_tools.py](../skills/_shared/office-tools/office_tools.py) — CLI help string for new commands

## New workflow step (existing skill)

Example: “layout preview after validate”, “production-lessons for compliance DOCX”.

- [ ] `skills/<skill>/SKILL.md` — numbered workflow + delivery checklist
- [ ] `skills/<skill>/references/<topic>.md` — detailed steps (link from Load First)
- [ ] `.cursor/rules/architect-doc-skill-execution.mdc` — execution rules row updated
- [ ] [AGENT-SKILL-INSTALL.md](AGENT-SKILL-INSTALL.md) — execution rules + common mistakes if agents often skip the step
- [ ] [README.md](../README.md) — only if user-facing install or troubleshooting changes

## New dependency (Python, system, or npm)

Example: LibreOffice Impress, new `office_tools` command, Playwright, `pptxgenjs`.

- [ ] Installer: [install_deps.sh](../scripts/install_deps.sh) and/or `skills/_shared/office-tools/install_deps.sh` and/or skill-specific `references/install_deps.sh`
- [ ] `SKILL.md` Setup section — what’s required vs optional for **completing** tasks
- [ ] [README.md](../README.md) Prerequisites / first-time preparation table
- [ ] [AGENT-SKILL-INSTALL.md](AGENT-SKILL-INSTALL.md) “First-time machine setup” table
- [ ] `.cursor/rules/architect-doc-skill-execution.mdc` — dependency matrix
- [ ] **`SKILL.md` `description` frontmatter** — if the dep blocks delivery (e.g. PPT requires `office-system`)

After changing installers, run the install path once and smoke-test the feature (e.g. `thumbnail` on a sample `.pptx`).

## New `office_tools.py` command

- [ ] Implement in `skills/_shared/office-tools/<script>.py`
- [ ] Register in [office_tools.py](../skills/_shared/office-tools/office_tools.py) `COMMANDS`
- [ ] [office-tools/README.md](../skills/_shared/office-tools/README.md)
- [ ] Consuming skill `SKILL.md` decision table + workflow
- [ ] `.cursor/rules/architect-doc-skill-execution.mdc` if agents should use it repo-wide
- [ ] [MAINTAINING-SKILLS.md](MAINTAINING-SKILLS.md) — this file if it sets a new pattern

## Skill `description` field (auto-invocation)

Cursor/Copilot match skills via the YAML `description`. When completion rules change, update `description` in the same PR—for example:

- PowerPoint: mention mandatory layout preview + LibreOffice/Poppler
- Excalidraw: mention render-to-PNG and visual review
- Word: mention validation and deliverable-only `.docx`

## PR self-check

Before merge:

1. Grep for outdated paths or “optional” language that contradicts new mandatory steps.
2. Confirm `.cursor/rules/` and `AGENT-SKILL-INSTALL.md` agree on execution rules (whole `.cursor/` is tracked in git).
3. If you only changed human docs, ask whether agents still get wrong defaults—update `SKILL.md` / `description` and `.mdc` rules if yes.
