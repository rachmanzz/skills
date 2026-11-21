# Validation Matrix

Use this matrix as a starting point for resilience and error-handling reviews or
fixes. Add scenarios that match the actual dependency and caller contracts, and
remove irrelevant rows. A passing test supports only the tested scope.

| Area | Scenario | Expected invariant | Evidence to record |
| --- | --- | --- | --- |
| Error Handling | Validation, auth, conflict, or permanent client error | Failure is classified accurately and propagated without being retried or converted into 5xx/success | Error class, HTTP/RPC status, and retry count |
| Error Handling | Partial batch or multi-item failure | Contracted `skip` or `fail` policy executes; skipped items and reasons are surfaced and counted | Processed/skipped counts and error summary |
| Error Handling | Exception/error propagation across module boundary | Root cause is preserved internally while PII, tokens, and secrets are redacted from external responses/logs | External payload, internal log fields, and redaction check |
| Silent Error | Dependency throws, rejects promise, or fails cleanup | Failure is propagated or logged/metered with cause and dependency ID; never returns synthetic success or empty fallback silently | Catch/error path trace, log entry, and metric increment |
| Degradation | Soft dependency times out or returns 5xx | Degraded path preserves authorization and tenant isolation, bounds staleness, and avoids fallback origin storms | Fallback response, staleness header/flag, and origin QPS |
| Degradation | Hard dependency is unavailable | Operation fails closed with an explicit dependency-unavailable error rather than partial/corrupt output | Returned status/error and absence of partial writes |
| Fault Isolation | One dependency becomes very slow (high latency) | Slow dependency exhausts only its own bulkhead/pool; unrelated endpoints and liveness probes stay responsive | Pool saturation, unrelated route latency, and probe status |
| Fault Isolation | Soft external dependency outage during readiness/liveness checks | Liveness probe stays healthy (no restart loop); readiness reflects actual serving contract | Liveness and readiness outputs during outage |
| Failure Propagation | Downstream failure under multi-hop caller chain | Caller fails fast when budget expires; error semantics remain intact without state contamination | Per-hop status, residual state, and caller behavior |
| Recovery | Failed dependency becomes healthy again | Circuit breaker/pool recovers automatically without restart; stale negative flags/dead connections clear and refill traffic is bounded | Half-open probe trace, recovery metric, and origin load curve |
| Retry | Transient failure (503/429/network reset) vs permanent 4xx | Retries run only on transient, idempotent-safe calls up to max attempts with jittered backoff and `Retry-After` respect | Attempt count, backoff intervals, and idempotency key |
| Retry | Multi-layer call chain (gateway -> service -> client) | Total downstream attempts remain bounded by a single retry layer or shared budget (no multiplicative amplification) | Per-layer attempt count and total downstream calls |
| Timeout | Slow connect, stalled read, or blocked pool acquisition | Pool-acquire, connect, read, and overall deadlines fire within the caller's outer budget; no orphaned retries continue after deadline | Configured timeouts, elapsed duration, and cancellation/abort evidence |

For each executed scenario record:

- exact configuration (timeouts, retry counts, pool sizes, circuit thresholds);
- fault-injection method or test command executed;
- observed output, log, metric, or runtime signal;
- inspected scope and limitations;
- claim status (`VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`, `PARTIAL`, `NOT_FOUND_IN_SCOPE`, or `UNKNOWN`);
- unresolved assumptions.
