#!/usr/bin/env python3
"""Installer integration tests; all writes stay in temporary fixture directories.

Run: python3 -m unittest discover -s scripts -p 'test_install_library.py'
Python 3.11+ is needed here for independent TOML parsing, not for installation.
"""

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parent.parent
BEGIN = b"<!-- BEGIN architect-library -->"
END = b"<!-- END architect-library -->"


def snapshot(directory):
    return {str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in directory.rglob("*") if path.is_file()}


class InstallLibraryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="architect-install-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "source"
        for name in ("scripts", "skills", "agents", "user-rules"):
            shutil.copytree(ROOT / name, self.repo / name,
                            ignore=shutil.ignore_patterns(".venv", "__pycache__", "vendor", "node_modules", ".npm-bootstrap"))
        self.home = self.root / "home"
        self.project = self.root / "project with spaces"
        self.home.mkdir()
        self.project.mkdir()
        self.env = os.environ.copy()
        for key in ("CODEX_HOME", "NODE_BIN", "NODE_PATH", "NPM_CONFIG_PREFIX",
                    "ARCHITECT_ENV_FILE", "XDG_CONFIG_HOME", "ARCHITECT_NPM_BOOTSTRAP"):
            self.env.pop(key, None)
        self.env["HOME"] = str(self.home)

    def install(self, *args, success=True, cwd=None):
        result = subprocess.run(["bash", str(self.repo / "scripts/install_library.sh"), *args],
                                cwd=cwd or self.project, env=self.env, text=True, capture_output=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("VERIFY: OK", result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def instructions(self):
        return Path(self.env.get("CODEX_HOME", self.home / ".codex")) / "AGENTS.md"

    def assert_skills(self, directory, editor):
        for source in (self.repo / "skills").iterdir():
            if not source.is_dir():
                continue
            if editor == "claude" and source.name in ("mcp-tool-rules", "context7-docs", "notion-mcp-ops"):
                self.assertFalse((directory / source.name).exists())
                continue
            shared = source / "SKILL.md"
            variant = source / f"SKILL.{editor}.md"
            if not shared.exists() and not variant.exists():
                continue
            installed = directory / source.name
            expected = variant if variant.exists() else shared
            self.assertEqual((installed / "SKILL.md").read_bytes(), expected.read_bytes())
            self.assertEqual(list(installed.glob("SKILL.*.md")), [])
        for relative in ("_shared/office-tools/office_tools.py", "word-document/references/docx-guide.md",
                         "notion-mcp-ops/references/formatting.md"):
            if editor == "claude" and relative.startswith("notion-"):
                continue
            self.assertEqual((directory / relative).read_bytes(), (self.repo / "skills" / relative).read_bytes())

    def test_codex_global_preserves_personal_content_and_other_editors(self):
        for editor in ("cursor", "copilot", "claude"):
            marker = self.home / f".{editor}/skills/handoff/personal.md"
            marker.parent.mkdir(parents=True)
            marker.write_text("legacy content owned by another editor")
        personal_skill = self.home / ".agents/skills/personal/SKILL.md"
        personal_skill.parent.mkdir(parents=True)
        personal_skill.write_text("personal skill")
        personal_agent = self.home / ".codex/agents/personal.toml"
        personal_agent.parent.mkdir(parents=True)
        personal_agent.write_text('name = "personal"\n')
        before = snapshot(self.home)
        self.instructions().write_bytes(b"# Personal\r\nKeep this text verbatim.")
        self.instructions().chmod(0o600)
        self.install("all", "codex")
        after = snapshot(self.home)
        for path, digest in before.items():
            self.assertEqual(after[path], digest)
        self.assert_skills(self.home / ".agents/skills", "codex")
        self.assertTrue(self.instructions().read_bytes().startswith(b"# Personal\r\nKeep this text verbatim."))
        self.assertEqual(self.instructions().stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.instructions().read_bytes().count(BEGIN), 1)
        self.assertIn(b"~/.agents/skills/review-handoff/SKILL.md", self.instructions().read_bytes())
        self.assertNotIn(b"alwaysApply:", self.instructions().read_bytes())
        for name in ("code-review", "security-auditor"):
            agent = tomllib.loads((self.home / f".codex/agents/{name}.toml").read_text())
            self.assertEqual(agent["name"], name)
            self.assertEqual(agent["sandbox_mode"], "read-only")
            self.assertNotIn("model", agent)
            self.assertIn((self.repo / f"agents/{name}/INSTRUCTIONS.md").read_text(), agent["developer_instructions"])
        stable = snapshot(self.home)
        self.install("all", "codex")
        self.assertEqual(snapshot(self.home), stable)

    def test_codex_preserves_shared_skills_with_legacy_names(self):
        names = ("docx", "pptx", "xlsx", "pdf", "terraform-apply-fix-review",
                 "terraform-commit-review", "terraform-apply-assistance",
                 "mcp-tool-rules-copilot", "handoff")
        cases = ((("all", "codex"), self.home),
                 (("skills", "codex", "project"), self.project),
                 (("all", "all"), self.home))
        for args, base in cases:
            with self.subTest(args=args):
                originals = {}
                for name in names:
                    path = base / ".agents/skills" / name / "SKILL.md"
                    path.parent.mkdir(parents=True, exist_ok=True)
                    originals[path] = f"personal {name} skill\r\n".encode()
                    path.write_bytes(originals[path])
                legacy_dirs = []
                if args == ("all", "all"):
                    for editor in ("cursor", "copilot", "claude"):
                        for name in names:
                            directory = self.home / f".{editor}/skills" / name
                            directory.mkdir(parents=True, exist_ok=True)
                            (directory / "SKILL.md").write_text("legacy library skill")
                            legacy_dirs.append(directory)
                self.install(*args)
                for path, content in originals.items():
                    self.assertTrue(path.is_file(), str(path))
                    self.assertEqual(path.read_bytes(), content)
                for directory in legacy_dirs:
                    self.assertFalse(directory.exists(), str(directory))

    def test_codex_partial_installs_and_custom_home(self):
        self.env["CODEX_HOME"] = str(self.root / "custom codex profile")
        self.install("skills", "codex")
        self.assertFalse(self.instructions().exists())
        self.assertFalse(self.instructions().parent.exists())
        self.install("agents", "codex")
        self.assertFalse(self.instructions().exists())
        self.assertTrue((self.instructions().parent / "agents/code-review.toml").exists())
        self.install("rules", "codex")
        self.assertTrue(self.instructions().exists())
        self.assertFalse((self.home / ".codex").exists())

    def test_managed_block_update_preserves_prefix_and_suffix(self):
        self.instructions().parent.mkdir()
        prefix, suffix = b"personal prefix\r\n\r\n", b"\r\npersonal suffix\r\n"
        self.instructions().write_bytes(prefix + BEGIN + b"\nold rules\n" + END + suffix)
        self.install("all", "codex")
        content = self.instructions().read_bytes()
        self.assertTrue(content.startswith(prefix + BEGIN))
        self.assertTrue(content.endswith(END + suffix))
        self.assertNotIn(b"old rules", content)

    def test_rules_only_missing_skill_changes_nothing(self):
        self.instructions().parent.mkdir()
        self.instructions().write_text("personal")
        before = snapshot(self.home)
        result = self.install("rules", "codex", success=False)
        self.assertIn("Missing review-handoff", result.stderr)
        self.assertEqual(snapshot(self.home), before)

    def test_conflicting_override_blocks_all_editors_before_writes(self):
        self.instructions().parent.mkdir()
        self.instructions().with_name("AGENTS.override.md").write_text("personal override")
        before = snapshot(self.home)
        result = self.install("all", "all", success=False)
        self.assertIn("hides AGENTS.md", result.stderr)
        self.assertEqual(snapshot(self.home), before)

    def test_empty_override_does_not_block(self):
        self.instructions().parent.mkdir()
        self.instructions().with_name("AGENTS.override.md").write_text("\n")
        self.install("all", "codex")

    def test_malformed_managed_markers_change_nothing(self):
        self.instructions().parent.mkdir()
        for content in (BEGIN, END, END + b"\n" + BEGIN,
                        BEGIN + b"\n" + BEGIN + b"\n" + END,
                        b"prefix " + BEGIN + b"\n" + END):
            with self.subTest(content=content):
                self.instructions().write_bytes(content)
                before = snapshot(self.home)
                result = self.install("all", "codex", success=False)
                self.assertIn("Malformed", result.stderr)
                self.assertEqual(snapshot(self.home), before)

    def test_instruction_symlink_is_rejected_before_writes(self):
        self.instructions().parent.mkdir()
        target = self.root / "personal.md"
        target.write_text("personal")
        self.instructions().symlink_to(target)
        self.install("all", "codex", success=False)
        self.assertEqual(target.read_text(), "personal")
        self.assertFalse((self.home / ".agents").exists())

    def test_codex_project_does_not_touch_home_or_project_instructions(self):
        (self.project / "AGENTS.md").write_text("project policy")
        (self.project / "AGENTS.override.md").write_text("project override")
        before = snapshot(self.home)
        for what in ("all", "skills", "agents", "rules"):
            self.install(what, "codex", "project")
        self.assertEqual(snapshot(self.home), before)
        self.assertEqual((self.project / "AGENTS.md").read_text(), "project policy")
        self.assertEqual((self.project / "AGENTS.override.md").read_text(), "project override")
        self.assert_skills(self.project / ".agents/skills", "codex")
        self.assertTrue((self.project / ".codex/agents/code-review.toml").exists())

    def test_generation_drift_and_missing_variant_fail_before_writes(self):
        fragment = self.repo / "user-rules/codex/edit-scope.md"
        original = fragment.read_bytes()
        fragment.write_text("stale instructions")
        result = self.install("all", "codex", success=False)
        self.assertIn("Stale Codex fragment", result.stdout + result.stderr)
        self.assertEqual(snapshot(self.home), {})
        fragment.write_bytes(original)
        (self.repo / "skills/mcp-tool-rules/SKILL.codex.md").unlink()
        result = self.install("all", "codex", success=False)
        self.assertIn("Missing codex skill", result.stderr)
        self.assertEqual(snapshot(self.home), {})

    def test_each_legacy_editor_is_isolated_and_both_excludes_codex(self):
        for editor in ("cursor", "copilot", "claude"):
            self.install("all", editor)
            self.assert_skills(self.home / f".{editor}/skills", editor)
            self.assertFalse((self.home / ".agents").exists())
        self.install("all", "both")
        self.assertFalse((self.home / ".codex").exists())
        self.install("all", "all")
        self.assertTrue(self.instructions().exists())
        self.assert_skills(self.home / ".agents/skills", "codex")
        # Cursor and Copilot also load ~/.agents/skills; the Codex variants must say they are Codex only.
        for name in ("mcp-tool-rules", "context7-docs", "notion-mcp-ops"):
            frontmatter, body = (self.home / f".agents/skills/{name}/SKILL.md").read_text().split("\n---\n", 1)
            self.assertIn("Codex only.", frontmatter)
            self.assertIn("**Codex only.**", body)
            self.assertNotIn("Codex only", (self.home / f".cursor/skills/{name}/SKILL.md").read_text())

    def test_project_scope_preserves_global_legacy_files(self):
        for editor in ("cursor", "copilot", "claude"):
            legacy = self.home / f".{editor}/skills/handoff/SKILL.md"
            legacy.parent.mkdir(parents=True)
            legacy.write_text("global legacy skill")
        before = snapshot(self.home)
        self.install("all", "all", "project")
        self.assertEqual(snapshot(self.home), before)
        self.assertTrue((self.project / ".cursor/rules/response-style.mdc").exists())
        self.assertFalse((self.project / ".github/copilot-instructions.md").exists())
        self.assertFalse((self.project / ".claude/rules").exists())
        self.assertFalse((self.project / "AGENTS.md").exists())

    def test_claude_rules_install_and_keep_personal_files(self):
        personal = {self.home / ".claude/CLAUDE.md": "personal instructions",
                    self.home / ".claude/rules/personal.md": "personal rule"}
        for path, text in personal.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        self.install("all", "claude")
        for source in (self.repo / "user-rules/claude").iterdir():
            installed = (self.home / ".claude/rules" / source.name).read_bytes()
            self.assertEqual(installed, source.read_bytes())
            self.assertNotIn(b"alwaysApply", installed)
        self.assertIn(b"~/.claude/skills/review-handoff/SKILL.md",
                      (self.home / ".claude/rules/review-handoff.md").read_bytes())
        for path, text in personal.items():
            self.assertEqual(path.read_text(), text)
        stable = snapshot(self.home)
        self.install("all", "claude")
        self.assertEqual(snapshot(self.home), stable)

    def test_claude_rules_only_missing_skill_changes_nothing(self):
        result = self.install("rules", "claude", success=False)
        self.assertIn("Missing review-handoff", result.stderr)
        self.assertEqual(snapshot(self.home), {})

    def test_maintainer_project_scope_preserves_rules(self):
        rules = self.repo / ".cursor/rules/response-style.mdc"
        rules.parent.mkdir(parents=True)
        rules.write_text("maintainer policy")
        self.install("all", "cursor", "project", cwd=self.repo)
        self.assertEqual(rules.read_text(), "maintainer policy")


if __name__ == "__main__":
    unittest.main()
