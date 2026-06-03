#!/usr/bin/env python3
"""XSD schema validation for OOXML documents.

Validates XML files against ECMA-376 / ISO-IEC 29500 XSD schemas.
Only reports NEW errors (errors not present in the original file).

Schemas are from the ECMA-376 5th Edition standard (free download).

Usage:
    python xsd_validator.py unpacked/ --original document.docx
    python xsd_validator.py unpacked/word/document.xml
"""

import argparse
import re
import sys
import tempfile
import zipfile
from pathlib import Path

from safe_zip import safe_extract

try:
    import lxml.etree as etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False
    print("Warning: lxml required for XSD validation", file=sys.stderr)

# Schema file mappings: key -> relative path under schemas/
SCHEMA_MAP = {
    # Main content schemas (ooxml/)
    "word": "ooxml/wml.xsd",
    "ppt": "ooxml/pml.xsd",
    "xl": "ooxml/sml.xsd",
    "chart": "ooxml/dml-chart.xsd",
    "theme": "ooxml/dml-main.xsd",
    "drawing": "ooxml/dml-main.xsd",
    # OPC schemas
    "[Content_Types].xml": "opc/opc-contentTypes.xsd",
    "app.xml": "ooxml/shared-documentPropertiesExtended.xsd",
    "core.xml": "opc/opc-coreProperties.xsd",
    "custom.xml": "ooxml/shared-documentPropertiesCustom.xsd",
    ".rels": "opc/opc-relationships.xsd",
}

MAIN_CONTENT_FOLDERS = {"word", "ppt", "xl"}

MC_NAMESPACE = "http://schemas.openxmlformats.org/markup-compatibility/2006"

OOXML_NAMESPACES = {
    "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "http://schemas.openxmlformats.org/schemaLibrary/2006/main",
    "http://schemas.openxmlformats.org/drawingml/2006/main",
    "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
    "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "http://schemas.openxmlformats.org/presentationml/2006/main",
    "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "http://schemas.openxmlformats.org/package/2006/relationships",
    "http://schemas.openxmlformats.org/package/2006/content-types",
    "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "http://purl.org/dc/elements/1.1/",
    "http://purl.org/dc/dcmitype/",
    "http://purl.org/dc/terms/",
    "urn:schemas-microsoft-com:office:office",
    "urn:schemas-microsoft-com:office:word",
    "urn:schemas-microsoft-com:vml",
    "http://www.w3.org/XML/1998/namespace",
}

IGNORED_PATTERNS = [
    "hyphenationZone",
    "purl.org/dc/terms",
]


def _get_schemas_dir() -> Path | None:
    """Find schemas directory relative to this script."""
    candidates = [
        Path(__file__).parent / "schemas",
        Path.cwd() / "schemas",
    ]
    for d in candidates:
        if d.exists() and (d / "ooxml" / "wml.xsd").exists():
            return d
    return None


def _get_schema_path(xml_file: Path, schemas_dir: Path) -> Path | None:
    """Determine which XSD schema applies to a given XML file."""
    if xml_file.name in SCHEMA_MAP:
        return schemas_dir / SCHEMA_MAP[xml_file.name]

    if xml_file.suffix == ".rels":
        return schemas_dir / SCHEMA_MAP[".rels"]

    if "charts/" in str(xml_file) and xml_file.name.startswith("chart"):
        return schemas_dir / SCHEMA_MAP["chart"]

    if "theme/" in str(xml_file) and xml_file.name.startswith("theme"):
        return schemas_dir / SCHEMA_MAP["theme"]

    if xml_file.parent.name in MAIN_CONTENT_FOLDERS:
        return schemas_dir / SCHEMA_MAP.get(xml_file.parent.name)

    return None


def _strip_ignorable_content(xml_doc):
    """Remove MC:Ignorable namespaces and elements for clean validation."""
    xml_string = etree.tostring(xml_doc, encoding="unicode")
    root = etree.fromstring(xml_string)

    # Remove mc:Ignorable attribute
    ignorable_attr = f"{{{MC_NAMESPACE}}}Ignorable"
    if ignorable_attr in root.attrib:
        del root.attrib[ignorable_attr]

    # Remove mc:AlternateContent elements
    for elem in root.xpath("//mc:AlternateContent",
                           namespaces={"mc": MC_NAMESPACE}):
        if elem.getparent() is not None:
            elem.getparent().remove(elem)

    # Remove attributes from non-OOXML namespaces
    for elem in root.iter():
        if not hasattr(elem, "attrib"):
            continue
        to_remove = []
        for attr in elem.attrib:
            if "{" in attr:
                ns = attr.split("}")[0][1:]
                if ns not in OOXML_NAMESPACES:
                    to_remove.append(attr)
        for attr in to_remove:
            del elem.attrib[attr]

    # Remove elements from non-OOXML namespaces
    _remove_non_ooxml_elements(root)

    return etree.ElementTree(root)


def _remove_non_ooxml_elements(elem):
    """Recursively remove elements from non-OOXML namespaces."""
    to_remove = []
    for child in list(elem):
        if not hasattr(child, "tag") or callable(child.tag):
            continue
        tag_str = str(child.tag)
        if tag_str.startswith("{"):
            ns = tag_str.split("}")[0][1:]
            if ns not in OOXML_NAMESPACES:
                to_remove.append(child)
                continue
        _remove_non_ooxml_elements(child)
    for child in to_remove:
        elem.remove(child)


