# Concurrency and Resource Limits

Concurrency can reduce latency but can also multiply memory, connections,
contention, retries, and dependency load.

## Design rules

- bound workers, tasks, goroutines, threads, and in-flight requests;
- use cancellation and deadlines;
- apply backpressure to queues and streams;
- avoid holding locks across I/O;
- identify shared mutable state and race behavior;
- coalesce duplicate work when many callers request the same result;
- make retries bounded and jittered;
- define behavior during dependency slowdown or outage.

Do not parallelize a loop without measuring dependency capacity, memory impact,
ordering requirements, and failure aggregation. Do not use a lock as a default
fix for unclear ownership.

## Validation

Test contention, cancellation, queue saturation, partial failure, retries,
shutdown, and recovery. Measure tail latency and dependency load, not only
average throughput.
