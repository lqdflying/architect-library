#!/usr/bin/env python3
"""Render Codex agents and preserve personal content around managed instructions.

Uses only the Python standard library. Called by install_library.sh.
"""

import argparse
import json
import os
from pathlib import Path
import stat
import tempfile


BEGIN = b"<!-- BEGIN architect-library -->"
END = b"<!-- END architect-library -->"


def agent_content(source):
    """JSON basic strings also safely encode these UTF-8 strings in TOML."""
    metadata = json.loads((source / "codex.json").read_text(encoding="utf-8"))
    instructions = (source / "INSTRUCTIONS.md").read_text(encoding="utf-8")
    instructions += "\n\n" + (source.parent / "codex-review.md").read_text(encoding="utf-8")
    fields = {
        "name": metadata["name"],
        "description": metadata["description"],
        "sandbox_mode": "read-only",
        "developer_instructions": instructions,
    }
    if any(not isinstance(value, str) or not value.strip() for value in fields.values()):
        raise ValueError(f"Incomplete Codex agent metadata: {source}")
    return "".join(f"{key} = {json.dumps(value, ensure_ascii=False)}\n" for key, value in fields.items()).encode("utf-8")


def instruction_content(fragments, destination):
    override = destination.with_name("AGENTS.override.md")
    if override.exists() and override.read_bytes().strip():
        raise ValueError(f"{override} hides AGENTS.md; reconcile that override before installing Codex rules")
    original = destination.read_bytes() if destination.exists() else b""
    block = BEGIN + b"\n" + b"\n".join(path.read_bytes() for path in fragments) + END
    # Require exactly one complete, standalone pair, or no markers at all.
    if BEGIN in original or END in original:
        lines = original.splitlines(keepends=True)
        starts = [i for i, line in enumerate(lines) if line.rstrip(b"\r\n") == BEGIN]
        ends = [i for i, line in enumerate(lines) if line.rstrip(b"\r\n") == END]
        if (original.count(BEGIN) != 1 or original.count(END) != 1
                or len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]):
            raise ValueError(f"Malformed or duplicate architect-library markers in {destination}; repair them before installing")
        end_line = lines[ends[0]]
        newline = end_line[len(END):]
        return b"".join(lines[:starts[0]]) + block + newline + b"".join(lines[ends[0] + 1:])
    separator = b"" if not original or original.endswith(b"\n\n") else (b"\n" if original.endswith(b"\n") else b"\n\n")
    return original + separator + block + b"\n"


def write_atomic(destination, content):
    # Do not redirect an install into an unrelated file via a symlink.
    if destination.is_symlink():
        raise ValueError(f"Refusing to replace symlink: {destination}")
    if destination.exists() and destination.read_bytes() == content:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(destination.stat().st_mode) if destination.exists() else 0o644
    fd, temporary = tempfile.mkstemp(prefix=".architect-library-", dir=destination.parent)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(content)
            os.fchmod(output.fileno(), mode)
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("agent", "instructions"))
    parser.add_argument("mode", choices=("preflight", "write", "verify"))
    parser.add_argument("destination", type=Path)
    parser.add_argument("sources", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        if args.destination.is_symlink():
            raise ValueError(f"Refusing to replace symlink: {args.destination}")
        content = (agent_content(args.sources[0]) if args.kind == "agent"
                   else instruction_content(args.sources, args.destination))
        if args.mode == "write":
            write_atomic(args.destination, content)
        elif args.mode == "verify":
            if not args.destination.is_file() or args.destination.read_bytes() != content:
                raise ValueError(f"Codex {args.kind} verification failed: {args.destination}")
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
