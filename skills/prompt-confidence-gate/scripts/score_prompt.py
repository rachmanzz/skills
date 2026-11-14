#!/usr/bin/env python3
"""Deterministic per-turn prompt confidence scorer and execution gate."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

FENCED_BLOCK_PATTERN = re.compile(r"(```[\s\S]*?```|~~~[\s\S]*?~~~)")
THRESHOLD_PATTERN = re.compile(
    r"^\s*(?:[-*]\s*)?`?confidence_threshold`?\s*[:=]\s*([+-]?[0-9]+(?:\.[0-9]+)?)\s*(%?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)

VAGUE_TOKENS = {
    "it",
    "this",
    "that",
    "they",
    "them",
    "something",
    "anything",
    "stuff",
    "things",
    "somehow",
    "maybe",
    "perhaps",
    "etc",
    "better",
    "improve",
    "fix",
    "update",
    "change",
}

SPECIFIC_MARKERS = re.compile(
    r"(/[\w.\-/]+|\b[\w]+\.(?:py|ts|tsx|js|jsx|go|rs|java|md|yaml|yml|json|sql)\b|`[^`]+`|\b(?:add|create|delete|remove|rename|refactor|test|validate|run)\b)",
    re.IGNORECASE,
)

MULTI_INTENT_MARKERS = re.compile(
    r"\b(?:or|either|alternatively|versus|vs\.?)\b|\?",
    re.IGNORECASE,
)

TIE_MARGIN = 0.05


def validate_unit_float(value: Any, field_name: str) -> float:
    """Validate that a value is a finite number in [0.0, 1.0]."""
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a numeric value in [0.0, 1.0]")
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a numeric value in [0.0, 1.0]") from exc
    if not math.isfinite(numeric) or not (0.0 <= numeric <= 1.0):
        raise ValueError(f"{field_name} must be finite and within [0.0, 1.0], got {value!r}")
    return numeric


def normalize_threshold(raw_value: float, is_percent: bool = False) -> float:
    """Normalize a decimal or percentage threshold into [0.0, 1.0]."""
    if not math.isfinite(raw_value):
        raise ValueError(f"Threshold must be finite, got {raw_value!r}")
    value = raw_value / 100.0 if (is_percent or raw_value > 1.0) else raw_value
    if not (0.0 <= value <= 1.0):
        raise ValueError(f"Threshold must normalize within [0.0, 1.0], got {raw_value}")
    return round(value, 4)


def parse_threshold_string(raw_str: str) -> float:
    """Parse a CLI threshold string such as '0.85' or '85%'."""
    text = raw_str.strip()
    if not text:
        raise ValueError("Threshold cannot be empty")
    is_pct = text.endswith("%")
    num_part = text[:-1].strip() if is_pct else text
    if not num_part or "%" in num_part:
        raise ValueError(f"Invalid threshold format: {raw_str!r}")
    try:
        raw_num = float(num_part)
    except ValueError as exc:
        raise ValueError(f"Invalid threshold number: {raw_str!r}") from exc
    return normalize_threshold(raw_num, is_pct)


def load_threshold_from_configs(config_paths: list[Path]) -> tuple[float | None, str | None]:
    """Read the first valid confidence_threshold directive outside fenced code blocks."""
    for path in config_paths:
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise ValueError(f"Failed to read config file {path}: {exc}") from exc

        stripped = FENCED_BLOCK_PATTERN.sub("", content)
        match = THRESHOLD_PATTERN.search(stripped)
        if not match:
            continue
        raw_num = float(match.group(1))
        is_pct = match.group(2) == "%"
        return normalize_threshold(raw_num, is_pct), str(path)
    return None, None


def score_raw_prompt(prompt: str) -> dict[str, Any]:
    """Compute a deterministic baseline confidence score for an unsplit prompt."""
    text = prompt.strip()
    if not text:
        return {
            "id": "primary",
            "label": "Empty prompt",
            "confidence": 0.0,
            "confidence_pct": 0.0,
            "signals": {"reason": "Prompt text is empty."},
        }

    words = re.findall(r"[a-zA-Z0-9_./`-]+", text.lower())
    word_count = len(words)

    length_score = min(1.0, word_count / 18.0) * 0.30
    markers = SPECIFIC_MARKERS.findall(text)
    specificity_score = min(1.0, len(markers) / 3.0) * 0.45

    vague_hits = sum(1 for w in words if w.strip(".,;:") in VAGUE_TOKENS)
    vague_penalty = min(0.35, vague_hits * 0.08)

    multi_hits = len(MULTI_INTENT_MARKERS.findall(text))
    multi_penalty = min(0.30, multi_hits * 0.12)

    base_clarity = 0.25
    raw_score = base_clarity + length_score + specificity_score - vague_penalty - multi_penalty
    confidence = round(max(0.0, min(1.0, raw_score)), 4)

    return {
        "id": "primary",
        "label": "Primary interpretation",
        "confidence": confidence,
        "confidence_pct": round(confidence * 100.0, 2),
        "signals": {
            "word_count": word_count,
            "specific_markers": len(markers),
            "vague_tokens": vague_hits,
            "multi_intent_markers": multi_hits,
        },
    }


def score_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Score and rank explicit candidate intents on [0.0, 1.0]."""
    raw_scores: list[tuple[dict[str, Any], float]] = []
    for index, item in enumerate(candidates, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Candidate at index {index - 1} must be a JSON object")

        specificity = validate_unit_float(item.get("specificity", 0.5), "specificity")
        target_clarity = validate_unit_float(item.get("target_clarity", 0.5), "target_clarity")
        constraints = validate_unit_float(
            item.get("constraint_completeness", 0.5), "constraint_completeness"
        )
        penalty = validate_unit_float(item.get("ambiguity_penalty", 0.0), "ambiguity_penalty")

        base = (0.40 * specificity) + (0.35 * target_clarity) + (0.25 * constraints) - penalty
        bounded = max(0.01, min(1.0, base))
        raw_scores.append(
            (
                {
                    "id": str(item.get("id", f"intent-{index}")),
                    "label": str(item.get("label", f"Candidate intent {index}")),
                    "summary": str(item.get("summary", "")),
                },
                bounded,
            )
        )

    total_weight = sum(score for _, score in raw_scores) or 1.0
    single_candidate = len(raw_scores) == 1

    scored: list[dict[str, Any]] = []
    for meta, raw in raw_scores:
        combined = raw if single_candidate else (0.65 * raw + 0.35 * (raw / total_weight))
        confidence = round(max(0.0, min(1.0, combined)), 4)
        scored.append(
            {
                **meta,
                "confidence": confidence,
                "confidence_pct": round(confidence * 100.0, 2),
            }
        )

    scored.sort(key=lambda entry: entry["confidence"], reverse=True)
    return scored


def parse_candidates_payload(payload: str) -> list[dict[str, Any]]:
    """Parse a JSON array of candidate intent objects."""
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid candidates JSON: {exc}") from exc
    if not isinstance(data, list) or not data:
        raise ValueError("Candidates payload must be a non-empty JSON array")
    return data


def load_candidates_file(path: Path) -> list[dict[str, Any]]:
    """Load and parse candidate intents from a JSON file."""
    if not path.is_file():
        raise ValueError(f"Candidates file not found: {path}")
    try:
        payload = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"Failed to read candidates file {path}: {exc}") from exc
    return parse_candidates_payload(payload)


