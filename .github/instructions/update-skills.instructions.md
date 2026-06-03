# Update Architect Document Skills (Global Copilot)

Trigger: user says "update skills", "refresh skills", "sync skills", "update architect skills", or similar.

## Procedure

1. **Verify repo layout:**
```bash
REPO=/home/opc/architect-doc-skill
test -f "$REPO/skills/excalidraw-diagram/SKILL.md" && \
test -f "$REPO/skills/word-document/SKILL.md" && \
test -f "$REPO/skills/powerpoint-presentation/SKILL.md" && \
test -f "$REPO/skills/spreadsheet-document/SKILL.md" && \
test -f "$REPO/skills/pdf-document/SKILL.md" && \
test -f "$REPO/skills/_shared/office-tools/office_tools.py" && \
echo "OK: repo layout valid"
```

2. **If repo needs updating**, `cd $REPO && git pull` first.

3. **Copy all 6 skills + _shared to ~/.copilot/skills/:**
```bash
REPO=/home/opc/architect-doc-skill
for name in excalidraw-diagram word-document powerpoint-presentation spreadsheet-document pdf-document _shared; do
  rm -rf ~/.copilot/skills/"$name"
  cp -a "$REPO/skills/$name" ~/.copilot/skills/"$name"
done
```

4. **Verify:**
```bash
CURSOR=~/.copilot/skills
ls -1 "$CURSOR" | sort
# Expect: _shared  excalidraw-diagram  pdf-document  powerpoint-presentation  spreadsheet-document  word-document
test -f "$CURSOR/_shared/office-tools/office_tools.py" && echo "OK: office-tools"
find "$CURSOR" -maxdepth 2 -name .git -type d | grep . && echo "WARN: nested .git" || echo "OK: no nested .git"
for name in excalidraw-diagram word-document powerpoint-presentation spreadsheet-document pdf-document; do
  diff -q "$REPO/skills/$name/SKILL.md" "$CURSOR/$name/SKILL.md" && echo "OK: $name" || echo "DIFF: $name"
done
```

5. **Tell user:** "Skills updated. Reload VS Code (Ctrl+Shift+P → Developer: Reload Window)."

## Source of truth
- Repo: `/home/opc/architect-doc-skill`
- Install doc: `docs/AGENT-SKILL-INSTALL.md`
- Skills: `skills/` → `~/.copilot/skills/`