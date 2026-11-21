"""Unit tests for skills/prompt-confidence-gate/scripts/score_prompt.py."""

import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "prompt-confidence-gate"
    / "scripts"
    / "score_prompt.py"
)

spec = importlib.util.spec_from_file_location("score_prompt", SCRIPT_PATH)
score_prompt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score_prompt)


class ScorePromptTests(unittest.TestCase):
    def run_cli(self, argv: list[str]) -> tuple[int, dict]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = score_prompt.main(argv)
        return code, json.loads(buf.getvalue())

    def test_missing_threshold_requires_user_input(self) -> None:
        result = score_prompt.evaluate("Refactor app/main.go", None, None)
        self.assertEqual(result["status"], "THRESHOLD_REQUIRED")
        self.assertIsNone(result["threshold"])

    def test_reads_decimal_threshold_from_agents_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents_md = Path(tmp) / "AGENTS.md"
            agents_md.write_text("# Rules\nconfidence_threshold: 0.85\n", encoding="utf-8")
            threshold, source = score_prompt.load_threshold_from_configs([agents_md])
            self.assertEqual(threshold, 0.85)
            self.assertEqual(source, str(agents_md))

    def test_ignores_fenced_code_block_examples_in_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gemini_md = Path(tmp) / "GEMINI.md"
            gemini_md.write_text(
                "````markdown\n```text\nconfidence_threshold: 0.50\n```\n````\n"
                "~~~\nconfidence_threshold: 0.40\n~~~\n"
                "- `confidence_threshold`: 90%\n",
                encoding="utf-8",
            )
            threshold, _ = score_prompt.load_threshold_from_configs([gemini_md])
            self.assertEqual(threshold, 0.90)

            bad_md = Path(tmp) / "BAD.md"
            bad_md.write_text("confidence_threshold: invalid_text\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                score_prompt.load_threshold_from_configs([bad_md])

            first_md = Path(tmp) / "AGENTS.md"
            first_md.write_text("confidence_threshold: 85\n", encoding="utf-8")
            threshold, source = score_prompt.load_threshold_from_configs([first_md, gemini_md])
            self.assertEqual(threshold, 0.85)
            self.assertEqual(source, str(first_md))

    def test_reads_percent_threshold_from_gemini_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gemini_md = Path(tmp) / "GEMINI.md"
            gemini_md.write_text("confidence_threshold = 80%\n", encoding="utf-8")
            threshold, source = score_prompt.load_threshold_from_configs(
                [Path(tmp) / "AGENTS.md", gemini_md]
            )
            self.assertEqual(threshold, 0.80)
            self.assertEqual(source, str(gemini_md))

    def test_clear_specific_prompt_passes_execute_gate(self) -> None:
        prompt = (
            "Create `skills/prompt-confidence-gate/SKILL.md` and run "
            "python3 tests/test_score_prompt.py to validate."
        )
        result = score_prompt.evaluate(prompt, 0.70, "cli:--threshold")
        self.assertEqual(result["status"], "EXECUTE")
        self.assertGreaterEqual(result["top_intent"]["confidence"], 0.70)

    def test_empty_prompt_with_threshold_triggers_clarify(self) -> None:
        for thresh in (0.0, 0.50):
            result = score_prompt.evaluate("   ", thresh, "cli:--threshold")
            self.assertEqual(result["status"], "CLARIFY")
            self.assertEqual(result["top_intent"]["confidence"], 0.0)

        with_candidates = score_prompt.evaluate(
            "   ",
            0.0,
            "cli:--threshold",
            [{"id": "a", "label": "Only option", "specificity": 1.0, "target_clarity": 1.0, "constraint_completeness": 1.0}],
        )
        self.assertEqual(with_candidates["status"], "CLARIFY")
        self.assertEqual(with_candidates["top_intent"]["confidence"], 0.0)

    def test_multi_intent_and_non_ascii_prompts(self) -> None:
        multi = score_prompt.score_raw_prompt("Add tests or refactor helper?")
        self.assertEqual(multi["signals"]["multi_intent_markers"], 2)
        non_ascii = score_prompt.score_raw_prompt("Perbaiki modul ini")
        self.assertEqual(non_ascii["signals"]["word_count"], 3)

    def test_ambiguous_vague_prompt_triggers_clarify(self) -> None:
        prompt = "maybe fix it."
        result = score_prompt.evaluate(prompt, 0.75, "cli:--threshold")
        self.assertEqual(result["status"], "CLARIFY")
        self.assertEqual(result["top_intent"]["signals"]["vague_tokens"], 3)
        self.assertLess(result["top_intent"]["confidence"], 0.75)

    def test_competing_candidates_with_close_tie_triggers_clarify(self) -> None:
        candidates = [
            {
                "id": "opt_a",
                "label": "Delete unused helper",
                "specificity": 0.8,
                "target_clarity": 0.8,
                "constraint_completeness": 0.7,
                "ambiguity_penalty": 0.0,
            },
            {
                "id": "opt_b",
                "label": "Refactor helper into shared module",
                "specificity": 0.8,
                "target_clarity": 0.8,
                "constraint_completeness": 0.7,
                "ambiguity_penalty": 0.0,
            },
        ]
        result = score_prompt.evaluate("handle helper", 0.50, "cli:--threshold", candidates)
        self.assertEqual(result["status"], "CLARIFY")
        self.assertTrue(result["has_close_tie"])

    def test_dominant_candidate_executes_at_high_threshold(self) -> None:
        candidates = [
            {
                "id": "primary",
                "label": "Run unit tests in tests/test_score_prompt.py",
                "specificity": 1.0,
                "target_clarity": 1.0,
                "constraint_completeness": 1.0,
                "ambiguity_penalty": 0.0,
            },
            {
                "id": "secondary",
                "label": "Unrelated guess",
                "specificity": 0.05,
                "target_clarity": 0.05,
                "constraint_completeness": 0.0,
                "ambiguity_penalty": 0.0,
            },
        ]
        result = score_prompt.evaluate("run tests", 0.85, "cli:--threshold", candidates)
        self.assertEqual(result["status"], "EXECUTE")
        self.assertGreaterEqual(result["top_intent"]["confidence"], 0.85)

    def test_weak_decoy_never_inflates_and_tie_margin_boundary(self) -> None:
        alone = score_prompt.score_candidates(
            [{"id": "a", "label": "Only", "specificity": 0.5, "target_clarity": 0.5, "constraint_completeness": 0.5}]
        )
        with_decoy = score_prompt.score_candidates(
            [
                {"id": "a", "label": "Main", "specificity": 0.5, "target_clarity": 0.5, "constraint_completeness": 0.5},
                {"id": "b", "label": "Decoy", "specificity": 0.0, "target_clarity": 0.0, "constraint_completeness": 0.0, "ambiguity_penalty": 1.0},
            ]
        )
        self.assertEqual(alone[0]["confidence"], 0.5)
        self.assertLessEqual(with_decoy[0]["confidence"], alone[0]["confidence"])

        tied_at_margin = score_prompt.evaluate(
            "run check",
            0.20,
            "cli:--threshold",
            [
                {"id": "a", "label": "A", "specificity": 0.6, "target_clarity": 0.6, "constraint_completeness": 0.6},
                {"id": "b", "label": "B", "specificity": 0.55, "target_clarity": 0.55, "constraint_completeness": 0.55},
            ],
        )
        self.assertTrue(tied_at_margin["has_close_tie"])
        self.assertEqual(tied_at_margin["status"], "CLARIFY")

    def test_rejects_nan_bool_null_and_out_of_range_candidate_attributes(self) -> None:
        with self.assertRaises(ValueError):
            score_prompt.score_candidates([{"id": "bad", "specificity": float("nan")}])
        with self.assertRaises(ValueError):
            score_prompt.score_candidates([{"id": "bad", "specificity": True}])
        with self.assertRaises(ValueError):
            score_prompt.score_candidates([{"id": "bad", "specificity": 1.1}])
        with self.assertRaises(ValueError):
            score_prompt.score_candidates([{"id": None}])
        with self.assertRaises(ValueError):
            score_prompt.score_candidates([])
        with self.assertRaises(ValueError):
            score_prompt.score_candidates([{"id": "bad", "ambiguity_penalty": -0.2}])
        with self.assertRaises(ValueError):
            score_prompt.score_candidates(["not-a-dict"])  # type: ignore[list-item]
        with self.assertRaises(ValueError):
            score_prompt.evaluate("run", None, None, [])

    def test_cli_outputs_valid_json_and_handles_errors_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gemini_md = Path(tmp) / "GEMINI.md"
            gemini_md.write_text("confidence_threshold: 75%\n", encoding="utf-8")
            code, payload = self.run_cli(
                [
                    "--config",
                    str(gemini_md),
                    "--prompt",
                    "Add unit tests in `tests/test_score_prompt.py` and run them",
                ]
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload["status"], "EXECUTE")
            self.assertEqual(payload["threshold"], 0.75)

            cand_file = Path(tmp) / "candidates.json"
            cand_file.write_text(
                json.dumps([{"id": "a", "label": "Only option", "specificity": 0.9, "target_clarity": 0.9, "constraint_completeness": 0.9}]),
                encoding="utf-8",
            )
            code, payload = self.run_cli(
                ["--threshold", "0.8", "--prompt", "do task", "--candidates-file", str(cand_file)]
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload["status"], "EXECUTE")

            code, payload = self.run_cli(["--prompt", "do task"])
            self.assertEqual(code, 0)
            self.assertEqual(payload["status"], "THRESHOLD_REQUIRED")

            code, payload = self.run_cli(
                ["--config", str(gemini_md), "--threshold", "0.99", "--prompt", "do task"]
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload["threshold"], 0.99)
            self.assertEqual(payload["threshold_source"], "cli:--threshold")

            empty_cand = Path(tmp) / "empty.json"
            empty_cand.write_text("[]", encoding="utf-8")
            code, payload = self.run_cli(
                ["--threshold", "0.8", "--prompt", "do task", "--candidates-file", str(empty_cand)]
            )
            self.assertEqual(code, 1)
            self.assertEqual(payload["status"], "ERROR")

            code, payload = self.run_cli(
                ["--threshold", "0.8", "--prompt", "do task", "--candidates-file", str(Path(tmp) / "missing.json")]
            )
            self.assertEqual(code, 1)
            self.assertEqual(payload["status"], "ERROR")

        for bad_args in (
            ["--threshold", "", "--prompt", "test"],
            ["--threshold", "abc", "--prompt", "test"],
            ["--threshold", "85%%", "--prompt", "test"],
            ["--threshold", "-0.1", "--prompt", "test"],
            ["--threshold", "150", "--prompt", "test"],
            ["--threshold", "0.8", "--candidates", "{bad json"],
            ["--threshold", "0.8", "--candidates", '{"a": 1}'],
            ["--threshold", "0.8", "--candidates", "[]"],
        ):
            code, payload = self.run_cli(bad_args)
            self.assertEqual(code, 1)
            self.assertEqual(payload["status"], "ERROR")
            self.assertIn("status", payload)
            self.assertTrue(payload["error"])


if __name__ == "__main__":
    unittest.main()
