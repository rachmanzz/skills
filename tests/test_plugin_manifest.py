"""Validate the Antigravity plugin manifest (plugin.json) at the repo root."""

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_MANIFEST = REPO_ROOT / "plugin.json"
NAME_PATTERN = re.compile(r"^[a-zA-Z0-9-_]+$")
SCHEMA_URL = "https://antigravity.google/schemas/v1/plugin.json"


class PluginManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(
            PLUGIN_MANIFEST.is_file(), f"missing plugin manifest: {PLUGIN_MANIFEST}"
        )
        self.manifest = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_is_a_json_object(self) -> None:
        self.assertIsInstance(self.manifest, dict)

    def test_manifest_declares_schema(self) -> None:
        self.assertEqual(self.manifest.get("$schema"), SCHEMA_URL)

    def test_name_is_present_and_matches_pattern(self) -> None:
        name = self.manifest.get("name", "")
        self.assertTrue(name, "plugin.json must declare a name")
        self.assertRegex(name, NAME_PATTERN)

    def test_description_is_present(self) -> None:
        self.assertTrue(self.manifest.get("description"))

    def test_skills_directory_contains_skills(self) -> None:
        skills_dir = REPO_ROOT / "skills"
        skill_files = sorted(skills_dir.glob("*/SKILL.md"))
        self.assertGreaterEqual(len(skill_files), 1)
        for skill_file in skill_files:
            self.assertTrue(skill_file.is_file())


if __name__ == "__main__":
    unittest.main()
