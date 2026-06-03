#!/usr/bin/env python3
"""Verify tracked changes in DOCX are correctly applied.

Core idea: strip the specified author's tracked changes from both the modified
and original documents, then compare the resulting plain text. If they differ,
some edits were made without proper change tracking.

This catches:
  - Text modified inside another author's <w:ins> or <w:del> tags
  - Edits made without tracked changes wrappers
  - Incorrect nesting of <w:del> inside <w:ins> when rejecting insertions

Usage:
    python verify_redlines.py unpacked/ original.docx
    python verify_redlines.py unpacked/ original.docx --author "Reviewer"
"""

import argparse
import difflib
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from safe_zip import safe_extract

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _extract_text(root) -> str:
    """Extract plain text from document XML, one line per paragraph."""
    p_tag = f"{{{WORD_NS}}}p"
    t_tag = f"{{{WORD_NS}}}t"
    paragraphs = []
    for p in root.findall(f".//{p_tag}"):
        parts = [t.text for t in p.findall(f".//{t_tag}") if t.text]
        text = "".join(parts)
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs)


def _strip_author_changes(root, author: str):
    """Remove the specified author's tracked changes in-place.

    - Author's <w:ins>: remove the entire element (insertion undone)
    - Author's <w:del>: unwrap children, converting <w:delText> -> <w:t>
      (deletion undone, original text restored)
    """
    ns = {"w": WORD_NS}
    ins_tag = f"{{{WORD_NS}}}ins"
    del_tag = f"{{{WORD_NS}}}del"
    deltext_tag = f"{{{WORD_NS}}}delText"
    t_tag = f"{{{WORD_NS}}}t"
    author_attr = f"{{{WORD_NS}}}author"

    # Pass 1: remove author's insertions entirely
    for parent in root.iter():
        to_remove = [
            child for child in parent
            if child.tag == ins_tag and child.get(author_attr) == author
        ]
        for elem in to_remove:
            parent.remove(elem)

    # Pass 2: unwrap author's deletions (restore deleted text)
    for parent in root.iter():
        to_process = [
            (child, list(parent).index(child))
            for child in parent
            if child.tag == del_tag and child.get(author_attr) == author
        ]
        for del_elem, idx in reversed(to_process):
            # Convert delText -> t so the text becomes visible
            for elem in del_elem.iter():
                if elem.tag == deltext_tag:
                    elem.tag = t_tag
            # Move children out of <w:del> into parent
            for child in reversed(list(del_elem)):
                parent.insert(idx, child)
            parent.remove(del_elem)


def _generate_diff(original: str, modified: str) -> str:
    """Generate a readable word-level diff between two texts."""
    orig_lines = original.splitlines(keepends=True)
    mod_lines = modified.splitlines(keepends=True)

    diff = list(difflib.unified_diff(
        orig_lines, mod_lines,
        fromfile="original (after stripping author changes)",
        tofile="modified (after stripping author changes)",
        n=1,
    ))

    if not diff:
        return ""

    # Format output
    lines = []
    for line in diff:
        line = line.rstrip("\n")
        if line.startswith("---") or line.startswith("+++"):
            lines.append(line)
        elif line.startswith("@@"):
            lines.append(f"\n{line}")
        elif line.startswith("-"):
            lines.append(f"  REMOVED: {line[1:]}")
        elif line.startswith("+"):
            lines.append(f"  ADDED:   {line[1:]}")
        else:
            lines.append(f"  {line}")

    return "\n".join(lines)


def verify_redlines(
    unpacked_dir: str,
    original_file: str,
    author: str = "Claude",
) -> tuple[bool, str]:
    """Verify tracked changes are correct. Returns (passed, message)."""
    modified_xml = Path(unpacked_dir) / "word" / "document.xml"
    if not modified_xml.exists():
        return False, f"Error: {modified_xml} not found"

    original_path = Path(original_file)
    if not original_path.exists():
        return False, f"Error: {original_file} not found"

    # Parse modified document
    try:
        mod_tree = ET.parse(modified_xml)
        mod_root = mod_tree.getroot()
    except ET.ParseError as e:
        return False, f"Error parsing modified document: {e}"

    # Check if there are any tracked changes by this author
    ns = {"w": WORD_NS}
    author_attr = f"{{{WORD_NS}}}author"
    has_changes = False
    for tag in ("ins", "del"):
        for elem in mod_root.findall(f".//w:{tag}", ns):
            if elem.get(author_attr) == author:
                has_changes = True
                break
        if has_changes:
            break

    if not has_changes:
        return True, f"No tracked changes by '{author}' found. Nothing to verify."

    # Parse original document
    try:
        with tempfile.TemporaryDirectory() as td:
            with zipfile.ZipFile(original_path, "r") as zf:
                safe_extract(zf, Path(td))
            orig_xml = Path(td) / "word" / "document.xml"
            if not orig_xml.exists():
                return False, f"Error: document.xml not found in {original_file}"
            orig_tree = ET.parse(orig_xml)
            orig_root = orig_tree.getroot()
    except Exception as e:
        return False, f"Error reading original: {e}"

    # Strip author's changes from both copies
    _strip_author_changes(mod_root, author)
    _strip_author_changes(orig_root, author)

    # Compare text content
    mod_text = _extract_text(mod_root)
    orig_text = _extract_text(orig_root)

    if mod_text == orig_text:
        return True, f"PASSED - All changes by '{author}' are properly tracked."

    # Generate diff for error report
    diff = _generate_diff(orig_text, mod_text)

    msg_parts = [
        f"FAILED - Document text doesn't match after removing '{author}' tracked changes.",
        "",
        "Likely causes:",
        "  1. Text modified inside another author's <w:ins> or <w:del>",
        "  2. Edits made without proper tracked change wrappers",
        "  3. Incorrect nesting when rejecting another author's insertion",
        "",
        "Correct patterns:",
        "  - Reject another's INSERTION: nest <w:del> inside their <w:ins>",
        "  - Restore another's DELETION: add <w:ins> AFTER their <w:del>",
    ]

    if diff:
        msg_parts.extend(["", "Differences:", "=" * 60, diff])

    return False, "\n".join(msg_parts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify DOCX tracked changes")
    parser.add_argument("unpacked_dir", help="Unpacked DOCX directory")
    parser.add_argument("original", help="Original .docx file")
    parser.add_argument("--author", default="Claude", help="Author name (default: Claude)")
    args = parser.parse_args()

    passed, message = verify_redlines(args.unpacked_dir, args.original, args.author)
    print(message)
    sys.exit(0 if passed else 1)
