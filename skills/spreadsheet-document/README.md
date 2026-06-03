# spreadsheet-document

Agent skill for Excel/spreadsheet tasks (`.xlsx`, `.xlsm`, `.csv`, `.tsv`).

## Setup

From repository root:

```bash
bash scripts/install_deps.sh office
bash scripts/install_deps.sh office-system   # LibreOffice — required for formula recalc
```

Or from this skill folder:

```bash
bash ../_shared/office-tools/install_deps.sh --with-system
```

## Key commands

```bash
cd ../_shared/office-tools
uv run python3 office_tools.py recalc model.xlsx
uv run python3 office_tools.py validate model.xlsx --auto-repair
```

## References

- `SKILL.md` — agent workflow
- `references/xlsx-guide.md` — detailed patterns
- `LICENSE.txt` — proprietary terms (Anthropic)