def _strip_template_tags(xml_doc):
    """Remove {{template}} tags from text nodes that would fail validation."""
    template_re = re.compile(r"\{\{[^}]*\}\}")
    root = etree.fromstring(etree.tostring(xml_doc, encoding="unicode"))
    for elem in root.iter():
        if not hasattr(elem, "tag") or callable(elem.tag):
            continue
        tag_str = str(elem.tag)
        if tag_str.endswith("}t") or tag_str == "t":
            continue
        if elem.text and template_re.search(elem.text):
            elem.text = template_re.sub("", elem.text)
        if elem.tail and template_re.search(elem.tail):
            elem.tail = template_re.sub("", elem.tail)
    return etree.ElementTree(root)


def validate_file_xsd(
    xml_file: Path,
    schemas_dir: Path,
    unpacked_dir: Path,
) -> tuple[bool | None, set[str]]:
    """Validate a single XML file against its XSD schema.

    Returns:
        (None, set()) - no schema found, skipped
        (True, set()) - valid
        (False, errors) - invalid with error messages
    """
    schema_path = _get_schema_path(xml_file, schemas_dir)
    if not schema_path or not schema_path.exists():
        return None, set()

    try:
        xsd_doc = etree.parse(str(schema_path),
                              parser=etree.XMLParser(),
                              base_url=str(schema_path))
        schema = etree.XMLSchema(xsd_doc)

        xml_doc = etree.parse(str(xml_file))

        # Preprocess: strip template tags and non-OOXML content
        xml_doc = _strip_template_tags(xml_doc)

        rel_path = xml_file.relative_to(unpacked_dir)
        if rel_path.parts and rel_path.parts[0] in MAIN_CONTENT_FOLDERS:
            xml_doc = _strip_ignorable_content(xml_doc)

        if schema.validate(xml_doc):
            return True, set()
        else:
            errors = {err.message for err in schema.error_log}
            return False, errors

    except Exception as e:
        return False, {str(e)}


def validate_xsd(
    unpacked_dir: Path,
    original_file: Path | None = None,
) -> tuple[bool, list[str]]:
    """Validate all XML files against XSD schemas.

    Only reports NEW errors (not present in the original file).
    Returns (all_passed, error_messages).
    """
    if not HAS_LXML:
        return True, ["Skipped: lxml not available"]

    schemas_dir = _get_schemas_dir()
    if not schemas_dir:
        return True, ["Skipped: schemas/ directory not found (run setup_schemas.py)"]

    xml_files = list(unpacked_dir.rglob("*.xml")) + list(unpacked_dir.rglob("*.rels"))
    new_errors = []
    stats = {"valid": 0, "skipped": 0, "with_original_errors": 0, "new_errors": 0}

    for xml_file in xml_files:
        is_valid, current_errors = validate_file_xsd(xml_file, schemas_dir, unpacked_dir)

        if is_valid is None:
            stats["skipped"] += 1
            continue
        elif is_valid:
            stats["valid"] += 1
            continue

        # Get original file's errors to diff
        original_errors = set()
        if original_file and original_file.exists():
            original_errors = _get_original_errors(
                xml_file, unpacked_dir, original_file, schemas_dir
            )

        # Only report NEW errors
        errors_diff = current_errors - original_errors
        errors_diff = {
            e for e in errors_diff
            if not any(p in e for p in IGNORED_PATTERNS)
        }

        if errors_diff:
            stats["new_errors"] += 1
            rel = xml_file.relative_to(unpacked_dir)
            new_errors.append(f"{rel}: {len(errors_diff)} new XSD error(s)")
            for err in list(errors_diff)[:3]:
                truncated = err[:200] + "..." if len(err) > 200 else err
                new_errors.append(f"  - {truncated}")
        else:
            stats["with_original_errors"] += 1
            stats["valid"] += 1

    return len(new_errors) == 0, new_errors


def _get_original_errors(
    xml_file: Path,
    unpacked_dir: Path,
    original_file: Path,
    schemas_dir: Path,
) -> set[str]:
    """Get XSD errors from the same file in the original document."""
    rel_path = xml_file.relative_to(unpacked_dir)
    try:
        with tempfile.TemporaryDirectory() as td:
            with zipfile.ZipFile(original_file, "r") as zf:
                safe_extract(zf, Path(td))
            orig_xml = Path(td) / rel_path
            if not orig_xml.exists():
                return set()
            _, errors = validate_file_xsd(orig_xml, schemas_dir, Path(td))
            return errors or set()
    except Exception:
        return set()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="XSD schema validation for OOXML")
    parser.add_argument("path", help="Unpacked directory or XML file")
    parser.add_argument("--original", help="Original Office file for error diffing")
    args = parser.parse_args()

    if not HAS_LXML:
        print("Error: lxml is required for XSD validation")
        sys.exit(1)

    path = Path(args.path)
    original = Path(args.original) if args.original else None

    with tempfile.TemporaryDirectory() as td:
        if path.is_file() and path.suffix.lower() in {".docx", ".pptx", ".xlsx"}:
            with zipfile.ZipFile(path, "r") as zf:
                safe_extract(zf, Path(td))
            unpacked = Path(td)
        else:
            unpacked = path

        passed, messages = validate_xsd(unpacked, original)

        for msg in messages:
            print(msg)
        if passed:
            print("XSD validation PASSED (no new errors)")
        else:
            print(f"\nXSD validation FAILED")
        sys.exit(0 if passed else 1)
