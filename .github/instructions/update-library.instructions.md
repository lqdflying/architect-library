# Update Architect Library (VS Code Copilot)

**Read first:** [AGENTS.md](../../AGENTS.md) — cross-editor install contract (editor scope, commands, anti-patterns).

Trigger: user says **install library**, install the library, patch library, refresh library, update library, install skills and agents, sync library, update architect library, update skills, refresh skills, sync skills, update agents, or similar.

**You are in VS Code Copilot.** Follow **AGENTS.md** § Install library with **`all copilot`** only. Do not write `~/.cursor/` or `~/.claude/` unless the user explicitly asks for all editors.

Do **not** ask which editor, scope, library subset, or runtime set to install for trigger phrases above. Do **not** install Node.js/nvm when `npm` is missing — report the error per AGENTS.md.

Use partial installs only when the user explicitly asks:

- Skills only: `bash scripts/install_library.sh skills copilot`
- Agents only: `bash scripts/install_library.sh agents copilot`
- All editors: `bash scripts/install_library.sh` — **only** when user asks

## Procedure

1. **Verify repo layout:**

```bash
REPO=/home/opc/architect-library
test -f "$REPO/skills/excalidraw-diagram/SKILL.md" && \
test -f "$REPO/skills/word-document/SKILL.md" && \
test -f "$REPO/agents/code-review/INSTRUCTIONS.md" && \
test -f "$REPO/user-rules/cursor/review-handoff-reconciliation.mdc" && \
test -f "$REPO/scripts/install_library.sh" && \
test -f "$REPO/skills/_shared/office-tools/office_tools.py" && \
echo "OK: repo layout valid"
```

2. **If repo needs updating**, `cd $REPO && git pull` first.

3. **Install runtimes from the repo clone (do not skip):**

```bash
REPO=/home/opc/architect-library
cd "$REPO"
bash scripts/install_deps.sh
bash scripts/install_deps.sh office-system
```

If a runtime command fails because of missing permissions, sudo, network, or npm, report the exact failing command and error. Run `bash scripts/runtime_readiness.sh` — library install can still proceed; Word may work via python-docx; new PPT decks need pptxgenjs or a user template. See [AGENTS.md](../../AGENTS.md) capability matrix.

4. **Install both libraries globally (Copilot only):**

```bash
REPO=/home/opc/architect-library
cd "$REPO"
bash scripts/install_library.sh all copilot
```

5. **Verify (Copilot):**

```bash
test -f ~/.copilot/skills/_shared/office-tools/office_tools.py && echo "OK: copilot skills"
test -f ~/.copilot/skills/word-document/SKILL.md && echo "OK: copilot skills"
test -f ~/.copilot/skills/verification-before-completion/SKILL.md && echo "OK: verification skill"
test -f ~/.copilot/skills/newagentlink/SKILL.md && echo "OK: newagentlink skill"
test -f ~/.copilot/skills/api-and-interface-design/SKILL.md && echo "OK: api skill"
test -f ~/.copilot/skills/deprecation-and-migration/SKILL.md && echo "OK: deprecation skill"
test -f ~/.copilot/agents/code-review.agent.md && echo "OK: copilot agents"
test -f ~/.copilot/agents/security-auditor.agent.md && echo "OK: security-auditor"
grep -q 'disallowedTools: edit' ~/.copilot/agents/security-auditor.agent.md && echo "OK: security-auditor readonly"
cd /home/opc/architect-library/skills/_shared/office-tools && uv run python3 office_tools.py --help >/dev/null && echo "OK: office tools"
command -v soffice >/dev/null && command -v pdftoppm >/dev/null && echo "OK: office-system"
source /home/opc/architect-library/scripts/architect_env.sh
command -v npm >/dev/null && echo "OK: npm CLI" || echo "WARN: npm CLI missing"
test -d ~/.npm-global/lib/node_modules/docx && test -d ~/.npm-global/lib/node_modules/pptxgenjs && echo "OK: docx/pptxgenjs on disk"
cd /home/opc/architect-library/skills/_shared/office-tools && uv run python3 -c "import docx" && echo "OK: python-docx"
bash /home/opc/architect-library/scripts/runtime_readiness.sh
```

6. **Tell user:** "Library ready under ~/.copilot/ with runtimes installed. Reload VS Code (new agent chat)." If any runtime command failed, say "Library instructions were installed, but artifact runtime readiness is incomplete" and include the failing command plus `runtime_readiness.sh` output.

**PATH / npm globals:** `install_deps.sh` sources `scripts/architect_env.sh` and `install_node.sh` writes `~/.config/architect-library/env.sh` (+ `~/.bashrc` hook). Do **not** tell users pptxgenjs works via python-docx — only **Word** has that fallback; **new PPT decks** need pptxgenjs or a template. For manual Node in a shell: `source "$REPO/scripts/architect_env.sh"`.

## Source of truth

- Repo: `/home/opc/architect-library`
- Install doc: `docs/AGENT-SKILL-INSTALL.md`
- Skills: `skills/` → `~/.copilot/skills/`
- Agents: `agents/` → `~/.copilot/agents/`
- Cursor user-global rules (`user-rules/cursor/`) are Cursor-only — Copilot install does not copy them
