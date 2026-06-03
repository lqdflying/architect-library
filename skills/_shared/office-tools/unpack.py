#!/usr/bin/env python3
"""Unpack Office files (DOCX/PPTX/XLSX) for editing.

Extracts ZIP, pretty-prints XML, and optionally:
  - Merges adjacent runs with identical formatting (DOCX)
  - Simplifies adjacent tracked changes from same author (DOCX)
  - Escapes smart quotes to XML entities for safe editing

Usage:
    python unpack.py document.docx unpacked/
    python unpack.py presentation.pptx unpacked/
    python unpack.py document.docx unpacked/ --no-merge-runs
"""

import argparse
import sys
import zipfile
from pathlib import Path

from safe_zip import safe_extract

try:
    import defusedxml.minidom as minidom_mod
    def parse_xml(text: str):
        return defusedxml.minidom.parseString(text)
except ImportError:
    import xml.dom.minidom as minidom_mod
    def parse_xml(text: str):
        return minidom_mod.parseString(text)


SMART_QUOTE_MAP = {
    "\u201c": "&#x201C;",  # left double
    "\u201d": "&#x201D;",  # right double
    "\u2018": "&#x2018;",  # left single
    "\u2019": "&#x2019;",  # right single / apostrophe
}


# ---------------------------------------------------------------------------
# XML helpers
# ---------------------------------------------------------------------------

def _find_elements(root, local_tag: str) -> list:
    """Find all elements matching a local tag name (ignoring namespace prefix)."""
    results = []
    def walk(node):
        if node.nodeType == node.ELEMENT_NODE:
            name = node.localName or node.tagName
            if name == local_tag or name.endswith(f":{local_tag}"):
                results.append(node)
            for child in node.childNodes:
                walk(child)
    walk(root)
    return results


def _get_child(parent, local_tag: str):
    for child in parent.childNodes:
        if child.nodeType == child.ELEMENT_NODE:
            name = child.localName or child.tagName
            if name == local_tag or name.endswith(f":{local_tag}"):
                return child
    return None


def _get_children(parent, local_tag: str) -> list:
    return [
        c for c in parent.childNodes
        if c.nodeType == c.ELEMENT_NODE
        and ((c.localName or c.tagName) == local_tag
             or (c.localName or c.tagName).endswith(f":{local_tag}"))
    ]


def _is_element(node, tag: str) -> bool:
    name = node.localName or node.tagName
    return name == tag or name.endswith(f":{tag}")


def _next_element_sibling(node):
    sib = node.nextSibling
    while sib:
        if sib.nodeType == sib.ELEMENT_NODE:
            return sib
        sib = sib.nextSibling
    return None


def _is_adjacent(e1, e2) -> bool:
    """True if e1 and e2 are adjacent (only whitespace text nodes between them)."""
    node = e1.nextSibling
    while node:
        if node is e2:
            return True
        if node.nodeType == node.ELEMENT_NODE:
            return False
        if node.nodeType == node.TEXT_NODE and node.data.strip():
            return False
        node = node.nextSibling
    return False


# ---------------------------------------------------------------------------
# Merge runs: combine adjacent <w:r> with identical <w:rPr>
# ---------------------------------------------------------------------------

def merge_runs(doc_xml: Path) -> int:
    """Merge adjacent runs with identical formatting. Returns merge count."""
    if not doc_xml.exists():
        return 0

    dom = parse_xml(doc_xml.read_text(encoding="utf-8"))
    root = dom.documentElement

    # Remove proofErr elements (spell/grammar markers block merging)
    for elem in _find_elements(root, "proofErr"):
        if elem.parentNode:
            elem.parentNode.removeChild(elem)

    # Strip rsid attributes from runs (revision metadata, doesn't affect rendering)
    for run in _find_elements(root, "r"):
        for attr in list(run.attributes.values()):
            if "rsid" in attr.name.lower():
                run.removeAttribute(attr.name)

    # Find all containers that hold runs
    containers = {run.parentNode for run in _find_elements(root, "r")}

    total = 0
    for container in containers:
        total += _merge_runs_in(container)

    doc_xml.write_bytes(dom.toxml(encoding="UTF-8"))
    return total


def _merge_runs_in(container) -> int:
    count = 0
    run = _first_child_matching(container, "r")
    while run:
        while True:
            nxt = _next_element_sibling(run)
            if nxt and _is_element(nxt, "r") and _can_merge_runs(run, nxt):
                # Move content nodes (skip rPr) from nxt into run
                for child in list(nxt.childNodes):
                    if child.nodeType == child.ELEMENT_NODE:
                        name = child.localName or child.tagName
                        if name != "rPr" and not name.endswith(":rPr"):
                            run.appendChild(child)
                container.removeChild(nxt)
                count += 1
            else:
                break
        _consolidate_text_nodes(run)
        run = _next_sibling_matching(run, "r")
    return count


def _first_child_matching(container, tag: str):
    for child in container.childNodes:
        if child.nodeType == child.ELEMENT_NODE and _is_element(child, tag):
            return child
    return None


def _next_sibling_matching(node, tag: str):
    sib = node.nextSibling
    while sib:
        if sib.nodeType == sib.ELEMENT_NODE and _is_element(sib, tag):
            return sib
        sib = sib.nextSibling
    return None


def _can_merge_runs(r1, r2) -> bool:
    rpr1 = _get_child(r1, "rPr")
    rpr2 = _get_child(r2, "rPr")
    if (rpr1 is None) != (rpr2 is None):
        return False
    if rpr1 is None:
        return True
    return rpr1.toxml() == rpr2.toxml()


