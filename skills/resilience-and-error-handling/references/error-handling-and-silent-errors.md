# Error Handling and Silent Errors

## Error Handling Audit

Evaluate every error boundary by classifying the failure and verifying that the
chosen action matches the domain and caller contract.

### Explicit decision per error class

For each failure source (validation, auth, not-found, conflict, rate-limit,
timeout, dependency unavailability, corrupt payload, internal invariant bug),
verify which action is taken and why:

- **Propagate**: return or rethrow with preserved root cause and domain-safe
  context. Do not collapse distinct failure classes (for example, turning a
  400 validation error or 409 conflict into a generic 500 or retryable error).
- **Retry**: allowed only for transient, safely repeatable operations with
  bounded attempts and backoff; never retry deterministic client errors or
  non-idempotent writes without an explicit idempotency contract.
- **Fallback**: allowed only when degraded output is explicitly acceptable,
  safe, and distinguishable from authoritative success.
- **Skip**: allowed only when partial item loss is part of the contract; must
  record the skipped item, reason, and count without falsely reporting 100%
  completion.

### Boundary checks

- Verify that low-level transport, driver, or SDK errors are translated at
  module boundaries without losing the underlying cause or diagnostic metadata.
- Verify that caller-facing error codes/statuses accurately distinguish caller
  faults from dependency or internal faults.
- Verify that propagated error responses and structured error logs redact
  secrets, credentials, tokens, raw sensitive payloads, and PII.
- Verify that cleanup or rollback errors do not overwrite the primary failure.

## Silent Error Audit

Hunt for every path where an operation fails without producing an observable
signal (error return, structured log, metric/alert, or explicit degraded flag).

### Common silent-error patterns

- Empty or catch-all exception blocks (`catch {}`, `except Exception: pass`,
  discarded Promises, ignored error returns such as `_ = fn()`).
- Fallback-on-catch that returns empty collections, `null`, `false`, zero
  values, or cached/dummy defaults without logging, incrementing error metrics,
  or surfacing degraded status.
- Fire-and-forget calls or background callbacks whose errors are dropped before
  reaching any logger or error reporter.
- Swallowed errors inside loops, batch processors, or cleanup hooks where one
  item's failure is neither aggregated nor reported.
- Runtime-specific traps: unawaited async calls or missing unhandled-rejection
  hooks (JS/TS), ignored `defer Close()` / `_ = fn()` errors (Go), broad
  `except:` or `except Exception:` swallowing cancellation/interrupt signals
  (Python), or unobserved `CompletableFuture`/reactive stream errors (JVM).
- Overly broad log suppression or `debug`-only logging on production failure
  paths that makes outages invisible to alerting.

### Verification requirements

- Trace every `try/catch`, error-return check, `.catch(...)`, and fallback
  branch in the inspected scope.
- Confirm that every handled failure either propagates to the caller or emits
  structured observability (root cause, operation/dependency identity, and
  impact) via logs or aggregated metrics/counters appropriate to its severity
  and contract (such as benign expected client-disconnect or `skip` item
  accounting).
- Never approve synthetic or dummy data returned inside a `catch` block as
  normal success.
