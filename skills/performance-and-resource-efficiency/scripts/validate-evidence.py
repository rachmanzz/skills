#!/usr/bin/env python3
"""Validate a Markdown evidence ledger used to support agent claims."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VALID_STATUSES = {
    "VERIFIED",
    "VERIFIED_IN_SCOPE",
    "CONTRADICTED_IN_SCOPE",
    "PARTIAL",
    "NOT_FOUND_IN_SCOPE",
    "ABSENT",
    "UNKNOWN",
}
VERIFIED_STATUSES = {"VERIFIED", "VERIFIED_IN_SCOPE"}
EVIDENCE_REQUIRED_STATUSES = {
    "VERIFIED",
    "VERIFIED_IN_SCOPE",
    "CONTRADICTED_IN_SCOPE",
    "PARTIAL",
}
REQUIRED_COLUMNS = ("claim", "evidence", "status", "validation")
MAX_FILE_BYTES = 1024 * 1024


def _read_bounded_text(path: Path, label: str) -> str:
    """Read a regular UTF-8 file up to MAX_FILE_BYTES without following symlinks."""
    if path.is_symlink():
        raise ValueError(f"{label} must not be a symlink: {path}")
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise ValueError(f"{label} exceeds maximum size ({MAX_FILE_BYTES} bytes): {path}")
    return path.read_text(encoding="utf-8")
DEFINITIVE_TERMS = (
    "already implemented",
    "implemented",
    "fixed",
    "working",
    "works",
    "faster",
    "more efficient",
    "tested successfully",
    "cache exists",
    "cache is working",
    "supports redis",
    "verified",
    "resilient",
    "secure",
    "authorized",
    "isolated",
    "race-free",
    "atomic",
    "idempotent",
    "durable",
    "leak-free",
    "compatible",
    "acyclic",
    "dead-code-free",
    "observable",
    "monitored",
    "traced",
    "alerted",
    "audited",
    "accurate",
    "contract-compliant",
    "webhook-safe",
)
NEGATING_TERMS = (
    "not implemented",
    "not working",
    "does not work",
    "not verified",
    "not secure",
    "not authorized",
    "not isolated",
    "not atomic",
    "not idempotent",
    "not durable",
    "not safe",
    "not resilient",
    "not compatible",
    "not audited",
    "not observable",
    "not accurate",
    "non-atomic",
    "non-idempotent",
    "partially verified",
    "requires validation",
    "untested",
    "unknown",
    "absent",
    "unverified",
    "no evidence",
    "not yet",
    "proposed",
)


def split_row(line: str) -> list[str]:
    value = line.strip()
    if not value.startswith("|"):
        return []
    if value.endswith("|") and not value.endswith(r"\|"):
        inner = value[1:-1]
    else:
        inner = value[1:]
    if "|" not in value[1:]:
        return []
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for ch in inner:
        if escaped:
            current.append(ch)
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == "|":
            cells.append("".join(current).strip())
            current = []
            continue
        current.append(ch)
    if escaped:
        current.append("\\")
    cells.append("".join(current).strip())
    return cells


def is_separator(row: list[str]) -> bool:
    return bool(row) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in row)


def _contains_term(text: str, term: str) -> bool:
    return bool(re.search(rf"(?<![a-z0-9-]){re.escape(term)}(?![a-z0-9-])", text))


CONTRACTION_NEGATIONS = (
    "isn't",
    "aren't",
    "wasn't",
    "weren't",
    "doesn't",
    "don't",
    "didn't",
    "can't",
    "cannot",
    "won't",
    "hasn't",
    "haven't",
)
CLAUSE_SPLIT_PATTERN = re.compile(r"[;,.]+|\b(?:but|while|whereas|although|however)\b")


def is_definitive_claim(claim: str) -> bool:
    lowered = claim.lower()
    for clause in CLAUSE_SPLIT_PATTERN.split(lowered):
        clause = clause.strip()
        if not clause:
            continue
        if any(_contains_term(clause, term) for term in NEGATING_TERMS):
            continue
        if any(_contains_term(clause, neg) for neg in CONTRACTION_NEGATIONS):
            continue
        if any(_contains_term(clause, term) for term in DEFINITIVE_TERMS):
            return True
    return False


def _strip_fenced_blocks(lines: list[str]) -> list[tuple[int, str]]:
    """Return (1-based line_number, line) outside fenced code blocks."""
    result: list[tuple[int, str]] = []
    fence_char: str | None = None
    fence_len = 0
    for line_number, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if fence_char is None:
            match = re.match(r"^(`{3,}|~{3,})", stripped)
            if match:
                fence_char = match.group(1)[0]
                fence_len = len(match.group(1))
                continue
            result.append((line_number, line))
        else:
            if re.match(rf"^{re.escape(fence_char)}{{{fence_len},}}\s*$", stripped):
                fence_char = None
                fence_len = 0
    return result


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        raw_lines = _read_bounded_text(path, "evidence ledger").splitlines()
    except (OSError, UnicodeDecodeError, ValueError) as error:
        return [f"failed to read {path}: {error}"]

    visible_lines = _strip_fenced_blocks(raw_lines)
    found_tables = 0
    idx = 0

    while idx < len(visible_lines):
        header_line_num, line = visible_lines[idx]
        row = split_row(line)
        normalized = [cell.lower() for cell in row]
        if not row or not all(column in normalized for column in REQUIRED_COLUMNS):
            idx += 1
            continue

        found_tables += 1
        positions = {column: normalized.index(column) for column in REQUIRED_COLUMNS}
        if idx + 1 >= len(visible_lines):
            errors.append(f"line {header_line_num}: evidence table missing separator row")
            break

        sep_line_num, sep_line = visible_lines[idx + 1]
        sep_row = split_row(sep_line)
        if not is_separator(sep_row) or len(sep_row) != len(normalized):
            errors.append(f"line {sep_line_num}: evidence table missing valid separator row")
            idx += 1
            continue

        data_rows = 0
        idx += 2
        while idx < len(visible_lines):
            line_number, row_line = visible_lines[idx]
            data_row = split_row(row_line)
            if not data_row:
                break
            if is_separator(data_row):
                idx += 1
                continue
            data_rows += 1
            if len(data_row) < len(normalized):
                errors.append(f"line {line_number}: evidence row has too few columns")
                idx += 1
                continue
            if len(data_row) > len(normalized):
                errors.append(f"line {line_number}: evidence row has too many columns")
                idx += 1
                continue

            claim = data_row[positions["claim"]]
            evidence = data_row[positions["evidence"]]
            status = data_row[positions["status"]].upper()
            validation = data_row[positions["validation"]]

            if not claim:
                errors.append(f"line {line_number}: claim is empty")
            if not evidence:
                if status in EVIDENCE_REQUIRED_STATUSES:
                    errors.append(f"line {line_number}: evidence is empty ({status} requires evidence)")
                else:
                    errors.append(f"line {line_number}: evidence is empty")
            if status not in VALID_STATUSES:
                errors.append(
                    f"line {line_number}: status must be one of {sorted(VALID_STATUSES)}"
                )
            if not validation:
                errors.append(f"line {line_number}: validation is empty")
            if is_definitive_claim(claim) and status not in VERIFIED_STATUSES:
                errors.append(
                    f"line {line_number}: definitive claim requires VERIFIED status (or VERIFIED_IN_SCOPE)"
                )
            idx += 1

        if data_rows == 0:
            errors.append(f"line {header_line_num}: Evidence table contains no data rows.")

    if found_tables == 0:
        return ["No evidence table with Claim, Evidence, Status, and Validation columns found."]
    return errors


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] in {"-h", "--help"}:
        print(f"Usage: {Path(sys.argv[0]).name} path/to/evidence-ledger.md")
        return 0 if len(sys.argv) == 2 else 2

    path = Path(sys.argv[1])
    if path.is_symlink():
        print(f"error: symlink input is not allowed: {path}", file=sys.stderr)
        return 2
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    errors = validate(path)
    if errors:
        print("Evidence ledger invalid:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Evidence ledger valid: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
