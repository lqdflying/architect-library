#!/usr/bin/env python3
"""Add comments to unpacked DOCX documents.

Handles all the XML boilerplate across multiple files:
  - word/comments.xml (comment body)
  - word/commentsExtended.xml (threading/reply structure)
  - word/commentsIds.xml (durable IDs)
  - word/commentsExtensible.xml (UTC timestamps)
  - word/_rels/document.xml.rels (relationships)
  - [Content_Types].xml (content type overrides)

After running, add markers to document.xml manually:
  <w:commentRangeStart w:id="ID"/>
  ... commented content ...
  <w:commentRangeEnd w:id="ID"/>
  <w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="ID"/></w:r>

Usage:
    python add_comment.py unpacked/ 0 "Comment text"
    python add_comment.py unpacked/ 1 "Reply text" --parent 0
    python add_comment.py unpacked/ 0 "Text with &amp; entities" --author "Reviewer"
"""

import argparse
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import defusedxml.minidom as minidom_mod
except ImportError:
    import xml.dom.minidom as minidom_mod

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w16cid": "http://schemas.microsoft.com/office/word/2016/wordml/cid",
    "w16cex": "http://schemas.microsoft.com/office/word/2018/wordml/cex",
}

SMART_QUOTE_MAP = {
    "\u201c": "&#x201C;",
    "\u201d": "&#x201D;",
    "\u2018": "&#x2018;",
    "\u2019": "&#x2019;",
}

# --- XML templates for comment infrastructure files ---

COMMENTS_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:comments xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
  xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
  xmlns:o="urn:schemas-microsoft-com:office:office"
  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
  xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
  xmlns:v="urn:schemas-microsoft-com:vml"
  xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
  xmlns:w10="urn:schemas-microsoft-com:office:word"
  xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
  xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
  xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"
  xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk"
  xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
  mc:Ignorable="w14 wpg wpi wps">
</w:comments>"""

COMMENTS_EXT_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w15:commentsEx
  xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml"
  xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
  mc:Ignorable="w15">
</w15:commentsEx>"""

COMMENTS_IDS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w16cid:commentsIds
  xmlns:w16cid="http://schemas.microsoft.com/office/word/2016/wordml/cid"
  xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
  mc:Ignorable="w16cid">
</w16cid:commentsIds>"""

COMMENTS_EXTENSIBLE_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w16cex:commentsExtensible
  xmlns:w16cex="http://schemas.microsoft.com/office/word/2018/wordml/cex"
  xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
  mc:Ignorable="w16cex">
</w16cex:commentsExtensible>"""

COMMENT_BODY_XML = """\
<w:comment w:id="{id}" w:author="{author}" w:date="{date}" w:initials="{initials}">
  <w:p w14:paraId="{para_id}" w14:textId="77777777">
    <w:r>
      <w:rPr><w:rStyle w:val="CommentReference"/></w:rPr>
      <w:annotationRef/>
    </w:r>
    <w:r>
      <w:rPr>
        <w:color w:val="000000"/>
        <w:sz w:val="20"/>
        <w:szCs w:val="20"/>
      </w:rPr>
      <w:t>{text}</w:t>
    </w:r>
  </w:p>
</w:comment>"""


def _hex_id() -> str:
    return f"{random.randint(0, 0x7FFFFFFE):08X}"


def _encode_smart_quotes(text: str) -> str:
    for char, entity in SMART_QUOTE_MAP.items():
        text = text.replace(char, entity)
    return text


