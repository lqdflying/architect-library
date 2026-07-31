---
name: notion-mcp-ops
description: >-
  Authoritative reference for operating Notion via the Notion MCP — CRUD operations,
  content formatting (callouts, tables, toggles, code blocks), and failure-avoidance
  patterns. Use whenever you need to create, read, update Notion pages; format content
  with callouts, tables, toggles, or code blocks; troubleshoot silent update failures or
  content absorption bugs; or design multi-step Notion editing workflows. Trigger when the
  user mentions Notion, update my notes, add to the page, create a new page, callout,
  notion table, or references any Notion page ID.
---

# Notion MCP Operations (VS Code Copilot)

Use the **Notion MCP server** for all Notion workspace operations. Training-data assumptions about Notion APIs are unreliable — follow this skill and live tool schemas.

> **MCP server name**: The Notion plugin registers as `notion` in `.vscode/mcp.json` or VS Code user settings. If tool calls fail with "server not found", check your MCP configuration for the actual server name.

## Load first

| Reference | When |
|-----------|------|
| [references/formatting.md](references/formatting.md) | Callouts, tables, toggles, code blocks, headings |
| [references/failure-modes.md](references/failure-modes.md) | Silent failures, anchors, multi-step edits |
| `notion://docs/enhanced-markdown-spec` | Before writing unfamiliar Markdown — fetch via `notion-fetch` |

## When to use

- Create, read, update Notion pages or database entries
- Search workspace or query databases
- Format Notion content (callouts, tables, toggles)
- Troubleshoot updates that appear to succeed but change nothing
- Multi-step page edits (renumbering, restructuring, cross-references)

## When NOT to use

- General markdown or documentation outside Notion (use `github-markdown`)
- Code review or security audit (use custom agents)
- Notion operations when MCP is not enabled — tell the user to enable the Notion plugin first

## Tool catalog

### Primary (CRUD)

| Tool | Purpose |
|------|---------|
| `notion-fetch` | Read page, database, or data-source schema; fetch docs via `notion://docs/*` URIs |
| `notion-create-pages` | Create one or more pages under a parent or as workspace private pages |
| `notion-update-page` | Update properties, content (`update_content`, `insert_content`, `replace_content`), templates, verification |
| `notion-search` | Keyword search across workspace |
| `notion-query-data-sources` | Query database entries with filters |

### Secondary

| Tool | Purpose |
|------|---------|
| `notion-move-pages` | Move pages to a new parent |
| `notion-duplicate-page` | Duplicate a page |
| `notion-create-comment` | Add comments on pages or specific content |
| `notion-get-comments` | Read discussion threads |
| `notion-create-attachment` | Upload files for embed/file blocks |
| `notion-get-async-task` | Poll async create/update tasks |

## Golden rule: fetch before you write

**Every update workflow starts with a fetch.** This is not optional.

`update_content` uses exact string matching (`old_str`). If `old_str` differs by even one character from the live page, the update **fails silently** — no error, no change.

```
WORKFLOW (every time):
1. notion-fetch     (current content)
2. Copy exact anchors from fetched output
3. notion-update-page (apply changes)
4. notion-fetch     (verify — mandatory for structural edits)
```

## MCP invocation pattern

```
#mcp_notion_notion-fetch({
  "id": "<page-id-or-url>"
})
```

For the Markdown spec:

```
#mcp_notion_notion-fetch({
  "id": "notion://docs/enhanced-markdown-spec"
})
```

## Create — `notion-create-pages`

### Database entry (default for database rows)

Always fetch the database URL first to get data-source IDs and property schema.

```json
{
  "parent": {
    "type": "data_source_id",
    "data_source_id": "<from collection://... in fetch output>"
  },
  "pages": [{
    "icon": "📌",
    "properties": {
      "Task Name": "Page title here",
      "Status": "In Progress"
    },
    "content": "## Section\n\nBody content..."
  }]
}
```

Invoke:

```
#mcp_notion_notion-create-pages({ ... })
```

### Critical create rules

- **Title property name comes from the fetched schema** — may be `title`, `Task Name`, etc. — not assumed `Title` or `Name`.
- **Parent type `data_source_id`** for database entries. `page_id` creates a nested child page.
- **Do not put the page title in `content`** — only in `properties`.
- **Property formats** vary by type (dates, checkboxes `__YES__`/`__NO__`, relations as ID arrays) — read schema from fetch.
- **Tags/select**: use plain strings matching schema options; verify format via fetch on the collection.

### Child page (intentional nesting only)

```json
{
  "parent": { "type": "page_id", "page_id": "<parent-page-id>" },
  "pages": [{ "properties": { "title": "Child page" }, "content": "..." }]
}
```

### Verify placement

After create, fetch the new page:

- Database entry: parent shows `collection://<data-source-id>`
- Child page: parent shows `page://<page-id>`

## Read — `notion-fetch`

```json
{ "id": "<page-id-or-url>" }
```

Also useful:

```json
{ "id": "collection://<data-source-id>" }
{ "id": "self" }
{ "id": "notion://docs/enhanced-markdown-spec" }
```

Fetched content may differ from what you originally wrote — Notion escapes `>`, `[`, `]`, backticks internally. **Never use memory as `old_str`.**

## Update — `notion-update-page`

Commands: `update_properties`, `update_content`, `insert_content`, `replace_content`, `apply_template`, `update_verification`.

### `update_content` — surgical patch (most common)

```json
{
  "page_id": "<page-id>",
  "command": "update_content",
  "content_updates": [{
    "old_str": "exact string from fetched content",
    "new_str": "replacement string"
  }]
}
```

```
#mcp_notion_notion-update-page({ ... })
```

Rules:

- `old_str` must match **exactly one** location by default. Zero or multiple matches → failure (often silent).
- Use `replace_all_matches: true` only when every occurrence should change.
- Batch related edits in one call via multiple `content_updates` entries.
- Re-fetch before the next edit on the same page — prior fetch is stale after any successful update.

### `insert_content` — prepend or append

```json
{
  "page_id": "<page-id>",
  "command": "insert_content",
  "content": "## Latest update\n\nStatus here.",
  "position": { "type": "start" }
}
```

Omit `position` or use `{ "type": "end" }` to append.

### `replace_content` — full rewrite

```json
{
  "page_id": "<page-id>",
  "command": "replace_content",
  "new_str": "# Section 1\n\nEntire new body..."
}
```

Use when structural reorganization, escaping mismatches, or many overlapping edits make `update_content` unreliable. Include all content you want to keep. Preserve child pages/databases with `<page url="...">` / `<database url="...">` from fetch output.

Prefer `update_content` or `insert_content` for small edits — full replace is slower and hits async limits more often.

### `update_properties`

```json
{
  "page_id": "<page-id>",
  "command": "update_properties",
  "properties": { "title": "New Page Title", "Status": "Done" },
  "icon": "🎯"
}
```

Use property names from the fetched database schema.

## Delete

No MCP delete tool. Delete or trash pages manually in Notion UI, or use `notion-move-pages` to reorganize.

## Pre-flight checklist

Before any Notion operation:

- [ ] Fetched current page content? (mandatory for updates)
- [ ] `old_str` copied from fetch output, not memory?
- [ ] Using `<callout>` tags, not `>` blockquotes? (see [formatting.md](references/formatting.md))
- [ ] Using HTML `<table>` syntax, not pipe tables?
- [ ] For create: `data_source_id` parent for database rows?
- [ ] For create: title property name from fetched schema?
- [ ] Headings start at H2 (`##`), not H1?
- [ ] Escaped `>` as `\>` inside callouts?
- [ ] Will verify with fetch after important edits?
