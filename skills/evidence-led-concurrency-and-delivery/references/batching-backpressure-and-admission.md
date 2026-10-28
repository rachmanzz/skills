# Batching, Backpressure, and Admission Control

## Large batches

Define limits for:

- items per batch;
- bytes per batch;
- memory retained per item;
- concurrent items;
- per-item timeout;
- total batch deadline;
- retryable and terminal item failures.

Prefer streaming or bounded chunks when the input can exceed memory or time
limits. Define whether partial success is committed, retried, rolled back, or
recorded individually. Never assume that splitting a batch preserves atomicity.

## Backpressure

Identify the signal that means capacity is exhausted and the chosen response:

- wait;
- reject;
- shed low-value work;
- reduce intake;
- degrade optional work;
- persist for later;
- fail fast.

Bound the response itself. Unbounded retries, waiting callers, buffers, or
fallback work are another overload path.

## Admission control

Admission should reserve the resources required by the accepted work or state
why reservation is impossible. Consider memory, queue slots, execution units,
storage capacity, dependency quotas, and tenant or priority limits.

Check the race between admission and execution: a task admitted under one
capacity estimate may become too expensive later. Define cancellation and
release behavior when a reservation cannot be fulfilled.

Distinguish unused reservations from resources still in use. A cancellation or
timeout does not by itself justify releasing an execution permit or memory
budget. Keep accounting attached to active work until use ends or accounting
ownership verifiably transfers, and prevent duplicate release on overlapping
cleanup, cancellation, and completion paths.

## Fairness

Measure or reason about starvation under sustained load. Check whether priority,
retries, large batches, or one tenant can consume all capacity. If fairness is
intentionally traded for latency or priority, document the rule and its bounds.
