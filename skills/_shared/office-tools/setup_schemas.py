#!/usr/bin/env python3
"""Download ECMA-376 XSD schemas from the official ECMA website.

Downloads the OOXML Transitional schemas (Part 4) and OPC schemas (Part 2)
from ecma-international.org. These are freely available public standards.

Usage:
    python setup_schemas.py
    python setup_schemas.py --target ./schemas
"""

import argparse
import io
import sys
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request

ECMA_PART4_URL = (
    "https://ecma-international.org/wp-content/uploads/"
    "ECMA-376-4_5th_edition_december_2016.zip"
)
ECMA_PART2_URL = (
    "https://ecma-international.org/wp-content/uploads/"
    "ECMA-376-2_5th_edition_december_2021.zip"
)

XML_XSD = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
  targetNamespace="http://www.w3.org/XML/1998/namespace" xml:lang="en">
  <xs:attribute name="lang" type="xs:language"/>
  <xs:attribute name="space">
    <xs:simpleType>
      <xs:restriction base="xs:NCName">
        <xs:enumeration value="default"/>
        <xs:enumeration value="preserve"/>
      </xs:restriction>
    </xs:simpleType>
  </xs:attribute>
  <xs:attribute name="base" type="xs:anyURI"/>
  <xs:attribute name="id" type="xs:ID"/>
  <xs:attributeGroup name="specialAttrs">
    <xs:attribute ref="xml:base"/>
    <xs:attribute ref="xml:lang"/>
    <xs:attribute ref="xml:space"/>
    <xs:attribute ref="xml:id"/>
  </xs:attributeGroup>
</xs:schema>"""


def download(url: str) -> bytes:
    """Download a URL and return bytes."""
    print(f"  Downloading {url.split('/')[-1]}...")
    req = Request(url, headers={"User-Agent": "office-tools/1.0"})
    with urlopen(req, timeout=60) as resp:
        return resp.read()


def extract_nested_zip(outer_data: bytes, inner_name: str) -> dict[str, bytes]:
    """Extract files from a ZIP nested inside another ZIP."""
    with zipfile.ZipFile(io.BytesIO(outer_data)) as outer:
        with outer.open(inner_name) as inner_file:
            with zipfile.ZipFile(io.BytesIO(inner_file.read())) as inner:
                return {
                    name: inner.read(name)
                    for name in inner.namelist()
                    if name.endswith(".xsd")
                }


def setup_schemas(target_dir: Path) -> bool:
    """Download and install ECMA-376 XSD schemas. Returns True on success."""
    ooxml_dir = target_dir / "ooxml"
    opc_dir = target_dir / "opc"
    ooxml_dir.mkdir(parents=True, exist_ok=True)
    opc_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Part 4: OOXML Transitional schemas (wml.xsd, pml.xsd, etc.)
        print("Downloading ECMA-376 Part 4 (OOXML Transitional schemas)...")
        part4_data = download(ECMA_PART4_URL)
        ooxml_files = extract_nested_zip(
            part4_data, "OfficeOpenXML-XMLSchema-Transitional.zip"
        )
        for name, data in ooxml_files.items():
            (ooxml_dir / name).write_bytes(data)
        print(f"  Installed {len(ooxml_files)} OOXML schemas")

        # Part 2: OPC schemas (opc-contentTypes.xsd, etc.)
        print("Downloading ECMA-376 Part 2 (OPC schemas)...")
        part2_data = download(ECMA_PART2_URL)
        opc_files = extract_nested_zip(
            part2_data, "OpenPackagingConventions-XMLSchema.zip"
        )
        for name, data in opc_files.items():
            (opc_dir / name).write_bytes(data)
        print(f"  Installed {len(opc_files)} OPC schemas")

        # xml.xsd (W3C XML namespace)
        (ooxml_dir / "xml.xsd").write_text(XML_XSD)
        print("  Added xml.xsd (W3C XML namespace)")

        total = len(ooxml_files) + len(opc_files) + 1
        print(f"\nDone: {total} schema files installed to {target_dir}/")
        return True

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        print(
            "\nManual download:",
            "\n  1. Go to https://ecma-international.org/publications-and-standards/standards/ecma-376/",
            "\n  2. Download Part 4 (5th Edition) and Part 2 (5th Edition)",
            "\n  3. Extract *-XMLSchema-*.zip from each",
            f"\n  4. Place .xsd files in {ooxml_dir}/ and {opc_dir}/",
            file=sys.stderr,
        )
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download ECMA-376 XSD schemas for OOXML validation"
    )
    parser.add_argument(
        "--target",
        default=str(Path(__file__).parent / "schemas"),
        help="Target directory (default: ./schemas)",
    )
    args = parser.parse_args()

    target = Path(args.target)
    success = setup_schemas(target)
    sys.exit(0 if success else 1)
