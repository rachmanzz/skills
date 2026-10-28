---
name: evidence-led-concurrency-and-delivery
description: Review, design, implement, or debug reliability-critical asynchronous or concurrent execution when the task concerns cancellation, failure isolation, ownership, durability, idempotency, backpressure, fairness, or graceful shutdown. Do not use for ordinary concurrency syntax or unrelated performance tuning.
metadata:
  short-description: Verify concurrent work and delivery behavior
---

# Evidence-Led Concurrency and Delivery

Use this skill when the requested work concerns lifecycle or delivery
guarantees, failure boundaries, overload behavior, or recovery of asynchronous
or concurrent execution. Do not invoke it merely because an implementation
uses threads, tasks, workers, callbacks, or asynchronous syntax. The goal is to
make claimed behavior explicit and verifiable within a stated scope across
languages, runtimes, storage systems, and deployment models.

This skill is product-agnostic and language-agnostic. Use the repository's
actual terminology only after mapping it to neutral concepts such as work item,
executor, delivery backend, durable storage, ownership period, and completion
acknowledgement. Do not assume that similarly named mechanisms have equivalent
semantics.

Read only the references needed for the current task:

- Read [evidence-and-assumption-control.md](references/evidence-and-assumption-control.md)
  before making claims about existing behavior, completed work, or guarantees.
- Read [cancellation-and-failure-propagation.md](references/cancellation-and-failure-propagation.md)
  for cancellation, timeout, error propagation, and child-work boundaries.
- Read [panic-recovery-and-leak-prevention.md](references/panic-recovery-and-leak-prevention.md)
  for failure isolation, cleanup, and leaked execution or resources.
- Read [join-wait-and-shutdown.md](references/join-wait-and-shutdown.md)
  for join/wait contracts, draining, and bounded graceful shutdown.
- Read [idempotency-and-transaction-boundaries.md](references/idempotency-and-transaction-boundaries.md)
  for duplicate work, side effects, transactions, and acknowledgement order.
- Read [ownership-visibility-and-durable-storage.md](references/ownership-visibility-and-durable-storage.md)
  for claims, leases, visibility, recovery, and durable versus volatile state.
- Read [batching-backpressure-and-admission.md](references/batching-backpressure-and-admission.md)
  for large batches, bounded resources, overload behavior, and admission control.
- Read [fairness-and-scheduling.md](references/fairness-and-scheduling.md)
  for ordering, starvation, priority, quotas, and fairness trade-offs.
- Read [validation-matrix.md](references/validation-matrix.md) when designing
  tests or reviewing evidence for reliability claims.

## Non-negotiable rules

1. Treat user statements, names, comments, documentation, and intended design
   as requirements or hypotheses, not proof that behavior exists.
2. Classify important claims as `VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`,
   `PARTIAL`, `NOT_FOUND_IN_SCOPE`, or `UNKNOWN`. Never upgrade `UNKNOWN` to
   `VERIFIED_IN_SCOPE` because an implementation looks plausible. Include the
   inspected boundary in every verified or not-found claim.
3. Do not claim that work is cancelled, stopped, joined, durable, atomic,
   idempotent, owned, visible, fair, leak-free, or gracefully shut down without
   direct supporting evidence.
4. Keep verified behavior, proposed design, test observation, and inference
   visibly separate. If evidence conflicts, report the conflict. Retain a valid
   counterexample to a claim as `CONTRADICTED_IN_SCOPE`; do not downgrade it to
   uncertainty or partial coverage merely because other tests passed.
5. Do not assume that retry implies idempotency, timeout implies cancellation,
   acknowledgement implies persistence, a transaction covers another backend,
   or in-memory state is durable.
6. Make ownership, visibility, acknowledgement, retry, and recovery boundaries
   explicit for every asynchronous work path.
7. Bound work and resources: batch size, memory, queue depth, retries, timers,
   concurrent execution, waiting time, and shutdown duration.
8. Do not hide a panic, exception, or fatal error behind generic recovery. Keep
   the original cause, cleanup result, and incomplete work observable.
