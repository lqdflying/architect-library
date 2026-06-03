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

For creating DOCX files from scratch, install the Node package used by the guide:

```bash
npm install -g docx
```

## References

- `SKILL.md` - agent workflow
- `references/docx-guide.md` - DOCX creation and XML editing details
- `../_shared/office-tools/` - validation, unpack, pack, comments, redline, and extraction tools
