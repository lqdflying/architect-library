---
name: word-document
description: Create, edit, and validate Microsoft Word DOCX architecture documents, HLDs, LLDs, ADRs, design docs, requirements, comments, tracked changes, and template-based Word files.
---

# Word Architecture Document Creator

Create and edit `.docx` architecture documents with production-quality structure, formatting, comments, tracked changes, and validation.

Use this skill when the user asks for a Word document, DOCX file, architecture design document, HLD, LLD, ADR, solution design, technical specification, migration plan, operating model, requirements document, or review document.

## Load First

Before authoring substantial content, read:

- `../_shared/architecture-document-principles.md`
- `references/docx-guide.md`
- `references/production-lessons.md` — table styling, compliance structure, generator workflow (read for ADD/compliance DOCX)
- `references/python-docx-patterns.md` — only if generating with python-docx instead of docx-js

For DOCX tooling, use the shared toolkit:

```bash
python3 ../_shared/office-tools/office_tools.py --help
```

If the skill is installed in an editor skills folder, `_shared` should be a sibling of `word-document`.

## Setup

Run once from this skill folder (or use `bash scripts/install_deps.sh office` from the repository root):

```bash
bash ../_shared/office-tools/install_deps.sh
```

For PDF conversion and accepting tracked changes, install optional system packages:

```bash
bash ../_shared/office-tools/install_deps.sh --with-system
```

For **new** DOCX files (docx-js workflow), install Node.js and the `docx` package globally:

```bash
npm install -g docx
```

After `install_deps.sh`, prefer the uv environment for Office toolkit commands:

```bash
cd ../_shared/office-tools
uv run python3 office_tools.py --help
```

From this skill folder you can also use `python3 ../_shared/office-tools/office_tools.py` if dependencies are already on your PATH.

## Decision Workflow

First decide which path fits the request.

| Task | Primary tool |
|------|--------------|
| Create a new DOCX from scratch | `docx` npm package (if no npm: python-docx per `python-docx-patterns.md`) |
| Edit an existing DOCX | Unpack, edit XML, pack |
| Add comments | `office_tools.py comment` |
| Accept tracked changes | `office_tools.py accept` |
| Verify redlines | `office_tools.py verify` |
| Extract text for analysis | `office_tools.py extract` |
| Validate output | `office_tools.py validate` |
| Convert DOCX to PDF | LibreOffice headless |

Do not hand-edit a `.docx` as a binary file. A DOCX is a ZIP package of XML parts. For existing documents, unpack it, edit the relevant XML parts, then repack and validate.

## New DOCX Workflow

Use `docx` (docx-js) for new documents.

1. Determine the document type and audience.
2. Build an outline using the architecture principles.
3. Create a Node script using the patterns in `references/docx-guide.md`.
4. Set page size and margins explicitly.
5. Define heading styles with correct `Heading1`, `Heading2`, and outline levels so the table of contents works.
6. Use Word numbering APIs for bullets and numbered lists. Do not type unicode bullets manually.
7. Use DXA units consistently.
8. Generate the DOCX with **one table-styling approach** (docx-js: explicit fills in `docx-guide.md`; python-docx: built-in `Medium Shading 1 Accent 1` + header row, or explicit fills only—never both). Use 9pt table text and fixed column widths.
9. For compliance/ADD docs, read `references/production-lessons.md` (parallel tool tables, TOC, visual verify).
10. Validate the output:

```bash
python3 ../_shared/office-tools/office_tools.py validate output.docx --auto-repair
```

## Existing DOCX Workflow

Use the shared Office toolkit.

```bash
python3 ../_shared/office-tools/office_tools.py unpack input.docx unpacked/
# edit XML under unpacked/word/
python3 ../_shared/office-tools/office_tools.py pack unpacked/ output.docx --original input.docx
```

When editing XML:

- Preserve relationship IDs and content types.
- Keep tracked-change elements valid.
- Use `w:delText` inside deletions, not `w:t`.
- Add `xml:space="preserve"` for text with leading or trailing whitespace.
- Keep comments synchronized across comments XML, relationships, and content types.
- Validate before returning the file.

## Comments and Review Workflow

For comments:

```bash
python3 ../_shared/office-tools/office_tools.py comment unpacked/ 0 "Comment text"
python3 ../_shared/office-tools/office_tools.py comment unpacked/ 1 "Reply text" --parent 0
```

For tracked changes:

```bash
python3 ../_shared/office-tools/office_tools.py accept input.docx clean-output.docx
python3 ../_shared/office-tools/office_tools.py verify unpacked/ original.docx
```

Use comments when the user wants review notes. Use tracked changes only when the user asks for redlines or revision markup.

## Architecture Document Quality

A good architecture DOCX should be navigable and reviewable:

- Clear title, version, owner, date, and status where appropriate
- Executive summary for mixed audiences
- Decision and rationale sections for approvers
- Tables for risks, assumptions, dependencies, requirements, interfaces, and open questions
- Diagrams embedded or referenced when they clarify structure or flow
- Consistent heading hierarchy and table formatting (themed headers, light row banding, 9pt table text)
- No placeholder sections left empty
- Validation completed before delivery

## Tables (required for new DOCX)

Production tables must not render as plain **Table Grid** (black borders only). **Pick one styling path and verify in Word** (not XML alone). See `references/production-lessons.md`.

| Toolchain | Table styling |
|-----------|----------------|
| **docx-js** | Explicit header fill, borders, banding in code (`docx-guide.md` § Tables) |
| **python-docx** | **Preferred:** `Medium Shading 1 Accent 1` + `w:tblHeader` on row 1 + 9pt fonts/margins/widths only — **no** manual cell fills |
| **python-docx fallback** | Full explicit OXML fills — **no** built-in table style name |

Shared rules: **9pt** table text; tight cell margins; fixed column widths; `cantSplit` on rows (python-docx); concise cells to avoid bad page breaks.

**Never mix** built-in table style with hand-painted cell shading or white header text — theme will flatten to Table Grid.

**Compliance / ADD:** If one subsection uses a full inventory table (e.g. tools 5.1.1), sibling subsections (5.1.2, 5.1.3) need matching tables — not paragraph summaries only.

## Delivery Checklist

Before finishing:

1. **Open in Word** (or use a user screenshot) — confirm table header banding, not plain grid.
2. Confirm the DOCX validates when possible; note non-blocking python-docx validator warnings if Word opens cleanly.
3. Extract text if you need to confirm section order and parallel tables.
4. Mention skipped checks (no LibreOffice, no npm, no Word preview).
5. **Deliver only the `.docx`** unless the user asked for more.
6. **Do not leave generator scripts** beside the deliverable unless requested — prefer `scripts/` for maintained `generate_*.py` / `.js`.
7. Keep unpacked working directories out of the deliverable unless the user asks for them.
8. **TOC:** use heading styles in the generator; tell the user to insert TOC in Word unless they asked for an embedded field.

Regenerate the file only when content, version, or generator logic changes — not for every submission handoff. Regenerating overwrites Word-only edits unless those edits were merged into the generator.

If the user explicitly wants a maintained regen script beside the document, place it only where they specify and say so in your reply.
