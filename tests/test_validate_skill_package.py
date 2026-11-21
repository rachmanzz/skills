"""Unit tests for scripts/validate-skill-package.py."""

import importlib.util
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
import io
from pathlib import Path
from unittest import mock

SCRIPTS_DIR = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "performance-and-resource-efficiency"
    / "scripts"
)


def load_script(module_name: str, file_name: str):
    """Load a validator script whose hyphenated file name is not importable."""
    spec = importlib.util.spec_from_file_location(
        module_name, SCRIPTS_DIR / file_name
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validate_skill_package = load_script(
    "validate_skill_package", "validate-skill-package.py"
)

VALID_FRONTMATTER = """---
name: my-skill
description: A test skill used only by unit tests.
---

# My Skill

See [evidence control](references/evidence-and-assumption-control.md).
"""


class SkillDirTestCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def make_skill(
        self,
        name: str = "my-skill",
        frontmatter: str = VALID_FRONTMATTER,
        with_required_reference: bool = True,
    ) -> Path:
        skill_dir = self.root / "skills" / name
        (skill_dir / "references").mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(frontmatter, encoding="utf-8")
        if with_required_reference:
            (skill_dir / "references" / "evidence-and-assumption-control.md").write_text(
                "reference\n", encoding="utf-8"
            )
        return skill_dir


class ValidateTests(SkillDirTestCase):
    def test_valid_skill_has_no_errors(self) -> None:
        skill_dir = self.make_skill()
        self.assertEqual(validate_skill_package.validate(skill_dir), [])

    def test_missing_skill_md_is_reported(self) -> None:
        skill_dir = self.root / "my-skill"
        skill_dir.mkdir()
        errors = validate_skill_package.validate(skill_dir)
        self.assertEqual(len(errors), 1)
        self.assertIn("missing", errors[0])

    def test_name_mismatching_folder_is_reported(self) -> None:
        frontmatter = VALID_FRONTMATTER.replace("name: my-skill", "name: other-skill")
        skill_dir = self.make_skill(frontmatter=frontmatter)
        errors = validate_skill_package.validate(skill_dir)
        self.assertEqual(len(errors), 1)
        self.assertIn("does not match folder", errors[0])

    def test_missing_name_is_reported(self) -> None:
        frontmatter = VALID_FRONTMATTER.replace("name: my-skill\n", "")
        skill_dir = self.make_skill(frontmatter=frontmatter)
        errors = validate_skill_package.validate(skill_dir)
        self.assertEqual(len(errors), 1)
        self.assertIn("missing name", errors[0])

    def test_missing_description_is_reported(self) -> None:
        frontmatter = VALID_FRONTMATTER.replace(
            "description: A test skill used only by unit tests.\n", ""
        )
        skill_dir = self.make_skill(frontmatter=frontmatter)
        errors = validate_skill_package.validate(skill_dir)
        self.assertEqual(len(errors), 1)
        self.assertIn("missing description", errors[0])

    def test_uppercase_name_is_reported(self) -> None:
        frontmatter = VALID_FRONTMATTER.replace("name: my-skill", "name: My Skill")
        skill_dir = self.make_skill(frontmatter=frontmatter, name="my-skill")
        errors = validate_skill_package.validate(skill_dir)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("lowercase" in e for e in errors))
        self.assertTrue(any("does not match folder" in e for e in errors))

    def test_frontmatter_edge_cases_and_bounds(self) -> None:
        skill_dir = self.make_skill(frontmatter="# No frontmatter\n")
        self.assertEqual(
            validate_skill_package.validate(skill_dir),
            ["SKILL.md must start with YAML frontmatter"],
        )

        unclosed = "---\nname: my-skill\ndescription: unclosed\n"
        skill_dir = self.make_skill(frontmatter=unclosed)
        self.assertEqual(
            validate_skill_package.validate(skill_dir),
            ["SKILL.md frontmatter is not closed"],
        )

        quoted_and_multiline = (
            "---\n"
            "name: 'my-skill'\n"
            "description: |\n"
            "  Multiline description line one.\n"
            "---   \n\n# Body\n"
        )
        skill_dir = self.make_skill(frontmatter=quoted_and_multiline)
        self.assertEqual(validate_skill_package.validate(skill_dir), [])

        long_name = "a" * 65
        skill_dir = self.make_skill(
            name=long_name,
            frontmatter=VALID_FRONTMATTER.replace("name: my-skill", f"name: {long_name}"),
        )
        errors = validate_skill_package.validate(skill_dir)
        self.assertEqual(len(errors), 1)
        self.assertIn("at most 64", errors[0])

        for bad_name in ("-my-skill", "my-skill-", "my--skill", "my_skill"):
            skill_dir = self.make_skill(
                name=bad_name,
                frontmatter=VALID_FRONTMATTER.replace("name: my-skill", f"name: {bad_name}"),
            )
            errors = validate_skill_package.validate(skill_dir)
            self.assertEqual(len(errors), 1, bad_name)
            self.assertIn("lowercase", errors[0])

    def test_overlong_description_is_reported(self) -> None:
        frontmatter = VALID_FRONTMATTER.replace(
            "description: A test skill used only by unit tests.",
            "description: " + "x" * 1025,
        )
        skill_dir = self.make_skill(frontmatter=frontmatter)
        errors = validate_skill_package.validate(skill_dir)
        self.assertEqual(len(errors), 1)
        self.assertIn("at most 1024", errors[0])

    def test_broken_reference_link_is_reported(self) -> None:
        frontmatter = VALID_FRONTMATTER.replace(
            "references/evidence-and-assumption-control.md",
            "references/does-not-exist.md",
        )
        skill_dir = self.make_skill(frontmatter=frontmatter)
        errors = validate_skill_package.validate(skill_dir)
        self.assertEqual(len(errors), 1)
        self.assertIn("missing SKILL.md reference", errors[0])

    def test_fragment_mailto_and_code_block_links_are_handled(self) -> None:
        content = (
            VALID_FRONTMATTER
            + "\nSee [anchor](references/evidence-and-assumption-control.md#top), "
            + "[section](#local), [mail](mailto:test@example.com), "
            + "[http](http://example.com).\n"
            + "```markdown\n[ignored](references/nonexistent.md)\n```\n"
            + "`[inline-ignored](references/nonexistent2.md)`\n"
        )
        skill_dir = self.make_skill(frontmatter=content)
        self.assertEqual(validate_skill_package.validate(skill_dir), [])

    def test_escaping_and_symlink_links_are_rejected(self) -> None:
        outside = self.root / "outside.md"
        outside.write_text("outside\n", encoding="utf-8")
        content = VALID_FRONTMATTER + "\nSee [escape](../../outside.md).\n"
        skill_dir = self.make_skill(frontmatter=content)
        errors = validate_skill_package.validate(skill_dir)
        self.assertEqual(len(errors), 1)
        self.assertIn("escapes skill directory", errors[0])

        sym_skill = self.make_skill(name="sym-skill", frontmatter=VALID_FRONTMATTER.replace("my-skill", "sym-skill"))
        sym_ref = sym_skill / "references" / "sym.md"
        try:
            sym_ref.symlink_to(sym_skill / "references" / "evidence-and-assumption-control.md")
        except OSError:
            self.skipTest("symlinks not supported on filesystem")
        errors = validate_skill_package.validate(sym_skill)
        self.assertTrue(any("symlink" in e for e in errors))

    def test_http_link_is_not_reported(self) -> None:
        frontmatter = VALID_FRONTMATTER.replace(
            "references/evidence-and-assumption-control.md",
            "https://example.com/docs",
        )
        skill_dir = self.make_skill(frontmatter=frontmatter)
        self.assertEqual(validate_skill_package.validate(skill_dir), [])

    def test_nested_skill_md_is_reported(self) -> None:
        skill_dir = self.make_skill()
        nested = skill_dir / "nested"
        nested.mkdir()
        (nested / "SKILL.md").write_text(VALID_FRONTMATTER, encoding="utf-8")
        errors = validate_skill_package.validate(skill_dir)
        self.assertEqual(len(errors), 1)
        self.assertIn("nested SKILL.md", errors[0])

    def test_missing_required_reference_is_reported(self) -> None:
        minimal = "---\nname: my-skill\ndescription: A test skill used only by unit tests.\n---\n\n# My Skill\n"
        skill_dir = self.make_skill(frontmatter=minimal, with_required_reference=False)
        errors = validate_skill_package.validate(skill_dir)
        self.assertEqual(len(errors), 1)
        self.assertIn("missing required reference", errors[0])

    def test_broken_link_inside_reference_file_is_reported(self) -> None:
        skill_dir = self.make_skill()
        (skill_dir / "references" / "evidence-and-assumption-control.md").write_text(
            "See [broken](missing-doc.md).\n", encoding="utf-8"
        )
        errors = validate_skill_package.validate(skill_dir)
        self.assertEqual(len(errors), 1)
        self.assertIn("missing reference link in", errors[0])


