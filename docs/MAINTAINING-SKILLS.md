# Maintaining skills, agents, user-global rules, and agent guidance

Use this checklist when adding or changing **skills**, **custom agents**, **Cursor user-global rules**, **workflow steps**, or **dependencies** in **architect-library**. Scripts and README alone are not enough—agents read `SKILL.md` frontmatter, **`.cursor/rules/`**, and `docs/AGENT-SKILL-INSTALL.md`.

**Reviewing external ref material (`tmp/skills/`, etc.)?** Read [`.cursor/skills/absorb-reference-materials/SKILL.md`](../.cursor/skills/absorb-reference-materials/SKILL.md) first — ship only high-value install targets, harden existing skills/agents, ignore the rest. That skill is **not** in `SKILL_BUNDLE`. After absorb: audit [README.md](../README.md) per [readme-after-absorb.md](../.cursor/skills/absorb-reference-materials/references/readme-after-absorb.md) (skills/agents tables, documentation map, repository layout).

## One skill file or one file per editor

A skill is one `SKILL.md` unless that file would tell another editor to use the wrong MCP server name, call syntax, config path, or output file.

A skill install writes a single `SKILL.md`.

### Shared skill

Use one `skills/<name>/SKILL.md` and add the folder to `SKILL_BUNDLE`.

The installer copies that folder unchanged to Cursor, Copilot, Claude Code, and Codex. One file may name each editor's install path. `pdf-document` and `iac-handoff-pdf` do this.

Keep one `SKILL.md` when the skill only mentions MCP. `excalidraw-diagram` does this.

An editor-only install hook stays beside that `SKILL.md`. `newagentlink` keeps `cursor.command.md` (copied to `~/.cursor/commands/` on a global Cursor install) and `agents/openai.yaml` (Codex explicit invocation). A new hook needs an installer change.

### Editor-variant skill

Write `SKILL.cursor.md`, `SKILL.copilot.md`, and `SKILL.codex.md`. Do not also commit `SKILL.md`. Keep the bundle string identical in [`.cursor/rules/architect-library-patch.mdc`](../.cursor/rules/architect-library-patch.mdc).

A variant with those three files goes in `EDITOR_VARIANT_SKILLS`. Claude Code does not receive that list.

A variant that also has `SKILL.claude.md` goes in `SKILL_BUNDLE`. That install path renames `SKILL.<editor>.md` for all four editors. Mark the Codex file Codex-only, because Cursor and Copilot also load `~/.agents/skills/`.

On install, the matching file is renamed to `SKILL.md` and the other `SKILL.*.md` files are deleted.

Each variant:

- uses the same YAML `name`
- states only that editor's server name, call syntax, config path, and output path
- loads procedure that is the same for every editor from `references/`

When you change a variant, put a shared step in `references/` instead of pasting it into the other variant files.

| Skill | What differs |
|:------|:-------------|
| `mcp-tool-rules` | Output file (`.mdc`, `.instructions.md`, or `.agents/mcp-tools/` plus an `AGENTS.md` block) and the discovery path |
| `context7-docs` | MCP server name and call syntax |
| `notion-mcp-ops` | MCP server name and call syntax |
| `wiz-code-scan` | MCP call, including a Claude Code file. Shared report files live in `scripts/`. Installed from `SKILL_BUNDLE` |

## New skill folder

Decide shared or editor-variant above before creating files.

Create `skills/<skill-name>/` with at minimum:

- [ ] `SKILL.md`, or `SKILL.cursor.md` + `SKILL.copilot.md` + `SKILL.codex.md` — YAML `name` + **`description`** (include completion criteria)
- [ ] `README.md` — human setup summary; an editor-variant README names the server or output file per editor
- [ ] `references/` — guides agents load from “Load First” in the skill file; shared steps for an editor-variant skill live here

Update **agent guidance** (all that apply):