def _consolidate_text_nodes(run):
    """Merge adjacent <w:t> elements within a single run."""
    t_elems = _get_children(run, "t")
    for i in range(len(t_elems) - 1, 0, -1):
        curr, prev = t_elems[i], t_elems[i - 1]
        if _is_adjacent(prev, curr):
            prev_text = prev.firstChild.data if prev.firstChild else ""
            curr_text = curr.firstChild.data if curr.firstChild else ""
            merged = prev_text + curr_text
            if prev.firstChild:
                prev.firstChild.data = merged
            else:
                prev.appendChild(run.ownerDocument.createTextNode(merged))
            if merged.startswith(" ") or merged.endswith(" "):
                prev.setAttribute("xml:space", "preserve")
            elif prev.hasAttribute("xml:space"):
                prev.removeAttribute("xml:space")
            run.removeChild(curr)


# ---------------------------------------------------------------------------
# Simplify redlines: merge adjacent <w:ins>/<w:del> from same author
# ---------------------------------------------------------------------------

def simplify_redlines(doc_xml: Path) -> int:
    """Merge adjacent tracked changes from same author. Returns merge count."""
    if not doc_xml.exists():
        return 0

    dom = parse_xml(doc_xml.read_text(encoding="utf-8"))
    root = dom.documentElement

    containers = _find_elements(root, "p") + _find_elements(root, "tc")
    total = 0
    for container in containers:
        for tag in ("ins", "del"):
            total += _merge_tracked_in(container, tag)

    doc_xml.write_bytes(dom.toxml(encoding="UTF-8"))
    return total


def _merge_tracked_in(container, tag: str) -> int:
    tracked = [
        c for c in container.childNodes
        if c.nodeType == c.ELEMENT_NODE and _is_element(c, tag)
    ]
    if len(tracked) < 2:
        return 0
    count = 0
    i = 0
    while i < len(tracked) - 1:
        curr, nxt = tracked[i], tracked[i + 1]
        if _same_author(curr, nxt) and _only_whitespace_between(curr, nxt):
            while nxt.firstChild:
                child = nxt.firstChild
                nxt.removeChild(child)
                curr.appendChild(child)
            container.removeChild(nxt)
            tracked.pop(i + 1)
            count += 1
        else:
            i += 1
    return count


def _same_author(e1, e2) -> bool:
    def get_author(e):
        a = e.getAttribute("w:author")
        if not a:
            for attr in e.attributes.values():
                if attr.localName == "author" or attr.name.endswith(":author"):
                    return attr.value
        return a
    return get_author(e1) == get_author(e2)


def _only_whitespace_between(e1, e2) -> bool:
    node = e1.nextSibling
    while node and node is not e2:
        if node.nodeType == node.ELEMENT_NODE:
            return False
        if node.nodeType == node.TEXT_NODE and node.data.strip():
            return False
        node = node.nextSibling
    return True


# ---------------------------------------------------------------------------
# Core unpack logic
# ---------------------------------------------------------------------------

def pretty_print_xml(xml_file: Path) -> None:
    try:
        content = xml_file.read_text(encoding="utf-8")
        dom = parse_xml(content)
        xml_file.write_bytes(dom.toprettyxml(indent="  ", encoding="utf-8"))
    except Exception:
        pass


def escape_smart_quotes(xml_file: Path) -> None:
    try:
        content = xml_file.read_text(encoding="utf-8")
        for char, entity in SMART_QUOTE_MAP.items():
            content = content.replace(char, entity)
        xml_file.write_text(content, encoding="utf-8")
    except Exception:
        pass


def unpack(
    input_file: str,
    output_directory: str,
    do_merge_runs: bool = True,
    do_simplify_redlines: bool = True,
) -> str:
    """Unpack an Office file for editing. Returns status message."""
    input_path = Path(input_file)
    output_path = Path(output_directory)

    if not input_path.exists():
        return f"Error: {input_file} does not exist"

    suffix = input_path.suffix.lower()
    if suffix not in {".docx", ".pptx", ".xlsx"}:
        return f"Error: {input_file} must be .docx, .pptx, or .xlsx"

    try:
        output_path.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(input_path, "r") as zf:
            safe_extract(zf, output_path)

        xml_files = list(output_path.rglob("*.xml")) + list(output_path.rglob("*.rels"))
        for xf in xml_files:
            pretty_print_xml(xf)

        msg = f"Unpacked {input_file} ({len(xml_files)} XML files)"

        if suffix == ".docx":
            doc_xml = output_path / "word" / "document.xml"
            if do_simplify_redlines:
                n = simplify_redlines(doc_xml)
                msg += f", simplified {n} tracked changes"
            if do_merge_runs:
                n = merge_runs(doc_xml)
                msg += f", merged {n} runs"

        for xf in xml_files:
            escape_smart_quotes(xf)

        return msg

    except zipfile.BadZipFile:
        return f"Error: {input_file} is not a valid Office file"
    except Exception as e:
        return f"Error unpacking: {e}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unpack Office file for editing")
    parser.add_argument("input_file", help="Office file (.docx/.pptx/.xlsx)")
    parser.add_argument("output_directory", help="Output directory")
    parser.add_argument("--no-merge-runs", action="store_true",
                        help="Skip merging adjacent runs (DOCX)")
    parser.add_argument("--no-simplify-redlines", action="store_true",
                        help="Skip simplifying tracked changes (DOCX)")
    args = parser.parse_args()

    message = unpack(
        args.input_file,
        args.output_directory,
        do_merge_runs=not args.no_merge_runs,
        do_simplify_redlines=not args.no_simplify_redlines,
    )
    print(message)
    if message.startswith("Error:"):
        sys.exit(1)