class MainTests(SkillDirTestCase):
    def test_main_accepts_package_with_skills_in_files(self) -> None:
        skill_dir = self.make_skill()
        package_file = self.root / "package.json"
        package_file.write_text(json.dumps({"files": ["skills"]}), encoding="utf-8")
        buf = io.StringIO()
        with mock.patch.object(sys, "argv", ["prog", str(skill_dir)]):
            with redirect_stdout(buf):
                self.assertEqual(validate_skill_package.main(), 0)
        self.assertIn("Skill package valid:", buf.getvalue())

    def test_main_rejects_package_without_skills_in_files(self) -> None:
        skill_dir = self.make_skill()
        package_file = self.root / "package.json"
        package_file.write_text(json.dumps({"files": ["dist"]}), encoding="utf-8")
        buf = io.StringIO()
        with mock.patch.object(sys, "argv", ["prog", str(skill_dir)]):
            with redirect_stdout(buf):
                self.assertEqual(validate_skill_package.main(), 1)
        self.assertIn("Skill package invalid:", buf.getvalue())

    def test_main_rejects_invalid_and_non_dict_package_json(self) -> None:
        skill_dir = self.make_skill()
        for raw in ("{ not json", "[]", json.dumps({"files": None})):
            (self.root / "package.json").write_text(raw, encoding="utf-8")
            buf = io.StringIO()
            with mock.patch.object(sys, "argv", ["prog", str(skill_dir)]):
                with redirect_stdout(buf):
                    self.assertEqual(validate_skill_package.main(), 1)
            self.assertIn("Skill package invalid:", buf.getvalue())

    def test_main_help_and_extra_args_and_standalone_skill(self) -> None:
        buf = io.StringIO()
        with mock.patch.object(sys, "argv", ["prog", "--help"]):
            with redirect_stdout(buf):
                self.assertEqual(validate_skill_package.main(), 0)
        self.assertIn("Usage:", buf.getvalue())

        err_buf = io.StringIO()
        with mock.patch.object(sys, "argv", ["prog", "a", "b"]):
            with mock.patch.object(sys, "stderr", err_buf):
                self.assertEqual(validate_skill_package.main(), 2)

        # Standalone skill not under skills/ ignores ancestor package.json
        (self.root / "package.json").write_text(json.dumps({"files": []}), encoding="utf-8")
        standalone = self.root / "standalone" / "my-skill"
        (standalone / "references").mkdir(parents=True)
        (standalone / "SKILL.md").write_text(VALID_FRONTMATTER, encoding="utf-8")
        (standalone / "references" / "evidence-and-assumption-control.md").write_text("ref\n", encoding="utf-8")
        buf = io.StringIO()
        with mock.patch.object(sys, "argv", ["prog", str(standalone)]):
            with redirect_stdout(buf):
                self.assertEqual(validate_skill_package.main(), 0)

    def test_main_rejects_symlink_skill_directory_and_package_json(self) -> None:
        skill_dir = self.make_skill()
        sym_dir = self.root / "sym-skill"
        target_pkg = self.root / "real-package.json"
        target_pkg.write_text(json.dumps({"files": ["skills"]}), encoding="utf-8")
        sym_pkg = self.root / "package.json"
        try:
            sym_dir.symlink_to(skill_dir)
            sym_pkg.symlink_to(target_pkg)
        except OSError:
            self.skipTest("symlinks not supported on filesystem")

        buf = io.StringIO()
        with mock.patch.object(sys, "argv", ["prog", str(sym_dir)]):
            with redirect_stdout(buf):
                self.assertEqual(validate_skill_package.main(), 1)
        self.assertIn("symlink skill directory is not allowed", buf.getvalue())

        buf = io.StringIO()
        with mock.patch.object(sys, "argv", ["prog", str(skill_dir)]):
            with redirect_stdout(buf):
                self.assertEqual(validate_skill_package.main(), 1)
        self.assertIn("package.json must not be a symlink", buf.getvalue())

    def test_validate_and_main_reject_oversized_files(self) -> None:
        skill_dir = self.make_skill()
        (self.root / "package.json").write_text(
            json.dumps({"files": ["skills"]}), encoding="utf-8"
        )
        with mock.patch.object(validate_skill_package, "MAX_FILE_BYTES", 10):
            errors = validate_skill_package.validate(skill_dir)
            self.assertTrue(any("exceeds maximum size" in e for e in errors))

            buf = io.StringIO()
            with mock.patch.object(sys, "argv", ["prog", str(skill_dir)]):
                with redirect_stdout(buf):
                    self.assertEqual(validate_skill_package.main(), 1)
            self.assertIn("exceeds maximum size", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
