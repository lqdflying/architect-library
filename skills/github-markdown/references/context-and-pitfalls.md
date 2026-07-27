# Context, Pitfalls, and Examples

## Context-specific behavior

### Repo `.md` files (README, docs/, etc.)

- Single newlines do **not** create line breaks — use two trailing spaces, `\`, or `<br/>`.
- `#123` does **not** autolink — use full URLs: `https://github.com/owner/repo/issues/123`.
- Color swatches in backticks do not render.
- Relative links and images work and survive branch switches.
- Footnotes, Mermaid, math, alerts, and task lists all work.

### Issues, pull requests, discussions

- Single newlines create line breaks.
- `#123`, `GH-123`, `@mentions`, and bare URLs autolink.
- Color swatches in backticks render.
- Task lists referencing issues unfurl with title and state.

### Wikis

- Same line-break rules as `.md` files.
- **Footnotes not supported** — use inline text or link out.
- Issue/PR autolinks (`#123`) **not supported**.
- Mermaid, math, alerts, and task lists generally work.

## Anti-patterns

| Wrong | Right |
|-------|-------|
| Generic Markdown only on GitHub | Use GFM: alerts, task lists, autolinks where supported |
| Footnotes in wiki pages | Plain text or external link |
| `#123` in README expecting a link | Full issue URL or prose reference |
| No blank line before table | Blank line before table header row |
| HTML entities for symbols (`&copy;`) | Literal Unicode (`©`) |
| Cursor code-citation fences (` ```12:15:path `) | Standard ` ```language ` fenced block |
| More than 2 alerts per doc | 1–2 alerts maximum |
| Consecutive alerts | Separate with body content |
| Mermaid node ID `User Service` | `UserService` or `user_service` |
| Mermaid `style` / `classDef` colors | Theme-neutral diagrams only |
| Broken multi-line link text | Single-line `[text](url)` |
| Absolute blob URLs for in-repo files | `docs/guide.md` or `/docs/guide.md` |

## Example 1: README section

### Before (broken)

```markdown
## Setup
Clone the repo then run install
[Full
guide](docs/SETUP.md)
| Step | Command |
| git clone | `git clone ...` |
```

Problems: no blank line before table; broken link text; table missing separator row.

### After (correct)

```markdown
## Setup

Clone the repository, then follow the [setup guide](docs/SETUP.md).

| Step | Command |
| --- | --- |
| Clone | `git clone https://github.com/org/repo.git` |
| Install | `npm install` |
```

## Example 2: Pull request description

### Before (context misuse)

```markdown
Fixes #42

Changes:
- updated handler

[^1]: See design doc for rationale.
```

Problems: footnote in a PR is unusual; task list would be clearer; no alert for breaking change.

### After (correct)

```markdown
Fixes #42

> [!WARNING]
> Removes the deprecated `v1/status` endpoint. Clients must migrate to `v2/status`.

## Changes

- [x] Update request handler
- [x] Add migration note to CHANGELOG
- [ ] \(Optional) Announce in #releases

Related: #38, org/other-repo#12
```

## Example 3: Documentation table with code

### Before

```markdown
### Commands
| Command | Description |
| `git status` | Shows status |
```

Problems: no blank line before table; missing header separator.

### After

```markdown
### Commands

| Command | Description |
| --- | --- |
| `git status` | List **new or modified** files |
| `git diff` | Show unstaged changes |
| `git log \| head` | Show recent commits (pipe escaped) |
```

## Mermaid checklist

Before delivering Mermaid in GitHub markdown:

- [ ] Node IDs use camelCase, PascalCase, or underscores — no spaces
- [ ] Edge labels with `()` or `:` are quoted
- [ ] Subgraph titles with special chars are in double quotes
- [ ] No `style`, `classDef`, or explicit fill colors
- [ ] Tested against GitHub rendering (not only other Mermaid viewers)

## Heading anchor maintenance

When renaming or reordering headings, update all `#anchor` links. Duplicate headings produce `-1`, `-2` suffixes — verify links after edits.

```markdown
## API Overview
[Details](#api-overview)

## API Overview
[First section](#api-overview)
[Second section](#api-overview-1)
```
