# Profiling and Benchmarking

Performance claims require a reproducible comparison. Keep the workload,
environment, input distribution, and correctness checks consistent.

## Baseline

Record the target metric, workload size, concurrency, runtime version, hardware
or container limits, dependency versions, warm-up behavior, and measurement
method. For latency, include percentiles rather than only averages.

## Measure

Use the language and runtime's profilers, allocation tools, tracing, database
plans, system metrics, and load tests. Measure CPU, wall time, allocations,
peak memory, I/O, queueing, cache hit/fallback behavior, errors, and saturation
where relevant.

## Compare

Run enough repetitions to distinguish noise from improvement. Check cold and
warm behavior, small and large inputs, normal and worst-case inputs, and
concurrent execution. Verify output equivalence and failure semantics.

Do not report a benchmark as production impact without stating the limits of the
test and the assumptions that may differ in production.
