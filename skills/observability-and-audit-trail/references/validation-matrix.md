# Validation Matrix

Use this matrix to verify logging, distributed tracing, metrics, alerting,
health checks, and audit trails.

| Area | Scenario | Expected invariant | Evidence to record |
| --- | --- | --- | --- |
| Logging | Trigger success, degraded fallback, and failure path with auth header | Structured logs include `request_id`/`trace_id`, error cause, and dependency ID; secrets/PII are redacted | Captured log output across paths |
| Tracing | Inbound request with `traceparent` calls DB + downstream HTTP/queue | Trace ID propagates end-to-end across child spans and outbound headers; failed spans record error status | Trace/span dump or header propagation test |
| Metrics | Hit route with varying user IDs and trigger 4xx/5xx/timeout | Route labels stay normalized (bounded cardinality); error, latency histogram, and saturation metrics update | `/metrics` scrape or metric registry test |
| Alerting | Inspect alert rules for 5xx spike, latency SLO, DLQ, pool saturation, and silent jobs | Rules exist for each inspected failure mode with sustained windows and clear severity | Alert rule config review |
| Health Check | Disconnect soft dependency vs hard dependency; trigger graceful shutdown | Liveness stays 200 when soft dependency fails; readiness returns 503 during hard outage or drain within bounded timeout | Probe HTTP status and latency under fault |
| Audit Trail | Perform admin/role/delete/financial mutation and failed attempt | Append-only audit entry records actor, action, target, timestamp, outcome, and correlation ID without secret leakage | Audit table/stream query after test |

For each check record exact commands/queries, observed signals, inspected scope,
and claim status (`VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`, `PARTIAL`,
`NOT_FOUND_IN_SCOPE`, or `UNKNOWN`).
