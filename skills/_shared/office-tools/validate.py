#!/usr/bin/env python3
"""Validate Office document XML and auto-repair common issues.

Checks: well-formed XML, whitespace preservation, tracked change correctness,
ID constraints (paraId/durableId), comment marker pairing, file references,
content types, unique IDs.

Auto-repair fixes:
  - durableId >= 0x7FFFFFFF (regenerates valid ID)
  - Missing xml:space="preserve" on w:t/a:t with leading/trailing whitespace

Usage:
    python validate.py unpacked/                           # validate unpacked dir
    python validate.py document.docx                       # validate packed file
    python validate.py unpacked/ --original document.docx  # compare against original
    python validate.py unpacked/ --auto-repair             # repair + validate
"""

import argparse
import random
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from safe_zip import safe_extract

try:
    import lxml.etree as etree
    HAS_LXML = True
except ImportError:
    import xml.etree.ElementTree as etree
    HAS_LXML = False

try:
    import defusedxml.minidom as minidom_mod
except ImportError:
    import xml.dom.minidom as minidom_mod

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14_NS = "http://schemas.microsoft.com/office/word/2010/wordml"
W16CID_NS = "http://schemas.microsoft.com/office/word/2016/wordml/cid"
PRES_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
PKG_RELS_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
XML_NS = "http://www.w3.org/XML/1998/namespace"


class ValidationResult:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.repairs: int = 0

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def error(self, msg: str):
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    def report(self) -> str:
        lines = []
        if self.repairs:
            lines.append(f"Auto-repaired {self.repairs} issue(s)")
        for w in self.warnings:
            lines.append(f"  WARN: {w}")
        for e in self.errors:
            lines.append(f"  FAIL: {e}")
        if self.ok:
            lines.append("All validations PASSED!")
        else:
            lines.insert(0, f"FAILED - {len(self.errors)} error(s) found:")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Repair functions
# ---------------------------------------------------------------------------

def repair_whitespace_preservation(unpacked_dir: Path) -> int:
    """Add xml:space='preserve' to text elements with leading/trailing whitespace."""
    repairs = 0
    for xml_file in _iter_xml_files(unpacked_dir):
        try:
            content = xml_file.read_text(encoding="utf-8")
            dom = minidom_mod.parseString(content)
            modified = False
            for elem in dom.getElementsByTagName("*"):
                if elem.tagName.endswith(":t") and elem.firstChild:
                    text = elem.firstChild.nodeValue
                    if text and (text[0] in " \t" or text[-1] in " \t"):
                        if elem.getAttribute("xml:space") != "preserve":
                            elem.setAttribute("xml:space", "preserve")
                            repairs += 1
                            modified = True
            if modified:
                xml_file.write_bytes(dom.toxml(encoding="UTF-8"))
        except Exception:
            pass
    return repairs


def repair_durable_ids(unpacked_dir: Path) -> int:
    """Fix durableId values that exceed OOXML limits."""
    repairs = 0
    for xml_file in _iter_xml_files(unpacked_dir):
        try:
            content = xml_file.read_text(encoding="utf-8")
            dom = minidom_mod.parseString(content)
            modified = False
            for elem in dom.getElementsByTagName("*"):
                if not elem.hasAttribute("w16cid:durableId"):
                    continue
                val = elem.getAttribute("w16cid:durableId")
                needs_fix = False
                is_numbering = xml_file.name == "numbering.xml"
                try:
                    base = 10 if is_numbering else 16
                    needs_fix = int(val, base) >= 0x7FFFFFFF
                except ValueError:
                    needs_fix = True
                if needs_fix:
                    new_val = random.randint(1, 0x7FFFFFFE)
                    new_id = str(new_val) if is_numbering else f"{new_val:08X}"
                    elem.setAttribute("w16cid:durableId", new_id)
                    repairs += 1
                    modified = True
            if modified:
                xml_file.write_bytes(dom.toxml(encoding="UTF-8"))
        except Exception:
            pass
    return repairs


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------

def validate_well_formed_xml(unpacked_dir: Path, result: ValidationResult):
    """Check all XML files are well-formed."""
    for xml_file in _iter_xml_files(unpacked_dir):
        try:
            if HAS_LXML:
                etree.parse(str(xml_file))
            else:
                etree.parse(str(xml_file))
        except Exception as e:
            rel = xml_file.relative_to(unpacked_dir)
            result.error(f"{rel}: Malformed XML: {e}")


