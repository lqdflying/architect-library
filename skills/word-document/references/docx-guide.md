# Word Document (.docx) Generation Guide

> Custom instruction for AI coding assistants (Cursor, Claude Code, etc.)
> Libraries: `docx` (docx-js) for creation, raw XML for editing
> License: MIT (this guide) | Libraries follow their own licenses

## Decision Matrix

| Task | Tool |
|------|------|
| Create new .docx from scratch | `docx` npm package (docx-js) |
| Edit existing .docx | Unzip -> edit XML -> rezip |
| Read / extract text | `pandoc` or unzip + parse XML |
| Convert .doc (legacy) to .docx | LibreOffice headless |
| Convert .docx to PDF | LibreOffice headless |
| Convert .docx to images | LibreOffice -> PDF -> `pdftoppm` |

---

## Part 1: Creating New Documents with docx-js

### Install

```bash
npm install -g docx
```

### Minimal Skeleton

```javascript
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, Header, Footer, AlignmentType, PageOrientation,
  LevelFormat, ExternalHyperlink, InternalHyperlink, Bookmark,
  FootnoteReferenceRun, PositionalTab, PositionalTabAlignment,
  PositionalTabRelativeTo, PositionalTabLeader,
  TabStopType, TabStopPosition, Column, SectionType,
  TableOfContents, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, PageBreak
} = require("docx");

const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },       // US Letter in DXA
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }  // 1 inch
      }
    },
    children: [
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Document Title")]
      }),
      new Paragraph({
        children: [new TextRun("Body text goes here.")]
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => fs.writeFileSync("output.docx", buf));
```

### Unit System: DXA

All dimensions in docx-js use DXA (twentieth of a point). Key conversions:

| Measure | DXA Value |
|---------|-----------|
| 1 inch | 1440 |
| 1 cm | 567 |
| 1 pt (font) | 2 (half-points for font size) |

Common page sizes:

| Paper | Width (DXA) | Height (DXA) | Content Width (1" margins) |
|-------|-------------|--------------|---------------------------|
| US Letter | 12,240 | 15,840 | 9,360 |
| A4 | 11,906 | 16,838 | 9,026 |

**docx-js defaults to A4.** Always set page size explicitly.

### Landscape Mode

docx-js handles the width/height swap internally. Pass the portrait dimensions and set the orientation flag:

```javascript
size: {
  width: 12240,    // short edge
  height: 15840,   // long edge
  orientation: PageOrientation.LANDSCAPE  // library swaps internally
}
// Usable content width = 15840 - leftMargin - rightMargin
```

### Heading Styles (required for TOC)

Override built-in styles with exact IDs (`Heading1`, `Heading2`, ...). Each heading must include `outlineLevel` or Table of Contents won't pick it up.

```javascript
const doc = new Document({
  styles: {
    default: {
      document: { run: { font: "Arial", size: 24 } }  // 12pt base
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1",
        basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2",
        basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 }
      },
    ]
  },
  sections: [{ children: [/* ... */] }]
});
```

### Lists

Never insert unicode bullet characters manually. Use the numbering API:

```javascript
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullet-list",
        levels: [{
          level: 0,
          format: LevelFormat.BULLET,
          text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
      {
        reference: "numbered-list",
        levels: [{
          level: 0,
          format: LevelFormat.DECIMAL,
          text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
    ]
  },
  sections: [{
    children: [
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("First bullet")]
      }),
      new Paragraph({
        numbering: { reference: "numbered-list", level: 0 },
        children: [new TextRun("Step one")]
      }),
    ]
  }]
});
```

Same `reference` value = continuous numbering. Different `reference` = restarts from 1.

### Tables

**docx-js (this section):** Apply **explicit** header shading, borders, and optional row banding in code so output looks finished without the user picking a Table Design theme.

**python-docx:** Prefer built-in `Medium Shading 1 Accent 1` + `w:tblHeader` with fonts/margins/widths only (`python-docx-patterns.md` Approach A). Use explicit fills here only as Approach B when Word still shows plain grid after visual check. **Never mix** both on the same table.

See `production-lessons.md` for compliance ADD structure (parallel tool tables, TOC, visual verify).

**Width (required):**

1. `columnWidths` on the Table
2. `width` on each TableCell

Always use `WidthType.DXA` — percentage widths break in Google Docs.

**Typography (architecture docs):**

- Table body: **9pt** (dense compliance/HLD tables); document body: 10–10.5pt
- Cell padding: `margins` top/bottom **80**, left/right **120** DXA (~4–6pt)
- US Letter with 1" margins: table width **9360** DXA (6.5") or **8640** DXA (6.0") for slightly narrower tables
- Two-column layouts: narrow label column (~2400 DXA) + wide detail column

**Visual pattern:**

- Header row: fill `D5E8F0`, text `1F3864`, bold
- Body: alternate `F7F7F7` / white on even/odd rows
- Borders: `BorderStyle.SINGLE`, size 1, color `CCCCCC` on all sides

```javascript
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const allBorders = { top: border, bottom: border, left: border, right: border };
const headerShading = { fill: "D5E8F0", type: ShadingType.CLEAR };
const bandShading = { fill: "F7F7F7", type: ShadingType.CLEAR };

function headerCell(widthDxa, text) {
  return new TableCell({
    borders: allBorders,
    width: { size: widthDxa, type: WidthType.DXA },
    shading: headerShading,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({
      children: [new TextRun({ text, bold: true, size: 18, color: "1F3864" })],  // 18 half-points = 9pt
    })],
  });
}

function bodyCell(widthDxa, text, banded) {
  return new TableCell({
    borders: allBorders,
    width: { size: widthDxa, type: WidthType.DXA },
    shading: banded ? bandShading : undefined,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({
      spacing: { before: 0, after: 0 },
      children: [new TextRun({ text, size: 18 })],
    })],
  });
}

new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [2400, 6960],
  rows: [
    new TableRow({
      children: [headerCell(2400, "Goal"), headerCell(6960, "Approach")],
    }),
    new TableRow({
      children: [bodyCell(2400, "Fail closed", false), bodyCell(6960, "Deny on authz or policy errors", true)],
    }),
  ],
});
```

**Pagination:**

- Keep each logical table row on one page when possible: short cell copy; avoid multi-sentence Approach cells in two-column goal tables
- In docx-js, prefer compact rows over `PageBreak` inside tables
- If using python-docx, see `python-docx-patterns.md` for `w:cantSplit` and `w:keepLines`

**Anti-patterns:**

- **Table Grid** as the effective style (plain black borders)
- **Mixing** built-in table style (python-docx) with manual cell fills or white header text — theme flattens; see `production-lessons.md`
- White header text without a header fill
- One subsection with a full tool/inventory table and sibling subsections with paragraph-only lists (compliance scans fail)
- Auto-TOC fields in generators without user request (validator noise; stale pages)
- Leaving `generate_*.py` beside the delivered `.docx` unless the user asked to keep it
- Trusting XML style names without opening the file in Word

### Images

`type` is mandatory on ImageRun:

```javascript
new Paragraph({
  children: [new ImageRun({
    type: "png",  // png | jpg | jpeg | gif | bmp | svg
    data: fs.readFileSync("logo.png"),
    transformation: { width: 200, height: 150 },
    altText: { title: "Logo", description: "Company logo", name: "logo" }
  })]
})
```

### Page Breaks

Must be inside a Paragraph:

```javascript
new Paragraph({ children: [new PageBreak()] })
// or
new Paragraph({ pageBreakBefore: true, children: [new TextRun("New page")] })
```

### Hyperlinks

```javascript
// External
new Paragraph({
  children: [new ExternalHyperlink({
    children: [new TextRun({ text: "Visit site", style: "Hyperlink" })],
    link: "https://example.com",
  })]
})

// Internal (bookmark target + anchor reference)
// 1. Destination
new Paragraph({
  heading: HeadingLevel.HEADING_1,
  children: [new Bookmark({ id: "sec1", children: [new TextRun("Section 1")] })]
})
// 2. Link
new Paragraph({
  children: [new InternalHyperlink({
    children: [new TextRun({ text: "Jump to Section 1", style: "Hyperlink" })],
    anchor: "sec1",
  })]
})
```

### Footnotes

```javascript
const doc = new Document({
  footnotes: {
    1: { children: [new Paragraph("Source: Annual Report 2024")] },
  },
  sections: [{
    children: [new Paragraph({
      children: [
        new TextRun("Revenue grew 15%"),
        new FootnoteReferenceRun(1),
      ]
    })]
  }]
});
```

### Tab Stops (simulating two-column single-line layout)

```javascript
// Left text + right-aligned text on same line
new Paragraph({
  children: [
    new TextRun("Company Name"),
    new TextRun("\tJanuary 2025"),
  ],
  tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
})
```

### Multi-Column Layouts

```javascript
sections: [{
  properties: {
    column: {
      count: 2,
      space: 720,        // 0.5 inch gap
      equalWidth: true,
      separate: true,     // vertical divider line
    }
  },
  children: [/* content flows across columns */]
}]
```

Force column break: use a new section with `type: SectionType.NEXT_COLUMN`.

### Table of Contents

```javascript
new TableOfContents("Table of Contents", {
  hyperlink: true,
  headingStyleRange: "1-3"
})
```

Headings MUST use `HeadingLevel` enum, not custom paragraph styles.

### Headers and Footers

```javascript
sections: [{
  headers: {
    default: new Header({
      children: [new Paragraph({ children: [new TextRun("Header Text")] })]
    })
  },
  footers: {
    default: new Footer({
      children: [new Paragraph({
        children: [
          new TextRun("Page "),
          new TextRun({ children: [PageNumber.CURRENT] })
        ]
      })]
    })
  },
  children: [/* body */]
}]
```

Do NOT use tables inside headers/footers for layout (cells have forced minimum height). Use tab stops instead.

---

## Part 2: Editing Existing Documents

A .docx is a ZIP archive of XML files. The workflow:

### Step 1: Unpack

```bash
mkdir unpacked
cd unpacked
unzip ../document.docx
```

Key files:
- `word/document.xml` — main body content
- `word/styles.xml` — style definitions
- `word/_rels/document.xml.rels` — relationships (images, hyperlinks, etc.)
- `[Content_Types].xml` — MIME type registry

### Step 2: Edit XML

Use a text editor or `sed`/programmatic XML manipulation.

Important XML patterns:

**Paragraphs and runs:**
```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="Heading1"/>
  </w:pPr>
  <w:r>
    <w:rPr><w:b/></w:rPr>
    <w:t>Bold heading text</w:t>
  </w:r>
</w:p>
```

**Tracked changes (insertion):**
```xml
<w:ins w:id="1" w:author="Author" w:date="2025-01-01T00:00:00Z">
  <w:r><w:t>new text</w:t></w:r>
</w:ins>
```

**Tracked changes (deletion):**
```xml
<w:del w:id="2" w:author="Author" w:date="2025-01-01T00:00:00Z">
  <w:r><w:delText>removed text</w:delText></w:r>
</w:del>
```

Inside `<w:del>`, use `<w:delText>` instead of `<w:t>`.

**Adding images:**
1. Place image file in `word/media/`
2. Add relationship in `word/_rels/document.xml.rels`
3. Add content type in `[Content_Types].xml`
4. Reference via `r:embed` in document.xml

### Step 3: Repack

```bash
cd unpacked
zip -r ../output.docx . -x "*.DS_Store"
```

### XML Editing Rules

- Element order in `<w:pPr>` matters: `<w:pStyle>` -> `<w:numPr>` -> `<w:spacing>` -> `<w:ind>` -> `<w:jc>` -> `<w:rPr>`
- Add `xml:space="preserve"` to any `<w:t>` with leading/trailing whitespace
- When making tracked-change edits, replace entire `<w:r>` blocks rather than injecting change tags inside a run
- Copy `<w:rPr>` from the original run into your replacement runs to preserve formatting
- Use smart quote XML entities: `&#x201C;` (left double), `&#x201D;` (right double), `&#x2018;` (left single), `&#x2019;` (right single / apostrophe)

---

## Part 3: Format Conversion

```bash
# .doc -> .docx
libreoffice --headless --convert-to docx document.doc

# .docx -> PDF
libreoffice --headless --convert-to pdf document.docx

# .docx -> images (via PDF intermediate)
libreoffice --headless --convert-to pdf document.docx
pdftoppm -jpeg -r 150 document.pdf page
```

### Text Extraction

```bash
# With pandoc
pandoc document.docx -t markdown -o output.md

# Show tracked changes
pandoc --track-changes=all document.docx -o output.md
```

---

## Critical Rules Summary

1. **Set page size explicitly** — library defaults to A4, not US Letter
2. **Landscape: pass portrait dimensions** — library swaps them internally
3. **Never use `\n`** — use separate Paragraph objects for line breaks
4. **Never use unicode bullets** — use `LevelFormat.BULLET` with numbering config
5. **PageBreak must be inside Paragraph** — standalone breaks produce invalid XML
6. **ImageRun requires `type`** — always specify the format
7. **Table widths: DXA only** — `WidthType.PERCENTAGE` breaks in Google Docs
8. **Tables need dual width specs** — both `columnWidths` array and per-cell `width`
9. **Cell `margins` are internal padding** — they shrink content area, don't enlarge the cell
10. **Use `ShadingType.CLEAR`** — `SOLID` fills cells with black
11. **No tables in headers/footers for layout** — use tab stops instead
12. **TOC only works with `HeadingLevel`** — custom paragraph styles are invisible to TOC
13. **Override built-in style IDs** — must use exact IDs like `Heading1`, `Heading2`
14. **Include `outlineLevel`** on heading styles — required for TOC generation (0 = H1, 1 = H2, ...)
15. **One table styling approach** — docx-js: explicit fills; python-docx: built-in style + `tblHeader` OR explicit fills, never both
16. **Architecture table text: 9pt** — tighter than body; use cell margins 80/120 DXA (docx-js) or 36–40 DXA (python-docx)
17. **Deliverable is the `.docx` only** — generator scripts belong in `scripts/` unless the user requests otherwise
18. **Short table rows for pagination** — concise cell copy; `cantSplit` on python-docx rows
19. **Verify tables in Word** — XML style names can lie; screenshot/open beats validator alone
20. **Parallel sections, parallel tables** — compliance ADD: matching tables in sibling subsections (e.g. 5.1.1–5.1.3)
21. **TOC in Word** — heading styles in generator; user inserts TOC via References unless embedded TOC is required
