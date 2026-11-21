"""Unit tests for scripts/validate-evidence.py."""

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
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

    def test_escaped_pipe_does_not_split_cell(self) -> None:
        self.assertEqual(validate_evidence.split_row(r"| A \| B | C |"), ["A | B", "C"])

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

    def test_mixed_clause_negation_does_not_hide_definitive_claim(self) -> None:
        self.assertTrue(
            validate_evidence.is_definitive_claim("Cache is working; TLS status unknown")
        )
        self.assertFalse(
            validate_evidence.is_definitive_claim("The cache isn't working")
        )

    def test_plain_claim_is_not_definitive(self) -> None:
        self.assertFalse(validate_evidence.is_definitive_claim("Latency was measured"))

    def test_audit_overclaim_terms_are_definitive_unless_negated(self) -> None:
        for claim in (
            "Endpoint is secure",
            "Transfer is atomic",
            "Handler is resilient",
            "Queries are isolated",
            "Schema is compatible",
        ):
            with self.subTest(claim=claim):
                self.assertTrue(validate_evidence.is_definitive_claim(claim))

        for negated in (
            "Endpoint is not secure",
            "Transfer is non-atomic",
            "Handler is partially verified",
            "Queries are untested",
            "Schema requires validation",
        ):
            with self.subTest(claim=negated):
                self.assertFalse(validate_evidence.is_definitive_claim(negated))


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
        self.assertEqual(len(errors), 1)
        self.assertIn("VERIFIED requires evidence", errors[0])
        self.assertIn("evidence is empty", errors[0])

    def test_row_with_too_few_or_too_many_columns_is_reported(self) -> None:
        path = self.ledger(
            "| Claim | Evidence | Status | Validation |\n"
            "| --- | --- | --- | --- |\n"
            "| Cache inspected | code only | UNKNOWN |\n"
            "| Extra col | code only | UNKNOWN | check | extra |\n"
        )
        errors = validate_evidence.validate(path)
        self.assertEqual(len(errors), 2)
        self.assertIn("too few columns", errors[0])
        self.assertIn("too many columns", errors[1])

    def test_missing_separator_row_and_fenced_table_and_multi_table(self) -> None:
        no_sep = self.ledger(
            "| Claim | Evidence | Status | Validation |\n"
            "| Cache inspected | code only | UNKNOWN | check |\n"
        )
        errors = validate_evidence.validate(no_sep)
        self.assertTrue(any("missing valid separator row" in e for e in errors))

        fenced_and_second = self.ledger(
            "```markdown\n"
            "| Claim | Evidence | Status | Validation |\n"
            "| --- | --- | --- | --- |\n"
            "| Cache is working | | UNKNOWN | |\n"
            "```\n\n"
            "| Claim | Evidence | Status | Validation |\n"
            "| --- | --- | --- | --- |\n"
            "| Cache inspected | code only | ABSENT | grep cache |\n\n"
            "| Claim | Evidence | Status | Validation |\n"
            "| --- | --- | --- | --- |\n"
            "| Auth works | none | UNKNOWN | test auth |\n"
        )
        errors = validate_evidence.validate(fenced_and_second)
        self.assertEqual(len(errors), 1)
        self.assertIn("definitive claim requires VERIFIED status", errors[0])

    def test_absent_and_empty_validation_and_mixed_case_status(self) -> None:
        path = self.ledger(
            "| claim | evidence | status | validation |\n"
            "| --- | --- | --- | --- |\n"
            "| Cache inspected | searched dir | absent |  |\n"
            "| Cache fallback |  | partial | add test |\n"
        )
        errors = validate_evidence.validate(path)
        self.assertEqual(len(errors), 2)
        self.assertIn("validation is empty", errors[0])
        self.assertIn("PARTIAL requires evidence", errors[1])

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

    def test_scoped_statuses_are_accepted(self) -> None:
        path = self.ledger(
            "| Claim | Evidence | Status | Validation |\n"
            "| --- | --- | --- | --- |\n"
            "| Retry limit is implemented in client.go | client.go:42 and fault test passed | VERIFIED_IN_SCOPE | rerun fault test |\n"
            "| Fallback preserves auth | handler.py:18 skips auth check on fallback | CONTRADICTED_IN_SCOPE | add auth guard test |\n"
            "| Circuit breaker in billing client | searched billing/ directory | NOT_FOUND_IN_SCOPE | inspect billing/ |\n"
        )
        self.assertEqual(validate_evidence.validate(path), [])

    def test_scoped_verified_and_contradicted_require_evidence(self) -> None:
        path = self.ledger(
            "| Claim | Evidence | Status | Validation |\n"
            "| --- | --- | --- | --- |\n"
            "| Timeout set |  | VERIFIED_IN_SCOPE | run timeout test |\n"
            "| Retry bounded |  | CONTRADICTED_IN_SCOPE | inspect retry loop |\n"
        )
        errors = validate_evidence.validate(path)
        self.assertEqual(len(errors), 2)
        self.assertIn("VERIFIED_IN_SCOPE requires evidence", errors[0])
        self.assertIn("CONTRADICTED_IN_SCOPE requires evidence", errors[1])

    def test_validate_rejects_symlink_and_oversized_ledger(self) -> None:
        real_path = self.ledger(
            "| Claim | Evidence | Status | Validation |\n"
            "| --- | --- | --- | --- |\n"
            "| Latency measured | benchmark output | VERIFIED | rerun |\n"
        )
        sym_path = self.root / "sym-ledger.md"
        try:
            sym_path.symlink_to(real_path)
        except OSError:
            self.skipTest("symlinks not supported on filesystem")

        sym_errors = validate_evidence.validate(sym_path)
        self.assertEqual(len(sym_errors), 1)
        self.assertIn("must not be a symlink", sym_errors[0])

        with mock.patch.object(validate_evidence, "MAX_FILE_BYTES", 32):
            size_errors = validate_evidence.validate(real_path)
        self.assertEqual(len(size_errors), 1)
        self.assertIn("exceeds maximum size", size_errors[0])


