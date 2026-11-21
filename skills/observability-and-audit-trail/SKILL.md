---
name: observability-and-audit-trail
description: Audit, design, or improve system observability and auditability—covering structured logging, monitoring coverage, metrics and label cardinality, distributed tracing and context propagation, alerting rules, liveness/readiness health checks, and append-only audit trails. Use when reviewing telemetry, probe endpoints, trace correlation, alerts, or activity history.
metadata:
  short-description: Audit logging, monitoring, metrics, tracing, alerting, health checks, and audit trails
---

# Observability and Audit Trail

Use this skill to verify that runtime behavior, failures, and sensitive state
changes are visible, measurable, correlated, alertable, and durably recorded.

This skill complements—and does not replace—the repository's adjacent skills:

- Use `resilience-and-error-handling` when the primary concern is error
  classification (`skip`/`retry`/`fallback`/`propagate`), silent errors in code,
  circuit breaking, or retry/timeout budgets.
- Use `application-security-and-isolation` when the primary concern is auth
  enforcement, injection, or secret/PII exposure vulnerabilities.
- Use `data-integrity-and-lifecycle` when the primary concern is database
  constraints, transactions, or data retention/purging mechanics.

Read only the references needed for the current task:

- Read [evidence-and-assumption-control.md](references/evidence-and-assumption-control.md)
  before claiming telemetry, alerts, health probes, or audit trails are
  complete.
- Read [logging-and-tracing.md](references/logging-and-tracing.md) for
  structured logging, severity discipline, redaction, and distributed trace
  propagation.
- Read [monitoring-metrics-and-alerting.md](references/monitoring-metrics-and-alerting.md)
  for golden signals, bounded metric cardinality, histogram buckets, and
  actionable alert coverage.
- Read [health-checks-and-audit-trail.md](references/health-checks-and-audit-trail.md)
  for liveness/readiness separation, bounded deep probes, and append-only audit
  trails.
- Read [validation-matrix.md](references/validation-matrix.md) when designing
  telemetry, probe, or audit-trail verification checks.

## Non-negotiable rules

1. Classify important claims as `VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`,
   `PARTIAL`, `NOT_FOUND_IN_SCOPE`, or `UNKNOWN`. Never upgrade `UNKNOWN` to
   `VERIFIED_IN_SCOPE` because an SDK is imported, and do not assume external
   dashboards or alerts exist without inspecting their definitions (record
   unverified infra expectations in an assumption ledger).
2. Keep verified telemetry behavior, proposed instrumentation, observed runtime
   outputs, and inference visibly separate.
3. Require structured, correlated logs (`request_id`/`trace_id`) with explicit
   secret and PII redaction; forbid silent high-volume log storms in loops.
4. Never allow unbounded identifiers (`user_id`, `request_id`, raw unnormalized
   URLs, raw error strings) as metric labels.
5. Propagate trace context across inbound trusted/internal handlers, internal
   async/worker handoffs, and outbound HTTP/gRPC/queue calls (regenerating or
   re-evaluating sampling on untrusted external edges).
6. Keep liveness probes isolated from all external dependencies (especially soft
   dependencies and shared databases) so transient outages do not cause
   cascading container restarts; bound all readiness probe dependency checks
   with short timeouts.
7. Persist critical security, administrative, and financial audit-trail events
   durably (append-only, with actor, action, target, outcome, UTC timestamp,
   and correlation ID) without logging raw credentials.

## Audit workflow

### 1. Map telemetry boundaries and critical events

Identify all inbound/outbound transports, logger setup, metric registries,
tracing instrumentation, `/livez`/`/readyz` probes, alert rule files, and
audit-log tables/sinks.

### 2. Build the evidence and assumption ledgers

Record material claims and unverified collector/alerting assumptions separately
using [evidence-and-assumption-control.md](references/evidence-and-assumption-control.md).

### 3. Audit logging and distributed tracing

Apply [logging-and-tracing.md](references/logging-and-tracing.md) to verify
structured logs, redaction, severity levels, and trace-context propagation across
sync and async boundaries.

### 4. Audit monitoring, metrics, and alerting

Apply [monitoring-metrics-and-alerting.md](references/monitoring-metrics-and-alerting.md)
to verify golden signals, fallback/saturation metrics, label cardinality, and
sustained alert coverage (including dead-man checks).

### 5. Audit health checks and audit trails

Apply [health-checks-and-audit-trail.md](references/health-checks-and-audit-trail.md)
to verify liveness vs readiness isolation, probe timeouts, and append-only audit
trail durability.

### 6. Implement and validate

Apply minimal fixes and verify log output, trace headers, metric labels, probe
responses under outage, and audit entries using
[validation-matrix.md](references/validation-matrix.md).

## Required report shape

Include only applicable sections; mark non-applicable sections `OUT_OF_SCOPE`
with a short reason:

1. Scope, telemetry/alerting configs, and probe/audit endpoints inspected.
2. Evidence ledger for observability claims.
3. Logging & distributed tracing findings.
4. Monitoring, metrics & alerting findings.
5. Health check & audit trail findings.
6. Validation performed and exact observed results.
7. Assumptions, uninspected external monitoring configs, and remaining risks.
