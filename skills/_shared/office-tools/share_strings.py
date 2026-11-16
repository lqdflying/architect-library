#!/usr/bin/env python3
"""Rewrite worksheet inlineStr cells into xl/sharedStrings.xml.

openpyxl 3.1 stores every string inline. That package is schema-valid, and
LibreOffice shows the text, but some viewers leave the cells blank. Shared
string items use the same CT_Rst content as an inline <is> element.
"""

import argparse
import io
import json
import sys
import zipfile
from pathlib import Path

from lxml import etree

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
SHARED_STRINGS_REL = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings"
)
SHARED_STRINGS_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"
)
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
SST_NAME = "xl/sharedStrings.xml"
CONTENT_TYPES = "[Content_Types].xml"
WORKBOOK_RELS = "xl/_rels/workbook.xml.rels"


def share_strings(filename):
    """Rewrite inline strings in place. Return a JSON-ready result dict."""
    path = Path(filename)
    if not path.is_file():
        return {"error": f"{filename} does not exist"}

    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            sheets = [name for name in names if _is_worksheet(name)]
            sheet_bytes = {name: archive.read(name) for name in sheets}
            sst_bytes = archive.read(SST_NAME) if SST_NAME in names else None
            content_types = archive.read(CONTENT_TYPES) if CONTENT_TYPES in names else None
            workbook_rels = archive.read(WORKBOOK_RELS) if WORKBOOK_RELS in names else None
    except zipfile.BadZipFile:
        return {"error": f"{filename} is not an xlsx package"}
    except OSError as error:
        return {"error": str(error)}

    if content_types is None or workbook_rels is None:
        return {"error": f"{filename} is missing workbook content types or relationships"}

    try:
        sheet_roots = {name: etree.fromstring(data) for name, data in sheet_bytes.items()}
        sst_root = etree.fromstring(sst_bytes) if sst_bytes is not None else None
    except etree.XMLSyntaxError as error:
        return {"error": f"Invalid XML in {filename}: {error}"}

    converted, sst_root, changed = _convert(sheet_roots, sst_root)
    inline_count, shared_count = _count_cells(sheet_roots.values())
    has_part = sst_bytes is not None or converted > 0

    if inline_count:
        return {
            "error": f"{filename} still has {inline_count} inlineStr cell(s)",
            "inline_strings": inline_count,
            "text_cells": shared_count,
        }
    if shared_count and not has_part:
        return {
            "error": f"{filename} has shared-string cells but no {SST_NAME}",
            "inline_strings": inline_count,
            "text_cells": shared_count,
            "shared_string_part": False,
        }
    if converted == 0:
        return _success(inline_count, shared_count, sst_bytes is not None, 0)

    if sst_root is None:
        return {"error": f"{filename} produced shared-string cells without a table"}

    si_count = sum(1 for child in sst_root if _local(child.tag) == "si")
    sst_root.set("count", str(shared_count))
    sst_root.set("uniqueCount", str(si_count))

    replacements = {
        name: _serialize(sheet_roots[name], sheet_bytes[name]) for name in changed
    }
    replacements[SST_NAME] = _serialize(sst_root, sst_bytes or b"")

    try:
        content_root = etree.fromstring(content_types)
        rels_root = etree.fromstring(workbook_rels)
    except etree.XMLSyntaxError as error:
        return {"error": f"Invalid workbook XML in {filename}: {error}"}

    if _ensure_content_type(content_root):
        replacements[CONTENT_TYPES] = _serialize(content_root, content_types)
    if _ensure_relationship(rels_root):
        replacements[WORKBOOK_RELS] = _serialize(rels_root, workbook_rels)

    try:
        _rewrite(path, replacements)
    except OSError as error:
        return {"error": str(error)}

    return _success(inline_count, shared_count, True, converted)


def _success(inline_count, shared_count, has_part, converted):
    return {
        "status": "success",
        "text_cells": shared_count,
        "inline_strings": inline_count,
        "shared_string_part": has_part,
        "converted": converted,
    }


def _is_worksheet(name):
    return (
        name.startswith("xl/worksheets/sheet")
        and name.endswith(".xml")
        and "/_rels/" not in name
    )


def _local(tag):
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1]


def _q(namespace, tag):
    return f"{{{namespace}}}{tag}"


def _namespace(element):
    tag = element.tag
    if isinstance(tag, str) and tag.startswith("{"):
        return tag[1:].split("}", 1)[0]
    return MAIN


def _cells(root):
    for element in root.iter():
        parent = element.getparent()
        if parent is not None and _local(element.tag) == "c" and _local(parent.tag) == "row":
            yield element


def _count_cells(roots):
    inline_count = 0
    shared_count = 0
    for root in roots:
        for cell in _cells(root):
            kind = cell.get("t")
            if kind == "inlineStr":
                inline_count += 1
            elif kind == "s":
                shared_count += 1
    return inline_count, shared_count


def _canon(element):
    attributes = tuple(sorted(element.attrib.items()))
    children = tuple(_canon(child) for child in element)
    return (_local(element.tag), attributes, element.text, children, element.tail)


def _payload_key(element):
    if element is None:
        return ()
    return tuple(_canon(child) for child in element)


