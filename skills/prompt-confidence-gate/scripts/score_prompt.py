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

THRESHOLD_PATTERN = re.compile(
    r"^\s*(?:[-*]\s*)?`?confidence_threshold`?\s*[:=]\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
MAX_CONFIG_BYTES = 1024 * 1024

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


def _strip_fenced_blocks(content: str) -> str:
    """Remove fenced code blocks of 3+ backticks or tildes without regex backtracking."""
    visible: list[str] = []
    fence_char: str | None = None
    fence_len = 0
    for line in content.splitlines():
        stripped = line.lstrip()
        if fence_char is None:
            match = re.match(r"^(`{3,}|~{3,})", stripped)
            if match:
                fence_char = match.group(1)[0]
                fence_len = len(match.group(1))
                continue
            visible.append(line)
        else:
            if re.match(rf"^{re.escape(fence_char)}{{{fence_len},}}\s*$", stripped):
                fence_char = None
                fence_len = 0
    return "\n".join(visible)


def _read_bounded_text(path: Path, label: str) -> str:
    """Read a regular UTF-8 file up to MAX_CONFIG_BYTES without following symlinks."""
    if path.is_symlink():
        raise ValueError(f"{label} must not be a symlink: {path}")
    try:
        size = path.stat().st_size
        if size > MAX_CONFIG_BYTES:
            raise ValueError(f"{label} exceeds maximum size ({MAX_CONFIG_BYTES} bytes): {path}")
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"Failed to read {label} {path}: {exc}") from exc


def load_threshold_from_configs(config_paths: list[Path]) -> tuple[float | None, str | None]:
    """Read the first valid confidence_threshold directive outside fenced code blocks."""
    for path in config_paths:
        if not path.exists():
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Config path must be a regular file: {path}")
        content = _read_bounded_text(path, "config file")
        stripped = _strip_fenced_blocks(content)
        match = THRESHOLD_PATTERN.search(stripped)
        if not match:
            continue
        raw_value = match.group(1).strip()
        return parse_threshold_string(raw_value), str(path)
    return None, None


def score_raw_prompt(prompt: str) -> dict[str, Any]:
    """Compute a deterministic lexical heuristic confidence score for an unsplit prompt."""
    text = prompt.strip()
    if not text:
        return {
            "id": "primary",
            "label": "Empty prompt",
            "confidence": 0.0,
            "confidence_pct": 0.0,
            "signals": {"reason": "Prompt text is empty."},
        }

    words = re.findall(r"[\w./`-]+", text.lower())
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


def _optional_string(item: dict[str, Any], key: str, default: str) -> str:
    if key not in item:
        return default
    val = item[key]
    if not isinstance(val, str):
        raise ValueError(f"Candidate field {key!r} must be a string")
    return val


def score_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Score and rank explicit candidate intents on [0.0, 1.0]."""
    if not candidates:
        raise ValueError("Candidates list must be non-empty")

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
        bounded = max(0.0, min(1.0, base))
        raw_scores.append(
            (
                {
                    "id": _optional_string(item, "id", f"intent-{index}"),
                    "label": _optional_string(item, "label", f"Candidate intent {index}"),
                    "summary": _optional_string(item, "summary", ""),
                },
                bounded,
            )
        )

    total_weight = sum(score for _, score in raw_scores)
    single_candidate = len(raw_scores) == 1

    scored: list[dict[str, Any]] = []
    for meta, raw in raw_scores:
        if single_candidate or total_weight == 0.0:
            combined = raw
        else:
            share = raw / total_weight
            combined = raw * (0.65 + 0.35 * share)
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
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Candidates file not found or invalid: {path}")
    payload = _read_bounded_text(path, "candidates file")
    return parse_candidates_payload(payload)


def evaluate(
    prompt: str,
    threshold: float | None,
    threshold_source: str | None,
    candidates_data: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Evaluate prompt confidence against the resolved threshold."""
    scored_candidates = score_candidates(candidates_data) if candidates_data is not None else None

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

    is_empty = not prompt.strip()
    if is_empty:
        candidates = [score_raw_prompt(prompt)]
    else:
        candidates = scored_candidates if scored_candidates is not None else [score_raw_prompt(prompt)]
    top = candidates[0]
    has_close_tie = (
        len(candidates) > 1
        and (top["confidence"] - candidates[1]["confidence"]) <= TIE_MARGIN
    )

    should_execute = (not is_empty) and top["confidence"] >= threshold and not has_close_tie
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