- [ ] [`.cursor/rules/`](../.cursor/rules/) — execution row, deps if needed
- [ ] [AGENT-SKILL-INSTALL.md](AGENT-SKILL-INSTALL.md) — skill table, execution rules
- [ ] [README.md](../README.md) — Skills table, documentation map
- [ ] [scripts/install_library.sh](../scripts/install_library.sh) — add a shared skill, or a variant that includes `SKILL.claude.md`, to `SKILL_BUNDLE`. Add a Cursor/Copilot/Codex-only variant to `EDITOR_VARIANT_SKILLS`
- [ ] Run full readiness: `bash scripts/install_deps.sh`, `bash scripts/install_deps.sh office-system`, then `bash scripts/install_library.sh all cursor` and `bash scripts/install_library.sh all copilot`

If the skill uses Office tools:

- [ ] [office-tools/README.md](../skills/_shared/office-tools/README.md)
- [ ] [office-tools/office_tools.py](../skills/_shared/office-tools/office_tools.py)

## New custom agent

Create `agents/<agent-name>/` with:

- [ ] `README.md` — catalog entry (purpose, MCP, invocation)
- [ ] `INSTRUCTIONS.md` — shared prompt body (no YAML frontmatter)
- [ ] `cursor.header.md` — Cursor frontmatter
- [ ] `copilot.header.md` — Copilot frontmatter
- [ ] `claude.header.md` — Claude Code frontmatter
- [ ] `codex.json` — Codex name + description; shared instructions and `agents/codex-review.md` are serialized into TOML by the installer

Update **agent guidance**:

- [ ] [scripts/install_library.sh](../scripts/install_library.sh) — add to `AGENT_BUNDLE`
- [ ] [docs/AGENTS.md](AGENTS.md) — catalog row
- [ ] [README.md](../README.md) — Custom agents table
- [ ] `.cursor/rules/architect-library-execution.mdc` — completion row if applicable
- [ ] Optional deep dive: `docs/<AGENT-NAME>-AGENT.md`
- [ ] Run full readiness: `bash scripts/install_deps.sh`, `bash scripts/install_deps.sh office-system`, then `bash scripts/install_library.sh all cursor` and `bash scripts/install_library.sh all copilot`

**Do not** add agents under `skills/` or to `SKILL_BUNDLE`.

## New user-global Cursor rule

Create `user-rules/cursor/<name>.mdc` with YAML frontmatter:

- [ ] `description` — what the rule does
- [ ] `alwaysApply: true` (user-global protocol) or `globs` + `alwaysApply: false` (file-triggered)
- [ ] Body is the protocol agents must follow in **any** Cursor project after install

Update **agent guidance**:

- [ ] [scripts/install_library.sh](../scripts/install_library.sh) — add the filename (no `.mdc`) to `CURSOR_RULE_BUNDLE`
- [ ] [README.md](../README.md) — layout + documentation map; distinguish from maintainer `.cursor/rules/`
- [ ] [AGENT-SKILL-INSTALL.md](AGENT-SKILL-INSTALL.md) — user-global rules table + verify commands
- [ ] [AGENTS.md](../AGENTS.md) — Cursor install target `~/.cursor/rules/`
- [ ] `.cursor/rules/architect-library-repo.mdc` and `architect-library-patch.mdc` — layout + bundle string
- [ ] Run `bash scripts/install_library.sh rules cursor` and `bash scripts/install_library.sh rules copilot` (or full `all cursor` and `all copilot`)

**Do not** copy `user-rules/cursor/` into this repo’s `.cursor/rules/` (those files are maintainer-only for architect-library). **Do not** add user-global rules to `SKILL_BUNDLE` or `AGENT_BUNDLE`. Cursor Settings → Customize → Rules is a different store — install does not write it. One protocol only: edit `user-rules/cursor/<name>.mdc` and reinstall; add retired filenames to `LEGACY_CURSOR_RULES` so `~/.cursor/rules/` cannot keep a second copy.

## Copilot always-on instruction

Fragments: `user-rules/copilot/response-style.md`, `user-rules/copilot/edit-scope.md`, `user-rules/copilot/branch-strategy.md`, `user-rules/copilot/review-handoff.md`, `user-rules/copilot/docs-lookup.md`, and `user-rules/copilot/temp-validators.md`. Plain Markdown. No `alwaysApply` frontmatter. Install concatenates them, in that order, to `~/.copilot/copilot-instructions.md`.

