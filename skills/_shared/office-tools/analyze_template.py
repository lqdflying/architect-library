#!/usr/bin/env python3
"""Analyze PPTX template structure: extract placeholder names, positions, and types.

Outputs a structured map of each slide's layout, showing:
  - Slide layout name and relationship
  - All shape/placeholder names, types, positions, and sizes
  - Text content preview (first 80 chars)
  - Image placeholders

This helps AI assistants map content to the right template placeholders
without manually inspecting XML.

Usage:
    python3 analyze_template.py template.pptx
    python3 analyze_template.py template.pptx -o analysis.md
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

PRES_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
DRAW_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_RELS_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

EMU_PER_INCH = 914400


def _emu_to_inches(emu: int) -> float:
    return round(emu / EMU_PER_INCH, 2)


def _get_text_preview(sp_elem, max_len: int = 80) -> str:
    """Extract text preview from a shape element."""
    parts = []
    for t in sp_elem.iter(f"{{{DRAW_NS}}}t"):
        if t.text:
            parts.append(t.text)
    text = " ".join(parts).strip()
    if len(text) > max_len:
        text = text[:max_len] + "..."
    return text


def _parse_shape(elem, tag_type: str) -> dict | None:
    """Parse a shape element into a structured dict."""
    # Get non-visual properties
    nvpr = None
    for child in elem:
        local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if local.startswith("nv") and local.endswith("Pr"):
            nvpr = child
            break

    if nvpr is None:
        return None

    # Find cNvPr (common non-visual properties)
    cnvpr = None
    for child in nvpr:
        local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if local == "cNvPr":
            cnvpr = child
            break

    if cnvpr is None:
        return None

    name = cnvpr.get("name", "")
    shape_id = cnvpr.get("id", "")

    # Check for placeholder properties
    ph_type = ""
    ph_idx = ""
    nvppr = nvpr.find(f"{{{PRES_NS}}}nvPr")
    if nvppr is None:
        # Try without namespace
        for child in nvpr:
            local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if local == "nvPr":
                nvppr = child
                break

    if nvppr is not None:
        ph = nvppr.find(f"{{{PRES_NS}}}ph")
        if ph is None:
            for child in nvppr:
                local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                if local == "ph":
                    ph = child
                    break
        if ph is not None:
            ph_type = ph.get("type", "body")
            ph_idx = ph.get("idx", "")

    # Get position and size from spPr/xfrm
    x, y, w, h = 0, 0, 0, 0
    for xfrm in elem.iter(f"{{{DRAW_NS}}}xfrm"):
        off = xfrm.find(f"{{{DRAW_NS}}}off")
        ext = xfrm.find(f"{{{DRAW_NS}}}ext")
        if off is not None:
            x = int(off.get("x", "0"))
            y = int(off.get("y", "0"))
        if ext is not None:
            w = int(ext.get("cx", "0"))
            h = int(ext.get("cy", "0"))
        break

    text = _get_text_preview(elem)

    info = {
        "id": shape_id,
        "name": name,
        "type": tag_type,
        "x": _emu_to_inches(x),
        "y": _emu_to_inches(y),
        "w": _emu_to_inches(w),
        "h": _emu_to_inches(h),
    }

    if ph_type:
        info["placeholder"] = ph_type
    if ph_idx:
        info["ph_idx"] = ph_idx
    if text:
        info["text"] = text

    return info


def analyze_slide(slide_xml: bytes) -> list[dict]:
    """Analyze a single slide's shapes and placeholders."""
    root = ET.fromstring(slide_xml)
    shapes = []

    # Shape types to look for
    shape_tags = {
        f"{{{PRES_NS}}}sp": "shape",
        f"{{{PRES_NS}}}pic": "picture",
        f"{{{PRES_NS}}}graphicFrame": "table/chart",
        f"{{{PRES_NS}}}grpSp": "group",
        f"{{{PRES_NS}}}cxnSp": "connector",
    }

    for sp_tree in root.iter(f"{{{PRES_NS}}}spTree"):
        for child in sp_tree:
            tag_type = shape_tags.get(child.tag, "")
            if not tag_type:
                # Try without namespace for compatibility
                local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                for k, v in shape_tags.items():
                    if k.split("}")[-1] == local:
                        tag_type = v
                        break
            if tag_type:
                info = _parse_shape(child, tag_type)
                if info:
                    shapes.append(info)

    return shapes


def analyze_template(pptx_path: Path) -> str:
    """Analyze PPTX template and return structured markdown report."""
    with zipfile.ZipFile(pptx_path, "r") as zf:
        # Get slide order
        pres_xml = ET.fromstring(zf.read("ppt/presentation.xml"))

        # Build rId -> slide mapping
        rid_to_slide = {}
        rels_path = "ppt/_rels/presentation.xml.rels"
        if rels_path in zf.namelist():
            rels = ET.fromstring(zf.read(rels_path))
            for rel in rels:
                target = rel.get("Target", "")
                rid = rel.get("Id", "")
                if target.startswith("slides/"):
                    rid_to_slide[rid] = target.replace("slides/", "")

        # Get ordered slides
        ordered = []
        for sld_id in pres_xml.iter(f"{{{PRES_NS}}}sldId"):
            rid = sld_id.get(f"{{{REL_NS}}}id", "")
            if rid in rid_to_slide:
                ordered.append(rid_to_slide[rid])

        if not ordered:
            ordered = sorted(
                [n.split("/")[-1] for n in zf.namelist()
                 if re.match(r"ppt/slides/slide\d+\.xml$", n)],
                key=lambda s: int(re.search(r"\d+", s).group())
            )

        # Analyze each slide
        sections = [f"# Template Analysis: {pptx_path.name}\n"]

        for slide_file in ordered:
            slide_path = f"ppt/slides/{slide_file}"
            if slide_path not in zf.namelist():
                continue

            # Get layout info from slide rels
            layout_name = ""
            slide_rels = f"ppt/slides/_rels/{slide_file}.rels"
            if slide_rels in zf.namelist():
                rels = ET.fromstring(zf.read(slide_rels))
                for rel in rels:
                    if "slideLayout" in rel.get("Type", ""):
                        layout_name = rel.get("Target", "").replace("../slideLayouts/", "")

            shapes = analyze_slide(zf.read(slide_path))

            section = f"## {slide_file}"
            if layout_name:
                section += f" (layout: {layout_name})"
            section += "\n"

            if not shapes:
                section += "(no shapes found)\n"
            else:
                for s in shapes:
                    # Format: name [type] at (x, y) size (w x h)
                    line = f"- **{s['name']}**"
                    if s.get("placeholder"):
                        line += f" [{s['placeholder']}]"
                    elif s["type"] != "shape":
                        line += f" [{s['type']}]"

                    line += f" at ({s['x']}\", {s['y']}\") size ({s['w']}\" x {s['h']}\")"

                    if s.get("text"):
                        line += f"\n  Content: \"{s['text']}\""

                    section += line + "\n"

            sections.append(section)

    return "\n".join(sections)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze PPTX template structure")
    parser.add_argument("file", help="Input .pptx file")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists() or path.suffix.lower() != ".pptx":
        print(f"Error: {args.file} is not a valid .pptx file", file=sys.stderr)
        sys.exit(1)

    report = analyze_template(path)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Analysis written to {args.output}")
    else:
        print(report)
