# Operational Controls

Caching needs controls for rollout, incidents, deployments, and recovery.

## Recommended controls

- feature flag to enable or disable each cache layer;
- kill switch that bypasses a failing cache;
- health check and readiness signal for shared backends;
- warm-up or controlled prefill for high-value keys;
- namespace or generation rotation during deployments;
- drain behavior for old cache generations;
- emergency TTL or stale-data policy;
- dashboard and alerts for hit rate, fallback rate, evictions, and database
  load.

Disabling a cache must leave a correct origin path. A kill switch must not be
implemented as a configuration change that still calls an unreachable backend.

## Rollout

Introduce cache behavior behind a measurable rollout. Compare origin load,
latency, correctness, stale responses, and error rates before increasing scope.
Document how to revert the change without deleting the source of truth.

## Recovery

After a cache backend recovers, avoid an uncontrolled refill storm. Use bounded
warm-up, request coalescing, jitter, or gradual traffic restoration.
