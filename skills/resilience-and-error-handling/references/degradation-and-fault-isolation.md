# Degradation and Fault Isolation

## Degradation Audit

Audit how the system behaves when a dependency, downstream service, storage
engine, or internal component slows down, returns partial errors, or becomes
unavailable.

### Checklist

- **Dependency criticality classification**: separate hard dependencies (must
  fail closed) from soft/optional dependencies (can degrade gracefully).
- **Slow-dependency behavior**: verify that degraded latency does not hold
  request threads, connections, or memory until the entire service stalls.
  Slow failures are often more destructive than fast errors.
- **Graceful degradation contract**: when serving cached, stale, partial, or
  reduced-feature responses, verify:
  - correctness, authorization, and tenant isolation are preserved;
  - staleness or partial completeness is bounded and observable;
  - the degraded path does not create an unbounded fallback storm on the origin
    or database.
- **Circuit breaking and load shedding**: verify whether repeated dependency
  failures trigger fast failure (open circuit) or selective shedding of
  low-priority work instead of queuing unboundedly.

## Fault Isolation Audit

Audit whether a failure, slowdown, or resource spike in one process, endpoint,
tenant, or dependency can disrupt unrelated healthy operations.

### Bulkheads and resource separation

- **Connection and thread/worker pools**: verify that slow or failing
  dependencies cannot exhaust shared pools used by healthy dependencies or
  health-check endpoints.
- **Per-tenant / per-key / per-route isolation**: verify that one noisy or
  failing tenant, payload, or route cannot starve capacity for others.
- **Process and memory boundaries**: verify that malformed inputs or failing
  subtasks in the inspected scope are bounded and isolated so they do not
  propagate into process-wide crashes, unbounded memory growth, or corrupted
  shared in-memory state.
- **Health/readiness probes**: verify that readiness checks accurately reflect
  fatal dependency loss without coupling liveness probes to soft external
  dependencies (which causes cascading restart loops).

### Validation cases

- Simulate high latency (not only immediate connection refused) on each
  external dependency and observe whether unrelated endpoints remain responsive.
- Verify that an open bulkhead or exhausted pool rejects fast with a clear
  status instead of blocking healthy callers.
