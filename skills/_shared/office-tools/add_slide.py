#!/usr/bin/env python3
"""Add a new slide to an unpacked PPTX directory.

Handles Content_Types, presentation.xml.rels, slide rels, and notes references.

Source can be:
  - A slide file (e.g., slide2.xml) -- duplicates the slide
  - A layout file (e.g., slideLayout2.xml) -- creates blank slide from layout

Usage:
    python add_slide.py unpacked/ slide2.xml          # duplicate slide2
    python add_slide.py unpacked/ slideLayout2.xml    # create from layout

Prints the <p:sldId> element to insert into presentation.xml <p:sldIdLst>.
"""

import re
import shutil
import sys
from pathlib import Path


def get_next_slide_number(slides_dir: Path) -> int:
    existing = [
        int(m.group(1))
        for f in slides_dir.glob("slide*.xml")
        if (m := re.match(r"slide(\d+)\.xml", f.name))
    ]
    return max(existing) + 1 if existing else 1


def _add_content_type(unpacked_dir: Path, slide_name: str) -> None:
    ct_path = unpacked_dir / "[Content_Types].xml"
    content = ct_path.read_text(encoding="utf-8")
    part = f"/ppt/slides/{slide_name}"
    if part not in content:
        override = (
            f'<Override PartName="{part}" '
            f'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        )
        content = content.replace("</Types>", f"  {override}\n</Types>")
        ct_path.write_text(content, encoding="utf-8")


def _add_presentation_rel(unpacked_dir: Path, slide_name: str) -> str:
    rels_path = unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels"
    content = rels_path.read_text(encoding="utf-8")

    rids = [int(m) for m in re.findall(r'Id="rId(\d+)"', content)]
    next_rid = max(rids) + 1 if rids else 1
    rid = f"rId{next_rid}"

    target = f"slides/{slide_name}"
    if target not in content:
        rel = (
            f'<Relationship Id="{rid}" '
            f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" '
            f'Target="{target}"/>'
        )
        content = content.replace("</Relationships>", f"  {rel}\n</Relationships>")
        rels_path.write_text(content, encoding="utf-8")

    return rid


def _get_next_slide_id(unpacked_dir: Path) -> int:
    pres_path = unpacked_dir / "ppt" / "presentation.xml"
    content = pres_path.read_text(encoding="utf-8")
    ids = [int(m) for m in re.findall(r'<p:sldId[^>]*id="(\d+)"', content)]
    return max(ids) + 1 if ids else 256


def duplicate_slide(unpacked_dir: Path, source: str) -> None:
    """Duplicate an existing slide."""
    slides_dir = unpacked_dir / "ppt" / "slides"
    rels_dir = slides_dir / "_rels"

    source_slide = slides_dir / source
    if not source_slide.exists():
        print(f"Error: {source_slide} not found", file=sys.stderr)
        sys.exit(1)

    next_num = get_next_slide_number(slides_dir)
    dest = f"slide{next_num}.xml"
    dest_slide = slides_dir / dest

    # Copy slide XML
    shutil.copy2(source_slide, dest_slide)

    # Copy slide rels, removing notesSlide references
    source_rels = rels_dir / f"{source}.rels"
    dest_rels = rels_dir / f"{dest}.rels"
    if source_rels.exists():
        content = source_rels.read_text(encoding="utf-8")
        # Remove notes slide references to avoid sharing notes between slides
        content = re.sub(
            r'\s*<Relationship[^>]*Type="[^"]*notesSlide"[^>]*/>\s*',
            "\n", content
        )
        dest_rels.write_text(content, encoding="utf-8")

    _add_content_type(unpacked_dir, dest)
    rid = _add_presentation_rel(unpacked_dir, dest)
    next_id = _get_next_slide_id(unpacked_dir)

    print(f"Created {dest} from {source}")
    print(f'Add to presentation.xml <p:sldIdLst>: <p:sldId id="{next_id}" r:id="{rid}"/>')


def create_from_layout(unpacked_dir: Path, layout_file: str) -> None:
    """Create a blank slide from a layout template."""
    slides_dir = unpacked_dir / "ppt" / "slides"
    rels_dir = slides_dir / "_rels"
    layouts_dir = unpacked_dir / "ppt" / "slideLayouts"

    if not (layouts_dir / layout_file).exists():
        print(f"Error: {layouts_dir / layout_file} not found", file=sys.stderr)
        print(f"Available layouts: {', '.join(f.name for f in layouts_dir.glob('*.xml'))}")
        sys.exit(1)

    next_num = get_next_slide_number(slides_dir)
    dest = f"slide{next_num}.xml"

    # Write minimal slide XML
    slide_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
        ' xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">\n'
        '  <p:cSld>\n'
        '    <p:spTree>\n'
        '      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>\n'
        '      <p:grpSpPr>\n'
        '        <a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
        '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm>\n'
        '      </p:grpSpPr>\n'
        '    </p:spTree>\n'
        '  </p:cSld>\n'
        '  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>\n'
        '</p:sld>'
    )
    (slides_dir / dest).write_text(slide_xml, encoding="utf-8")

    # Write rels pointing to layout
    rels_dir.mkdir(exist_ok=True)
    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        f'  <Relationship Id="rId1"'
        f' Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"'
        f' Target="../slideLayouts/{layout_file}"/>\n'
        '</Relationships>'
    )
    (rels_dir / f"{dest}.rels").write_text(rels_xml, encoding="utf-8")

    _add_content_type(unpacked_dir, dest)
    rid = _add_presentation_rel(unpacked_dir, dest)
    next_id = _get_next_slide_id(unpacked_dir)

    print(f"Created {dest} from layout {layout_file}")
    print(f'Add to presentation.xml <p:sldIdLst>: <p:sldId id="{next_id}" r:id="{rid}"/>')


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] in ("-h", "--help", "help"):
        print("Usage: python3 add_slide.py <unpacked_dir> <source>")
        print("  source: slide2.xml (duplicate) or slideLayout2.xml (from layout)")
        sys.exit(0 if len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help", "help") else 1)

    unpacked_dir = Path(sys.argv[1])
    source = sys.argv[2]

    if not unpacked_dir.exists():
        print(f"Error: {unpacked_dir} not found", file=sys.stderr)
        sys.exit(1)

    if source.startswith("slideLayout") and source.endswith(".xml"):
        create_from_layout(unpacked_dir, source)
    else:
        duplicate_slide(unpacked_dir, source)


if __name__ == "__main__":
    main()
