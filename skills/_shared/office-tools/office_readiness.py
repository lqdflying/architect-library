#!/usr/bin/env python3
"""Check Office schema validation and rendering using disposable fixtures."""

import argparse
from pathlib import Path
import subprocess
import tempfile
import zipfile

from xsd_validator import check_schemas


def convert_preview(source: Path, scratch: Path, export_filter: str):
    from PIL import Image
    from soffice_wrapper import run_soffice

    output_dir = scratch / source.stem
    output_dir.mkdir()
    profile = output_dir / "profile"
    result = run_soffice(
        [
            f"-env:UserInstallation={profile.as_uri()}",
            "--headless", "--convert-to", f"pdf:{export_filter}",
            "--outdir", str(output_dir), str(source),
        ],
        capture_output=True, text=True, timeout=60,
    )
    pdf = output_dir / f"{source.stem}.pdf"
    if result.returncode != 0 or not pdf.is_file() or pdf.stat().st_size == 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"No usable PDF (exit {result.returncode}): {detail}")
    subprocess.run(["pdfinfo", str(pdf)], check=True, capture_output=True, timeout=30)
    prefix = output_dir / "page"
    subprocess.run(
        ["pdftoppm", "-f", "1", "-singlefile", "-scale-to", "640", "-png", str(pdf), str(prefix)],
        check=True, capture_output=True, timeout=30,
    )
    with Image.open(prefix.with_suffix(".png")) as image:
        image.verify()


def create_docx(target: Path):
    from docx import Document
    from docx.oxml.ns import qn

    document = Document()
    document.add_paragraph("Architect Library runtime check")
    document.settings.element.find(qn("w:zoom")).set(qn("w:percent"), "100")
    document.save(target)


def create_pptx(target: Path):
    script = """
const PptxGenJS = require('pptxgenjs');
const presentation = new PptxGenJS();
presentation.addSlide().addText('Architect Library runtime check', {x: 1, y: 1, w: 7, h: 1});
presentation.writeFile({fileName: process.argv[1]}).catch(error => {
    console.error(error.message);
    process.exitCode = 1;
});
"""
    subprocess.run(
        ["node", "-e", script, str(target)],
        cwd=target.parent, check=True, capture_output=True, timeout=30,
    )
    if not target.is_file() or target.stat().st_size == 0:
        raise RuntimeError("PPTX generator produced no file")


def validate_docx(source: Path, scratch: Path):
    from safe_zip import safe_extract
    from validate import validate

    unpacked = scratch / "unpacked"
    with zipfile.ZipFile(source) as archive:
        safe_extract(archive, unpacked)
    result = validate(unpacked, file_type="docx")
    if not result.ok:
        raise RuntimeError(result.report())


def run_checks(schemas_only=False) -> bool:
    def report(label, operation):
        try:
            operation()
        except Exception as error:
            print(f"  {label}: FAILED ({error})")
            return False
        print(f"  {label}: OK")
        return True

    def schema_check():
        errors = check_schemas(Path(__file__).parent / "schemas")
        if errors:
            raise RuntimeError("; ".join(errors))

    schemas_ok = report("Offline schema compilation", schema_check)
    if schemas_only:
        return schemas_ok

    with tempfile.TemporaryDirectory(prefix="architect-office-") as directory:
        scratch = Path(directory)
        docx = scratch / "word.docx"
        pptx = scratch / "slides.pptx"
        docx_ok = report("DOCX generation (python-docx)", lambda: create_docx(docx))
        validation_ok = report("DOCX validation", lambda: validate_docx(docx, scratch))
        word_ok = report("DOCX preview (Writer + Poppler)", lambda: convert_preview(docx, scratch, "writer_pdf_Export"))
        pptx_ok = report("PPTX generation (pptxgenjs)", lambda: create_pptx(pptx))
        slides_ok = report("PPTX preview (Impress + Poppler)", lambda: convert_preview(pptx, scratch, "impress_pdf_Export"))
    print("  XLSX recalculation: NOT CHECKED (requires Calc)")
    return all((schemas_ok, docx_ok, validation_ok, word_ok, pptx_ok, slides_ok))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schemas-only", action="store_true")
    arguments = parser.parse_args()
    raise SystemExit(0 if run_checks(arguments.schemas_only) else 1)