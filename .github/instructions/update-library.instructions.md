# Update Architect Library (VS Code Copilot)

Trigger: user says **install library**, install the library, patch library, refresh library, update library, install skills and agents, sync library, update architect library, update skills, refresh skills, sync skills, update agents, or similar.

**Editor scope:** You are in **VS Code Copilot**. Install to **Copilot paths only** — do not write `~/.cursor/` or `~/.claude/` unless the user explicitly asks for all editors.

**Default action:** full Copilot readiness install — runtimes, skills, and agents:

```bash
bash scripts/install_deps.sh
bash scripts/install_deps.sh office-system
npm install -g docx pptxgenjs
bash scripts/install_library.sh all copilot
```

Do **not** ask which editor, scope, library subset, or runtime set to install for trigger phrases above. In VS Code Copilot, the default is already decided: **full global readiness for Copilot only**. Ask only when the user explicitly requests a non-default target but leaves that target ambiguous.

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
npm install -g docx pptxgenjs
```

If a runtime command fails because of missing permissions, sudo, network, or npm, report the exact failing command and error. Do not claim full readiness until all runtime commands finish successfully.

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
test -f ~/.copilot/skills/api-and-interface-design/SKILL.md && echo "OK: api skill"
test -f ~/.copilot/skills/deprecation-and-migration/SKILL.md && echo "OK: deprecation skill"
test -f ~/.copilot/agents/code-review.agent.md && echo "OK: copilot agents"
test -f ~/.copilot/agents/security-auditor.agent.md && echo "OK: security-auditor"
grep -q 'disallowedTools: edit' ~/.copilot/agents/security-auditor.agent.md && echo "OK: security-auditor readonly"
cd /home/opc/architect-library/skills/_shared/office-tools && uv run python3 office_tools.py --help >/dev/null && echo "OK: office tools"
command -v soffice >/dev/null && command -v pdftoppm >/dev/null && echo "OK: office-system"
npm list -g docx pptxgenjs --depth=0 >/dev/null && echo "OK: npm docx/pptxgenjs"
```

6. **Tell user:** "Library ready under ~/.copilot/ with runtimes installed. Reload VS Code (new agent chat)." If any runtime command failed, say "Library instructions were installed, but runtime readiness is incomplete" and include the failing command.

## Source of truth

- Repo: `/home/opc/architect-library`
- Install doc: `docs/AGENT-SKILL-INSTALL.md`
- Skills: `skills/` → `~/.copilot/skills/`
- Agents: `agents/` → `~/.copilot/agents/`