def _si_elements(sst_root):
    return [child for child in sst_root if _local(child.tag) == "si"]


def _append_si(sst_root, si_element):
    for index, child in enumerate(list(sst_root)):
        if _local(child.tag) == "extLst":
            sst_root.insert(index, si_element)
            return
    sst_root.append(si_element)


def _new_sst():
    return etree.Element(_q(MAIN, "sst"), nsmap={None: MAIN})


def _drop_xml_space(element):
    # sml.xsd types t as ST_Xstring, which has no attributes. validate rejects
    # xml:space here. The characters stay in the text node.
    if XML_SPACE in element.attrib:
        del element.attrib[XML_SPACE]
    for child in element:
        _drop_xml_space(child)


def _shared_item(cell):
    inline = next((child for child in cell if _local(child.tag) == "is"), None)
    item = etree.Element(_q(MAIN, "si"))
    if inline is not None:
        for child in inline:
            copied = etree.fromstring(etree.tostring(child))
            _drop_xml_space(copied)
            item.append(copied)
    return item


def _point_at_shared(cell, index):
    for child in list(cell):
        if _local(child.tag) == "is":
            cell.remove(child)
    cell.set("t", "s")
    value = next((child for child in cell if _local(child.tag) == "v"), None)
    if value is None:
        value = etree.Element(_q(_namespace(cell), "v"))
        insert_at = len(cell)
        for position, child in enumerate(list(cell)):
            if _local(child.tag) == "extLst":
                insert_at = position
                break
        cell.insert(insert_at, value)
    value.text = str(index)


def _convert(sheet_roots, sst_root):
    if sst_root is None:
        sst_root = _new_sst()
        created = True
    else:
        created = False

    index_by_key = {}
    for index, item in enumerate(_si_elements(sst_root)):
        index_by_key.setdefault(_payload_key(item), index)

    converted = 0
    changed = []
    for name, root in sheet_roots.items():
        # Snapshot first. lxml's iterator skips siblings when a cell's children change.
        sheet_converted = 0
        for cell in list(_cells(root)):
            if cell.get("t") != "inlineStr":
                continue
            item = _shared_item(cell)
            key = _payload_key(item)
            if key not in index_by_key:
                index_by_key[key] = len(_si_elements(sst_root))
                _append_si(sst_root, item)
            _point_at_shared(cell, index_by_key[key])
            sheet_converted += 1
        if sheet_converted:
            changed.append(name)
            converted += sheet_converted

    if converted == 0 and created:
        return 0, None, []
    return converted, sst_root, changed


def _ensure_content_type(root):
    part = "/xl/sharedStrings.xml"
    for child in root:
        if _local(child.tag) == "Override" and child.get("PartName") == part:
            return False
    element = etree.SubElement(root, _q(_namespace(root), "Override"))
    element.set("PartName", part)
    element.set("ContentType", SHARED_STRINGS_TYPE)
    return True


def _ensure_relationship(root):
    for child in root:
        if _local(child.tag) == "Relationship" and child.get("Type") == SHARED_STRINGS_REL:
            return False
    used = set()
    for child in root:
        rel_id = child.get("Id") or ""
        if rel_id.startswith("rId") and rel_id[3:].isdigit():
            used.add(int(rel_id[3:]))
    element = etree.SubElement(root, _q(_namespace(root), "Relationship"))
    element.set("Id", f"rId{(max(used) if used else 0) + 1}")
    element.set("Type", SHARED_STRINGS_REL)
    element.set("Target", "sharedStrings.xml")
    return True


def _serialize(root, original):
    body = etree.tostring(root, xml_declaration=False, encoding="UTF-8")
    if original.startswith(b"<?xml"):
        end = original.find(b"?>")
        declaration = original[: end + 2]
        newline = b"\n" if end + 2 < len(original) and original[end + 2 : end + 3] in (b"\n", b"\r") else b""
        if original[end + 2 : end + 4] == b"\r\n":
            newline = b"\r\n"
        return declaration + newline + body
    return b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + body


def _clone_info(info):
    cloned = zipfile.ZipInfo(filename=info.filename, date_time=info.date_time)
    cloned.compress_type = info.compress_type or zipfile.ZIP_DEFLATED
    cloned.external_attr = info.external_attr
    return cloned


def _rewrite(path, replacements):
    buffer = io.BytesIO()
    with zipfile.ZipFile(path) as source, zipfile.ZipFile(buffer, "w") as target:
        seen = set()
        for info in source.infolist():
            seen.add(info.filename)
            data = replacements.get(info.filename, source.read(info.filename))
            target.writestr(_clone_info(info), data)
        for name, data in replacements.items():
            if name in seen:
                continue
            info = zipfile.ZipInfo(filename=name)
            info.compress_type = zipfile.ZIP_DEFLATED
            target.writestr(info, data)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(buffer.getvalue())
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(
        description="Rewrite inlineStr cells into xl/sharedStrings.xml"
    )
    parser.add_argument("xlsx", help="Workbook to rewrite in place (.xlsx or .xlsm)")
    args = parser.parse_args()
    result = share_strings(args.xlsx)
    print(json.dumps(result, indent=2))
    failed = "error" in result or result.get("status") != "success"
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