class MainCliTests(LedgerTestCase):
    def test_main_help_missing_file_valid_and_invalid(self) -> None:
        buf = io.StringIO()
        with mock.patch.object(sys, "argv", ["validate-evidence.py", "--help"]):
            with redirect_stdout(buf):
                self.assertEqual(validate_evidence.main(), 0)
        self.assertIn("Usage:", buf.getvalue())

        with mock.patch.object(sys, "argv", ["validate-evidence.py"]):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(validate_evidence.main(), 2)

        err_buf = io.StringIO()
        with mock.patch.object(sys, "argv", ["validate-evidence.py", str(self.root / "missing.md")]):
            with mock.patch.object(sys, "stderr", err_buf):
                self.assertEqual(validate_evidence.main(), 2)
        self.assertIn("file not found", err_buf.getvalue())

        valid_path = self.ledger(
            "| Claim | Evidence | Status | Validation |\n"
            "| --- | --- | --- | --- |\n"
            "| Latency measured | benchmark output | VERIFIED_IN_SCOPE | rerun |\n"
        )
        buf = io.StringIO()
        with mock.patch.object(sys, "argv", ["validate-evidence.py", str(valid_path)]):
            with redirect_stdout(buf):
                self.assertEqual(validate_evidence.main(), 0)
        self.assertIn("Evidence ledger valid:", buf.getvalue())

        invalid_path = self.ledger("No table\n")
        buf = io.StringIO()
        with mock.patch.object(sys, "argv", ["validate-evidence.py", str(invalid_path)]):
            with redirect_stdout(buf):
                self.assertEqual(validate_evidence.main(), 1)
        self.assertIn("Evidence ledger invalid:", buf.getvalue())

        sym_path = self.root / "sym-main.md"
        try:
            sym_path.symlink_to(valid_path)
        except OSError:
            self.skipTest("symlinks not supported on filesystem")
        sym_err = io.StringIO()
        with mock.patch.object(sys, "argv", ["validate-evidence.py", str(sym_path)]):
            with mock.patch.object(sys, "stderr", sym_err):
                self.assertEqual(validate_evidence.main(), 2)
        self.assertIn("symlink input is not allowed", sym_err.getvalue())


if __name__ == "__main__":
    unittest.main()