def validate_whitespace_preservation(unpacked_dir: Path, result: ValidationResult):
    """Check w:t elements with leading/trailing whitespace have xml:space='preserve'."""
    for xml_file in _iter_xml_files(unpacked_dir):
        if xml_file.name != "document.xml":
            continue
        try:
            if not HAS_LXML:
                continue
            root = etree.parse(str(xml_file)).getroot()
            for elem in root.iter(f"{{{WORD_NS}}}t"):
                if elem.text:
                    text = elem.text
                    if re.search(r"^[ \t\n\r]", text) or re.search(r"[ \t\n\r]$", text):
                        space_attr = f"{{{XML_NS}}}space"
                        if elem.attrib.get(space_attr) != "preserve":
                            preview = repr(text)[:50]
                            rel = xml_file.relative_to(unpacked_dir)
                            result.error(f"{rel}: w:t missing xml:space='preserve': {preview}")
        except Exception as e:
            result.error(f"{xml_file.name}: {e}")


def validate_tracked_changes(unpacked_dir: Path, result: ValidationResult):
    """Check <w:del> uses <w:delText> not <w:t>, and <w:ins> doesn't use <w:delText>."""
    if not HAS_LXML:
        return
    for xml_file in _iter_xml_files(unpacked_dir):
        if xml_file.name != "document.xml":
            continue
        try:
            root = etree.parse(str(xml_file)).getroot()
            ns = {"w": WORD_NS}
            rel = xml_file.relative_to(unpacked_dir)

            # w:t inside w:del is wrong (should be w:delText)
            for t_elem in root.xpath(".//w:del//w:t", namespaces=ns):
                if t_elem.text:
                    preview = repr(t_elem.text)[:50]
                    result.error(f"{rel}: <w:t> found inside <w:del> (use <w:delText>): {preview}")

            # w:instrText inside w:del is wrong (should be w:delInstrText)
            for elem in root.xpath(".//w:del//w:instrText", namespaces=ns):
                result.error(f"{rel}: <w:instrText> inside <w:del> (use <w:delInstrText>)")

            # w:delText inside w:ins (without enclosing w:del) is wrong
            for elem in root.xpath(".//w:ins//w:delText[not(ancestor::w:del)]", namespaces=ns):
                preview = repr(elem.text or "")[:50]
                result.error(f"{rel}: <w:delText> inside <w:ins> without <w:del>: {preview}")

        except Exception as e:
            result.error(f"{xml_file.name}: {e}")


def validate_id_constraints(unpacked_dir: Path, result: ValidationResult):
    """Check paraId < 0x80000000 and durableId < 0x7FFFFFFF."""
    if not HAS_LXML:
        return
    para_id_attr = f"{{{W14_NS}}}paraId"
    durable_id_attr = f"{{{W16CID_NS}}}durableId"

    for xml_file in _iter_xml_files(unpacked_dir):
        try:
            for elem in etree.parse(str(xml_file)).iter():
                if val := elem.get(para_id_attr):
                    try:
                        if int(val, 16) >= 0x80000000:
                            result.error(f"{xml_file.name}: paraId={val} >= 0x80000000")
                    except ValueError:
                        result.error(f"{xml_file.name}: paraId={val} is not valid hex")

                if val := elem.get(durable_id_attr):
                    is_num = xml_file.name == "numbering.xml"
                    try:
                        base = 10 if is_num else 16
                        if int(val, base) >= 0x7FFFFFFF:
                            result.error(f"{xml_file.name}: durableId={val} >= 0x7FFFFFFF")
                    except ValueError:
                        result.error(f"{xml_file.name}: durableId={val} invalid")
        except Exception:
            pass


