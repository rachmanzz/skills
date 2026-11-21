"""Validate plugin/package manifests and all repository skill packages."""

import importlib.util
import io
import json
import re
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_MANIFEST = REPO_ROOT / "package.json"
PLUGIN_MANIFEST = REPO_ROOT / "plugin.json"
VALIDATOR_PATH = (
    REPO_ROOT
    / "skills"
    / "performance-and-resource-efficiency"
    / "scripts"
    / "validate-skill-package.py"
)
EVIDENCE_VALIDATOR_PATH = (
    REPO_ROOT
    / "skills"
    / "performance-and-resource-efficiency"
    / "scripts"
    / "validate-evidence.py"
)
LEDGER_TEMPLATE_PATH = (
    REPO_ROOT
    / "skills"
    / "performance-and-resource-efficiency"
    / "references"
    / "evidence-ledger-template.md"
)
NAME_PATTERN = re.compile(r"^[a-zA-Z0-9-_]+$")
SCHEMA_URL = "https://antigravity.google/schemas/v1/plugin.json"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _strip_yaml_scalar(raw: str) -> str:
    val = raw.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in {'"', "'"}:
        return val[1:-1]
    if " #" in val:
        val = val.split(" #", 1)[0].rstrip()
    return val


def _parse_openai_yaml(path: Path) -> dict[str, dict[str, str]]:
    sections: dict[str, dict[str, str]] = {}
    current_section: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith((" ", "\t")) and line.endswith(":"):
            current_section = line[:-1].strip()
            sections.setdefault(current_section, {})
            continue
        if current_section and line.startswith((" ", "\t")) and ":" in line:
            key, value = line.split(":", 1)
            sections[current_section][key.strip()] = _strip_yaml_scalar(value)
    return sections


def _extract_short_description(skill_md: Path) -> str:
    for line in skill_md.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("short-description:"):
            return _strip_yaml_scalar(line.split(":", 1)[1])
    return ""


class PluginManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(
            PLUGIN_MANIFEST.is_file(), f"missing plugin manifest: {PLUGIN_MANIFEST}"
        )
        self.assertTrue(
            PACKAGE_MANIFEST.is_file(), f"missing package manifest: {PACKAGE_MANIFEST}"
        )
        self.manifest = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
        self.package = json.loads(PACKAGE_MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_is_a_json_object(self) -> None:
        self.assertIsInstance(self.manifest, dict)
        self.assertIsInstance(self.package, dict)

    def test_manifest_declares_schema(self) -> None:
        self.assertEqual(self.manifest.get("$schema"), SCHEMA_URL)

    def test_name_is_present_and_matches_pattern(self) -> None:
        name = self.manifest.get("name")
        self.assertIsInstance(name, str)
        self.assertTrue(name.strip(), "plugin.json must declare a non-empty name")
        self.assertRegex(name, NAME_PATTERN)

    def test_description_and_version_are_present(self) -> None:
        description = self.manifest.get("description")
        self.assertIsInstance(description, str)
        self.assertTrue(description.strip())
        self.assertEqual(self.manifest.get("version"), self.package.get("version"))

    def test_package_manifest_fields_are_valid(self) -> None:
        self.assertIsInstance(self.package.get("name"), str)
        self.assertTrue(self.package["name"].strip())
        self.assertIsInstance(self.package.get("version"), str)
        self.assertTrue(self.package["version"].strip())
        self.assertEqual(self.package.get("license"), "MIT")
        self.assertIn("skills", self.package.get("files", []))

    def test_skills_directory_contains_only_skill_dirs(self) -> None:
        skills_dir = REPO_ROOT / "skills"
        entries = sorted(skills_dir.iterdir())
        self.assertGreaterEqual(len(entries), 1)
        for entry in entries:
            self.assertTrue(entry.is_dir(), f"unexpected non-directory in skills/: {entry}")
            self.assertTrue((entry / "SKILL.md").is_file(), f"missing SKILL.md in {entry}")

    def test_all_repository_skills_pass_package_validator_main(self) -> None:
        validator = _load_module("repo_skill_validator", VALIDATOR_PATH)
        skill_dirs = sorted(p for p in (REPO_ROOT / "skills").iterdir() if p.is_dir())
        self.assertGreaterEqual(len(skill_dirs), 1)
        for skill_dir in skill_dirs:
            with self.subTest(skill=skill_dir.name):
                buf = io.StringIO()
                with mock.patch.object(sys, "argv", ["validate-skill-package.py", str(skill_dir)]):
                    with redirect_stdout(buf):
                        code = validator.main()
                self.assertEqual(code, 0, buf.getvalue())
                self.assertIn("Skill package valid:", buf.getvalue())

    def test_evidence_ledger_template_passes_validator(self) -> None:
        evidence_validator = _load_module("repo_evidence_validator", EVIDENCE_VALIDATOR_PATH)
        self.assertEqual(evidence_validator.validate(LEDGER_TEMPLATE_PATH), [])

    def test_all_repository_skills_have_valid_and_aligned_openai_yaml(self) -> None:
        skill_dirs = sorted(p for p in (REPO_ROOT / "skills").iterdir() if p.is_dir())
        for skill_dir in skill_dirs:
            with self.subTest(skill=skill_dir.name):
                yaml_path = skill_dir / "agents" / "openai.yaml"
                self.assertTrue(yaml_path.is_file(), f"missing {yaml_path}")
                parsed = _parse_openai_yaml(yaml_path)
                interface = parsed.get("interface", {})
                policy = parsed.get("policy", {})
                self.assertTrue(interface.get("display_name", "").strip())
                short_desc = interface.get("short_description", "").strip()
                self.assertTrue(short_desc)
                self.assertEqual(short_desc, _extract_short_description(skill_dir / "SKILL.md"))
                self.assertIn(f"${skill_dir.name}", interface.get("default_prompt", ""))
                self.assertIn(
                    policy.get("allow_implicit_invocation"), {"true", "false"}
                )


if __name__ == "__main__":
    unittest.main()
