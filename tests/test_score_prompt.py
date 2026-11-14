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
                "```markdown\nconfidence_threshold: 0.50\n```\nconfidence_threshold: 90%\n",
                encoding="utf-8",
            )
            threshold, _ = score_prompt.load_threshold_from_configs([gemini_md])
            self.assertEqual(threshold, 0.90)

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
        result = score_prompt.evaluate("   ", 0.50, "cli:--threshold")
        self.assertEqual(result["status"], "CLARIFY")
        self.assertEqual(result["top_intent"]["confidence"], 0.0)

        with_candidates = score_prompt.evaluate(
            "   ",
            0.50,
            "cli:--threshold",
            [{"id": "a", "label": "Only option", "specificity": 1.0, "target_clarity": 1.0, "constraint_completeness": 1.0}],
        )
        self.assertEqual(with_candidates["status"], "CLARIFY")
        self.assertEqual(with_candidates["top_intent"]["confidence"], 0.0)

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

    def test_rejects_nan_and_out_of_range_candidate_attributes(self) -> None:
        with self.assertRaises(ValueError):
            score_prompt.score_candidates([{"id": "bad", "specificity": float("nan")}])
        with self.assertRaises(ValueError):
            score_prompt.score_candidates([{"id": "bad", "ambiguity_penalty": -0.2}])
        with self.assertRaises(ValueError):
            score_prompt.score_candidates(["not-a-dict"])  # type: ignore[list-item]

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

        for bad_args in (
            ["--threshold", "abc", "--prompt", "test"],
            ["--threshold", "85%%", "--prompt", "test"],
            ["--threshold", "-0.1", "--prompt", "test"],
            ["--threshold", "150", "--prompt", "test"],
            ["--threshold", "0.8", "--candidates", "{bad json"],
            ["--threshold", "0.8", "--candidates", '{"a": 1}'],
        ):
            code, payload = self.run_cli(bad_args)
            self.assertEqual(code, 1)
            self.assertEqual(payload["status"], "ERROR")
            self.assertTrue(payload["error"])


if __name__ == "__main__":
    unittest.main()
