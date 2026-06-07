---
name: pdf-document
description: Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting/decrypting PDFs, extracting images, and OCR on scanned PDFs to make them searchable. If the user mentions a .pdf file or asks to produce one, use this skill.
---

# PDF Document Skill

Read, create, merge, split, and fill PDF files. Deliver the requested `.pdf` unless the user asks for extracted text or images only.

## Load First

- `references/pdf-guide.md` — common operations (pypdf, pdfplumber, reportlab, CLI tools)
- `references/pdf-reference.md` — advanced APIs and troubleshooting
- `references/forms.md` — PDF form fill workflows and validation scripts

## Setup

```bash
bash references/install_deps.sh
# or from repo root:
#   bash scripts/install_deps.sh pdf
```

Optional system tools (documented in `pdf-guide.md`, not installed by default): `qpdf`, `pdftk`, Poppler (`pdftotext`, `pdfimages`). OCR: `pytesseract`, `pdf2image`.

## Form Fill Workflow

When filling PDF forms, follow `references/forms.md` and run validation scripts under `scripts/` (uv project is `references/`):

```bash
uv run --project skills/pdf-document/references python skills/pdf-document/scripts/check_fillable_fields.py form.pdf
uv run --project skills/pdf-document/references python skills/pdf-document/scripts/create_validation_image.py ...
```

## Delivery Checklist

1. Deliver the requested `.pdf` (or agreed export format).
2. For form fills: run check/validation scripts per `forms.md` before finishing.
3. Note skipped optional tools (OCR, qpdf) if used workarounds.
