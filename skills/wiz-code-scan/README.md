# wiz-code-scan

Read Wiz Infrastructure-as-Code scan findings for a repository and place each finding of medium severity or above in one of four fix levels.

This is an editor-variant skill in `SKILL_BUNDLE`. Install renames `SKILL.<editor>.md` to `SKILL.md` and deletes the other variant files. `scripts/report_template.py` and `scripts/pil-logo.png` are shared. Codex uses the `name` and `description` in `SKILL.codex.md`.

| Editor | MCP call |
|--------|----------|
| Cursor | `user-wiz` |
| VS Code Copilot | `wiz-discover` and `wiz-execute` |
| Claude Code | `mcp__wiz__discover` and `mcp__wiz__execute` |
| Codex | `mcp__wiz` |
