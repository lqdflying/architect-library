#!/usr/bin/env python3
"""Remove unreferenced files from an unpacked PPTX directory.

Removes:
  - Orphaned slides (not in presentation.xml sldIdLst)
  - Orphaned media, embeddings, charts, diagrams, drawings, ink files
  - Orphaned .rels files for deleted resources
  - Unreferenced theme files
  - Unreferenced notes slides
  - [trash] directory if present
  - Content-Type overrides for deleted files

Usage:
    python3 clean_pptx.py unpacked/
"""

import argparse
import sys
from pathlib import Path

try:
    import defusedxml.minidom as minidom_mod
except ImportError:
    import xml.dom.minidom as minidom_mod

import re


def _get_referenced_slides(unpacked_dir: Path) -> set[str]:
    """Get slide filenames listed in <p:sldIdLst>."""
    pres = unpacked_dir / "ppt" / "presentation.xml"
    pres_rels = unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels"

    if not pres.exists() or not pres_rels.exists():
        return set()

    # Build rId -> slide filename mapping
    rels_dom = minidom_mod.parse(str(pres_rels))
    rid_to_slide = {}
    for rel in rels_dom.getElementsByTagName("Relationship"):
        rid = rel.getAttribute("Id")
        target = rel.getAttribute("Target")
        rel_type = rel.getAttribute("Type")
        if "slide" in rel_type and target.startswith("slides/"):
            rid_to_slide[rid] = target.replace("slides/", "")

    # Get rIds referenced in sldIdLst
    pres_content = pres.read_text(encoding="utf-8")
    referenced_rids = set(re.findall(r'<p:sldId[^>]*r:id="([^"]+)"', pres_content))

    return {rid_to_slide[rid] for rid in referenced_rids if rid in rid_to_slide}


def _remove_orphaned_slides(unpacked_dir: Path) -> list[str]:
    """Remove slides not listed in sldIdLst."""
    slides_dir = unpacked_dir / "ppt" / "slides"
    rels_dir = slides_dir / "_rels"
    pres_rels = unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels"

    if not slides_dir.exists():
        return []

    referenced = _get_referenced_slides(unpacked_dir)
    removed = []

    for slide_file in slides_dir.glob("slide*.xml"):
        if slide_file.name not in referenced:
            rel = str(slide_file.relative_to(unpacked_dir))
            slide_file.unlink()
            removed.append(rel)

            # Remove corresponding .rels
            rels_file = rels_dir / f"{slide_file.name}.rels"
            if rels_file.exists():
                rels_file.unlink()
                removed.append(str(rels_file.relative_to(unpacked_dir)))

    # Clean up presentation.xml.rels
    if removed and pres_rels.exists():
        dom = minidom_mod.parse(str(pres_rels))
        changed = False
        for rel in list(dom.getElementsByTagName("Relationship")):
            target = rel.getAttribute("Target")
            if target.startswith("slides/"):
                slide_name = target.replace("slides/", "")
                if slide_name not in referenced:
                    if rel.parentNode:
                        rel.parentNode.removeChild(rel)
                        changed = True
        if changed:
            pres_rels.write_bytes(dom.toxml(encoding="utf-8"))

    return removed


def _remove_trash(unpacked_dir: Path) -> list[str]:
    """Remove [trash] directory."""
    trash = unpacked_dir / "[trash]"
    removed = []
    if trash.exists() and trash.is_dir():
        for f in trash.iterdir():
            if f.is_file():
                removed.append(str(f.relative_to(unpacked_dir)))
                f.unlink()
        trash.rmdir()
    return removed


def _get_all_referenced_files(unpacked_dir: Path) -> set[Path]:
    """Collect all files referenced by any .rels file."""
    referenced = set()
    for rels_file in unpacked_dir.rglob("*.rels"):
        try:
            dom = minidom_mod.parse(str(rels_file))
            for rel in dom.getElementsByTagName("Relationship"):
                target = rel.getAttribute("Target")
                if not target:
                    continue
                target_path = (rels_file.parent.parent / target).resolve()
                try:
                    referenced.add(target_path.relative_to(unpacked_dir.resolve()))
                except ValueError:
                    pass
        except Exception:
            pass
    return referenced


