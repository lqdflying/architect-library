# Update Architect Library (VS Code Copilot)

Trigger: user says **install library**, install the library, patch library, refresh library, update library, install skills and agents, sync library, update architect library, update skills, refresh skills, sync skills, update agents, or similar.

**Editor scope:** You are in **VS Code Copilot**. Install to **Copilot paths only** — do not write `~/.cursor/` or `~/.claude/` unless the user explicitly asks for all editors.

**Default action:** full global install for Copilot only:

```bash
bash scripts/install_library.sh all copilot
```

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

3. **Install both libraries globally (Copilot only):**

```bash
REPO=/home/opc/architect-library
cd "$REPO"
bash scripts/install_library.sh all copilot
```

4. **Verify (Copilot):**

```bash
test -f ~/.copilot/skills/_shared/office-tools/office_tools.py && echo "OK: copilot skills"
test -f ~/.copilot/skills/word-document/SKILL.md && echo "OK: copilot skills"
test -f ~/.copilot/agents/code-review.agent.md && echo "OK: copilot agents"
```

5. **Tell user:** "Library updated (skills + agents) under ~/.copilot/. Reload VS Code (new agent chat)."

## Source of truth

- Repo: `/home/opc/architect-library`
- Install doc: `docs/AGENT-SKILL-INSTALL.md`
- Skills: `skills/` → `~/.copilot/skills/`
- Agents: `agents/` → `~/.copilot/agents/`
