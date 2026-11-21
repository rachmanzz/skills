---
name: performance-and-resource-efficiency
description: Analyze, design, implement, or review software performance across programming languages, focusing on memory efficiency, allocation, loop and algorithm design, method design, I/O, concurrency, caching, and evidence-based optimization. Use when a user asks to make code faster, reduce memory usage, improve loops or functions, optimize data access, or design reliable caches.
metadata:
  short-description: Improve performance with measured resource efficiency
---

# Performance and Resource Efficiency

Use this skill to improve performance without sacrificing correctness,
maintainability, data isolation, or operational safety. Treat performance work
as an evidence-driven engineering task. Do not optimize based on intuition when
profiling, benchmarks, complexity analysis, or resource measurements can answer
the question.

Choose implementation details from the actual language, runtime, libraries, and
deployment model. The function of this skill is to connect a measurable
performance problem to an appropriate code change and validation method. For
general error-handling audits, silent errors, circuit breaking, blast-radius
isolation, or cross-layer retry/timeout budgets unrelated to performance tuning
or cache sizing, use `resilience-and-error-handling`. For database schema
integrity, CRUD transaction safety, cross-table/service consistency, mutation
idempotency, or data retention/archival lifecycles, use
`data-integrity-and-lifecycle`. For module coupling, circular dependencies, dead
code, duplication, or configuration hygiene, use
`architecture-and-config-hygiene`; for logging, metrics, tracing, alerting, or
health/audit-trail checks, use `observability-and-audit-trail`; and for API
contracts, schema compatibility, or wire serialization correctness, use
`api-contracts-and-integrations`. Read only the relevant references:

- Read [memory-efficiency.md](references/memory-efficiency.md) for allocation,
  object lifetime, copying, leaks, and memory budgets.
- Read [loop-and-algorithm-design.md](references/loop-and-algorithm-design.md)
  for loop structure, complexity, batching, early exit, and algorithm choice.
- Read [method-design.md](references/method-design.md) for function boundaries,
  side effects, data flow, recursion, and API design.
- Read [data-structures.md](references/data-structures.md) when choosing or
  replacing collections, indexes, maps, sets, queues, or trees.
- Read [io-and-database-efficiency.md](references/io-and-database-efficiency.md)
  for query count, batching, pagination, serialization, and network costs.
- Read [concurrency.md](references/concurrency.md) for parallelism, limits,
  contention, backpressure, and race safety.
- Read [profiling-and-benchmarking.md](references/profiling-and-benchmarking.md)
  before making performance claims or comparing implementations.
- Read
  [evidence-and-assumption-control.md](references/evidence-and-assumption-control.md)
  and [evidence-ledger-template.md](references/evidence-ledger-template.md)
  before making claims about existing behavior, completed work, performance,
  compatibility, tests, or runtime state.
- Read [validation-matrix.md](references/validation-matrix.md) for required
  measurement and cache-fallback scenarios.
- Use the bundled
  [validate-evidence.py](scripts/validate-evidence.py) when producing a
  Markdown evidence ledger. Use [validate-skill-package.py](scripts/validate-skill-package.py)
  to validate the skill structure before publishing.
- Read the cache references under
  [cache-reliability-and-fallback/](references/cache-reliability-and-fallback/)
  for TTL, LRU capacity, cache rotation, shared backends, and database
  fallback.
- Read the matching file under [language-adapters/](references/language-adapters/)
  for language-specific runtime behavior. If the language is not listed, use
  the language-agnostic rules and the repository's established tools.

## Non-negotiable rules

1. Establish a baseline or a reasoned complexity/resource model before making
   a performance claim.
2. Preserve behavior, authorization, and data consistency—and any explicit
   freshness or stale-while-revalidate contract when caching is used. A faster
   wrong result is a regression.
3. Avoid unbounded resources: memory, cache entries, queues, retries, goroutines,
   threads, tasks, open connections, and buffered work.
4. Do not replace a requested backend, algorithm, or execution model with a
   cheaper-looking substitute without stating the trade-off and verifying the
   requirement.
5. Prefer high-leverage changes such as better complexity, fewer allocations,
   fewer I/O round trips, bounded concurrency, and appropriate data structures
   before micro-optimizing syntax.
6. Keep hot-path behavior observable. Add or use measurements for latency,
   throughput, allocation, memory, error rate, and resource saturation.
7. Do not claim an optimization is implemented or effective without code
   evidence and a relevant test, benchmark, profile, or runtime signal.
8. Treat caching as one performance technique, not a substitute for fixing an
   inefficient algorithm, query, loop, or method boundary.
9. When cache fallback is involved, protect the database or origin from an
   unbounded miss storm and report the exact fallback path.
10. Separate verified-in-scope behavior, contradicted claims, partial
    implementation, not-found-in-scope items, and unknown repository state in
    the final report.
11. Treat user statements as requirements or hypotheses, not proof that a
    feature already exists or works.
12. Do not claim that work is complete, a bug is fixed, code is faster, a cache
    exists, or a test passed without direct evidence.
13. Never upgrade `UNKNOWN` to `VERIFIED_IN_SCOPE` because an implementation
    seems likely. Keep missing evidence visible.
