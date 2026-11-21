#!/usr/bin/env python3
"""Validate an installable skill package without dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\]\(([^)]+)\)")
INLINE_CODE_PATTERN = re.compile(r"`[^`\n]+`")
MAX_FILE_BYTES = 1024 * 1024


def _read_bounded_text(path: Path, label: str) -> str:
    """Read a regular UTF-8 file up to MAX_FILE_BYTES without following symlinks."""
    if path.is_symlink():
        raise ValueError(f"{label} must not be a symlink: {path}")
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise ValueError(f"{label} exceeds maximum size ({MAX_FILE_BYTES} bytes): {path}")
    return path.read_text(encoding="utf-8")


def _strip_code_segments(text: str) -> str:
    """Remove fenced code blocks and inline code spans before scanning links."""
    out_lines: list[str] = []
    fence_char: str | None = None
    fence_len = 0
    for line in text.splitlines():
        stripped = line.lstrip()
        if fence_char is None:
            match = re.match(r"^(`{3,}|~{3,})", stripped)
            if match:
                fence_char = match.group(1)[0]
                fence_len = len(match.group(1))
                continue
            out_lines.append(INLINE_CODE_PATTERN.sub("", line))
        else:
            close_match = re.match(rf"^({re.escape(fence_char)}{{{fence_len},}})\s*$", stripped)
            if close_match:
                fence_char = None
                fence_len = 0
    return "\n".join(out_lines)


def _extract_local_target(raw_target: str) -> str | None:
    """Return local relative path from a Markdown link target, or None if external/anchor-only."""
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")].strip()
    else:
        # Strip optional link title (e.g., `path.md "title"`).
        target = re.split(r"\s+", target, maxsplit=1)[0]
    if not target or target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    path_only = target.split("#", 1)[0].split("?", 1)[0].strip()
    return path_only or None


def _parse_frontmatter_fields(fm_lines: list[str]) -> dict[str, str]:
    """Parse top-level scalar and block-scalar YAML frontmatter keys."""
    values: dict[str, str] = {}
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        if not line.strip() or line.lstrip().startswith("#") or line.startswith((" ", "\t")):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, raw_val = line.split(":", 1)
        key = key.strip()
        val = raw_val.strip()
        if val in {"|", ">", "|-", ">-"}:
            block_lines: list[str] = []
            i += 1
            while i < len(fm_lines):
                nxt = fm_lines[i]
                if nxt.strip() and not nxt.startswith((" ", "\t")):
                    break
                block_lines.append(nxt.strip())
                i += 1
            joiner = "\n" if val.startswith("|") else " "
            values[key] = joiner.join(part for part in block_lines if part).strip()
            continue
        if (val.startswith('"') and val.endswith('"') and len(val) >= 2) or (
            val.startswith("'") and val.endswith("'") and len(val) >= 2
        ):
            val = val[1:-1]
        values[key] = val
        i += 1
    return values


def frontmatter(skill_file: Path) -> tuple[str, str, list[str]]:
    errors: list[str] = []
    try:
        lines = _read_bounded_text(skill_file, "SKILL.md").splitlines()
    except (OSError, UnicodeDecodeError, ValueError) as error:
        return "", "", [f"failed to read {skill_file}: {error}"]

    if not lines or lines[0].strip() != "---":
        return "", "", ["SKILL.md must start with YAML frontmatter"]

    end = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end = idx
            break
    if end is None:
        return "", "", ["SKILL.md frontmatter is not closed"]

    values = _parse_frontmatter_fields(lines[1:end])
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


def _validate_links(
    doc_path: Path,
    skill_dir_resolved: Path,
    base_dir: Path,
    label: str,
    errors: list[str],
) -> None:
    try:
        text = _read_bounded_text(doc_path, label)
    except (OSError, UnicodeDecodeError, ValueError) as error:
        errors.append(f"failed to read {label}: {error}")
        return

    for match in LINK_PATTERN.finditer(_strip_code_segments(text)):
        target = _extract_local_target(match.group(1))
        if target is None:
            continue
        candidate = base_dir / target
        if candidate.is_symlink():
            errors.append(f"symlink link is not allowed in {label}: {target}")
            continue
        resolved = candidate.resolve()
        if not resolved.is_relative_to(skill_dir_resolved):
            errors.append(f"link escapes skill directory in {label}: {target}")
            continue
        if not resolved.exists():
            errors.append(f"missing {label} reference: {target}")


def validate(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    if skill_dir.is_symlink():
        return [f"symlink skill directory is not allowed: {skill_dir}"]

    skill_dir_resolved = skill_dir.resolve()
    skill_file = skill_dir / "SKILL.md"
    if skill_file.is_symlink() or not skill_file.is_file():
        return [f"missing {skill_file}"]

    name, _, frontmatter_errors = frontmatter(skill_file)
    errors.extend(frontmatter_errors)
    if name and name != skill_dir.name:
        errors.append(f"frontmatter name {name!r} does not match folder {skill_dir.name!r}")

    _validate_links(skill_file, skill_dir_resolved, skill_dir, "SKILL.md", errors)

    references_dir = skill_dir / "references"
    if references_dir.is_symlink():
        errors.append("symlink references directory is not allowed")
    elif references_dir.is_dir():
        for ref_file in sorted(references_dir.rglob("*.md")):
            rel_ref = ref_file.relative_to(skill_dir)
            if ref_file.is_symlink():
                errors.append(f"symlink reference file is not allowed: {rel_ref}")
                continue
            _validate_links(ref_file, skill_dir_resolved, ref_file.parent, f"reference link in {rel_ref}", errors)

    nested_skills = [
        path
        for path in skill_dir.rglob("SKILL.md")
        if path != skill_file
    ]
    errors.extend(f"nested SKILL.md is not allowed: {path.relative_to(skill_dir)}" for path in nested_skills)

    required_reference = skill_dir / "references" / "evidence-and-assumption-control.md"
    if required_reference.is_symlink() or not required_reference.is_file():
        errors.append(f"missing required reference: {required_reference.relative_to(skill_dir)}")
    return errors


def main() -> int:
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] in {"-h", "--help"}):
        stream = sys.stdout if len(sys.argv) == 2 and sys.argv[1] in {"-h", "--help"} else sys.stderr
        print(f"Usage: {Path(sys.argv[0]).name} [path/to/skill-dir]", file=stream)
        return 0 if len(sys.argv) == 2 else 2

    skill_dir = (
        Path(sys.argv[1])
        if len(sys.argv) == 2
        else Path(__file__).resolve().parents[1]
    )
    if not skill_dir.is_symlink():
        skill_dir = skill_dir.resolve()
    errors = validate(skill_dir)

    if len(skill_dir.parents) >= 2 and skill_dir.parent.name == "skills":
        package_file = skill_dir.parents[1] / "package.json"
        if package_file.is_symlink():
            errors.append("package.json must not be a symlink")
        elif package_file.is_file():
            try:
                package = json.loads(_read_bounded_text(package_file, "package.json"))
                if not isinstance(package, dict):
                    errors.append("package.json must be a JSON object")
                else:
                    files = package.get("files", [])
                    if not isinstance(files, list) or "skills" not in files:
                        errors.append("package.json files must include 'skills'")
            except (json.JSONDecodeError, OSError, UnicodeDecodeError, ValueError) as error:
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
