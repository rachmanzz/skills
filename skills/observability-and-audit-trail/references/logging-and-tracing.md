# Logging and Distributed Tracing

## Logging Audit

Evaluate whether logs are structured, actionable, correlated, safe, and
cost-bounded during normal operation and incidents.

### Checklist

- **Structured format & consistent schema**: emit machine-parseable JSON/key-value
  logs with consistent field names (`timestamp`, `level`, `service`, `event`,
  `request_id`, `trace_id`, `error`) instead of ad-hoc `fmt.Println`/`print`.
- **Severity discipline**: use `error` for unexpected/actionable failures, `warn`
  for handled degradations/retries/fallbacks, `info` for key lifecycle events,
  and `debug` for high-volume diagnostics; avoid logging expected 4xx client
  typos at `error` level or hiding production outages at `debug` level.
- **Failure & decision context**: log operation name, dependency identity,
  duration, retry attempt, and root cause (`err`), never bare `"failed"` strings.
- **PII & secret redaction**: verify passwords, tokens, cookies, API keys, and
  regulated PII are masked or excluded at logger/middleware boundaries.
- **Volume & log-storm control**: avoid logging inside tight per-item loops or
  unbounded payload dumps without sampling or rate limiting.

## Tracing Audit

Verify end-to-end request correlation across process, thread/goroutine, queue,
and service boundaries.

### Checklist

- **Inbound & outbound propagation**: extract W3C `traceparent`/`tracestate` (or
  the system's standard header/metadata) on trusted inbound HTTP/gRPC/queue
  messages—while untrusted public edges should sanitize, rate-limit sampling,
  or start a fresh root span with external trace ID as an attribute—and inject
  context on outbound internal/compatible client calls and published jobs/events.
- **In-process context propagation**: pass trace/request context through async
  tasks, worker pools, and DB calls so child spans remain attached to the parent
  trace rather than spawning disconnected root traces, and clear thread-local /
  MDC context on pooled workers so `trace_id`/`tenant_id` never bleeds across
  unrelated requests.
- **Span coverage & error tagging**: create spans around external dependencies,
  DB queries, cache calls, and heavy steps; record error status and error kind on
  failed spans.
- **Head/tail sampling & attribute hygiene**: verify error/slow traces are not
  silently dropped by naive sampling and avoid storing large bodies or secrets in
  span attributes.
