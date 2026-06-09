# Production lessons (real architecture DOCX deliveries)

Captured from compliance ADD generation and review. Use with `docx-guide.md` and `python-docx-patterns.md`.

## Table styling — pick one approach

| Approach | When | Do |
|----------|------|-----|
| **Built-in Word table style** (python-docx) | No npm; repeatable generator in Python | `Medium Shading 1 Accent 1`, first row `w:tblHeader`, 9pt fonts, tight margins, fixed widths, `cantSplit` — **no manual cell fills or per-cell border overrides** |
| **Explicit fills in code** (docx-js or python-docx) | docx-js new docs; or python-docx when built-in theme still renders as plain grid after visual check | Header `D5E8F0`, borders `CCCCCC`, banding — **do not** also set a built-in table style name |

**Never mix** built-in table style with hand-painted cell shading or white header text. That reverts to flat **Table Grid** in Word even when XML lists `MediumShading1-Accent1`.

**Verify in Word** (open file or screenshot). Style names in XML are not enough.

## Structural parallelism (compliance / ADD)

Compliance readers scan by section shape, not only prose.

- If **5.1.1** has a full **Tool / Purpose** table, **5.1.2** and **5.1.3** need the same — do not summarize tool lists in paragraphs only.
- Apply the same pattern to risks, controls, and design-goal tables across sibling subsections.
- Align table column headers across parallel sections (`Tool`, `Purpose` or `Goal`, `Approach`).

## Table of contents

- **Do not** embed auto-TOC fields in generators unless the user requires it — they can cause validator/XML noise and stale page numbers.
- Use `Heading1` / `Heading2` with `outlineLevel` so TOC works when added.
- Tell the user: **References → Table of Contents** in Word for the final compliance pack.

## docx-js vs python-docx

| | docx-js (preferred) | python-docx (fallback) |
|--|---------------------|-------------------------|
| Requires | `bash scripts/install_deps.sh node` | `bash scripts/install_deps.sh office` (python-docx in uv env) |
| Table theme | Explicit shading in JS | Built-in style + `tblHeader`, or explicit OXML fills |
| Validation | Usually cleaner | `office_tools.py validate` may warn on some XML; file may still open fine in Word |
| After generate | Run validator | Run validator; **confirm visually in Word** |

If npm is unavailable, use python-docx and document the trade-off in your reply.

## Generator workflow

- **Regenerating overwrites** the `.docx` — one-off edits (owner, approver, TOC) belong in Word or in the generator source, not only in the binary.
- **Run the generator** when content, product version, or layout logic changes — not for every submission handoff.
- Keep style names and layout constants in **one place** (e.g. `TABLE_STYLE = "Medium Shading 1 Accent 1"`); run the script after every generator edit to catch `NameError` and broken output.
- **Deliverable**: `.docx` only in the user folder unless they asked to keep `generate_*.py` (prefer `scripts/` for maintained generators).

## Delivery checklist additions

1. Open the `.docx` in Word (or accept a user screenshot) — confirm table header band and row banding, not plain grid.
2. Scan parallel sections for matching table structure.
3. Run `office_tools.py validate` when available; note warnings that do not block Word open.
4. Do not leave one-off generator scripts beside the deliverable unless requested.
