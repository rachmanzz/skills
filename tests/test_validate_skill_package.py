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
        (skill_dir / "references").mkdir(parents=True)
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
        self.assertTrue(any("does not match folder" in e for e in errors))

    def test_missing_name_is_reported(self) -> None:
        frontmatter = VALID_FRONTMATTER.replace("name: my-skill\n", "")
        skill_dir = self.make_skill(frontmatter=frontmatter)
        errors = validate_skill_package.validate(skill_dir)
        self.assertTrue(any("missing name" in e for e in errors))

    def test_missing_description_is_reported(self) -> None:
        frontmatter = VALID_FRONTMATTER.replace(
            "description: A test skill used only by unit tests.\n", ""
        )
        skill_dir = self.make_skill(frontmatter=frontmatter)
        errors = validate_skill_package.validate(skill_dir)
        self.assertTrue(any("missing description" in e for e in errors))

    def test_uppercase_name_is_reported(self) -> None:
        frontmatter = VALID_FRONTMATTER.replace("name: my-skill", "name: My Skill")
        skill_dir = self.make_skill(frontmatter=frontmatter, name="my-skill")
        errors = validate_skill_package.validate(skill_dir)
        self.assertTrue(any("lowercase" in e for e in errors))

    def test_overlong_description_is_reported(self) -> None:
        frontmatter = VALID_FRONTMATTER.replace(
            "description: A test skill used only by unit tests.",
            "description: " + "x" * 1025,
        )
        skill_dir = self.make_skill(frontmatter=frontmatter)
        errors = validate_skill_package.validate(skill_dir)
        self.assertTrue(any("at most 1024" in e for e in errors))

    def test_broken_reference_link_is_reported(self) -> None:
        frontmatter = VALID_FRONTMATTER.replace(
            "references/evidence-and-assumption-control.md",
            "references/does-not-exist.md",
        )
        skill_dir = self.make_skill(frontmatter=frontmatter)
        errors = validate_skill_package.validate(skill_dir)
        self.assertTrue(any("missing SKILL.md reference" in e for e in errors))

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
        self.assertTrue(any("nested SKILL.md" in e for e in errors))

    def test_missing_required_reference_is_reported(self) -> None:
        skill_dir = self.make_skill(with_required_reference=False)
        errors = validate_skill_package.validate(skill_dir)
        self.assertTrue(any("missing required reference" in e for e in errors))


class MainTests(SkillDirTestCase):
    def test_main_accepts_package_with_skills_in_files(self) -> None:
        skill_dir = self.make_skill()
        package_file = self.root / "package.json"
        package_file.write_text(json.dumps({"files": ["skills"]}), encoding="utf-8")
        with mock.patch.object(sys, "argv", ["prog", str(skill_dir)]):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(validate_skill_package.main(), 0)

    def test_main_rejects_package_without_skills_in_files(self) -> None:
        skill_dir = self.make_skill()
        package_file = self.root / "package.json"
        package_file.write_text(json.dumps({"files": ["dist"]}), encoding="utf-8")
        with mock.patch.object(sys, "argv", ["prog", str(skill_dir)]):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(validate_skill_package.main(), 1)

    def test_main_rejects_invalid_package_json(self) -> None:
        skill_dir = self.make_skill()
        (self.root / "package.json").write_text("{ not json", encoding="utf-8")
        with mock.patch.object(sys, "argv", ["prog", str(skill_dir)]):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(validate_skill_package.main(), 1)


if __name__ == "__main__":
    unittest.main()
