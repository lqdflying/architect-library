# Notion MCP Content Formatting

Load this reference when formatting page content for `notion-create-pages`, `notion-update-page`, or `notion-fetch` output interpretation.

For the full Notion-flavored Markdown specification, fetch `notion://docs/enhanced-markdown-spec` via `notion-fetch` — do not guess syntax.

## Callout blocks

**This is the single most error-prone formatting element.**

Correct syntax:

```
<callout icon="📌" color="gray_bg">
	Content line 1 here.
	Content line 2 here.
	**Bold text** and `inline code` work inside callouts.
</callout>
```

Rules:

- Content lines inside the callout **must be tab-indented** (use actual tab character).
- The `>` character inside a callout **must be escaped as `\>`**. Example:
  `shape changes from [2, 768] \> [2, 3072]`
- Available colors: `gray_bg`, `yellow_bg`, `blue_bg`, `red_bg`, `green_bg`,
  `purple_bg`, `pink_bg`, `orange_bg`, `brown_bg`

**NEVER use `>` blockquote syntax for callouts.**

| Syntax | Notion renders as | Problem |
|--------|-------------------|---------|
| `> text` | Quote block | Absorbs all subsequent content until a blank line; does NOT support embedded code blocks |
| `<callout icon="..." color="...">` | Callout block | Independent block, supports icon + background color, does not absorb subsequent content |

The `>` quote block absorption bug: when you write `> some text` followed by a code block or more paragraphs, Notion's quote block **swallows everything after it** into the quote. This causes content duplication, missing sections, and broken code blocks. The only fix is to not use `>` for callouts.

## Tables

Use HTML-style table syntax:

```
<table header-row="true">
<tr>
<td>Column 1</td>
<td>Column 2</td>
<td>Column 3</td>
</tr>
<tr>
<td>Row 1 data</td>
<td>Row 1 data</td>
<td>Row 1 data</td>
</tr>
</table>
```

Notes:

- `header-row="true"` makes the first row a header row.
- You can optionally add `<colgroup>` with `<col width="...">` for column widths, but this is not required.
- **Bold**, `inline code`, and links work inside `<td>` cells.
- Markdown pipe tables (`| col | col |`) are NOT reliably supported by the Notion MCP for content updates. Use HTML table syntax.

## Collapsible / toggle blocks

```
<details>
<summary>Click to expand this section</summary>

	Content inside the toggle goes here.
	It should be tab-indented.

	```javascript
	// Code blocks inside toggles also need tab-indentation
	// before the triple backticks
	const x = 42;
	```

</details>
```

Notes:

- Content inside `<details>` should be tab-indented.
- Code blocks within `<details>` require a tab character before the opening ``` fence.
- Verify rendering after write — support may differ from native Notion toggles.

## Code blocks

Standard markdown fenced code blocks work:

````
```javascript
// All code block content must be English only
const result = model.predict(input);
```
````

Rules:

- Language tag (javascript, python, yaml, etc.) is supported.
- **All human-readable text inside code blocks must be English** — comments, strings, log output, error messages, variable names.

## Headings

- Use `##` (H2) as the starting heading level in page content. H1 (`#`) conflicts with the page title.
- For sub-sections: `###` (H3), `####` (H4).
- Square brackets in headings must be escaped: `### Shape \\[2, 768\\]`
- Do not put the page title in content — set it via `properties` on create or `update_properties`.

## Inline formatting

- **Bold**: `**text**`
- *Italic*: `*text*`
- `Inline code`: backtick-wrapped
- ~~Strikethrough~~: `~~text~~`
- Links: `[display text](url)`
- Gray annotation text: `<span color="gray">*annotation text*</span>`

## Math / LaTeX

- Inline: `$formula$`
- Block: `$$formula$$`
- Notion's LaTeX support is limited — test complex formulas after writing.