def _append_xml(xml_path: Path, root_tag: str, fragment: str) -> None:
    """Append an XML fragment as a child of root_tag in xml_path."""
    dom = minidom_mod.parseString(xml_path.read_text(encoding="utf-8"))
    roots = dom.getElementsByTagName(root_tag)
    if not roots:
        raise ValueError(f"Root tag '{root_tag}' not found in {xml_path}")
    root = roots[0]

    ns_attrs = " ".join(f'xmlns:{k}="{v}"' for k, v in NS.items())
    wrapper = minidom_mod.parseString(f"<root {ns_attrs}>{fragment}</root>")
    for child in wrapper.documentElement.childNodes:
        if child.nodeType == child.ELEMENT_NODE:
            root.appendChild(dom.importNode(child, True))

    output = _encode_smart_quotes(dom.toxml(encoding="UTF-8").decode("utf-8"))
    xml_path.write_text(output, encoding="utf-8")


def _find_para_id(comments_path: Path, comment_id: int) -> str | None:
    dom = minidom_mod.parseString(comments_path.read_text(encoding="utf-8"))
    for c in dom.getElementsByTagName("w:comment"):
        if c.getAttribute("w:id") == str(comment_id):
            for p in c.getElementsByTagName("w:p"):
                pid = p.getAttribute("w14:paraId")
                if pid:
                    return pid
    return None


def _get_next_rid(rels_path: Path) -> int:
    dom = minidom_mod.parseString(rels_path.read_text(encoding="utf-8"))
    max_rid = 0
    for rel in dom.getElementsByTagName("Relationship"):
        rid = rel.getAttribute("Id")
        if rid and rid.startswith("rId"):
            try:
                max_rid = max(max_rid, int(rid[3:]))
            except ValueError:
                pass
    return max_rid + 1


def _ensure_file(path: Path, template: str):
    if not path.exists():
        path.write_text(template, encoding="utf-8")


def _ensure_relationships(unpacked_dir: Path) -> None:
    rels_path = unpacked_dir / "word" / "_rels" / "document.xml.rels"
    if not rels_path.exists():
        return

    dom = minidom_mod.parseString(rels_path.read_text(encoding="utf-8"))

    # Check if comments.xml relationship already exists
    for rel in dom.getElementsByTagName("Relationship"):
        if rel.getAttribute("Target") == "comments.xml":
            return

    root = dom.documentElement
    next_rid = _get_next_rid(rels_path)

    rels = [
        ("http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments", "comments.xml"),
        ("http://schemas.microsoft.com/office/2011/relationships/commentsExtended", "commentsExtended.xml"),
        ("http://schemas.microsoft.com/office/2016/09/relationships/commentsIds", "commentsIds.xml"),
        ("http://schemas.microsoft.com/office/2018/08/relationships/commentsExtensible", "commentsExtensible.xml"),
    ]

    for rel_type, target in rels:
        rel = dom.createElement("Relationship")
        rel.setAttribute("Id", f"rId{next_rid}")
        rel.setAttribute("Type", rel_type)
        rel.setAttribute("Target", target)
        root.appendChild(rel)
        next_rid += 1

    rels_path.write_bytes(dom.toxml(encoding="UTF-8"))


def _ensure_content_types(unpacked_dir: Path) -> None:
    ct_path = unpacked_dir / "[Content_Types].xml"
    if not ct_path.exists():
        return

    dom = minidom_mod.parseString(ct_path.read_text(encoding="utf-8"))

    # Check if already present
    for override in dom.getElementsByTagName("Override"):
        if override.getAttribute("PartName") == "/word/comments.xml":
            return

    root = dom.documentElement
    overrides = [
        ("/word/comments.xml", "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"),
        ("/word/commentsExtended.xml", "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtended+xml"),
        ("/word/commentsIds.xml", "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsIds+xml"),
        ("/word/commentsExtensible.xml", "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtensible+xml"),
    ]
    for part, ct in overrides:
        o = dom.createElement("Override")
        o.setAttribute("PartName", part)
        o.setAttribute("ContentType", ct)
        root.appendChild(o)

    ct_path.write_bytes(dom.toxml(encoding="UTF-8"))


