# Basic GitHub Markdown Syntax

Sources: [Basic writing and formatting syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax) · [GFM spec](https://github.github.com/gfm/)

## Headings

Use one to six `#` symbols before heading text. GitHub auto-generates a table of contents (Outline menu) when a file has two or more headings.

```markdown
# First-level heading
## Second-level heading
### Third-level heading
```

## Text styling

| Style | Syntax | Example |
|-------|--------|---------|
| Bold | `** **` or `__ __` | `**bold**` |
| Italic | `* *` or `_ _` | `_italic_` |
| Strikethrough | `~~ ~~` | `~~mistake~~` |
| Bold + italic | `*** ***` | `***important***` |
| Subscript | `<sub></sub>` | `H<sub>2</sub>O` |
| Superscript | `<sup></sup>` | `x<sup>2</sup>` |

Nested emphasis: `**This is _extremely_ important**`

## Blockquotes

```markdown
> Quoted text
```

## Inline and fenced code

Inline: `` Use `git status` to list changes. ``

Fenced block:

````markdown
```
git status
git add .
git commit -m "message"
```
````

See `advanced-formatting.md` for syntax highlighting and nested-list indentation.

## Color models (issues/PRs/discussions only)

Supported inside backticks with no leading/trailing spaces:

| Model | Syntax | Example |
|-------|--------|---------|
| HEX | `` `#RRGGBB` `` | `` `#0969DA` `` |
| RGB | `` `rgb(R,G,B)` `` | `` `rgb(9, 105, 218)` `` |
| HSL | `` `hsl(H,S,L)` `` | `` `hsl(212, 92%, 45%)` `` |

Not rendered in repo `.md` files.

## Links

### Inline links

```markdown
[GitHub Pages](https://pages.github.com/)
```

GitHub also autolinks bare URLs: `https://github.com`

Link text must be on a single line.

### Section links (heading anchors)

Rules for auto-generated anchors:

1. Letters → lowercase
2. Spaces → hyphens; other whitespace/punctuation removed
3. Leading/trailing whitespace removed
4. Markup stripped (`_italics_` → `italics`)
5. Duplicate headings get `-1`, `-2`, … suffix

```markdown
## Sample Section

[Jump to sample](#sample-section)
```

### Relative links

```markdown
[Contributing](docs/CONTRIBUTING.md)
[Root readme](/README.md)
[Parent](../README.md)
```

Prefer relative links for files in the same repository.

### Custom anchors

```markdown
<a name="my-anchor"></a>
Text without its own heading.

[Link here](#my-anchor)
```

Custom anchors are not included in the document outline.

## Line breaks

| Context | Single newline behavior |
|---------|-------------------------|
| Issues, PRs, discussions | Renders as line break |
| `.md` files / wikis | Needs trailing two spaces, `\`, or `<br/>` |

Paragraph break: leave a blank line between lines.

```markdown
Line one with two trailing spaces  
Line two

Or use a backslash\
Or <br/>
```

## Images

```markdown
![Alt text](https://example.com/image.png)
![Repo image](/assets/images/logo.png)
```

Use relative paths for images in the repository. The `<picture>` HTML element is supported.

## Lists

### Unordered

```markdown
- Item one
* Item two
+ Item three
```

### Ordered

```markdown
1. First
2. Second
3. Third
```

Numbers need not be sequential — GitHub renumbers automatically.

### Nested lists

Align the list marker under the first character of the parent item's text. For `100. First item`, indent nested items at least five spaces.

```markdown
1. First list item
   - Nested item
     - Deeper nested item

100. First list item
     - Nested under 100.
```

## Task lists

```markdown
- [x] Completed task
- [ ] Open task
- [ ] Add delight :tada:
```

Escape descriptions starting with `(`:

```markdown
- [ ] \(Optional) Follow-up issue
```

In issues/PRs, task items referencing `#123` unfurl to show title and state.

## Mentions and references

```markdown
@octocat What do you think?
@github/support
#739
GH-740
octo-org/octo-repo#26
```

Autolinked issue/PR references work in **conversations**, not in repo `.md` files or wikis.

## Emoji

```markdown
:rocket: :white_check_mark: :shipit:
```

Full list: [emoji-cheat-sheet](https://github.com/ikatyang/emoji-cheat-sheet/blob/github-actions-auto-update/README.md)

## Footnotes

```markdown
Here is a footnote[^1].

[^1]: Footnote text. Use two trailing spaces for a line break inside the note.
  Second line of the footnote.
```

Footnote position in source does not affect render position (always at bottom). **Not supported in wikis.**

## Alerts

```markdown
> [!NOTE]
> Useful information users should know when skimming.

> [!TIP]
> Helpful advice for doing things better.

> [!IMPORTANT]
> Key information needed to achieve the goal.

> [!WARNING]
> Urgent info requiring immediate attention.

> [!CAUTION]
> Risks or negative outcomes of certain actions.
```

Rules: max 1–2 per document; do not stack consecutively; cannot nest inside other elements.

## HTML comments

```markdown
<!-- This content is hidden from rendered output -->
```

## Escaping Markdown

Prefix special characters with `\`:

```markdown
Let's rename \*our-project\* without italics.
\*not a list item\*
```

Markdown in issue/PR **titles** is not escaped — titles are plain text.