def evaluate(
    prompt: str,
    threshold: float | None,
    threshold_source: str | None,
    candidates_data: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Evaluate prompt confidence against the resolved threshold."""
    if threshold is None:
        return {
            "status": "THRESHOLD_REQUIRED",
            "threshold": None,
            "threshold_source": None,
            "message": (
                "No confidence_threshold found in AGENTS.md, GEMINI.md, or --threshold. "
                "Ask the user to specify the minimum confidence score before executing."
            ),
            "candidates": [],
        }

    if not prompt.strip():
        candidates = [score_raw_prompt(prompt)]
    else:
        candidates = score_candidates(candidates_data) if candidates_data else [score_raw_prompt(prompt)]
    top = candidates[0]
    has_close_tie = (
        len(candidates) > 1
        and (top["confidence"] - candidates[1]["confidence"]) <= TIE_MARGIN
    )

    should_execute = top["confidence"] >= threshold and not has_close_tie
    status = "EXECUTE" if should_execute else "CLARIFY"

    return {
        "status": status,
        "threshold": threshold,
        "threshold_pct": round(threshold * 100.0, 2),
        "threshold_source": threshold_source,
        "top_intent": top,
        "has_close_tie": has_close_tie,
        "candidates": candidates,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate per-turn prompt confidence against a minimum threshold."
    )
    parser.add_argument("--prompt", default="", help="User prompt text for the current turn.")
    parser.add_argument(
        "--config",
        action="append",
        default=[],
        help="Path to AGENTS.md or GEMINI.md to read confidence_threshold from.",
    )
    parser.add_argument(
        "--threshold",
        default=None,
        help="Explicit minimum confidence threshold (e.g. 0.85 or 85%%).",
    )
    candidate_group = parser.add_mutually_exclusive_group()
    candidate_group.add_argument(
        "--candidates",
        default=None,
        help=(
            "Inline JSON array of candidate intent objects "
            "(fields: id, label, summary, specificity, target_clarity, "
            "constraint_completeness, ambiguity_penalty)."
        ),
    )
    candidate_group.add_argument(
        "--candidates-file",
        default=None,
        help="Path to a JSON file containing a candidate intent array.",
    )

    args = parser.parse_args(argv)

    try:
        threshold: float | None = None
        threshold_source: str | None = None

        if args.threshold is not None:
            threshold = parse_threshold_string(str(args.threshold))
            threshold_source = "cli:--threshold"
        elif args.config:
            threshold, threshold_source = load_threshold_from_configs([Path(p) for p in args.config])

        candidates_data: list[dict[str, Any]] | None = None
        if args.candidates is not None:
            candidates_data = parse_candidates_payload(args.candidates)
        elif args.candidates_file is not None:
            candidates_data = load_candidates_file(Path(args.candidates_file))

        result = evaluate(args.prompt, threshold, threshold_source, candidates_data)
    except ValueError as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, indent=2))
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