def validate_ms_extensions(unpacked_dir: Path, result: ValidationResult):
    """Validate Microsoft Word extension elements (w14/w15/w16cid/w16cex namespaces).

    Covers the checks that would otherwise require Microsoft's private XSD schemas.
    """
    if not HAS_LXML:
        return

    W15_NS = "http://schemas.microsoft.com/office/word/2012/wordml"
    W16CEX_NS = "http://schemas.microsoft.com/office/word/2018/wordml/cex"

    HEX8_RE = re.compile(r"^[0-9A-Fa-f]{8}$")

    # --- Check w14:textId format in document.xml ---
    for xml_file in _iter_xml_files(unpacked_dir):
        if xml_file.name != "document.xml" or "word" not in str(xml_file):
            continue
        try:
            root = etree.parse(str(xml_file)).getroot()
            text_id_attr = f"{{{W14_NS}}}textId"
            for elem in root.iter():
                val = elem.get(text_id_attr)
                if val is not None and val != "-1" and not HEX8_RE.match(val):
                    tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                    result.error(
                        f"document.xml: <{tag}> w14:textId='{val}' "
                        f"is not valid 8-char hex (expected e.g. '77777777')"
                    )
        except Exception:
            pass

    # --- Check w15:commentsEx structure ---
    comments_ext = unpacked_dir / "word" / "commentsExtended.xml"
    if comments_ext.exists():
        try:
            root = etree.parse(str(comments_ext)).getroot()
            for elem in root.iter(f"{{{W15_NS}}}commentEx"):
                para_id = elem.get(f"{{{W15_NS}}}paraId")
                done = elem.get(f"{{{W15_NS}}}done")

                if para_id is None:
                    result.error("commentsExtended.xml: w15:commentEx missing required w15:paraId")
                elif not HEX8_RE.match(para_id):
                    result.error(
                        f"commentsExtended.xml: w15:commentEx w15:paraId='{para_id}' "
                        f"is not valid 8-char hex"
                    )

                if done is None:
                    result.error("commentsExtended.xml: w15:commentEx missing required w15:done")
                elif done not in ("0", "1"):
                    result.error(
                        f"commentsExtended.xml: w15:commentEx w15:done='{done}' "
                        f"must be '0' or '1'"
                    )

                # If it's a reply, check paraIdParent is valid hex
                parent = elem.get(f"{{{W15_NS}}}paraIdParent")
                if parent is not None and not HEX8_RE.match(parent):
                    result.error(
                        f"commentsExtended.xml: w15:commentEx w15:paraIdParent='{parent}' "
                        f"is not valid 8-char hex"
                    )
        except Exception as e:
            result.error(f"commentsExtended.xml: parse error: {e}")

    # --- Check w16cid:commentsIds structure ---
    comments_ids = unpacked_dir / "word" / "commentsIds.xml"
    if comments_ids.exists():
        try:
            root = etree.parse(str(comments_ids)).getroot()
            for elem in root.iter(f"{{{W16CID_NS}}}commentId"):
                para_id = elem.get(f"{{{W16CID_NS}}}paraId")
                durable_id = elem.get(f"{{{W16CID_NS}}}durableId")

                if para_id is None:
                    result.error("commentsIds.xml: w16cid:commentId missing required w16cid:paraId")
                elif not HEX8_RE.match(para_id):
                    result.error(
                        f"commentsIds.xml: w16cid:commentId w16cid:paraId='{para_id}' "
                        f"is not valid 8-char hex"
                    )

                if durable_id is None:
                    result.error("commentsIds.xml: w16cid:commentId missing required w16cid:durableId")
                elif not HEX8_RE.match(durable_id):
                    result.error(
                        f"commentsIds.xml: w16cid:commentId w16cid:durableId='{durable_id}' "
                        f"is not valid 8-char hex"
                    )
        except Exception as e:
            result.error(f"commentsIds.xml: parse error: {e}")

    # --- Check w16cex:commentsExtensible structure ---
    comments_cex = unpacked_dir / "word" / "commentsExtensible.xml"
    if comments_cex.exists():
        try:
            root = etree.parse(str(comments_cex)).getroot()
            ISO_DT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

            for elem in root.iter(f"{{{W16CEX_NS}}}commentExtensible"):
                durable_id = elem.get(f"{{{W16CEX_NS}}}durableId")
                date_utc = elem.get(f"{{{W16CEX_NS}}}dateUtc")

                if durable_id is None:
                    result.error(
                        "commentsExtensible.xml: w16cex:commentExtensible "
                        "missing required w16cex:durableId"
                    )
                elif not HEX8_RE.match(durable_id):
                    result.error(
                        f"commentsExtensible.xml: w16cex:commentExtensible "
                        f"w16cex:durableId='{durable_id}' is not valid 8-char hex"
                    )

                if date_utc is not None and not ISO_DT_RE.match(date_utc):
                    result.error(
                        f"commentsExtensible.xml: w16cex:commentExtensible "
                        f"w16cex:dateUtc='{date_utc}' is not valid ISO 8601"
                    )
        except Exception as e:
            result.error(f"commentsExtensible.xml: parse error: {e}")

    # --- Cross-check: paraId consistency across comment files ---
    _cross_check_comment_para_ids(unpacked_dir, result)


