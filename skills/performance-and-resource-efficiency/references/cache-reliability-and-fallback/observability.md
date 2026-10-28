# Observability and Validation

Caching without evidence encourages false confidence. Instrument the complete
path from cache request to origin fallback.

## Metrics

Track, preferably by cache layer and operation:

- hits and misses;
- expired entries;
- evictions and capacity pressure;
- backend errors and timeouts;
- fallback reads;
- database reads caused by fallback;
- cache population success and failure;
- lookup and refill latency;
- entry count and estimated bytes;
- stale responses and refresh failures;
- database concurrency used by fallback;
- single-flight/coalescing group size and wait time;
- circuit-breaker state and rejected attempts;
- cache bypass or kill-switch activation.

Use bounded labels. Do not put raw user IDs or unbounded cache keys into metric
labels.

## Logs and traces

Record the selected path and failure reason without exposing secrets or full
sensitive values. Trace whether the response came from local cache, shared
cache, database, stale data, or an error path.

## Test matrix

Verify at minimum:

1. no cache configured;
2. cold cache;
3. warm cache;
4. cache miss;
5. expired entry;
6. LRU eviction;
7. local cache restart;
8. shared backend timeout or outage;
9. malformed value;
10. database fallback success;
11. database failure;
12. cache repopulation;
13. invalidation or namespace rotation;
14. concurrent misses for one key.

Also verify database protection under cache outage, write/invalidation ordering,
security boundaries, operational bypass controls, and recovery after backend
restoration.

Tests should prove behavior, not just the presence of a cache object or a
configuration value.
