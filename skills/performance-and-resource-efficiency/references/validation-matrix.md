# Validation Matrix

Use this matrix as a starting point for performance and resource-efficiency
reviews or changes. Add scenarios that match the actual workload, memory
budget, and cache contract, and remove irrelevant rows. A passing test or
benchmark supports only the tested workload and scope.

| Area | Scenario | Expected invariant | Evidence to record |
| --- | --- | --- | --- |
| Baseline & Profiling | Representative and peak workloads before changes | Bottleneck is measured (latency percentiles, throughput, allocations, or I/O count) before optimizing | Profiler/benchmark command, sample size, and baseline metrics |
| Complexity & Loops | Large, empty, and worst-case inputs | Asymptotic cost and per-iteration allocations stay bounded without quadratic blowups or repeated work | Complexity analysis and before/after benchmark output |
| Memory & Ownership | Sustained traffic with large payloads or buffers | Peak memory, retained buffers, and GC/allocator pressure remain bounded without unbounded growth | Heap profile, allocation rate, and RSS over window |
| I/O & Database | List/batch endpoints under realistic row counts | Queries/round-trips are batched/paginated cleanly without N+1 queries or unbounded payloads | Query count, payload size, and p95/p99 latency |
| Concurrency | Concurrent callers under saturation and cancellation | Workers, queues, and connections remain bounded; cancelled callers abort promptly without leaks | Concurrency config, saturation test output, and goroutine/task count |
| Cache Contract | Cache hit, miss, stale-while-revalidate, and eviction | Capacity, TTL, tenant/key isolation, and documented freshness semantics hold under load | Cache config, eviction/hit metrics, and correctness check |
| Cache Fallback | Cache backend outage or slow response | Origin/DB is protected from miss storms; kill switch or bounded fallback preserves correctness and auth | Fault-injection output, origin QPS, and fallback status |

For each executed scenario record:

- exact workload parameters (input size, concurrency, cache size/TTL);
- benchmark, profile, or test command executed;
- observed before/after numbers and runtime signals;
- inspected scope and limitations;
- claim status (`VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`, `PARTIAL`, `NOT_FOUND_IN_SCOPE`, or `UNKNOWN`);
- unresolved assumptions.