def _cross_check_comment_para_ids(unpacked_dir: Path, result: ValidationResult):
    """Verify paraId values are consistent across comments.xml, commentsExtended.xml,
    and commentsIds.xml."""
    if not HAS_LXML:
        return

    W15_NS = "http://schemas.microsoft.com/office/word/2012/wordml"

    # Collect paraIds from comments.xml
    comments_para_ids = set()
    comments_xml = unpacked_dir / "word" / "comments.xml"
    if comments_xml.exists():
        try:
            root = etree.parse(str(comments_xml)).getroot()
            for p in root.iter(f"{{{WORD_NS}}}p"):
                pid = p.get(f"{{{W14_NS}}}paraId")
                if pid:
                    comments_para_ids.add(pid)
        except Exception:
            pass

    if not comments_para_ids:
        return  # no comments, nothing to cross-check

    # Collect paraIds from commentsExtended.xml
    ext_para_ids = set()
    ext_xml = unpacked_dir / "word" / "commentsExtended.xml"
    if ext_xml.exists():
        try:
            root = etree.parse(str(ext_xml)).getroot()
            for elem in root.iter(f"{{{W15_NS}}}commentEx"):
                pid = elem.get(f"{{{W15_NS}}}paraId")
                if pid:
                    ext_para_ids.add(pid)
        except Exception:
            pass

    # Collect paraIds from commentsIds.xml
    ids_para_ids = set()
    ids_xml = unpacked_dir / "word" / "commentsIds.xml"
    if ids_xml.exists():
        try:
            root = etree.parse(str(ids_xml)).getroot()
            for elem in root.iter(f"{{{W16CID_NS}}}commentId"):
                pid = elem.get(f"{{{W16CID_NS}}}paraId")
                if pid:
                    ids_para_ids.add(pid)
        except Exception:
            pass

    # Check: every comment paraId should appear in extended and ids files
    if ext_para_ids:
        missing = comments_para_ids - ext_para_ids
        for pid in sorted(missing):
            result.error(
                f"paraId={pid} in comments.xml but missing from commentsExtended.xml"
            )

    if ids_para_ids:
        missing = comments_para_ids - ids_para_ids
        for pid in sorted(missing):
            result.error(
                f"paraId={pid} in comments.xml but missing from commentsIds.xml"
            )


def validate_comment_markers(unpacked_dir: Path, result: ValidationResult):
    """Check comment markers are properly paired (start/end/reference)."""
    if not HAS_LXML:
        return
    doc_xml = None
    comments_xml = None
    for xf in _iter_xml_files(unpacked_dir):
        if xf.name == "document.xml" and "word" in str(xf):
            doc_xml = xf
        elif xf.name == "comments.xml":
            comments_xml = xf
    if not doc_xml:
        return

    try:
        root = etree.parse(str(doc_xml)).getroot()
        ns = {"w": WORD_NS}

        starts = {e.get(f"{{{WORD_NS}}}id") for e in root.xpath(".//w:commentRangeStart", namespaces=ns)}
        ends = {e.get(f"{{{WORD_NS}}}id") for e in root.xpath(".//w:commentRangeEnd", namespaces=ns)}
        refs = {e.get(f"{{{WORD_NS}}}id") for e in root.xpath(".//w:commentReference", namespaces=ns)}

        for cid in sorted(ends - starts, key=lambda x: int(x) if x and x.isdigit() else 0):
            result.error(f"commentRangeEnd id={cid} has no matching commentRangeStart")
        for cid in sorted(starts - ends, key=lambda x: int(x) if x and x.isdigit() else 0):
            result.error(f"commentRangeStart id={cid} has no matching commentRangeEnd")

        if comments_xml and comments_xml.exists():
            croot = etree.parse(str(comments_xml)).getroot()
            comment_ids = {e.get(f"{{{WORD_NS}}}id") for e in croot.xpath(".//w:comment", namespaces=ns)}
            all_markers = starts | ends | refs
            for cid in sorted(all_markers - comment_ids, key=lambda x: int(x) if x and x.isdigit() else 0):
                if cid:
                    result.error(f"marker id={cid} references non-existent comment")
    except Exception as e:
        result.error(f"Comment validation error: {e}")