def add_comment(
    unpacked_dir: str,
    comment_id: int,
    text: str,
    author: str = "Claude",
    initials: str = "C",
    parent_id: int | None = None,
) -> str:
    """Add a comment (or reply) to the unpacked DOCX. Returns status message."""
    word = Path(unpacked_dir) / "word"
    if not word.exists():
        return f"Error: {word} not found"

    para_id = _hex_id()
    durable_id = _hex_id()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Ensure infrastructure files exist
    comments = word / "comments.xml"
    first_comment = not comments.exists()
    if first_comment:
        _ensure_file(comments, COMMENTS_XML_TEMPLATE)
        _ensure_relationships(Path(unpacked_dir))
        _ensure_content_types(Path(unpacked_dir))

    # Add comment body
    _append_xml(
        comments, "w:comments",
        COMMENT_BODY_XML.format(
            id=comment_id, author=author, date=ts,
            initials=initials, para_id=para_id, text=text,
        ),
    )

    # Add extended info (threading)
    ext = word / "commentsExtended.xml"
    _ensure_file(ext, COMMENTS_EXT_TEMPLATE)
    if parent_id is not None:
        parent_para = _find_para_id(comments, parent_id)
        if not parent_para:
            return f"Error: Parent comment {parent_id} not found"
        _append_xml(ext, "w15:commentsEx",
                    f'<w15:commentEx w15:paraId="{para_id}" w15:paraIdParent="{parent_para}" w15:done="0"/>')
    else:
        _append_xml(ext, "w15:commentsEx",
                    f'<w15:commentEx w15:paraId="{para_id}" w15:done="0"/>')

    # Add durable ID
    ids = word / "commentsIds.xml"
    _ensure_file(ids, COMMENTS_IDS_TEMPLATE)
    _append_xml(ids, "w16cid:commentsIds",
                f'<w16cid:commentId w16cid:paraId="{para_id}" w16cid:durableId="{durable_id}"/>')

    # Add extensible data
    extensible = word / "commentsExtensible.xml"
    _ensure_file(extensible, COMMENTS_EXTENSIBLE_TEMPLATE)
    _append_xml(extensible, "w16cex:commentsExtensible",
                f'<w16cex:commentExtensible w16cex:durableId="{durable_id}" w16cex:dateUtc="{ts}"/>')

    action = "reply" if parent_id is not None else "comment"
    return f"Added {action} {comment_id} (para_id={para_id})"


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Add comments to unpacked DOCX")
    p.add_argument("unpacked_dir", help="Unpacked DOCX directory")
    p.add_argument("comment_id", type=int, help="Comment ID (must be unique)")
    p.add_argument("text", help="Comment text (pre-escaped XML)")
    p.add_argument("--author", default="Claude", help="Author name (default: Claude)")
    p.add_argument("--initials", default="C", help="Author initials")
    p.add_argument("--parent", type=int, help="Parent comment ID (for replies)")
    args = p.parse_args()

    msg = add_comment(args.unpacked_dir, args.comment_id, args.text,
                      args.author, args.initials, args.parent)
    print(msg)
    if msg.startswith("Error:"):
        sys.exit(1)

    cid = args.comment_id
    if args.parent is not None:
        print(f"\nNest markers inside parent {args.parent}'s markers:")
        print(f'  <w:commentRangeStart w:id="{args.parent}"/><w:commentRangeStart w:id="{cid}"/>')
        print(f'  <w:r>...</w:r>')
        print(f'  <w:commentRangeEnd w:id="{cid}"/><w:commentRangeEnd w:id="{args.parent}"/>')
        print(f'  <w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="{args.parent}"/></w:r>')
        print(f'  <w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="{cid}"/></w:r>')
    else:
        print(f"\nAdd to document.xml (markers are siblings of w:r, never inside w:r):")
        print(f'  <w:commentRangeStart w:id="{cid}"/>')
        print(f'  <w:r>...</w:r>')
        print(f'  <w:commentRangeEnd w:id="{cid}"/>')
        print(f'  <w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="{cid}"/></w:r>')
