# Loop and Algorithm Design

Analyze the work performed by a loop before changing its syntax. Prefer an
algorithmic improvement over a cosmetic rewrite.

## Review checklist

- What are the time and space complexities?
- Is work repeated for the same input or key?
- Can an index, set, map, sort, or precomputed structure avoid repeated scans?
- Can the loop stop early when the result is known?
- Can independent work be batched or streamed?
- Are nested loops operating on data that can be joined or indexed?
- Does the implementation preserve ordering and error behavior?
- Does the language introduce iterator, closure, boxing, or bounds-check costs
  that matter for this workload?

Do not assume a loop is slow because it is explicit, or fast because it is
declarative. Measure the actual workload and consider input distribution,
branch behavior, memory locality, and allocation.

## Common transformations

Consider indexing, grouping, one-pass aggregation, early exit, batching,
streaming, incremental processing, and work reuse. Reject a transformation if
it increases memory beyond the budget, changes semantics, or makes failure
handling unverifiable.
