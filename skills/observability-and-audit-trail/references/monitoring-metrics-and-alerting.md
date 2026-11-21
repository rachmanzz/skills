# Monitoring, Metrics, and Alerting

## Monitoring and Metrics Audit

Verify that golden signals, dependency saturation, and business-critical
failures are measured accurately without exploding metric cardinality.

### Checklist

- **Four Golden Signals per boundary**: measure **Latency** (aggregatable
  histograms for p50/p95/p99 across instances rather than averages or
  non-aggregatable client summaries alone), **Traffic** (RPS/throughput),
  **Errors** (classified by error type/status/dependency), and **Saturation**
  (DB pool in-use/wait, queue depth, worker utilization, memory/CPU).
- **Silent-degradation & reliability counters**: expose counters/gauges for
  retries, timeouts, circuit-breaker state changes, cache fallbacks, DLQ
  enqueues, and dropped/shed requests.
- **Cardinality discipline**: strictly forbid unbounded values (`user_id`,
  `order_id`, `request_id`, raw URL path with IDs, raw error messages) as metric
  labels; use normalized route templates (`/orders/{id}`) and bounded enums.
- **Histogram bucket alignment**: verify latency histogram buckets cover the
  service's actual SLO/timeout range (for example, milliseconds to seconds).

## Alerting Audit

Verify that critical failures and degradation states produce timely, actionable
alerts rather than failing quietly or paging on noise.

### Checklist

- **Symptom & SLO coverage**: alert on sustained error-rate spikes, tail-latency
  SLO burn, dependency saturation, pool exhaustion, queue-lag growth, DLQ
  accumulation, and failed scheduled/cleanup jobs.
- **Missing alerts on degraded paths**: verify that fallback activation, open
  circuit breakers, and skipped batch items trigger warnings/alerts when
  sustained rather than being hidden by 200 OK fallback responses.
- **Noise & false-positive hygiene**: ensure alerts use sustained evaluation
  windows (`for:` duration) and clear thresholds/severity tiers (`page` vs
  `ticket`), with runbook pointers and exact failing component context.
- **Dead-man / heartbeat alerts**: verify critical cron/worker pipelines alert
  when they stop running altogether, not only when they throw an exception.
