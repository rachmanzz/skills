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

Supported separators are `:` and `=`. Values greater than `1.0` and up to `100.0` are treated as percentages and normalized to `[0.0, 1.0]`.

## Scoring dimensions

`scripts/score_prompt.py` evaluates prompt clarity deterministically on `[0.0, 1.0]`:

- **Specificity**: Concrete action verbs, explicit file paths, symbol names, or measurable outcomes increase confidence.
- **Target clarity**: Clear subject and scope boundaries increase confidence; dangling pronouns or missing targets reduce confidence.
- **Constraint completeness**: Explicit acceptance criteria, formats, or boundaries increase confidence.
- **Ambiguity penalty**: Multiple competing intents, open-ended phrasing, or contradictory requirements reduce confidence.

When `--candidates` (inline JSON array) or `--candidates-file` (path to JSON file) is supplied, each candidate intent object supports `id`, `label`, `summary`, plus numeric attributes on `[0.0, 1.0]`: `specificity`, `target_clarity`, `constraint_completeness`, and `ambiguity_penalty`. Competing intents are weighted by both intrinsic quality and relative share so that evenly split interpretations naturally produce lower per-intent confidence without capping a clearly dominant intent.

## Gate decision outcomes

- `THRESHOLD_REQUIRED`: Neither `--threshold` nor any `--config` file supplied a valid `confidence_threshold`.
- `EXECUTE`: `top_intent.confidence >= threshold` and no other candidate is tied within `0.05` when `len(candidates) > 1`.
- `CLARIFY`: `top_intent.confidence < threshold`, or multiple candidates are tied near the top.