The fragments are generated. Edit the Cursor source in `user-rules/cursor/`, then run `bash scripts/sync_copilot_rules.sh`, `bash scripts/sync_codex_rules.sh`, and `bash scripts/sync_claude_rules.sh`. Install verify runs `--check` and fails on drift.

- [ ] New fragment: add the `cursor:copilot` name pair to `PAIRS` in [scripts/sync_copilot_rules.sh](../scripts/sync_copilot_rules.sh) and the name to `COPILOT_INSTRUCTION_FRAGMENTS`
- [ ] Review handoff: edit the protocol in `skills/review-handoff/SKILL.md`; `review-handoff-reconciliation.mdc` stays a short trigger that points at it
- [ ] Each fragment says it applies in every VS Code Copilot chat
- [ ] [scripts/install_library.sh](../scripts/install_library.sh) concatenates the fragments on global `copilot` or `both` rules install
- [ ] Project scope does not write `.github/copilot-instructions.md`
- [ ] Run `bash scripts/install_library.sh rules copilot`

## Codex skills and user instructions

- [ ] Every shared skill installs to `~/.agents/skills/`. An editor-variant skill follows [One skill file or one file per editor](#one-skill-file-or-one-file-per-editor): `SKILL.codex.md` is installed as `SKILL.md`, and the installer deletes the other variant files.
- [ ] Adapt actual tool discovery, Codex configuration paths, and invocation syntax; do not copy Cursor or Copilot tool prefixes.
- [ ] `newagentlink/agents/openai.yaml` preserves explicit-only invocation in Codex.
- [ ] Generate all six `user-rules/codex/` fragments from Cursor sources with `bash scripts/sync_codex_rules.sh`; never hand-edit them.
- [ ] New rule: update `PAIRS` in all three sync scripts and the instruction fragment bundles in the installer.
- [ ] Global instructions live in the marked Architect Library block in `${CODEX_HOME:-$HOME/.codex}/AGENTS.md`; preserve personal content outside it.
- [ ] Project installs leave `AGENTS.md` untouched. A rules-only global install requires the `review-handoff` skill already present.
- [ ] Run `bash scripts/sync_codex_rules.sh --check` and `python3 -m unittest discover -s scripts -p 'test_install_library.py'` (test runner needs Python 3.11+).
- [ ] When Codex is the requested target, run runtime setup followed by `bash scripts/install_library.sh all codex`; otherwise keep the default Cursor + Copilot pair.
- [ ] Check a fresh Codex session discovers skills and both custom agents; report discovery as unverified if Codex cannot run.

## Claude Code user rules

- [ ] Generate all six `user-rules/claude/` fragments from Cursor sources with `bash scripts/sync_claude_rules.sh`; never hand-edit them.
- [ ] Global install copies them to `~/.claude/rules/<name>.md` (`CLAUDE_RULE_BUNDLE`). It never edits `~/.claude/CLAUDE.md`. Project scope does not write `.claude/rules/`.
- [ ] A rules-only global install requires the `review-handoff` skill already present in `~/.claude/skills/`.
- [ ] Run `bash scripts/sync_claude_rules.sh --check` and the installer tests, then `bash scripts/install_library.sh all claude` when Claude Code is the requested target.

## New workflow step (existing skill)

- [ ] `skills/<skill>/SKILL.md` — numbered workflow + delivery checklist
- [ ] `skills/<skill>/references/<topic>.md`
- [ ] `.cursor/rules/architect-library-execution.mdc` — execution row
- [ ] [AGENT-SKILL-INSTALL.md](AGENT-SKILL-INSTALL.md) if agents often skip the step

## New dependency (Python, system, or npm)

- [ ] [install_deps.sh](../scripts/install_deps.sh) and/or skill-specific installers
- [ ] `SKILL.md` Setup section
- [ ] [README.md](../README.md) Prerequisites table
- [ ] [AGENTS.md](../AGENTS.md) § Runtime capability matrix (if artifact delivery affected)
- [ ] `.cursor/rules/architect-library-execution.mdc` — dependency matrix
- [ ] **`SKILL.md` `description`** if the dep blocks delivery
- [ ] After install script changes: `bash scripts/runtime_readiness.sh` reflects new deps

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
3. If skills, agents, or user-global rules changed, run full editor-scoped readiness install and verify runtimes plus installed files.