9. A shutdown timeout is evidence that the shutdown deadline expired; it is not
   evidence that active work stopped.
10. Preserve the requested storage, execution, and delivery model. State any
    fallback or substitution and validate its behavioral consequences.
11. Validate normal, empty, large, duplicate, cancelled, failed, overloaded,
    dependency-loss, and shutdown paths proportionally to the risk.
12. Report what was inspected and what was not inspected. Do not claim tests,
    benchmarks, profiles, or runtime checks that were not actually observed.

## Workflow

### 1. Define the contract

Write down the work item's lifecycle and required guarantees:

- creation and admission;
- storage location and durability requirement;
- scheduling and ordering;
- ownership and visibility period;
- execution and child-work behavior;
- acknowledgement and retry;
- idempotency boundary;
- cancellation and failure propagation;
- join/wait behavior;
- shutdown and recovery behavior.

If a guarantee is not specified, mark it `UNKNOWN` instead of choosing a
convenient default.

### 2. Build the evidence ledger

For every material claim, record the evidence source, status, and validation
method using [evidence-and-assumption-control.md](references/evidence-and-assumption-control.md).
Search implementation, configuration, tests, operational signals, and failure
paths. Negative evidence is scoped: use `NOT_FOUND_IN_SCOPE` only after naming
and searching the inspected boundary. It does not establish global absence or
exclude behavior supplied by an uninspected dependency, platform, or runtime.

### 3. Map lifecycle and ownership

Trace one work item from admission through completion or abandonment. Identify
which component owns each state transition and what happens when ownership
expires, if applicable. Look for recovery and stale-owner protections without
assuming they exist. Record mechanisms not found in the searched scope or
unknown behavior using the appropriate evidence status.

### 4. Analyze cancellation and failure boundaries

Determine whether cancellation is cooperative, preemptive, or only a request.
Trace causes to child work and identify the runtime's panic/exception and cleanup
boundaries. Verify cleanup and joins for the paths the runtime can handle, and
record outcomes when cleanup fails, blocks, or cannot run after abrupt process
termination. A cancellation request alone does not establish resource release.

### 5. Analyze durability, transactions, and duplicates

Separate volatile state from durable state. Identify the actual transaction
boundary and the ordering between persistence, side effects, and completion
acknowledgement. Define how duplicate execution is safe or rejected.

### 6. Bound batches and admission

Define limits for large batches, memory, queue depth, retries, concurrency, and
waiting. Specify whether overload causes wait, reject, shed, degrade, or retry.
Check fairness and starvation under sustained load.

### 7. Implement the smallest testable change

Do not combine reliability changes with unrelated refactors. Preserve a
rollback path. Add observability for state transitions, ownership loss,
cancellation causes, recovery, saturation, and shutdown incompleteness.

### 8. Validate and report

Use the relevant scenarios in [validation-matrix.md](references/validation-matrix.md).
Report behavior verified within the inspected scope, partial coverage,
claims contradicted in that scope, capabilities not found, unknowns, assumptions,
trade-offs, and remaining risks. Use precise wording such as “cancellation was requested” when
the evidence does not prove execution ended.

## Required report shape

For a review or implementation, include only the applicable sections below.
Mark a non-applicable section as `OUT_OF_SCOPE` with a short reason; do not
invent evidence or classify an uninspected, irrelevant area as `UNKNOWN`.

1. Contract and scope inspected.
2. Lifecycle and ownership map.
3. Evidence ledger for material claims.
4. Cancellation, failure, join, and shutdown behavior.
5. Idempotency and transaction boundaries.
6. Durability and visibility guarantees.
7. Batch, backpressure, admission, and fairness limits.
8. Validation performed and exact observed results.
9. Assumptions, their impact, and validation plan.
10. `CONTRADICTED_IN_SCOPE` findings and remaining `PARTIAL`,
    `NOT_FOUND_IN_SCOPE`, and `UNKNOWN` items.
