---
name: spreadsheet-document
description: "Open, create, edit, or analyze spreadsheet files (.xlsx, .xlsm, .csv, .tsv). Deliver .xlsx with zero formula errors after office_tools recalc when formulas are used. Financial models, data cleanup, tabular exports. Install office + office-system for recalc. Do not use when the primary deliverable is Word, PDF, or a standalone script."
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
bash ../_shared/office-tools/install_deps.sh --with-system   # LibreOffice for recalc
# or from repo root:
#   bash scripts/install_deps.sh office
#   bash scripts/install_deps.sh office-system
```

Prefer the uv environment:

```bash
cd ../_shared/office-tools
uv run python3 office_tools.py --help
```

## Decision Workflow

| Task | Primary tool |
|------|--------------|
| Data analysis, bulk read/write | pandas (`read_excel` / `to_excel`) |
| Formulas, formatting, multi-sheet edits | openpyxl |
| Recalculate formula values | `office_tools.py recalc` (requires LibreOffice) |
| Edit XLSX XML directly | `office_tools.py unpack` → edit → `pack` |
| Validate OOXML | `office_tools.py validate` |

## Delivery Workflow

1. Choose pandas vs openpyxl per `references/xlsx-guide.md`.
2. Use Excel formulas in cells — do not hardcode Python-calculated values.
3. Save the workbook.
4. If the file contains formulas, recalculate and verify:

```bash
python3 ../_shared/office-tools/office_tools.py recalc output.xlsx
```

5. Fix any errors reported in JSON (`error_summary`) and recalc again until `status` is `success`.
6. When using unpack/pack, run `validate` before delivery.

## Completion discipline

**REQUIRED SUB-SKILL:** Read `../verification-before-completion/SKILL.md` (or `verification-before-completion` when installed globally) before any completion claim.

| Excuse | Reality |
|--------|---------|
| "File saved" | Not done if formulas present — run `recalc` |
| "Recalc passed earlier" | Re-run `recalc` in this message |
| "Values look right" | Python-calculated cells ≠ Excel formulas verified |

## Delivery Checklist

1. Deliver `.xlsx` (or `.xlsm` if macros required).
2. Zero formula errors when formulas are present — fresh `recalc` JSON `status: success` in this message.
3. Match existing template conventions when editing templates.
4. Mention skipped checks (no LibreOffice, recalc not run).
