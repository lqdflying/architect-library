---
name: spreadsheet-document
description: "Open, create, edit, or analyze spreadsheet files (.xlsx, .xlsm, .xltx, .csv, .tsv). Deliver .xlsx with zero formula errors after office_tools recalc when formulas are used. Use formulas LibreOffice can evaluate. Financial models, data cleanup, tabular exports. Install office + office-system for recalc. Do not use when the primary deliverable is Word, PDF, a standalone script, or a Google Sheets API integration."
---

# Spreadsheet Creator

Create and edit `.xlsx` spreadsheets with formulas, formatting, and validation. Use when the deliverable is a spreadsheet file.

## Load First

- `references/xlsx-guide.md` — formulas, pandas/openpyxl, financial model conventions, recalc workflow

For OOXML spreadsheet tooling (unpack/pack/validate):

```bash
python3 ../_shared/office-tools/office_tools.py --help
```

If installed in an editor skills folder, `_shared` must be a sibling of `spreadsheet-document`.

## Setup

```bash
bash ../_shared/office-tools/install_deps.sh
bash ../_shared/office-tools/install_deps.sh --with-system   # LibreOffice Calc for recalc
# or from repo root:
#   bash scripts/install_deps.sh office
#   bash scripts/install_deps.sh office-system
```

Prefer the uv environment:

```bash
cd ../_shared/office-tools
uv run python3 office_tools.py --help
```

`openpyxl` and `pandas` come from that environment. Do not `pip install` them first.

## Decision Workflow

| Task | Primary tool |
|------|--------------|
| Data analysis, bulk read/write | pandas (`read_excel` / `to_excel`) |
| Formulas, formatting, multi-sheet edits | openpyxl |
| Recalculate formula values | `office_tools.py recalc` (LibreOffice Calc) |
| Edit XLSX XML directly | `office_tools.py unpack` → edit → `pack` |
| Validate OOXML | `office_tools.py validate` |

## Requirements for every workbook

- **Professional font** (Arial or Times New Roman) unless the user says otherwise.
- **Excel formulas, never hardcoded results.** Write `sheet['B10'] = '=SUM(B2:B9)'`, not a Python-computed total. The sheet must recalculate when its inputs change.
- **Follow the user's spec.** Exact sheet names, exact column headers, and the formula they spelled out.
- **Document every assumption and hardcoded number** where the reader will see it: a cell comment, or a note at the end of the table. Cite a real source when one exists (`Source: Company 10-K, FY2024, Page 45, Revenue Note, [URL]`). When the number came from the user, say so.
- **A workbook you create for someone to fill in** needs a short legend of which cells to edit, and one example row of realistic values. Do not add that row to a file you were asked to edit.
- **Editing an existing file: match its conventions.** They override the financial-model colors below. Find designated input cells first (a distinct font color, fill, or shading), write only there, and leave existing formulas untouched.
- **Zero formula errors** (`#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?`, `#NULL!`, `#NUM!`). If you think an error predates you, prove it: load the original with `data_only=True` and read that cell.

## Formulas LibreOffice can verify

`recalc` evaluates formulas with LibreOffice. A function it cannot evaluate is stored as `#NAME?`.

- Prefer Excel-2007-era functions: `SUMIFS`, `INDEX`, `MATCH`, `IFERROR`, `SUMPRODUCT`. They need no prefix.
- These six later functions work only with an `_xlfn.` prefix, because openpyxl writes the formula text verbatim and Excel stores those names prefixed: `_xlfn.TEXTJOIN`, `_xlfn.CONCAT`, `_xlfn.IFS`, `_xlfn.SWITCH`, `_xlfn.MAXIFS`, `_xlfn.MINIFS`. Written bare, each yields `#NAME?`.
- Do not use `XLOOKUP`, `XMATCH`, `SORT`, `FILTER`, `UNIQUE`, or `SEQUENCE`. This LibreOffice cannot evaluate them under any prefix. They are spilling array functions, and an openpyxl file has no spill metadata, so a newer build can fill only the top-left cell and still report `total_errors: 0`. Use `INDEX`/`MATCH`. Sort, filter, and de-duplicate in Python before writing cells.
- A formula LibreOffice could not parse is written back lowercased. That, next to `#NAME?`, means the function name did not survive.

## Recalculate

openpyxl writes formulas as strings with no cached values. Until you recalculate, those cells read as `None` to `pandas`, `load_workbook(data_only=True)`, and most previewers.

```bash
cd ../_shared/office-tools
uv run python3 office_tools.py recalc output.xlsx
# optional: timeout seconds, then --force
# uv run python3 office_tools.py recalc output.xlsx 60 --force
```

