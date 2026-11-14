---
name: prompt-confidence-gate
description: Evaluate every user prompt on every turn against a minimum confidence threshold before executing actions. Read the threshold from AGENTS.md or GEMINI.md, ask the user if unset, and use the Python scorer to evaluate candidate intents when a prompt is ambiguous.
metadata:
  short-description: Gate execution on per-turn prompt confidence
---

# Prompt Confidence Gate

Use this skill on **every turn** before executing any action, tool call, or code change. Its purpose is to verify that the user's prompt is sufficiently unambiguous and meets the required minimum confidence threshold prior to execution.

Read the supporting references as needed:

- Read [evidence-and-assumption-control.md](references/evidence-and-assumption-control.md) before making claims about user intent, thresholds, or confidence scores.
- Read [confidence-rubric.md](references/confidence-rubric.md) for threshold configuration syntax, scoring dimensions, and CLI usage of `scripts/score_prompt.py`.

## Per-turn execution workflow

Follow these four steps on every turn without exception:

### 1. Resolve the minimum confidence threshold

1. Inspect `AGENTS.md` and `GEMINI.md` in the active workspace (and user-level agent configuration if present) for an explicit `confidence_threshold` directive (for example, `confidence_threshold: 0.85` or `confidence_threshold: 85%`).
2. If a valid threshold is defined in `AGENTS.md` or `GEMINI.md`, use it as the authoritative minimum threshold for the current turn.
3. If no threshold is defined in `AGENTS.md` or `GEMINI.md` and none has been provided by the user for this session, **halt execution** and ask the user to specify the minimum confidence value (`0.00`–`1.00` or `0%`–`100%`) required before execution.

### 2. Identify candidate intents when ambiguity exists

1. Inspect the user's prompt for ambiguity signals: multiple plausible interpretations, missing target files or symbols, underspecified scope, conflicting constraints, or vague references.
2. When the prompt admits more than one plausible interpretation, enumerate each distinct candidate intent (`id`, `label`, and clarity/ambiguity attributes) rather than guessing silently.

### 3. Score confidence with Python

Run `scripts/score_prompt.py` to compute a deterministic confidence score for the prompt and each candidate intent:

```bash
python3 skills/prompt-confidence-gate/scripts/score_prompt.py \
  --config AGENTS.md \
  --config GEMINI.md \
  --prompt "<user prompt>"
```

When multiple candidate interpretations exist, pass them as an inline JSON array via `--candidates` (or from a file via `--candidates-file`) using the schema defined in [confidence-rubric.md](references/confidence-rubric.md) so each candidate receives an explicit, comparable confidence score. Pass workspace or user-level `AGENTS.md` and `GEMINI.md` paths via `--config`.

### 4. Enforce the execution gate

1. **`THRESHOLD_REQUIRED`**: No threshold was found in `AGENTS.md`, `GEMINI.md`, or CLI flags. Ask the user for the minimum confidence threshold before proceeding.
2. **`EXECUTE`** (`top_intent.confidence >= threshold` and no unresolved tie): Proceed to execute the top intent.
3. **`CLARIFY`** (`top_intent.confidence < threshold` or competing intents are tied): Do **not** execute. Present the candidate intents with their computed confidence scores and ask the user to confirm the intended meaning.
