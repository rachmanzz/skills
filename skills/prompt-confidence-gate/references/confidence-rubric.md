# Confidence Rubric and Configuration

## Threshold configuration in `AGENTS.md` or `GEMINI.md`

Embed the minimum confidence threshold in `AGENTS.md` or `GEMINI.md` using any of the following forms:

```markdown
confidence_threshold: 0.85
```

or as a percentage:

```markdown
confidence_threshold: 85%
```

Supported separators are `:` and `=`. Values with a `%` suffix or values greater than `1.0` and up to `100.0` are treated as percentages and normalized to `[0.0, 1.0]` (note: a `0.0` threshold still requires a non-empty prompt to execute). The first matching `confidence_threshold` directive outside fenced code blocks across `--config` paths is used and must be valid; `--threshold` overrides `--config`.

## Scoring dimensions

`scripts/score_prompt.py` evaluates confidence deterministically on `[0.0, 1.0]` using two modes:

1. **Raw prompt mode** (no `--candidates` / `--candidates-file`): evaluates a lexical heuristic based on token count (`word_count`), explicit path/extension/backtick/verb markers (`specific_markers`), vague-word hits (`vague_tokens`), and multi-intent markers (`or`, `either`, `alternatively`, `versus`, `vs.`, `?`).
2. **Candidate intent mode** (`--candidates` or `--candidates-file` with a non-empty `--prompt`): computes each candidate's intrinsic score from the caller-supplied `[0.0, 1.0]` attributes (`specificity`, `target_clarity`, `constraint_completeness`, `ambiguity_penalty`, defaulting omitted attributes to `0.5` and `0.0`):
   - **Specificity** (`0.40`): Concrete action verbs, explicit file paths, symbol names, or measurable outcomes.
   - **Target clarity** (`0.35`): Clear subject and scope boundaries rather than dangling pronouns or missing targets.
   - **Constraint completeness** (`0.25`): Explicit acceptance criteria, formats, or boundaries.
   - **Ambiguity penalty** (`-ambiguity_penalty`): Multiple competing intents, open-ended phrasing, or contradictory requirements.

Each candidate's intrinsic quality is `raw = clamp(0.40*specificity + 0.35*target_clarity + 0.25*constraint_completeness - ambiguity_penalty, 0.0, 1.0)`. With a single candidate (or zero total weight), `confidence = raw`. With multiple competing candidates, `confidence = raw * (0.65 + 0.35 * (raw / total_weight))`, so evenly split interpretations drop below their intrinsic score while weak decoys never inflate a candidate above `raw`.

## Gate decision outcomes

- `THRESHOLD_REQUIRED`: Neither `--threshold` nor any `--config` file supplied a `confidence_threshold`.
- `EXECUTE`: Non-empty prompt, `top_intent.confidence >= threshold`, and `(top_intent.confidence - second_intent.confidence) > 0.05` when `len(candidates) > 1`.
- `CLARIFY`: Empty/whitespace prompt, `top_intent.confidence < threshold`, or `(top_intent.confidence - second_intent.confidence) <= 0.05`.