14. Do not claim to have run a command, test, benchmark, profile, or deployment
    check that was not actually run and observed.
15. State assumptions that materially affect the solution, including their
    impact and validation method. If evidence is missing, either ask for the
    needed information or proceed with a clearly bounded assumption.
16. Do not silently substitute a proposed design, mock, configuration value, or
    dependency declaration for a working runtime implementation.

## Workflow

### 1. Define the performance target

Clarify the target metric and constraint:

- latency, especially tail latency;
- throughput;
- memory or allocation budget;
- CPU usage;
- database or network load;
- startup time;
- battery or energy use;
- cost per request;
- correctness or freshness boundary.

Record the workload shape: input size, frequency, concurrency, hot and cold
paths, data distribution, and expected growth.

### 2. Inspect the existing implementation

Trace the full path before changing it. Inspect loops, method boundaries, data
structures, allocations, serialization, I/O, database calls, concurrency,
cache layers, configuration, and tests. Identify the actual bottleneck instead
of optimizing the most visible code.

If there is no benchmark or runtime evidence, label the suspected bottleneck as
`UNKNOWN` and create a measurement plan before making a strong claim.

### 2.5. Apply the evidence gate

Before making any claim about current behavior or a completed change, create a
small claim ledger:

| Claim | Evidence | Status | Validation |
| --- | --- | --- | --- |
| What is being asserted | File, line, config, test, command, or runtime signal | `VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`, `PARTIAL`, `NOT_FOUND_IN_SCOPE`, or `UNKNOWN` | How the status can be checked |

Use `NOT_FOUND_IN_SCOPE` only after searching the relevant repository scope and
finding no implementation. Use `UNKNOWN` when the search or runtime evidence is
insufficient. User intent, a package being installed, a variable being named,
or a configuration key existing is not proof of behavior.

When running the bundled validator from this skill directory (or via its full
installed plugin path), run:

```bash
python3 scripts/validate-evidence.py path/to/evidence-ledger.md
```

The ledger must contain non-empty `Claim`, `Evidence`, `Status`, and
`Validation` columns. Definitive claims such as “implemented,” “fixed,”
“working,” “faster,” or “tested successfully” require `VERIFIED_IN_SCOPE` (or
legacy `VERIFIED`) status and supporting evidence.

### 3. Analyze memory and complexity

Estimate time and space complexity. Check for repeated allocations, accidental
copies, retained references, unbounded collections, large intermediate values,
object churn, leaks, and poor locality. Check whether a loop or method repeats
work that can be indexed, memoized, batched, streamed, or moved outside the
hot path.

### 4. Design loops and methods deliberately

Choose loop structure, method boundaries, data ownership, error handling, and
return behavior based on the workload and language. Prefer clear control flow
with bounded work. Use early exit, batching, streaming, or precomputation when
they reduce measured cost without obscuring correctness.

Do not introduce abstraction, recursion, caching, parallelism, or clever syntax
solely because it appears faster. Explain the trade-off and measure it.

### 5. Optimize I/O and resource coordination

Reduce unnecessary database queries, network round trips, serialization, and
contention. Bound concurrency, retries, queues, and connection usage. If a cache
is appropriate, apply the cache references and verify expiration, capacity,
fallback, invalidation, and backend behavior.

### 6. Implement incrementally

Make the smallest change that tests the hypothesis. Keep a rollback path. Do
not combine unrelated refactors with performance changes unless the separation
would make correctness or measurement impossible.

### 7. Measure and validate

Compare the same workload before and after the change. Measure the target
metric, tail behavior, memory/allocation, CPU, I/O, correctness, and failure
paths. Include realistic input sizes and concurrency. Run unit, integration,
load, and failure tests appropriate to the risk.

At minimum, consider small input, large input, empty input, worst-case input,
repeated input, concurrent input, resource exhaustion, and dependency failure.

## Required report shape

Report:

- the target metric and workload assumptions;
- the suspected bottleneck and how it was measured;
- time and space complexity before and after when applicable;
- memory, allocation, I/O, and concurrency changes;
- cache layers, capacity, expiration, and fallback if caching is involved;
- benchmark, profile, test, or runtime evidence;
- regressions, trade-offs, and remaining risks;
- assumptions, their impact, and how they were validated;
- an evidence ledger for claims about existing behavior and completed work;
- evidence status for important claims.

Use these statuses:

- `VERIFIED_IN_SCOPE`: supported by code inspection and a passing test,
  benchmark, profile, or runtime signal in the inspected scope;
- `CONTRADICTED_IN_SCOPE`: disproven by direct evidence in the inspected scope;
- `PARTIAL`: improved only for some paths, workloads, or failure modes;
- `NOT_FOUND_IN_SCOPE`: the capability or optimization was not found within the
  inspected scope;
- `UNKNOWN`: the repository does not provide enough evidence to decide.

Never use “already implemented,” “fixed,” “working,” “faster,” “more
efficient,” or “tested successfully” unless the evidence ledger supports the
claim. Use “proposed,” “not verified,” or “requires validation” when evidence
is incomplete.
