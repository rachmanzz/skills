# Failure Propagation and Recovery

## Failure Propagation Audit

Trace how a failure in one component travels upward, laterally, or downstream
across callers, services, and data layers.

### Blast-radius analysis

- **Upstream propagation**: verify whether one downstream failure takes down an
  entire composite response when partial results or isolation would be safe, or
  conversely whether an error is improperly masked so upstream retries blindly.
- **Cascading overload**: check whether dependency failures trigger retries,
  fallback queries, or synchronous re-reads that amplify load onto struggling
  components or shared databases.
- **Restart and health-check cascades**: check whether a transient dependency
  outage fails liveness probes, drains all instances simultaneously, or shifts
  100% of traffic onto fewer remaining healthy nodes.
- **Data/state contamination**: check whether a failed step leaves partially
  mutated shared state, poisoned caches, or broken invariants that cause
  subsequent requests to fail.

### Propagation rules

- Fail fast once a hard dependency or deadline is exhausted rather than doing
  doomed downstream work.
- Preserve failure semantics across hops (for example, distinguish client
  4xx/validation errors from 503/504 dependency overload so upstream callers do
  not misclassify or endlessly retry).

## Recovery Audit

Verify how the system transitions from degraded or failed state back to normal
operation once the underlying cause resolves.

### Checklist

- **Automatic vs manual recovery**: confirm whether circuit breakers,
  connection pools, caches, and background clients automatically detect when a
  dependency recovers (for example, half-open probing or pool eviction of dead
  connections) without requiring a process restart.
- **Thundering-herd / refill protection**: when a failed dependency or cache
  recovers, verify that queued callers or expired entries do not slam the
  recovering service all at once (use bounded concurrency, jitter, singleflight/
  coalescing, or gradual ramp-up).
- **Stale state & poison-data cleanup**: verify that temporary failure flags,
  stale negative caches, or broken connections are cleared upon recovery.
- **Data reconciliation**: where partial failures or skipped operations occurred
  during an outage, verify whether a bounded repair, dead-letter, or
  reconciliation path exists and how operators observe recovery completion.
- **Observability of recovery**: confirm logs, metrics, or health signals
  record both entry into and exit from degraded/open-circuit states.
