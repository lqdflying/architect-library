# Notion MCP Failure Modes and Workflows

Load this reference when updates fail silently, content looks wrong after a write, or you need multi-step editing patterns.

## Anchor string selection for `update_content`

Choosing the right `old_str` is the difference between a successful update and a silent failure.

### Best anchors (most reliable)

1. **Section headings** — `## 3.2 Attention Mechanism` is almost always unique.
2. **Multi-line code comment blocks** — unique and unlikely to repeat.
3. **Heading + first line combination** — `## Section Title\n\nFirst paragraph text`

### Acceptable anchors

4. **Unique phrases** within the content — but verify uniqueness via the fetched content.
5. **Table header rows** — usually unique enough if the table structure is distinct.

### Dangerous anchors (avoid)

6. **Single bullet points** — `- **Bold item**` may match multiple locations.
7. **Short generic phrases** — `The model` or `## Summary` might repeat.
8. **Content you wrote from memory** — always copy from the fetched content.

### Insertion patterns

Insert **before** an existing heading:

```json
{
  "old_str": "last line of previous section\n## Next Section Heading",
  "new_str": "last line of previous section\n\n## NEW SECTION\n\nNew content here.\n\n---\n\n## Next Section Heading"
}
```

Append **after** an existing section:

```json
{
  "old_str": "last line of the section where you want to append",
  "new_str": "last line of the section where you want to append\n\n### New Subsection\n\nNew content here."
}
```

## Common failure modes and fixes

### Silent update failure

**Symptom**: `update_content` appears to succeed but nothing changed.

**Cause**: `old_str` does not exactly match any content on the page.

**Fix**: Re-fetch the page, copy the exact string from the fetched output, and retry. Common mismatches:

- Extra/missing whitespace or newlines
- Notion internally escaping `>` as `\>` or `[` as `\\[`
- Content was already modified by a previous update in the same session (stale context)

### Multiple matches

**Symptom**: Update applies to the wrong location, or does not apply at all.

**Cause**: `old_str` appears in multiple places (default: operation fails).

**Fix**: Extend `old_str` with more surrounding context until unique, or set `replace_all_matches: true` when every occurrence should change.

### Quote block absorbs subsequent content

**Symptom**: After updating, content after a `>` line is missing, duplicated, or rendered inside a quote block.

**Cause**: Used `>` blockquote syntax.

**Fix**: Replace with `<callout>` tag syntax. If the page is badly broken, use `replace_content` to rewrite the entire page.

### Code block inside callout breaks

**Symptom**: A fenced code block inside a `>` quote renders incorrectly or disappears.

**Cause**: Notion quote blocks do not support embedded fenced code blocks.

**Fix**: Move the code block outside the callout, or use `<callout>` tag syntax.

### Created page appears as child page instead of database entry

**Symptom**: New page is nested under another page instead of appearing as a sibling in the database.

**Cause**: Used `page_id` parent instead of `data_source_id`.

**Fix**: Create again with the correct parent. Delete the wrongly-created child page manually in Notion.

### Page creation succeeds but title is blank

**Symptom**: Page is created but has no title.

**Cause**: Used wrong property key for the title (e.g. `Name` instead of the schema's title property).

**Fix**: Fetch the data-source schema first. Use `update_properties` with the correct title property name from the schema.

### Wrong database placement

**Symptom**: Page created in wrong database or as workspace private page.

**Cause**: Omitted parent or used database URL as `page_id` instead of `data_source_id`.

**Fix**: Always `notion-fetch` the database URL first to get data-source IDs (`collection://...`).

## Multi-step editing workflows

### Section insertion with renumbering

When inserting a new section between existing ones, batch all renumbering in one `update_content` call:

```json
{
  "content_updates": [
    {"old_str": "## 3 — Old Section Three", "new_str": "## 4 — Old Section Three"},
    {"old_str": "## 4 — Old Section Four", "new_str": "## 5 — Old Section Four"},
    {"old_str": "see Section 3", "new_str": "see Section 4"},
    {"old_str": "see Section 4", "new_str": "see Section 5"},
    {"old_str": "end of section 2 content\n## 4 — Old Section Three",
     "new_str": "end of section 2 content\n\n## 3 — New Section\n\nNew content.\n\n---\n\n## 4 — Old Section Three"}
  ]
}
```

Put renumbering replacements **before** the insertion replacement to avoid intermediate states where later `old_str` values no longer match.

### Major restructure

For restructures involving more than 3–4 surgical edits:

1. Fetch the full page
2. Reconstruct the entire content with changes applied
3. Use `replace_content` with `new_str` to write the whole page at once
4. Fetch to verify

When using `replace_content`, child pages and databases must be preserved via `<page url="...">` or `<database url="...">` tags from the fetch output, or the operation fails.

### Cross-reference updates

When content references another page's structure:

1. Update the source page
2. Search for pages that cross-reference the changed section
3. Update cross-references in those pages
