# Retry and Timeout Budgets

## Retry Audit

Check every retry loop, SDK auto-retry, queue redelivery, and client wrapper for
boundedness, safety, and cross-layer amplification.

### Checklist

- **Bounded attempts and total retry time**: verify an explicit upper bound on
  both attempt count and cumulative retry duration; never allow unbounded
  retries.
- **Retryability classification**: verify retries run only on genuinely
  transient failures (for example, network reset, 503/429, transient lock
  conflict) and not on permanent `400`/`403`/schema errors or business rejections
  (with narrow exceptions such as a single bounded `401` retry after token
  refresh or a bounded `404` retry for documented read-after-write consistency).
- **Idempotency gate**: verify that non-idempotent mutations are not retried
  blindly without an idempotency key or safe deduplication contract.
- **Backoff and jitter**: verify exponential (or bounded) backoff with
  randomized jitter so concurrent callers do not synchronize retry spikes.
- **`Retry-After` / overload respect**: verify callers honor server-supplied
  backoff headers or rate-limit signals instead of hammering immediately.
- **Retry amplification across layers**: trace multi-hop calls (e.g., gateway
  retries x service retries x SDK/DB retries). If Layer A retries 3x and Layer B
  retries 3x, total downstream attempts become 9x or 16x. Enforce a shared
  retry budget or limit retries to a single well-defined layer.
- **Circuit-breaker interaction**: do not retry blindly into an open circuit
  breaker, and clarify whether local circuit-breaker rejections count toward or
  short-circuit the caller's retry loop so fast-fail stays fast.

## Timeout Audit

Check timeout presence, consistency, and propagation across every I/O hop
(inbound server, internal RPC/HTTP clients, DB queries, locks, cache calls).

### Checklist

- **No missing or infinite timeouts**: every outbound network call, DB query,
  and distributed/DB/try-lock acquisition must have an explicit timeout or
  deadline (and long-lived streams must enforce idle/heartbeat bounds; avoid
  holding non-timed in-process mutexes across I/O). Never rely on implicit
  infinite library defaults.
- **Pool-acquire vs connect vs read vs overall timeout**: bound connection-pool
  acquisition separately from TCP/TLS connect, per-attempt read/request, and
  overall operation deadline so pool saturation or stalled reads cannot bypass
  the caller's limit.
- **Cross-layer consistency (deadline budget)**:
  - downstream timeouts must fit inside the caller's remaining deadline rather
    than exceeding it;
  - cumulative retry time (`attempts * per_attempt_timeout + backoff`) must
    not exceed the outer request timeout (which causes orphaned retries after
    the caller already gave up);
  - server/gateway idle and write timeouts must align with handler budgets.
- **Timeout error clarity**: on hard dependencies (or when no soft-dependency
  fallback contract applies), timeouts must surface as explicit timeout/504
  errors with dependency identity, never silently converted into empty results
  or misreported as `not found`; when a soft dependency triggers a cached or
  partial fallback, record the timeout via structured logs/metrics and explicit
  degraded/staleness markers.
