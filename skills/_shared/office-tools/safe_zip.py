"""Safe ZIP extraction helpers (Zip Slip mitigation)."""

from __future__ import annotations

import zipfile
from pathlib import Path


def _is_safe_member(dest_dir: Path, member_name: str) -> bool:
    """Return True if member extracts under dest_dir (no path traversal)."""
    dest_root = dest_dir.resolve()
    target = (dest_root / member_name).resolve()
    return target == dest_root or str(target).startswith(str(dest_root) + "/")


def safe_extract(zip_file: zipfile.ZipFile, dest_dir: Path) -> None:
    """Extract all members of zip_file into dest_dir, rejecting unsafe paths."""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    for info in zip_file.infolist():
        name = info.filename
        if not name or name.endswith("/"):
            if not _is_safe_member(dest_dir, name):
                raise ValueError(f"Unsafe ZIP path: {name!r}")
            # Directory entry — create if needed
            (dest_dir / name).mkdir(parents=True, exist_ok=True)
            continue
        if not _is_safe_member(dest_dir, name):
            raise ValueError(f"Unsafe ZIP path: {name!r}")
        zip_file.extract(info, dest_dir)
