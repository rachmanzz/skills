# Memory Efficiency

Optimize memory only after identifying the allocation, retention, or residency
problem. A lower memory footprint is useful when it improves capacity, latency,
stability, or cost without changing correctness.

## Inspect

Look for:

- repeated temporary allocations in hot paths;
- unnecessary copies, conversions, or materialization;
- retained references that extend object lifetime;
- unbounded maps, lists, queues, buffers, and caches;
- large intermediate collections where streaming is possible;
- duplicated representations of the same data;
- oversized serialized payloads;
- object churn that increases garbage-collection work.

## Design choices

Choose deliberately between copying and sharing, eager and lazy evaluation,
materialized and streamed results, mutable and immutable data, pooled and
short-lived objects, and compressed and uncompressed values. Document ownership
and lifetime when the language does not make them obvious.

Every buffer, pool, queue, cache, and retained result needs a bound or a
release policy. A memory optimization is incomplete if it only moves the leak
to a different layer.

## Validation

Measure peak resident memory, live heap, allocation rate, retained size,
garbage-collection pauses, and out-of-memory behavior using representative
workloads. Include long-running and high-concurrency tests.
