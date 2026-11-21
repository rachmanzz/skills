# Evidence and Assumption Control

Use this reference before claiming that failures are logged, metrics or
traces propagate, alerts fire, health checks reflect real state, or audit
trails are complete and tamper-resistant.

## Claim statuses

| Status | Meaning |
| --- | --- |
| `VERIFIED_IN_SCOPE` | A specifically scoped observability claim is supported by direct code/config/rule inspection and observed telemetry, probe, or log output within that boundary. |
| `CONTRADICTED_IN_SCOPE` | Direct evidence or a test shows missing logs, dropped trace context, unbounded cardinality, false-green health checks, or missing audit records within its named scope. |
| `PARTIAL` | Telemetry or audit records exist only for identified paths, transports, or failure modes. |
| `NOT_FOUND_IN_SCOPE` | A named scope was searched and no log, metric, trace propagation, alert rule, health check, or audit record was found there. |
| `UNKNOWN` | Collector pipelines, Grafana/Alertmanager/Cloud monitoring rules, or production retention policies reside outside the inspected repository. |

Never upgrade `UNKNOWN` to `VERIFIED_IN_SCOPE` because an SDK or middleware is
registered. Keep verified behavior, proposed changes, test output, and
inference visibly separate, and do not convert `NOT_FOUND_IN_SCOPE` into global
absence. Having a logger or OpenTelemetry SDK imported does not prove
correlation IDs, trace context, or failure alerts work at runtime. Inspect
middleware wiring, metric label values, probe handlers, and alert definitions
directly, and observe actual emitted signals.

## Claim ledger

| Claim | Evidence | Status | Validation |
| --- | --- | --- | --- |
| Observability or audit-trail property and scope | File, line, dashboard/alert config, or test output | One status above | Log/metric/trace/probe check |

## Assumption ledger

Record assumptions separately and never assume external dashboards, SIEM, or
alert routers cover uninspected gaps:

| Assumption | Impact if false | Validation | Fallback |
| --- | --- | --- | --- |
| External collector, alert router, or SIEM expectation | Blind outage or missing audit history | Config/infra inspection | Emit structured app-level signals |

An assumption is not a fact. If it materially affects incident detection or
audit compliance, verify the external config or label the claim conditional.

## Completion gate

Before saying “observable”, “monitored”, “traced”, “alerted”, or “audited”,
qualify the statement with its scope and require:

1. relevant telemetry emitters or endpoints in scope (logs, metrics, trace
   propagation, health probes, or audit-trail writers) were inspected;
2. PII/secret redaction and metric label cardinality were checked where logs,
   traces, or metrics are in scope;
3. if health probes are in scope, they were verified under dependency failure
   and slow states;
4. runtime output or tests confirmed emitted signals and audit entries for the
   inspected area;
5. external infra/alerting layers outside the repo are disclosed as `UNKNOWN`
   if not inspected.

If any item is missing, use “proposed”, “partially verified”, “not observed”,
or “requires validation”.
