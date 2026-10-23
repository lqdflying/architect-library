#!/usr/bin/env python3
"""Behavior tests for purge_handoff.py."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("purge_handoff.py")


def load_purge():
    spec = importlib.util.spec_from_file_location("purge_handoff", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


PURGE = load_purge()


def run(ledger: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(ledger), "--timestamp", "2026-10-23T00:00:00Z", *extra],
        capture_output=True,
        text=True,
        check=False,
    )


class PurgeHandoffTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(dir="/tmp")
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def ledger(self, name: str, text: str) -> Path:
        path = self.dir / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_archives_rounds_before_the_last_two(self) -> None:
        path = self.ledger(
            "topic-handoff.md",
            """**Status:** open
**Must fix:** #1
**Standing:** #3 DEFER — waits on the user
**Closed:** #2 FIXED `a.py:4` test passed
Purge-ready: yes

## Round 1

old finding

## Round 2

middle

## Round 3

latest
""",
        )
        result = run(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("purged 1 section", result.stdout)
        active = path.read_text(encoding="utf-8")
        self.assertIn("## Round 2", active)
        self.assertIn("## Round 3", active)
        self.assertNotIn("old finding", active)
        self.assertNotIn("Purge-ready: yes", active)
        self.assertIn("topic-handoff-archive.md", active)
        archive = (self.dir / "topic-handoff-archive.md").read_text(encoding="utf-8")
        self.assertIn("old finding", archive)
        self.assertNotIn("middle", archive)
        self.assertNotIn("latest", archive)

    def test_still_open_subsection_stays_inside_its_round(self) -> None:
        path = self.ledger(
            "topic-handoff.md",
            """**Status:** open
**Must fix:** #1
**Standing:** none
**Closed:** none
Purge-ready: yes

## Round 1

### Still open

old open text

## Round 2

kept

## Round 3

### Still open

current open text
""",
        )
        result = run(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("purged 1 section", result.stdout)
        active = path.read_text(encoding="utf-8")
        self.assertIn("## Round 2", active)
        self.assertIn("## Round 3", active)
        self.assertIn("current open text", active)
        self.assertNotIn("old open text", active)
        archive = (self.dir / "topic-handoff-archive.md").read_text(encoding="utf-8")
        self.assertIn("old open text", archive)
        self.assertNotIn("current open text", archive)

    def test_two_rounds_with_still_open_subsection_are_not_purged(self) -> None:
        text = """**Status:** open
**Must fix:** #1
**Standing:** none
**Closed:** none
Purge-ready: yes

## Round 1

### Still open

full text

## Round 2

latest
"""
        path = self.ledger("topic-handoff.md", text)
        result = run(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("nothing to purge", result.stdout)
        active = path.read_text(encoding="utf-8")
        self.assertIn("full text", active)
        self.assertIn("latest", active)
        self.assertFalse((self.dir / "topic-handoff-archive.md").exists())

    def test_trailing_space_on_closing_fence_purges(self) -> None:
        path = self.ledger(
            "topic-handoff.md",
            """**Status:** open
**Must fix:** none
**Standing:** none
**Closed:** none
Purge-ready: yes

## Round 1

```text
sample
```  

## Round 2

two

## Round 3

three
""",
        )
        result = run(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("purged 1 section", result.stdout)
        active = path.read_text(encoding="utf-8")
        self.assertIn("## Round 2", active)
        self.assertIn("## Round 3", active)
        self.assertNotIn("sample", active)
        archive = (self.dir / "topic-handoff-archive.md").read_text(encoding="utf-8")
        self.assertIn("sample", archive)

    def test_fence_does_not_split_a_section(self) -> None:
        path = self.ledger(
            "topic-handoff.md",
            """**Status:** open
**Must fix:** none
**Standing:** none
**Closed:** none
Purge-ready: yes

## Round 1

old

## Already verified

belongs to round 1

## Round 2

before fence

```text
## Round 9 — inside a fence
```

middle

## Round 3

latest
""",
        )
        result = run(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        active = path.read_text(encoding="utf-8")
        self.assertIn("before fence", active)
        self.assertIn("inside a fence", active)
        self.assertIn("middle", active)
        self.assertIn("latest", active)
        self.assertNotIn("belongs to round 1", active)
        archive = (self.dir / "topic-handoff-archive.md").read_text(encoding="utf-8")
        self.assertIn("belongs to round 1", archive)
        self.assertIn("old", archive)
        self.assertNotIn("before fence", archive)
        self.assertNotIn("## Round 9 — inside a fence", archive)

    def test_missing_flag_leaves_the_file_unchanged(self) -> None:
        text = """**Status:** open
**Must fix:** #1
**Standing:** none
**Closed:** none

## Round 1

old

## Round 2

middle

## Round 3

latest
"""
        path = self.ledger("topic-handoff.md", text)
        result = run(path)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Purge-ready: yes", result.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), text)
        self.assertFalse((self.dir / "topic-handoff-archive.md").exists())

    def test_fewer_than_three_rounds_is_a_noop(self) -> None:
        text = """**Status:** open
**Must fix:** none
**Standing:** none
**Closed:** none
Purge-ready: yes

## Round 1

only
"""
        path = self.ledger("topic-handoff.md", text)
        result = run(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("nothing to purge", result.stdout)
        active = path.read_text(encoding="utf-8")
        self.assertIn("only", active)
        self.assertNotIn("Purge-ready: yes", active)
        self.assertFalse((self.dir / "topic-handoff-archive.md").exists())

    def test_second_run_does_not_duplicate_the_archive(self) -> None:
        path = self.ledger(
            "topic-handoff.md",
            """**Status:** open
**Must fix:** none
**Standing:** none
**Closed:** #1 FIXED `a.py:1`
Purge-ready: yes

## Round 1

old

## Round 2

middle

## Round 3

latest
""",
        )
        first = run(path)
        self.assertEqual(first.returncode, 0, first.stderr)
        archive = self.dir / "topic-handoff-archive.md"
        once = archive.read_text(encoding="utf-8")
        # Resume the same content: put the flag back without a new round.
        active = path.read_text(encoding="utf-8")
        path.write_text(active.replace("**Status:** open\n", "**Status:** open\nPurge-ready: yes\n", 1), encoding="utf-8")
        second = run(path)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("nothing to purge", second.stdout)
        self.assertEqual(archive.read_text(encoding="utf-8"), once)

    def test_refuses_a_ledger_outside_tmp(self) -> None:
        outside = Path("/var/tmp/purge-handoff-outside.md")
        outside.write_text("**Status:** open\n\n## Round 1\n\nx\n", encoding="utf-8")
        self.addCleanup(outside.unlink, missing_ok=True)
        result = run(outside)
        self.assertEqual(result.returncode, 2)
        self.assertIn("not under /tmp", result.stderr)
        self.assertIn("## Round 1", outside.read_text(encoding="utf-8"))

    def test_resume_after_archive_write_does_not_duplicate(self) -> None:
        text = """**Status:** open
**Must fix:** none
**Standing:** none
**Closed:** none
Purge-ready: yes

## Round 1

old

## Round 2

middle

## Round 3

latest
"""
        path = self.ledger("topic-handoff.md", text)
        archive = self.dir / "topic-handoff-archive.md"
        _header, sections = PURGE.split_sections(text)
        to_archive, _keep = PURGE.partition(sections)
        PURGE.write_archive(archive, path, to_archive, "2026-10-23T00:00:00Z")
        once = archive.read_text(encoding="utf-8")
        result = run(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(archive.read_text(encoding="utf-8"), once)
        self.assertNotIn("old", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
