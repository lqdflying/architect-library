#!/usr/bin/env python3
"""Merge the library's managed keys into a Claude Code settings.json.

Uses only the Python standard library. Called by install_library.sh.
"""

import argparse
import json
from pathlib import Path

from codex_install import write_atomic


def load(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {path}: {error}; repair it before installing Claude settings")
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return data


def merge(current, managed):
    """Managed keys win. Nested objects merge, so personal keys beside them stay."""
    merged = dict(current)
    for key, value in managed.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("preflight", "write", "verify"))
    parser.add_argument("destination", type=Path)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    try:
        if args.destination.is_symlink():
            raise ValueError(f"Refusing to replace symlink: {args.destination}")
        current = load(args.destination) if args.destination.exists() else {}
        merged = merge(current, load(args.source))
        # Equal data is left alone, so a personal file keeps its own formatting.
        if merged != current:
            if args.mode == "write":
                write_atomic(args.destination, (json.dumps(merged, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
            elif args.mode == "verify":
                raise ValueError(f"Claude settings verification failed: {args.destination}")
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
