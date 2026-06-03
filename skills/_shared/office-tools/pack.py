#!/usr/bin/env python3
"""Pack an unpacked directory into a DOCX/PPTX/XLSX file.

Validates with auto-repair, condenses XML (removes pretty-print whitespace),
and creates the Office file.

Usage:
    python pack.py unpacked/ output.docx --original input.docx
    python pack.py unpacked/ output.pptx
    python pack.py unpacked/ output.docx --no-validate
"""

import argparse
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

try:
    import defusedxml.minidom as minidom_mod
except ImportError:
    import xml.dom.minidom as minidom_mod

from validate import validate

SMART_QUOTE_MAP = {
    "\u201c": "&#x201C;",
    "\u201d": "&#x201D;",
    "\u2018": "&#x2018;",
    "\u2019": "&#x2019;",
}


def condense_xml(xml_file: Path) -> None:
    """Remove pretty-print whitespace from XML, preserving text content.

    Strips whitespace-only text nodes from all elements EXCEPT text elements
    (w:t, a:t, etc.) where whitespace is meaningful content.
    """
    try:
        with open(xml_file, encoding="utf-8") as f:
            dom = minidom_mod.parse(f)

        for element in dom.getElementsByTagName("*"):
            # Skip text elements where whitespace matters
            if element.tagName.endswith(":t"):
                continue
            for child in list(element.childNodes):
                if (child.nodeType == child.TEXT_NODE
                        and child.nodeValue
                        and child.nodeValue.strip() == ""):
                    element.removeChild(child)
                elif child.nodeType == child.COMMENT_NODE:
                    element.removeChild(child)

        xml_file.write_bytes(dom.toxml(encoding="UTF-8"))
    except Exception as e:
        print(f"ERROR: Failed to condense {xml_file.name}: {e}", file=sys.stderr)
        raise


def encode_smart_quotes(xml_file: Path) -> None:
    """Re-encode smart quotes as XML entities for safe round-tripping."""
    try:
        content = xml_file.read_text(encoding="utf-8")
        for char, entity in SMART_QUOTE_MAP.items():
            content = content.replace(char, entity)
        xml_file.write_text(content, encoding="utf-8")
    except Exception:
        pass


def pack(
    input_directory: str,
    output_file: str,
    original_file: str | None = None,
    do_validate: bool = True,
) -> str:
    """Pack directory into Office file. Returns status message."""
    input_dir = Path(input_directory)
    output_path = Path(output_file)
    suffix = output_path.suffix.lower()

    if not input_dir.is_dir():
        return f"Error: {input_dir} is not a directory"

    if suffix not in {".docx", ".pptx", ".xlsx"}:
        return f"Error: {output_file} must be .docx, .pptx, or .xlsx"

    # Validate with auto-repair
    if do_validate:
        original_path = Path(original_file) if original_file else None
        if original_path and not original_path.exists():
            print(
                f"Warning: --original {original_file} not found; validating unpacked dir only.",
                file=sys.stderr,
            )
            original_path = None
        elif not original_path:
            print(
                "Warning: no --original provided; validating unpacked dir only "
                "(redline comparison skipped).",
                file=sys.stderr,
            )
        result = validate(
            input_dir,
            original_path,
            auto_repair=True,
            file_type=suffix.lstrip("."),
        )
        print(result.report())
        if not result.ok:
            return f"Error: Validation failed for {input_dir}"

    # Work on a copy to avoid modifying the unpacked source
    with tempfile.TemporaryDirectory() as temp_dir:
        work_dir = Path(temp_dir) / "content"
        shutil.copytree(input_dir, work_dir)

        # Condense XML and re-encode smart quotes
        for pattern in ("*.xml", "*.rels"):
            for xml_file in work_dir.rglob(pattern):
                condense_xml(xml_file)
                encode_smart_quotes(xml_file)

        # Create ZIP
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in work_dir.rglob("*"):
                if f.is_file():
                    zf.write(f, f.relative_to(work_dir))

    return f"Successfully packed {input_dir} to {output_file}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pack directory into Office file")
    parser.add_argument("input_directory", help="Unpacked Office document directory")
    parser.add_argument("output_file", help="Output file (.docx/.pptx/.xlsx)")
    parser.add_argument("--original", help="Original file for validation comparison")
    parser.add_argument("--no-validate", action="store_true", help="Skip validation")
    args = parser.parse_args()

    message = pack(
        args.input_directory,
        args.output_file,
        original_file=args.original,
        do_validate=not args.no_validate,
    )
    print(message)
    if message.startswith("Error:"):
        sys.exit(1)