LibreOffice rewrites the file in place and prints JSON:

| Field | Meaning |
|-------|---------|
| `status` | `success` or `errors_found` |
| `total_formulas` / `total_errors` | Counts after recalc |
| `error_summary` | Up to 100 cells per error type. `locations_truncated` is how many were withheld. Trust `total_errors`. |
| `error` (no `status`) | Nothing was recalculated: missing file, not writable, LibreOffice failure, or external-link refusal |

Fix named cells and run `recalc` again. Delivery requires `status: success` from a run in this message. A non-zero exit covers both an `error` key and `errors_found`. Read the JSON.

**`status: success` means the formulas evaluated. It does not mean they are right.** An off-by-one range is a clean file with wrong numbers. Check 2–3 formulas against the values you expect before filling a grid.

### External links

A formula such as `='[1]Returns Analysis'!$B$2` points at another workbook. The `[1]` is an index into the external-reference list, not a sheet in this file. openpyxl strips the cached value on save. LibreOffice then fails the link, writes `#NAME?`, and deletes it.

`recalc` refuses when `xl/externalLinks/` is present and a linked formula's cached value is already gone. Copy those cells' values from the original before you save over them. `--force` recalculates anyway and accepts the loss. Charts and conditional formats can hold external references the cell scan does not list.

## Financial models

Unless the user says otherwise, or the existing file already does something else. Number formats in full: `references/xlsx-guide.md`.

- Blue text `RGB(0,0,255)`: inputs and scenario levers. Black: formulas. Green `RGB(0,128,0)`: another sheet in this workbook. Red `RGB(255,0,0)`: another file. Yellow fill `RGB(255,255,0)`: key assumptions and cells to fill in.
- Currency `$#,##0`, unit named in the header (`Revenue ($mm)`). Zeros render as `-`, including percentages (`$#,##0;($#,##0);-`). Negatives in parentheses. Percentages `0.0%`, **stored as fractions** (`0.15` renders `15.0%`). Multiples `0.0x`. Years as text (`"2024"`, never `2,024`).
- Every assumption lives in its own labeled cell (`=B5*(1+$B$6)`, never `=B5*1.05`). The same formula across every projection period. Guard denominators that can be zero.

## openpyxl

- Reading a model takes two loads. The default returns formula strings and no values. `data_only=True` returns cached values and drops the formulas. One pass cannot give you both.
- Saving a workbook opened with `data_only=True` replaces every formula with a literal.
- `data_only=True` on a file openpyxl just wrote returns `None` until `recalc`. A formula whose result is `""` also reads back as `None`.
- Merged cells: write the top-left anchor only. Other cells in the range are read-only.
- `.xlsm` loses its macros unless `load_workbook(..., keep_vba=True)`.
- A sheet name with a space must be quoted: `='Assumptions Inputs'!$B$5`. Unquoted, it evaluates to `#VALUE!`.

## Delivery Workflow

1. Choose pandas vs openpyxl per `references/xlsx-guide.md`.
2. Use Excel formulas in cells — do not hardcode Python-calculated values.
3. Save the workbook.
4. If the file contains formulas, recalculate:

```bash
cd ../_shared/office-tools
uv run python3 office_tools.py recalc output.xlsx
```

5. Fix `error_summary` and recalc again until `status` is `success`.
6. Check 2–3 calculated values against the spec.
7. When using unpack/pack, run `validate` before delivery.

## Completion discipline

**REQUIRED SUB-SKILL:** Read `../verification-before-completion/SKILL.md` (or `verification-before-completion` when installed globally) before any completion claim.

| Excuse | Reality |
|--------|---------|
| "File saved" | Not done if formulas are present — run `recalc` |
| "Recalc passed earlier" | Re-run `recalc` in this message |
| "Values look right" | Python-calculated cells are not verified Excel formulas |
| "`status: success`" | Formulas evaluated. Still check 2–3 results |
| "XLOOKUP is clearer" | LibreOffice verification cannot evaluate it |
| "That `#REF!` was already there" | Prove it on the original with `data_only=True` |
| "Exit code 0" | Read JSON `status`. An `error` key means nothing was recalculated |

## Delivery Checklist

1. Deliver `.xlsx` (or `.xlsm` with `keep_vba=True` if macros are required).
2. Zero formula errors when formulas are present — fresh `recalc` JSON `status: success` in this message.
3. Formulas use functions LibreOffice can evaluate (see above).
4. Match existing conventions when editing a file. New financial models use the color and number rules above.
5. Mention skipped checks (no LibreOffice Calc, recalc not run, `--force` used on external links).