def validate_content_types(unpacked_dir: Path, result: ValidationResult):
    """Check that Content_Types.xml references existing files."""
    ct_path = unpacked_dir / "[Content_Types].xml"
    if not ct_path.exists():
        result.error("Missing [Content_Types].xml")
        return
    try:
        dom = minidom_mod.parseString(ct_path.read_text(encoding="utf-8"))
        for override in dom.getElementsByTagName("Override"):
            part = override.getAttribute("PartName").lstrip("/")
            if part and not (unpacked_dir / part).exists():
                result.warn(f"Content type override for missing file: /{part}")
    except Exception as e:
        result.error(f"Content_Types.xml error: {e}")


def validate_relationships(unpacked_dir: Path, result: ValidationResult):
    """Check relationship targets exist."""
    for rels_file in unpacked_dir.rglob("*.rels"):
        try:
            dom = minidom_mod.parseString(rels_file.read_text(encoding="utf-8"))
            for rel in dom.getElementsByTagName("Relationship"):
                target = rel.getAttribute("Target")
                if not target or target.startswith("http://") or target.startswith("https://"):
                    continue
                target_path = (rels_file.parent.parent / target).resolve()
                try:
                    rel_path = target_path.relative_to(unpacked_dir.resolve())
                    if not target_path.exists():
                        result.warn(f"{rels_file.relative_to(unpacked_dir)}: target missing: {target}")
                except ValueError:
                    pass
        except Exception:
            pass


def validate_unique_ids(unpacked_dir: Path, result: ValidationResult):
    """Check for duplicate IDs within files that should be unique."""
    id_tags = {"comment", "commentrangestart", "commentrangeend", "bookmarkstart", "bookmarkend"}

    for xml_file in _iter_xml_files(unpacked_dir):
        if xml_file.name != "document.xml":
            continue
        try:
            dom = minidom_mod.parseString(xml_file.read_text(encoding="utf-8"))
            for tag in id_tags:
                seen: dict[str, int] = {}
                for elem in dom.getElementsByTagName(f"w:{tag}"):
                    val = elem.getAttribute("w:id")
                    if val:
                        seen[val] = seen.get(val, 0) + 1
                for val, count in seen.items():
                    if count > 1:
                        result.error(f"{xml_file.name}: duplicate w:{tag} id={val} ({count} times)")
        except Exception:
            pass


def validate_rid_cross_references(unpacked_dir: Path, result: ValidationResult):
    """Check r:id/r:embed/r:link in content XML match entries in .rels files."""
    if not HAS_LXML:
        return
    OFFICE_RELS_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

    for xml_file in _iter_xml_files(unpacked_dir):
        if xml_file.suffix == ".rels":
            continue
        rels_file = xml_file.parent / "_rels" / f"{xml_file.name}.rels"
        if not rels_file.exists():
            continue
        try:
            rels_root = etree.parse(str(rels_file)).getroot()
            valid_rids = set()
            for rel in rels_root.findall(f".//{{{PKG_RELS_NS}}}Relationship"):
                rid = rel.get("Id")
                if rid:
                    valid_rids.add(rid)

            content_root = etree.parse(str(xml_file)).getroot()
            rel_path = xml_file.relative_to(unpacked_dir)
            for elem in content_root.iter():
                if not hasattr(elem, "tag") or callable(elem.tag):
                    continue
                for attr_suffix in ("id", "embed", "link"):
                    rid_val = elem.get(f"{{{OFFICE_RELS_NS}}}{attr_suffix}")
                    if rid_val and rid_val not in valid_rids:
                        tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                        result.error(
                            f"{rel_path}: <{tag_name}> r:{attr_suffix}='{rid_val}' "
                            f"not found in {rels_file.relative_to(unpacked_dir)}"
                        )
        except Exception:
            pass


