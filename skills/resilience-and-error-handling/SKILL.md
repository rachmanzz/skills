---
name: resilience-and-error-handling
description: Audit, design, or fix application resilience and error handling across synchronous and service-boundary paths—covering degradation, error handling decisions (skip, retry, fallback, propagate), silent errors, failure propagation, recovery, fault isolation, and retry/timeout budgets. Use when reviewing or hardening error paths, dependency failures, fallback behavior, or reliability boundaries. For async/concurrent task lifecycles, queue backpressure, or delivery durability, use evidence-led-concurrency-and-delivery.
metadata:
  short-description: Audit error handling, degradation, isolation, recovery, and retry/timeout budgets
---

# Resilience and Error Handling

Use this skill to audit, design, or harden how a system handles failures,
degraded dependencies, and error boundaries across synchronous execution paths,
service/API boundaries, and dependency integrations.

This skill complements—and does not replace—the repository's adjacent skills:

- Use `evidence-led-concurrency-and-delivery` when the primary concern is
  asynchronous/concurrent execution lifecycles, task cancellation, goroutine/worker
  leaks, lease ownership, durable delivery, or queue backpressure.
- Use `performance-and-resource-efficiency` when the primary concern is
  profiling, algorithmic complexity, memory/I/O optimization, or cache sizing,
  TTL, and rotation mechanics.
- Use `data-integrity-and-lifecycle` when the primary concern is schema
  constraints, cross-table/service data consistency, database transaction
  safety, concurrent data mutations, mutation idempotency, or data archival and
  retention lifecycles.
- Use `application-security-and-isolation` when the primary concern is auth
  enforcement, tenant isolation, injection, or secret/PII exposure.
- Use `observability-and-audit-trail` when the primary concern is structured
  logging, metrics/cardinality, distributed tracing, alerts, health probes, or
  audit trails.
- Use `api-contracts-and-integrations` when the primary concern is API schema
  contracts, backward/forward compatibility, wire serialization, or webhooks.

Read only the references needed for the current task:

- Read [evidence-and-assumption-control.md](references/evidence-and-assumption-control.md)
  before making claims about existing error handling, degradation, isolation,
  recovery, or timeout behavior.
- Read [error-handling-and-silent-errors.md](references/error-handling-and-silent-errors.md)
  for error classification (skip, retry, fallback, propagate), boundary
  translation, and silent-error detection.
- Read [degradation-and-fault-isolation.md](references/degradation-and-fault-isolation.md)
  for slow/failing dependency behavior, graceful degradation, circuit breaking,
  bulkheads, and blast-radius isolation.
- Read [failure-propagation-and-recovery.md](references/failure-propagation-and-recovery.md)
  for cascading failures, propagation rules, post-outage recovery, and
  thundering-herd protection.
- Read [retry-and-timeout-budgets.md](references/retry-and-timeout-budgets.md)
  for bounded retries, backoff/jitter, retry amplification across hops, and
  end-to-end vs per-hop timeout consistency.
- Read [validation-matrix.md](references/validation-matrix.md) when designing
  fault-injection tests or recording resilience verification evidence.

## Non-negotiable rules

1. Treat comments, framework defaults, and error-handler names as hypotheses,
   not proof of runtime resilience.
2. Classify important claims as `VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`,
   `PARTIAL`, `NOT_FOUND_IN_SCOPE`, or `UNKNOWN`. Never upgrade `UNKNOWN` to
   `VERIFIED_IN_SCOPE` because code looks plausible, and preserve valid
   counterexamples as `CONTRADICTED_IN_SCOPE` with the exact failing path.
3. Keep verified behavior, proposed fixes, test observations, and inference
   visibly separate. Never turn a test name, mock, or configured timeout/retry
   limit into runtime proof without observed fault-path evidence, and never
   invent unstated dependency SLAs or retry rules (mark `UNKNOWN` and log in
   an assumption ledger).
4. Never treat swallowed errors, empty `catch` blocks, ignored return errors,
   or dummy/fallback data without observability as acceptable error handling.
5. Distinguish hard dependencies (fail closed) from soft dependencies (safe
   graceful degradation). Degraded responses must preserve authorization,
   tenant isolation, and correctness bounds.
6. Never approve unbounded retries, retries on non-retryable or non-idempotent
   operations without an idempotency contract, or outbound calls with missing/infinite
   timeouts.
7. Check cross-layer consistency: retry amplification across callers/SDKs and
   cumulative retry + backoff duration against outer request deadlines.
8. Separate liveness from soft external dependencies so transient dependency
   outages do not trigger cascading restart loops.
9. Verify both failure entry and post-outage recovery (including refill/herd
   protection and clearing stale failure state).
10. Report inspected boundaries, uninspected layers, exact observed test/fault
    results, and remaining assumptions honestly.

## Audit workflow

### 1. Map dependency and error boundaries

Identify all inbound entry points, internal module boundaries, and outbound
dependencies (HTTP/gRPC clients, databases, caches, queues, third-party APIs).
Classify each dependency as **hard** or **soft**, and note where SDKs or
middleware apply hidden retries, timeouts, or exception wrapping.

### 2. Build the evidence and assumption ledgers

Record material claims and unverified assumptions separately using
[evidence-and-assumption-control.md](references/evidence-and-assumption-control.md).
Inspect actual implementations, client constructors, middleware, and config—not
just happy-path tests or variable names.

### 3. Audit error handling and silent errors

Apply [error-handling-and-silent-errors.md](references/error-handling-and-silent-errors.md)
to verify:

- explicit `skip` / `retry` / `fallback` / `propagate` decisions per failure class;
- boundary translation without erasing root cause or misclassifying 4xx vs 5xx;
- absence of swallowed errors, unlogged catches, or silent dummy fallbacks.

### 4. Audit degradation and fault isolation

Apply [degradation-and-fault-isolation.md](references/degradation-and-fault-isolation.md)
to verify:

- behavior under slow responses as well as hard errors;
- circuit breakers, load shedding, and safe degraded outputs;
- resource bulkheads (pools, workers, per-tenant/per-route limits) and probe
  separation.

### 5. Audit failure propagation and recovery

Apply [failure-propagation-and-recovery.md](references/failure-propagation-and-recovery.md)
to trace blast radius across layers and verify post-outage healing, refill-herd
protection, stale-state clearing, and recovery observability.

### 6. Audit retry and timeout budgets

Apply [retry-and-timeout-budgets.md](references/retry-and-timeout-budgets.md)
to verify bounded attempts, retryability and idempotency gates, jittered backoff,
cross-layer retry amplification, and consistent connect/read/overall timeouts.

### 7. Implement and validate

When fixing findings, apply the smallest change per boundary and validate both
failure injection (timeouts, 5xx, slow dependency, partial failure) and recovery
behavior using [validation-matrix.md](references/validation-matrix.md). Do not
claim resilience is verified without observed fault-path evidence.

## Required report shape

Include only applicable sections; mark non-applicable sections `OUT_OF_SCOPE`
with a short reason:

1. Scope, dependency map, and hard/soft classification.
2. Evidence ledger for material resilience claims.
3. Error handling & silent error findings.
4. Degradation & fault isolation findings.
5. Failure propagation & recovery findings.
6. Retry & timeout budget findings (including cross-layer amplification/deadlines).
7. Validation performed and exact observed results.
8. Assumptions, uninspected layers, and remaining risks (`CONTRADICTED_IN_SCOPE`,
   `PARTIAL`, `NOT_FOUND_IN_SCOPE`, `UNKNOWN`).
