# Update Architect Library (Global Copilot / Cursor)

Trigger: user says **install library**, install the library, patch library, refresh library, update library, install skills and agents, sync library, update architect library, update skills, refresh skills, sync skills, update agents, or similar.

**Default action:** full global install (`bash scripts/install_library.sh` with no args). Use partial installs only when the user explicitly asks for skills-only or agents-only.

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

3. **Install both libraries globally:**

```bash
REPO=/home/opc/architect-library
cd "$REPO"
bash scripts/install_library.sh
```

4. **Verify:**

```bash
test -f ~/.cursor/skills/_shared/office-tools/office_tools.py && echo "OK: cursor skills"
test -f ~/.copilot/skills/word-document/SKILL.md && echo "OK: copilot skills"
test -f ~/.cursor/agents/code-review.md && echo "OK: cursor agents"
test -f ~/.copilot/agents/code-review.agent.md && echo "OK: copilot agents"
grep -q 'readonly: true' ~/.cursor/agents/code-review.md && echo "OK: code-review readonly"
```

5. **Tell user:** "Library updated (skills + agents). Reload VS Code / Cursor (new agent chat)."

## Source of truth

- Repo: `/home/opc/architect-library`
- Install doc: `docs/AGENT-SKILL-INSTALL.md`
- Skills: `skills/` → `~/.cursor/skills/`, `~/.copilot/skills/`
- Agents: `agents/` → `~/.cursor/agents/`, `~/.copilot/agents/`