def _remove_orphaned_resources(unpacked_dir: Path, referenced: set[Path]) -> list[str]:
    """Remove unreferenced files from resource directories."""
    resource_dirs = ["media", "embeddings", "charts", "diagrams", "tags", "drawings", "ink"]
    removed = []

    for dir_name in resource_dirs:
        dir_path = unpacked_dir / "ppt" / dir_name
        if not dir_path.exists():
            continue
        for f in dir_path.glob("*"):
            if f.is_file():
                rel = f.relative_to(unpacked_dir)
                if rel not in referenced:
                    f.unlink()
                    removed.append(str(rel))

    # Themes
    theme_dir = unpacked_dir / "ppt" / "theme"
    if theme_dir.exists():
        for f in theme_dir.glob("theme*.xml"):
            rel = f.relative_to(unpacked_dir)
            if rel not in referenced:
                f.unlink()
                removed.append(str(rel))
                theme_rels = theme_dir / "_rels" / f"{f.name}.rels"
                if theme_rels.exists():
                    theme_rels.unlink()
                    removed.append(str(theme_rels.relative_to(unpacked_dir)))

    # Notes slides
    notes_dir = unpacked_dir / "ppt" / "notesSlides"
    if notes_dir.exists():
        for f in notes_dir.glob("*.xml"):
            if f.is_file():
                rel = f.relative_to(unpacked_dir)
                if rel not in referenced:
                    f.unlink()
                    removed.append(str(rel))
        # Clean orphaned notes rels
        notes_rels = notes_dir / "_rels"
        if notes_rels.exists():
            for f in notes_rels.glob("*.rels"):
                notes_file = notes_dir / f.name.replace(".rels", "")
                if not notes_file.exists():
                    f.unlink()
                    removed.append(str(f.relative_to(unpacked_dir)))

    return removed


def _remove_orphaned_rels(unpacked_dir: Path) -> list[str]:
    """Remove .rels files whose parent resource no longer exists."""
    dirs = ["charts", "diagrams", "drawings"]
    removed = []
    slide_referenced = set()

    # Get files referenced by slides
    rels_dir = unpacked_dir / "ppt" / "slides" / "_rels"
    if rels_dir.exists():
        for rf in rels_dir.glob("*.rels"):
            try:
                dom = minidom_mod.parse(str(rf))
                for rel in dom.getElementsByTagName("Relationship"):
                    target = rel.getAttribute("Target")
                    if target:
                        target_path = (rf.parent.parent / target).resolve()
                        try:
                            slide_referenced.add(target_path.relative_to(unpacked_dir.resolve()))
                        except ValueError:
                            pass
            except Exception:
                pass

    for dir_name in dirs:
        rels_path = unpacked_dir / "ppt" / dir_name / "_rels"
        if not rels_path.exists():
            continue
        for rf in rels_path.glob("*.rels"):
            resource = rels_path.parent / rf.name.replace(".rels", "")
            try:
                rel = resource.resolve().relative_to(unpacked_dir.resolve())
            except ValueError:
                continue
            if not resource.exists() or rel not in slide_referenced:
                rf.unlink()
                removed.append(str(rf.relative_to(unpacked_dir)))

    return removed


def _update_content_types(unpacked_dir: Path, removed_files: list[str]) -> None:
    """Remove Content_Types entries for deleted files."""
    ct_path = unpacked_dir / "[Content_Types].xml"
    if not ct_path.exists():
        return

    dom = minidom_mod.parse(str(ct_path))
    changed = False
    for override in list(dom.getElementsByTagName("Override")):
        part = override.getAttribute("PartName").lstrip("/")
        if part in removed_files:
            if override.parentNode:
                override.parentNode.removeChild(override)
                changed = True
    if changed:
        ct_path.write_bytes(dom.toxml(encoding="utf-8"))


def clean(unpacked_dir: Path) -> list[str]:
    """Remove all unreferenced files. Returns list of removed paths."""
    all_removed = []

    all_removed.extend(_remove_orphaned_slides(unpacked_dir))
    all_removed.extend(_remove_trash(unpacked_dir))

    # Iterate until no more orphans (cascading cleanup)
    while True:
        removed_rels = _remove_orphaned_rels(unpacked_dir)
        referenced = _get_all_referenced_files(unpacked_dir)
        removed_files = _remove_orphaned_resources(unpacked_dir, referenced)

        batch = removed_rels + removed_files
        if not batch:
            break
        all_removed.extend(batch)

    if all_removed:
        _update_content_types(unpacked_dir, all_removed)

    return all_removed


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove orphaned PPTX files")
    parser.add_argument("unpacked_dir", help="Unpacked PPTX directory")
    args = parser.parse_args()

    unpacked_dir = Path(args.unpacked_dir)
    if not unpacked_dir.exists():
        print(f"Error: {unpacked_dir} not found", file=sys.stderr)
        sys.exit(1)

    removed = clean(unpacked_dir)
    if removed:
        print(f"Removed {len(removed)} unreferenced files:")
        for f in removed:
            print(f"  {f}")
    else:
        print("No unreferenced files found")


if __name__ == "__main__":
    main()
