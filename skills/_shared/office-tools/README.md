# office-tools

Open-source Python toolkit for programmatic DOCX and PPTX manipulation.
Drop-in custom instructions for AI coding assistants (Cursor, Claude Code, etc.).

## Quick Start

```bash
uv sync
# or: pip install lxml Pillow defusedxml
```

## Unified CLI

```bash
python3 office_tools.py <command> [args...]
```

| Command | Purpose |
|---------|---------|
| `unpack` | Unzip + pretty-print XML + merge runs + simplify tracked changes + smart quotes |
| `pack` | Validate + auto-repair + condense XML + repack |
| `validate` | Full validation suite (15 checks) with auto-repair |
| `analyze` | Extract PPTX template placeholder structure |
| `extract` | Pure Python text extraction (no pandoc needed) |
| `comment` | Add DOCX comments/replies across 4+ XML files |
| `accept` | Accept all tracked changes via LibreOffice macro |
| `verify` | Verify tracked changes correctness via text comparison |
| `slide` | Duplicate PPTX slides or create from layout |
| `clean` | Remove orphaned PPTX files (cascading) |
| `thumbnail` | PPTX layout preview: thumbnail grid and/or per-slide JPEGs (`--per-slide`, `--dpi`, `--no-grid`) |

### Standalone scripts (also usable directly)

| Script | Extras |
|--------|--------|
| `analyze_template.py` | Same as `analyze` command (standalone entry) |
| `soffice_wrapper.py` | LibreOffice wrapper with AF_UNIX socket shim |

## Validation Checks (15 total)

| # | Check | DOCX | PPTX | Auto-repair |
|---|-------|------|------|-------------|
| 1 | Well-formed XML | yes | yes | - |
| 2 | Content types vs files | yes | yes | - |
| 3 | Relationship targets exist | yes | yes | - |
| 4 | Unique element IDs | yes | yes | - |
| 5 | r:id cross-references vs .rels | yes | yes | - |
| 6 | Bidirectional file references | yes | yes | - |
| 7 | Media extension declarations | yes | yes | - |
| 8 | xml:space="preserve" on whitespace | yes | - | **yes** |
| 9 | Tracked changes (delText in del) | yes | - | - |
| 10 | paraId/durableId constraints | yes | - | **yes** |
| 11 | Comment marker pairing | yes | - | - |
| 12 | Paragraph count comparison | yes | - | - |
| 13 | **Redlining verification** (text diff) | yes | - | - |
| 14 | Slide layout uniqueness | - | yes | - |
| 15 | Notes slide reference uniqueness | - | yes | - |

## Workflows

### Create new DOCX
```bash
node create_document.js          # use docx-js (see docx-guide.md)
python3 office_tools.py validate output.docx --auto-repair
```

### Edit existing DOCX with tracked changes
```bash
python3 office_tools.py unpack document.docx unpacked/
# Edit XML in unpacked/word/document.xml
python3 office_tools.py pack unpacked/ output.docx --original document.docx
# Pack runs: auto-repair -> validation checks -> redline verification (if --original) -> pack
```

### Add comments
```bash
python3 office_tools.py unpack document.docx unpacked/
python3 office_tools.py comment unpacked/ 0 "This needs revision"
python3 office_tools.py comment unpacked/ 1 "Agreed" --parent 0
# Add markers to document.xml, then pack
```

### Accept all tracked changes
```bash
python3 office_tools.py accept input.docx clean_output.docx
```

### Analyze PPTX template before editing
```bash
python3 analyze_template.py template.pptx     # structured placeholder map
python3 office_tools.py thumbnail template.pptx /tmp/preview --cols 4
python3 office_tools.py thumbnail deck.pptx /tmp/preview --per-slide /tmp/slides --dpi 150 --no-grid
```

### Edit PPTX template
```bash
python3 office_tools.py unpack template.pptx unpacked/
python3 office_tools.py slide unpacked/ slide2.xml       # duplicate
python3 office_tools.py slide unpacked/ slideLayout3.xml  # from layout
# Edit slide XML, reorder in presentation.xml
python3 office_tools.py clean unpacked/
python3 office_tools.py pack unpacked/ output.pptx --original template.pptx
```

### Extract text (no pandoc needed)
```bash
python3 office_tools.py extract document.docx
python3 office_tools.py extract presentation.pptx
```

## Integration

### Skills Repository
This toolkit is shared by the sibling `word-document` and `powerpoint-presentation` skills.

Expected installed layout:

```text
<skills-root>/
	word-document/
	powerpoint-presentation/
	_shared/
		office-tools/
```

From either Office skill, reference this toolkit as `../_shared/office-tools/`.

### Claude Code
```markdown
# Architecture Document Skills
Scripts in ../_shared/office-tools/ support DOCX/PPTX manipulation.
See ../word-document/references/docx-guide.md and ../powerpoint-presentation/references/pptx-guide.md for API patterns.
```

## Dependencies

- **Required:** Python 3.10+, `lxml`, `Pillow`, `defusedxml`
- **Install (Python only):** `bash install_deps.sh` then `uv run python3 office_tools.py` from this directory
- **Install (with layout preview / PDF):** `bash install_deps.sh --with-system` (from repo root: `bash scripts/install_deps.sh office-system`)

### System packages (optional — `--with-system`)

| You want… | Install system deps? | Packages (typical) |
|-----------|----------------------|--------------------|
| Create new DOCX/PPTX (docx-js / pptxgenjs) | No | Node only |
| `validate`, `extract`, `unpack`, `pack`, `analyze` | No | Python (`uv sync`) only |
| **PPTX layout preview** (`thumbnail` grid / per-slide JPEGs) | **Yes** | LibreOffice **Impress**, Poppler |
| DOCX/PPTX → PDF or images | Yes | LibreOffice, Poppler |
| `accept` tracked changes on DOCX | Yes | LibreOffice |

On RHEL/Oracle Linux, PPTX conversion needs `libreoffice-impress` (not `libreoffice-core` alone). `install_deps.sh --with-system` installs the correct set on dnf/yum.

**PowerPoint skill:** system deps are required on every deck (mandatory `thumbnail` layout review). Install `--with-system` before PPT work.

**Word-only / docx-js:** agents can deliver without system deps if they skip PDF conversion and accept-changes.
- **Node.js:** `docx` (create DOCX), `pptxgenjs` (create PPTX)

## License

MIT
