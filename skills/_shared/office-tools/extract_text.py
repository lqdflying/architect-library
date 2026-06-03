#!/usr/bin/env python3
"""Extract text from DOCX/PPTX files as readable markdown.

Pure Python, no external dependencies (pandoc, LibreOffice not needed).

Output format:
  DOCX: paragraphs with heading markers (# H1, ## H2, ...)
  PPTX: ## Slide N sections with slide content

Usage:
    python extract_text.py document.docx
    python extract_text.py presentation.pptx
    python extract_text.py document.docx -o output.md
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
DRAW_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
PRES_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


# ---------------------------------------------------------------------------
# DOCX text extraction
# ---------------------------------------------------------------------------

def extract_docx(docx_path: Path) -> str:
    """Extract text from DOCX as markdown-like output."""
    with zipfile.ZipFile(docx_path, "r") as zf:
        if "word/document.xml" not in zf.namelist():
            return "Error: word/document.xml not found"

        root = ET.fromstring(zf.read("word/document.xml"))

        # Load styles to detect headings
        styles = {}
        if "word/styles.xml" in zf.namelist():
            styles = _parse_docx_styles(zf.read("word/styles.xml"))

    lines = []
    ns = {"w": WORD_NS}

    for p in root.findall(f".//w:p", ns):
        # Get paragraph style
        style_id = ""
        ppr = p.find("w:pPr", ns)
        if ppr is not None:
            ps = ppr.find("w:pStyle", ns)
            if ps is not None:
                style_id = ps.get(f"{{{WORD_NS}}}val", "")

        # Collect text from all runs (including inside tracked changes)
        parts = []
        for t in p.findall(f".//w:t", ns):
            if t.text:
                parts.append(t.text)
        for dt in p.findall(f".//w:delText", ns):
            if dt.text:
                parts.append(f"~~{dt.text}~~")  # show deletions as strikethrough

        text = "".join(parts)

        # Apply heading prefix
        heading_level = _get_heading_level(style_id, styles)
        if heading_level and text.strip():
            prefix = "#" * heading_level
            lines.append(f"{prefix} {text}")
        elif text.strip():
            lines.append(text)
        else:
            lines.append("")  # preserve paragraph breaks

    # Clean up excessive blank lines
    result = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
    return result.strip()


def _parse_docx_styles(styles_xml: bytes) -> dict:
    """Parse styles.xml to map style IDs to their outline levels."""
    root = ET.fromstring(styles_xml)
    ns = {"w": WORD_NS}
    mapping = {}
    for style in root.findall("w:style", ns):
        sid = style.get(f"{{{WORD_NS}}}styleId", "")
        name = ""
        name_elem = style.find("w:name", ns)
        if name_elem is not None:
            name = name_elem.get(f"{{{WORD_NS}}}val", "")

        # Check outlineLevel in pPr
        ppr = style.find("w:pPr", ns)
        if ppr is not None:
            ol = ppr.find("w:outlineLevel", ns)
            if ol is not None:
                level = int(ol.get(f"{{{WORD_NS}}}val", "-1"))
                if 0 <= level <= 8:
                    mapping[sid] = level + 1  # outlineLevel 0 = H1

        # Fallback: detect from style name
        if sid not in mapping and name:
            m = re.match(r"heading\s*(\d)", name, re.IGNORECASE)
            if m:
                mapping[sid] = int(m.group(1))

    return mapping


def _get_heading_level(style_id: str, styles: dict) -> int:
    """Return heading level (1-9) or 0 if not a heading."""
    if style_id in styles:
        return styles[style_id]
    # Common built-in style IDs
    m = re.match(r"Heading(\d)", style_id)
    if m:
        return int(m.group(1))
    return 0


# ---------------------------------------------------------------------------
# PPTX text extraction
# ---------------------------------------------------------------------------

def extract_pptx(pptx_path: Path) -> str:
    """Extract text from PPTX, organized by slide."""
    with zipfile.ZipFile(pptx_path, "r") as zf:
        # Get slide order from presentation.xml
        slide_order = _get_slide_order(zf)

        sections = []
        for slide_file in slide_order:
            path = f"ppt/slides/{slide_file}"
            if path not in zf.namelist():
                continue

            root = ET.fromstring(zf.read(path))
            texts = _extract_pptx_slide_text(root)

            section = f"## {slide_file}\n"
            if texts:
                section += "\n".join(texts)
            else:
                section += "(empty slide)"
            sections.append(section)

    return "\n\n".join(sections)


def _get_slide_order(zf: zipfile.ZipFile) -> list[str]:
    """Get slide filenames in presentation order."""
    if "ppt/presentation.xml" not in zf.namelist():
        # Fallback: sort by filename
        slides = [n.split("/")[-1] for n in zf.namelist()
                  if re.match(r"ppt/slides/slide\d+\.xml$", n)]
        return sorted(slides, key=lambda s: int(re.search(r"\d+", s).group()))

    pres = ET.fromstring(zf.read("ppt/presentation.xml"))

    # Build rId -> slide filename mapping from rels
    rid_to_slide = {}
    rels_path = "ppt/_rels/presentation.xml.rels"
    if rels_path in zf.namelist():
        rels = ET.fromstring(zf.read(rels_path))
        for rel in rels:
            target = rel.get("Target", "")
            rid = rel.get("Id", "")
            if target.startswith("slides/"):
                rid_to_slide[rid] = target.replace("slides/", "")

    # Walk sldIdLst in order
    ordered = []
    ns_p = {"p": PRES_NS}
    ns_r = {"r": REL_NS}

    for sld_id in pres.findall(".//p:sldIdLst/p:sldId", ns_p):
        rid = sld_id.get(f"{{{REL_NS}}}id", "")
        if rid in rid_to_slide:
            ordered.append(rid_to_slide[rid])

    if not ordered:
        # Fallback
        slides = [n.split("/")[-1] for n in zf.namelist()
                  if re.match(r"ppt/slides/slide\d+\.xml$", n)]
        return sorted(slides, key=lambda s: int(re.search(r"\d+", s).group()))

    return ordered


def _extract_pptx_slide_text(root) -> list[str]:
    """Extract all text from a single slide XML."""
    ns_a = {"a": DRAW_NS}
    texts = []

    # Find all text frames (sp/txBody or graphicFrame)
    for txbody in root.iter(f"{{{DRAW_NS}}}txBody"):
        frame_texts = []
        for p in txbody.findall(f"a:p", ns_a):
            parts = []
            for r in p.findall(f"a:r", ns_a):
                t = r.find(f"a:t", ns_a)
                if t is not None and t.text:
                    parts.append(t.text)
            # Also check for field text
            for fld in p.findall(f"a:fld", ns_a):
                t = fld.find(f"a:t", ns_a)
                if t is not None and t.text:
                    parts.append(t.text)
            line = "".join(parts).strip()
            if line:
                frame_texts.append(line)

        if frame_texts:
            texts.extend(frame_texts)

    return texts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def extract_text(file_path: str) -> str:
    """Extract text from DOCX or PPTX file."""
    path = Path(file_path)
    if not path.exists():
        return f"Error: {file_path} not found"

    suffix = path.suffix.lower()
    if suffix == ".docx":
        return extract_docx(path)
    elif suffix == ".pptx":
        return extract_pptx(path)
    else:
        return f"Error: unsupported format {suffix} (use .docx or .pptx)"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text from DOCX/PPTX")
    parser.add_argument("file", help="Input .docx or .pptx file")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    args = parser.parse_args()

    text = extract_text(args.file)

    if text.startswith("Error:"):
        print(text, file=sys.stderr)
        sys.exit(1)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Extracted to {args.output}")
    else:
        print(text)
