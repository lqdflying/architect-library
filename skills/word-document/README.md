# Word Document Skill

Create, edit, and validate Microsoft Word architecture documents.

## Use When

- The user asks for a `.docx` file.
- The artifact is an HLD, LLD, ADR, solution design, migration plan, requirements document, or review document.
- The task requires comments, tracked changes, text extraction, or validation of an existing Word file.

## Setup

Install the shared Office toolkit dependencies from the installed skills root:

```bash
cd ../_shared/office-tools
bash install_deps.sh
```

For creating DOCX files from scratch:

```bash
bash scripts/install_deps.sh node    # docx-js (preferred)
# Without npm: bash scripts/install_deps.sh office — python-docx fallback
```

## References

- `SKILL.md` - agent workflow
- `references/docx-guide.md` - docx-js creation and XML editing (explicit table theming)
- `references/production-lessons.md` - compliance ADD lessons, one styling path, visual verify
- `references/python-docx-patterns.md` - python-docx: built-in table style + tblHeader, or explicit fills
- `../_shared/office-tools/` - validation, unpack, pack, comments, redline, and extraction tools
