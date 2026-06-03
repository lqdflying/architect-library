# python-docx patterns (fallback only)

Use the **docx-js** workflow in `docx-guide.md` when `npm` and `docx` are available. Use python-docx when the environment has no Node toolchain or the repo already ships a Python generator.

Read `production-lessons.md` for compliance ADD pitfalls (mixed styling, missing parallel tables, TOC, visual verify).

## Table styling — choose exactly one approach

### Approach A — built-in Word style (preferred for python-docx)

Best maintenance and closest to Word’s Table Design gallery. Works when you **do not** override cell fills or header font colors manually.

```python
from docx.oxml import OxmlElement
from docx.shared import Pt

TABLE_STYLE = "Medium Shading 1 Accent 1"  # single constant; never delete while referenced
TABLE_FONT_PT = 9
TABLE_CELL_MARGIN_DXA = 40

def set_header_row(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tr_pr.append(OxmlElement("w:tblHeader"))

def set_row_cant_split(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tr_pr.append(OxmlElement("w:cantSplit"))

def format_table_cell_runs(cell, *, bold: bool = False) -> None:
    """Font and spacing only — no fill, no border overrides, no white header text."""
    for paragraph in cell.paragraphs:
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(0)
        for run in paragraph.runs:
            run.font.name = "Arial"
            run.font.size = Pt(TABLE_FONT_PT)
            run.bold = bold

def add_themed_table(doc, headers, rows, col_widths_inches, table_width_inches=6.5):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = TABLE_STYLE
    # set fixed widths, cell margins (tcMar), then cell text
    set_header_row(t.rows[0])
    set_row_cant_split(t.rows[0])
    for i, h in enumerate(headers):
        t.rows[0].cells[i].text = h
        format_table_cell_runs(t.rows[0].cells[i], bold=True)
    for ri, row_data in enumerate(rows):
        tr = t.rows[ri + 1]
        set_row_cant_split(tr)
        for ci, val in enumerate(row_data):
            tr.cells[ci].text = val
            format_table_cell_runs(tr.cells[ci], bold=False)
    return t
```

**Do not** call `shade_cell`, set `Table Grid`, or force white header text on this path.

### Approach B — explicit OXML fills (fallback)

Use when Approach A still renders as plain **Table Grid** after opening in Word. Implement full header/body shading and borders in code (same palette as `docx-guide.md`). **Do not** set `t.style` to a built-in table style on this path.

See `docx-guide.md` § Tables for colors; use `w:shd`, `w:tcBorders`, `cantSplit`, `keepLines` as needed.

## Common failures

| Symptom | Cause | Fix |
|---------|--------|-----|
| Plain **Table Grid** | Default style or style name typo | Set `TABLE_STYLE` constant; use Approach A or B consistently |
| Theme “lost again” after edit | Mixed built-in style + manual cell colors / white header text | Revert to **one** approach; remove per-cell `w:shd` overrides on Approach A |
| XML says `MediumShading1-Accent1`, Word looks plain | Manual run/cell formatting fought the style | Approach A only: style + `tblHeader` + fonts/margins/widths |
| Tables too large | Default 10pt+, loose padding | **9pt** table text; margins **36–40 DXA**; fixed column widths |
| Row splits across pages | Tall cells, no `cantSplit` | `cantSplit` on rows; shorten cell copy; `keepLines` on paragraphs if needed |
| `NameError: TABLE_STYLE` | Constant removed, reference left | Keep style name in one module-level constant; run script after every generator change |
| Validator warnings, Word OK | python-docx XML quirks | Note in delivery; fix only if Word breaks or validator errors are blocking |

## Generator script placement

- Write the **deliverable** `.docx` to the path the user requested.
- Prefer maintained generators under `scripts/` — not beside the deliverable unless the user wants them there for regen.
- Regenerating **overwrites** the file; Word-only tweaks (TOC, sign-off names) must be reapplied or moved into the generator.

## TOC

Do not insert auto-TOC fields in python-docx unless required. Use proper heading styles; user adds TOC in Word via **References → Table of Contents**.
