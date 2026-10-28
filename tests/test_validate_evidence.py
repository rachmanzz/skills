"""Unit tests for scripts/validate-evidence.py."""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

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


validate_evidence = load_script("validate_evidence", "validate-evidence.py")


class LedgerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def ledger(self, content: str) -> Path:
        path = self.root / "ledger.md"
        path.write_text(content, encoding="utf-8")
        return path


class SplitRowTests(unittest.TestCase):
    def test_table_row_splits_and_strips_cells(self) -> None:
        self.assertEqual(validate_evidence.split_row("| A | B |"), ["A", "B"])

    def test_plain_line_returns_no_cells(self) -> None:
        self.assertEqual(validate_evidence.split_row("plain text"), [])

    def test_line_with_single_pipe_returns_no_cells(self) -> None:
        self.assertEqual(validate_evidence.split_row("|only-start"), [])


class SeparatorTests(unittest.TestCase):
    def test_dashes_are_separator(self) -> None:
        self.assertTrue(validate_evidence.is_separator(["---", "---"]))

    def test_alignment_colons_are_separator(self) -> None:
        self.assertTrue(validate_evidence.is_separator([":---", "---:", ":---"]))

    def test_content_cell_is_not_separator(self) -> None:
        self.assertFalse(validate_evidence.is_separator(["Claim", "---"]))

    def test_empty_row_is_not_separator(self) -> None:
        self.assertFalse(validate_evidence.is_separator([]))


class DefinitiveClaimTests(unittest.TestCase):
    def test_definitive_terms_are_definitive(self) -> None:
        for claim in (
            "The cache exists",
            "The fix works",
            "Already implemented",
            "The path is faster",
            "Tested successfully",
        ):
            with self.subTest(claim=claim):
                self.assertTrue(validate_evidence.is_definitive_claim(claim))

    def test_negating_terms_block_definitive(self) -> None:
        for claim in (
            "Not implemented",
            "Not working",
            "Unknown latency",
            "Proposed design",
            "Not yet implemented",
        ):
            with self.subTest(claim=claim):
                self.assertFalse(validate_evidence.is_definitive_claim(claim))

    def test_plain_claim_is_not_definitive(self) -> None:
        self.assertFalse(validate_evidence.is_definitive_claim("Latency was measured"))


class ValidateTests(LedgerTestCase):
    def test_valid_ledger_has_no_errors(self) -> None:
        path = self.ledger(
            "| Claim | Evidence | Status | Validation |\n"
            "| --- | --- | --- | --- |\n"
            "| Latency measured at 40ms | benchmark output | VERIFIED | rerun benchmark |\n"
            "| Fallback path inspected | code inspection | PARTIAL | add outage test |\n"
        )
        self.assertEqual(validate_evidence.validate(path), [])

    def test_column_order_is_flexible(self) -> None:
        path = self.ledger(
            "| Status | Claim | Validation | Evidence |\n"
            "| --- | --- | --- | --- |\n"
            "| VERIFIED | Cache configured | rerun | configuration file |\n"
        )
        self.assertEqual(validate_evidence.validate(path), [])

    def test_missing_table_is_reported(self) -> None:
        path = self.ledger("Only narrative text, no table at all.\n")
        errors = validate_evidence.validate(path)
        self.assertEqual(len(errors), 1)
        self.assertIn("No evidence table", errors[0])

    def test_empty_claim_is_reported(self) -> None:
        path = self.ledger(
            "| Claim | Evidence | Status | Validation |\n"
            "| --- | --- | --- | --- |\n"
            "|  | profile output | UNKNOWN | rerun |\n"
        )
        errors = validate_evidence.validate(path)
        self.assertTrue(any("claim is empty" in e for e in errors))

    def test_invalid_status_is_reported(self) -> None:
        path = self.ledger(
            "| Claim | Evidence | Status | Validation |\n"
            "| --- | --- | --- | --- |\n"
            "| Latency measured | profile output | MAYBE | rerun |\n"
        )
        errors = validate_evidence.validate(path)
        self.assertTrue(any("status must be one of" in e for e in errors))

    def test_definitive_claim_requires_verified_status(self) -> None:
        path = self.ledger(
            "| Claim | Evidence | Status | Validation |\n"
            "| --- | --- | --- | --- |\n"
            "| Cache exists | code inspection | UNKNOWN | check code |\n"
        )
        errors = validate_evidence.validate(path)
        self.assertTrue(
            any("definitive claim requires VERIFIED status" in e for e in errors)
        )

    def test_verified_requires_evidence(self) -> None:
        path = self.ledger(
            "| Claim | Evidence | Status | Validation |\n"
            "| --- | --- | --- | --- |\n"
            "| Latency measured |  | VERIFIED | rerun |\n"
        )
        errors = validate_evidence.validate(path)
        self.assertTrue(any("evidence is empty" in e for e in errors))
        self.assertTrue(any("VERIFIED requires evidence" in e for e in errors))

    def test_row_with_too_few_columns_is_reported(self) -> None:
        path = self.ledger(
            "| Claim | Evidence | Status | Validation |\n"
            "| --- | --- | --- | --- |\n"
            "| Cache inspected | code only | UNKNOWN |\n"
        )
        errors = validate_evidence.validate(path)
        self.assertTrue(any("too few columns" in e for e in errors))

    def test_table_without_data_rows_is_reported(self) -> None:
        path = self.ledger(
            "| Claim | Evidence | Status | Validation |\n"
            "| --- | --- | --- | --- |\n"
        )
        errors = validate_evidence.validate(path)
        self.assertTrue(any("no data rows" in e for e in errors))

    def test_negated_definitive_claim_is_allowed_as_unknown(self) -> None:
        path = self.ledger(
            "| Claim | Evidence | Status | Validation |\n"
            "| --- | --- | --- | --- |\n"
            "| Cache not implemented | search found no cache | UNKNOWN | inspect again |\n"
        )
        self.assertEqual(validate_evidence.validate(path), [])


if __name__ == "__main__":
    unittest.main()
