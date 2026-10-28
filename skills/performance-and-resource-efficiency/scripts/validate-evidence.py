#!/usr/bin/env python3
"""Validate a Markdown evidence ledger used to support agent claims."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VALID_STATUSES = {"VERIFIED", "PARTIAL", "ABSENT", "UNKNOWN"}
REQUIRED_COLUMNS = ("claim", "evidence", "status", "validation")
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
)
NEGATING_TERMS = (
    "not implemented",
    "not working",
    "does not work",
    "unknown",
    "absent",
    "unverified",
    "no evidence",
    "not yet",
    "proposed",
)


def split_row(line: str) -> list[str]:
    value = line.strip()
    if not value.startswith("|") or "|" not in value[1:]:
        return []
    return [cell.strip() for cell in value.strip("|").split("|")]


def is_separator(row: list[str]) -> bool:
    return bool(row) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in row)


def is_definitive_claim(claim: str) -> bool:
    lowered = claim.lower()
    if any(term in lowered for term in NEGATING_TERMS):
        return False
    return any(term in lowered for term in DEFINITIVE_TERMS)


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    header_index = None
    header: list[str] = []

    for index, line in enumerate(lines):
        row = split_row(line)
        if not row:
            continue
        normalized = [cell.lower() for cell in row]
        if all(column in normalized for column in REQUIRED_COLUMNS):
            header_index = index
            header = normalized
            break

    if header_index is None:
        return ["No evidence table with Claim, Evidence, Status, and Validation columns found."]

    positions = {column: header.index(column) for column in REQUIRED_COLUMNS}
    data_rows = 0
    for line_number, line in enumerate(lines[header_index + 2 :], header_index + 3):
        row = split_row(line)
        if not row:
            if data_rows:
                break
            continue
        if is_separator(row):
            continue
        data_rows += 1
        if len(row) < len(header):
            errors.append(f"line {line_number}: evidence row has too few columns")
            continue

        claim = row[positions["claim"]]
        evidence = row[positions["evidence"]]
        status = row[positions["status"]].upper()
        validation = row[positions["validation"]]

        if not claim:
            errors.append(f"line {line_number}: claim is empty")
        if not evidence:
            errors.append(f"line {line_number}: evidence is empty")
        if status not in VALID_STATUSES:
            errors.append(
                f"line {line_number}: status must be one of {sorted(VALID_STATUSES)}"
            )
        if not validation:
            errors.append(f"line {line_number}: validation is empty")
        if status in {"VERIFIED", "PARTIAL"} and not evidence:
            errors.append(f"line {line_number}: {status} requires evidence")
        if is_definitive_claim(claim) and status != "VERIFIED":
            errors.append(
                f"line {line_number}: definitive claim requires VERIFIED status"
            )

    if data_rows == 0:
        errors.append("Evidence table contains no data rows.")
    return errors


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] in {"-h", "--help"}:
        print(f"Usage: {Path(sys.argv[0]).name} path/to/evidence-ledger.md")
        return 0 if len(sys.argv) == 2 else 2

    path = Path(sys.argv[1])
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
