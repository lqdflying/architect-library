#!/usr/bin/env python3
"""Shift a horizontal or vertical band in an existing Excalidraw file.

Layout QA for edits — not a diagram generator. Do not use this to synthesize
a whole poster. See edit-existing.md.

Examples:
    uv run python shift_region.py diagram.excalidraw --below 1075 --dy 108 --dry-run
    uv run python shift_region.py diagram.excalidraw --below 1075 --dy 108 --exclude inv_identity
    uv run python shift_region.py diagram.excalidraw --right-of 1680 --dx 40
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Shift Excalidraw elements in a band (edit-existing collision pass).",
    )
    parser.add_argument("input", type=Path, help="Path to .excalidraw JSON")
    parser.add_argument(
        "--below",
        type=float,
        default=None,
        metavar="Y",
        help="Shift elements with y >= Y by --dy",
    )
    parser.add_argument(
        "--dy",
        type=float,
        default=0,
        help="Vertical delta (positive = down)",
    )
    parser.add_argument(
        "--right-of",
        type=float,
        default=None,
        metavar="X",
        help="Shift elements with x >= X by --dx",
    )
    parser.add_argument(
        "--dx",
        type=float,
        default=0,
        help="Horizontal delta (positive = right)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="ID",
        help="Element id to leave unmoved (repeatable)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would move; do not write",
    )
    args = parser.parse_args()

    if args.below is None and args.right_of is None:
        print("ERROR: pass --below Y and/or --right-of X", file=sys.stderr)
        return 2
    if args.below is not None and args.dy == 0:
        print("ERROR: --below requires non-zero --dy", file=sys.stderr)
        return 2
    if args.right_of is not None and args.dx == 0:
        print("ERROR: --right-of requires non-zero --dx", file=sys.stderr)
        return 2
    if not args.input.is_file():
        print(f"ERROR: file not found: {args.input}", file=sys.stderr)
        return 2

    data = json.loads(args.input.read_text(encoding="utf-8"))
    if data.get("type") != "excalidraw" or not isinstance(data.get("elements"), list):
        print("ERROR: not an Excalidraw JSON file", file=sys.stderr)
        return 2

    exclude = set(args.exclude)
    moved: list[tuple[str, float, float, float, float]] = []
    for el in data["elements"]:
        if el.get("isDeleted"):
            continue
        eid = el.get("id")
        if not eid or eid in exclude:
            continue
        x = float(el.get("x") or 0)
        y = float(el.get("y") or 0)
        nx, ny = x, y
        if args.below is not None and y >= args.below:
            ny = y + args.dy
        if args.right_of is not None and x >= args.right_of:
            nx = x + args.dx
        if nx == x and ny == y:
            continue
        moved.append((eid, x, y, nx, ny))
        if not args.dry_run:
            el["x"] = nx
            el["y"] = ny
            el["version"] = int(el.get("version") or 1) + 1
            el["versionNonce"] = int(el.get("versionNonce") or 1) + 1

    print(f"{'would move' if args.dry_run else 'moved'} {len(moved)} elements")
    for eid, x, y, nx, ny in moved:
        print(f"  {eid}: ({x:.1f},{y:.1f}) -> ({nx:.1f},{ny:.1f})")

    if args.dry_run:
        return 0

    args.input.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
