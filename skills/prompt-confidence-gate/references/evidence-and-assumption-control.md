# Evidence and Assumption Control

1. Never invent, assume, or silently default a minimum confidence threshold when none is configured in `AGENTS.md`, `GEMINI.md`, or explicitly provided by the user.
2. Keep observed prompt text, configured thresholds, computed Python scorer outputs, and inferred intent hypotheses visibly separate.
3. Report exact numeric confidence scores returned by `scripts/score_prompt.py`; do not round up a failing score to pass the gate.
4. Do not execute file modifications, commands, or destructive actions when the gate returns `CLARIFY` or `THRESHOLD_REQUIRED`.
5. Re-evaluate the prompt and threshold on every turn; prior-turn clearance does not grant permanent bypass for subsequent ambiguous prompts.
