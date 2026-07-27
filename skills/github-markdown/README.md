# github-markdown

Agent skill for writing correct **GitHub Flavored Markdown (GFM)** on READMEs, issues, PRs, discussions, wikis, and repo documentation.

## Install

From the architect-library repo root:

```bash
# Cursor
bash scripts/install_library.sh all cursor

# VS Code Copilot
bash scripts/install_library.sh all copilot

# Both editors
bash scripts/install_library.sh all both
```

Install paths:

| Editor | Path |
|--------|------|
| Cursor | `~/.cursor/skills/github-markdown/` |
| VS Code Copilot | `~/.copilot/skills/github-markdown/` |
| Claude Code | `~/.claude/skills/github-markdown/` |

No runtime dependencies. Open a new agent chat after install so the skill description reloads.

## Official references

- [Basic writing and formatting syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
- [Working with advanced formatting](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting)
- [GitHub Flavored Markdown Spec](https://github.github.com/gfm/)

## Layout

| File | Purpose |
|------|---------|
| `SKILL.md` | Workflow, context matrix, writing rules, delivery checklist |
| `references/basic-syntax.md` | Headings through alerts |
| `references/advanced-formatting.md` | Tables, code, diagrams, math, collapsed sections |
| `references/context-and-pitfalls.md` | Context differences and before/after examples |