def validate_bidirectional_refs(unpacked_dir: Path, result: ValidationResult):
    """Check for files that exist but are not referenced by any .rels file."""
    all_referenced = set()
    for rels_file in unpacked_dir.rglob("*.rels"):
        try:
            dom = minidom_mod.parseString(rels_file.read_text(encoding="utf-8"))
            for rel in dom.getElementsByTagName("Relationship"):
                target = rel.getAttribute("Target")
                if not target or target.startswith("http") or target.startswith("mailto:"):
                    continue
                if target.startswith("/"):
                    target_path = unpacked_dir / target.lstrip("/")
                elif rels_file.name == ".rels":
                    target_path = unpacked_dir / target
                else:
                    target_path = rels_file.parent.parent / target
                try:
                    all_referenced.add(target_path.resolve().relative_to(unpacked_dir.resolve()))
                except ValueError:
                    pass
        except Exception:
            pass

    skip_patterns = {"[Content_Types].xml", "_rels", "docProps"}
    for f in unpacked_dir.rglob("*"):
        if not f.is_file():
            continue
        if f.name == "[Content_Types].xml" or f.suffix == ".rels":
            continue
        if any(s in f.parts for s in skip_patterns):
            continue
        try:
            rel = f.relative_to(unpacked_dir)
            if rel not in all_referenced:
                result.warn(f"Unreferenced file: {rel}")
        except ValueError:
            pass


def validate_media_content_types(unpacked_dir: Path, result: ValidationResult):
    """Check media files have matching Default extension declarations in Content_Types."""
    ct_path = unpacked_dir / "[Content_Types].xml"
    if not ct_path.exists():
        return

    MEDIA_TYPES = {
        "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "gif": "image/gif", "bmp": "image/bmp", "tiff": "image/tiff",
        "wmf": "image/x-wmf", "emf": "image/x-emf", "svg": "image/svg+xml",
    }

    try:
        dom = minidom_mod.parseString(ct_path.read_text(encoding="utf-8"))
        declared_exts = set()
        for default in dom.getElementsByTagName("Default"):
            ext = default.getAttribute("Extension")
            if ext:
                declared_exts.add(ext.lower())

        for f in unpacked_dir.rglob("*"):
            if not f.is_file() or "_rels" in f.parts:
                continue
            ext = f.suffix.lstrip(".").lower()
            if ext in MEDIA_TYPES and ext not in declared_exts:
                result.error(
                    f'{f.relative_to(unpacked_dir)}: extension "{ext}" not declared '
                    f'in [Content_Types].xml (add: <Default Extension="{ext}" '
                    f'ContentType="{MEDIA_TYPES[ext]}"/>)'
                )
    except Exception:
        pass


def compare_paragraph_counts(unpacked_dir: Path, original_file: Path | None, result: ValidationResult):
    """Compare paragraph counts between original and modified."""
    if not original_file or not HAS_LXML:
        return

    def count_paragraphs(root):
        return len(root.findall(f".//{{{WORD_NS}}}p"))

    try:
        doc_xml = unpacked_dir / "word" / "document.xml"
        if not doc_xml.exists():
            return
        new_root = etree.parse(str(doc_xml)).getroot()
        new_count = count_paragraphs(new_root)

        with tempfile.TemporaryDirectory() as td:
            with zipfile.ZipFile(original_file, "r") as zf:
                safe_extract(zf, Path(td))
            orig_root = etree.parse(str(Path(td) / "word" / "document.xml")).getroot()
            orig_count = count_paragraphs(orig_root)

        diff = new_count - orig_count
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        result.warn(f"Paragraphs: {orig_count} -> {new_count} ({diff_str})")
    except Exception:
        pass


# --- PPTX-specific checks ---

