#!/usr/bin/env python3
"""Move closed review-handoff rounds out of the active ledger.

Keeps the header and the two newest ``## Round`` or ``## Fixer`` sections.
Other ``##`` headings stay inside the round that contains them. Appends
the removed rounds verbatim to the sibling ``*-archive.md`` file.

Refuses unless the header contains ``Purge-ready: yes`` plus the
``**Status:**``, ``**Must fix:**``, ``**Standing:**``, and ``**Closed:**``
labels. A missing flag leaves the ledger unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

KEEP_ROUNDS = 2
PURGE_READY = "Purge-ready: yes"
# Other ``##`` headings stay inside the round. Real ledgers use them for
# subsections such as "Already verified" and finding titles.
SECTION_START = re.compile(r"^## (?:Round|Fixer)\b")
REQUIRED_LABELS = ("**Status:**", "**Must fix:**", "**Standing:**", "**Closed:**")


def archive_path_for(ledger: Path) -> Path:
    name = ledger.name
    if name.endswith(".md"):
        return ledger.with_name(name[:-3] + "-archive.md")
    return ledger.with_name(name + "-archive.md")


def under_tmp(path: Path) -> bool:
    try:
        path.resolve().relative_to(Path("/tmp").resolve())
    except ValueError:
        return False
    return True


def fence_marker(line: str) -> str | None:
    """Return the fence characters when ``line`` opens or closes a fence."""
    indent = len(line) - len(line.lstrip(" "))
    if indent > 3:
        return None
    body = line.lstrip(" ").rstrip("\r\n")
    if not body or body[0] not in "`~":
        return None
    char = body[0]
    count = 0
    for ch in body:
        if ch != char:
            break
        count += 1
    if count < 3:
        return None
    rest = body[count:]
    if rest.strip() and char == "`" and "`" in rest:
        return None
    return char * count


def is_closing_fence(line: str, opened: str) -> bool:
    marker = fence_marker(line)
    if marker is None or marker[0] != opened[0] or len(marker) < len(opened):
        return False
    body = line.lstrip(" ").rstrip("\r\n")
    return body.rstrip(" \t") == marker


def split_sections(text: str) -> tuple[str, list[str]]:
    """Split a ledger into the header and round sections.

    A section starts at ``## Round`` or ``## Fixer``. Fenced code does not
    start a section. Other headings, including ``### Still open``, stay in
    the current round.
    """
    header: list[str] = []
    sections: list[list[str]] = []
    current: list[str] | None = None
    opened: str | None = None
    for line in text.splitlines(keepends=True):
        if opened is not None:
            if is_closing_fence(line, opened):
                opened = None
            if current is None:
                header.append(line)
            else:
                current.append(line)
            continue
        marker = fence_marker(line)
        if marker is not None:
            opened = marker
            if current is None:
                header.append(line)
            else:
                current.append(line)
            continue
        if SECTION_START.match(line):
            if current is not None:
                sections.append(current)
            current = [line]
            continue
        if current is None:
            header.append(line)
        else:
            current.append(line)
    if current is not None:
        sections.append(current)
    return "".join(header), ["".join(part) for part in sections]


def partition(sections: list[str]) -> tuple[list[str], list[str]]:
    """Return ``(archive, keep)`` for the two newest rounds."""
    if len(sections) <= KEEP_ROUNDS:
        return [], sections
    return sections[:-KEEP_ROUNDS], sections[-KEEP_ROUNDS:]


def missing_ready_label(header: str) -> str | None:
    lines = [line.strip() for line in header.splitlines()]
    if PURGE_READY not in lines:
        return f"header lacks {PURGE_READY}"
    for label in REQUIRED_LABELS:
        if label not in header:
            return f"header lacks {label}"
    return None


def rewrite_header(header: str, archive: Path) -> str:
    archive_line = (
        f"Archive: {archive} (read only when a closed item is contested "
        f"or an open item's full text is missing)\n"
    )
    kept: list[str] = []
    replaced = False
    for line in header.splitlines(keepends=True):
        stripped = line.strip()
        if stripped == PURGE_READY:
            continue
        if stripped.startswith("Archive:"):
            if not replaced:
                kept.append(archive_line)
                replaced = True
            continue
        kept.append(line)
    if replaced:
        text = "".join(kept)
        if text and not text.endswith("\n"):
            text += "\n"
        return text
    body = "".join(kept).rstrip("\n")
    if body:
        body += "\n"
    return body + archive_line + "\n"


def archive_preamble(source: Path) -> str:
    return (
        "# Handoff archive\n\n"
        f"Source: {source}\n\n"
        "Closed rounds moved here verbatim. "
        "Do not read this file on an ordinary review or fix turn.\n"
    )


def write_archive(archive: Path, source: Path, sections: list[str], timestamp: str) -> None:
    body = "".join(sections)
    if not body.endswith("\n"):
        body += "\n"
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
    marker = f"<!-- archived-batch {digest} -->\n"
    existing = archive.read_text(encoding="utf-8") if archive.exists() else ""
    if marker in existing:
        return
    block = f"\n## Archived {timestamp}\n\n{marker}\n{body}"
    if not existing:
        block = archive_preamble(source) + block
    archive.parent.mkdir(parents=True, exist_ok=True)
    with archive.open("a", encoding="utf-8") as handle:
        handle.write(block)


def purge(ledger: Path, timestamp: str) -> tuple[int, str]:
    if not under_tmp(ledger):
        return 2, "refusing to purge: ledger is not under /tmp"
    if not ledger.is_file():
        return 2, f"refusing to purge: {ledger} does not exist"
    text = ledger.read_text(encoding="utf-8")
    header, sections = split_sections(text)
    to_archive, to_keep = partition(sections)
    if not to_archive:
        if any(line.strip() == PURGE_READY for line in header.splitlines()):
            updated = "".join(
                line
                for line in header.splitlines(keepends=True)
                if line.strip() != PURGE_READY
            )
            new_text = updated + "".join(to_keep)
            if new_text != text:
                _replace(ledger, new_text)
        return 0, "nothing to purge"
    reason = missing_ready_label(header)
    if reason is not None:
        return 2, f"refusing to purge: {reason}"
    archive = archive_path_for(ledger)
    if not under_tmp(archive):
        return 2, "refusing to purge: archive path is not under /tmp"
    write_archive(archive, ledger, to_archive, timestamp)
    new_text = rewrite_header(header, archive) + "".join(to_keep)
    _replace(ledger, new_text)
    count = len(to_archive)
    noun = "section" if count == 1 else "sections"
    return 0, f"purged {count} {noun} to {archive}"


def _replace(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + ".purge-tmp")
    try:
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument(
        "--timestamp",
        default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    args = parser.parse_args(argv)
    code, message = purge(args.ledger, args.timestamp)
    if code == 0:
        print(message)
    else:
        print(message, file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
