#!/usr/bin/env python3
"""Validate the installable performance skill package without dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\]\(([^)]+)\)")


def frontmatter(skill_file: Path) -> tuple[str, str, list[str]]:
    errors: list[str] = []
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return "", "", ["SKILL.md must start with YAML frontmatter"]

    try:
        end = lines.index("---", 1)
    except ValueError:
        return "", "", ["SKILL.md frontmatter is not closed"]

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line or line.startswith((" ", "\t")):
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')

    name = values.get("name", "")
    description = values.get("description", "")
    if not name:
        errors.append("frontmatter is missing name")
    if not description:
        errors.append("frontmatter is missing description")
    if len(name) > 64:
        errors.append("name must be at most 64 characters")
    if name and not NAME_PATTERN.fullmatch(name):
        errors.append("name must contain lowercase letters, numbers, and hyphens")
    if len(description) > 1024:
        errors.append("description must be at most 1024 characters")
    return name, description, errors


def validate(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return [f"missing {skill_file}"]

    name, _, frontmatter_errors = frontmatter(skill_file)
    errors.extend(frontmatter_errors)
    if name and name != skill_dir.name:
        errors.append(f"frontmatter name {name!r} does not match folder {skill_dir.name!r}")

    for match in LINK_PATTERN.finditer(skill_file.read_text(encoding="utf-8")):
        target = match.group(1)
        if target.startswith(("http://", "https://", "#")):
            continue
        resolved = (skill_dir / target).resolve()
        if not resolved.exists():
            errors.append(f"missing SKILL.md reference: {target}")

    nested_skills = [
        path
        for path in skill_dir.rglob("SKILL.md")
        if path != skill_file
    ]
    errors.extend(f"nested SKILL.md is not allowed: {path.relative_to(skill_dir)}" for path in nested_skills)

    required_reference = skill_dir / "references" / "evidence-and-assumption-control.md"
    if not required_reference.is_file():
        errors.append(f"missing required reference: {required_reference.relative_to(skill_dir)}")
    return errors


def main() -> int:
    skill_dir = Path(__file__).resolve().parents[1]
    errors = validate(skill_dir)
    package_file = skill_dir.parents[1] / "package.json"
    if package_file.is_file():
        try:
            package = json.loads(package_file.read_text(encoding="utf-8"))
            if "skills" not in package.get("files", []):
                errors.append("package.json files must include 'skills'")
        except json.JSONDecodeError as error:
            errors.append(f"package.json is invalid: {error}")

    if errors:
        print("Skill package invalid:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Skill package valid: {skill_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