def validate_pptx_slide_layouts(unpacked_dir: Path, result: ValidationResult):
    """Check slide layout references and notes slide uniqueness."""
    if not HAS_LXML:
        return

    # Check for duplicate slideLayout references per slide
    for rels_file in unpacked_dir.glob("ppt/slides/_rels/*.xml.rels"):
        try:
            root = etree.parse(str(rels_file)).getroot()
            layout_rels = [
                r for r in root.findall(f".//{{{PKG_RELS_NS}}}Relationship")
                if "slideLayout" in r.get("Type", "")
            ]
            if len(layout_rels) > 1:
                result.error(f"{rels_file.relative_to(unpacked_dir)}: {len(layout_rels)} slideLayout refs (expected 1)")
        except Exception:
            pass

    # Check for notes slides referenced by multiple slides
    notes_refs: dict[str, list[str]] = {}
    for rels_file in unpacked_dir.glob("ppt/slides/_rels/*.xml.rels"):
        try:
            root = etree.parse(str(rels_file)).getroot()
            for rel in root.findall(f".//{{{PKG_RELS_NS}}}Relationship"):
                if "notesSlide" in rel.get("Type", ""):
                    target = rel.get("Target", "").replace("../", "")
                    slide = rels_file.stem.replace(".xml", "")
                    notes_refs.setdefault(target, []).append(slide)
        except Exception:
            pass
    for target, slides in notes_refs.items():
        if len(slides) > 1:
            result.error(f"Notes slide '{target}' referenced by multiple slides: {', '.join(slides)}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _iter_xml_files(unpacked_dir: Path):
    yield from unpacked_dir.rglob("*.xml")
    yield from unpacked_dir.rglob("*.rels")


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def validate(
    unpacked_dir: Path,
    original_file: Path | None = None,
    auto_repair: bool = False,
    file_type: str | None = None,
    author: str = "Claude",
) -> ValidationResult:
    """Run all validations and optional repairs. Returns ValidationResult."""
    result = ValidationResult()

    if not file_type:
        if (unpacked_dir / "word").exists():
            file_type = "docx"
        elif (unpacked_dir / "ppt").exists():
            file_type = "pptx"
        elif original_file:
            file_type = original_file.suffix.lower().lstrip(".")

    # Repair phase
    if auto_repair:
        result.repairs += repair_whitespace_preservation(unpacked_dir)
        if file_type == "docx":
            result.repairs += repair_durable_ids(unpacked_dir)

    # Validation phase - common checks
    validate_well_formed_xml(unpacked_dir, result)
    if result.errors:
        return result  # further checks useless if XML is broken

    validate_content_types(unpacked_dir, result)
    validate_relationships(unpacked_dir, result)
    validate_unique_ids(unpacked_dir, result)
    validate_rid_cross_references(unpacked_dir, result)
    validate_bidirectional_refs(unpacked_dir, result)
    validate_media_content_types(unpacked_dir, result)

    # DOCX-specific checks
    if file_type == "docx":
        validate_whitespace_preservation(unpacked_dir, result)
        validate_tracked_changes(unpacked_dir, result)
        validate_id_constraints(unpacked_dir, result)
        validate_ms_extensions(unpacked_dir, result)
        validate_comment_markers(unpacked_dir, result)
        compare_paragraph_counts(unpacked_dir, original_file, result)

        # Redlining verification (most important DOCX check)
        if original_file and original_file.exists():
            try:
                from verify_redlines import verify_redlines
                passed, msg = verify_redlines(str(unpacked_dir), str(original_file), author)
                if not passed and "No tracked changes" not in msg:
                    result.error(msg)
            except ImportError:
                pass

    # PPTX-specific checks
    if file_type == "pptx":
        validate_pptx_slide_layouts(unpacked_dir, result)

    # XSD schema validation (both DOCX and PPTX)
    try:
        from xsd_validator import validate_xsd
        xsd_passed, xsd_messages = validate_xsd(unpacked_dir, original_file)
        if not xsd_passed:
            for msg in xsd_messages:
                result.error(f"XSD: {msg}")
    except ImportError:
        pass  # xsd_validator not available, skip silently

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Office document XML")
    parser.add_argument("path", help="Unpacked directory or packed Office file")
    parser.add_argument("--original", help="Original file for comparison")
    parser.add_argument("--auto-repair", action="store_true", help="Auto-repair common issues")
    parser.add_argument(
        "--author",
        default="Claude",
        help="Author name for tracked-change verification (default: Claude)",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        sys.exit(1)

    original = Path(args.original) if args.original else None

    temp_dir: str | None = None
    try:
        # If path is a file, unpack to temp dir
        if path.is_file() and path.suffix.lower() in {".docx", ".pptx", ".xlsx"}:
            temp_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(path, "r") as zf:
                safe_extract(zf, Path(temp_dir))
            unpacked = Path(temp_dir)
            ft = path.suffix.lower().lstrip(".")
        else:
            unpacked = path
            ft = original.suffix.lower().lstrip(".") if original else None

        result = validate(
            unpacked,
            original,
            auto_repair=args.auto_repair,
            file_type=ft,
            author=args.author,
        )
        print(result.report())
        sys.exit(0 if result.ok else 1)
    finally:
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)
