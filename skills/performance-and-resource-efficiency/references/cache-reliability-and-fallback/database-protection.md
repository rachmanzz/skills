# Database Protection During Fallback

The database fallback keeps the application correct, but an unbounded fallback
can turn a cache outage into a database outage. Treat origin capacity as a
finite resource.

## Required controls

Choose controls based on the workload:

- **Request coalescing or single-flight:** one origin request refreshes a key
  while concurrent callers share the result.
- **Concurrency limits:** cap simultaneous cache refills and database reads
  caused by cache misses.
- **Circuit breaker:** stop attempting an unhealthy cache or origin for a
  bounded period and recover through controlled probes.
- **Backoff and jitter:** avoid synchronized retries and repeated pressure.
- **Rate limiting or load shedding:** protect the origin when demand exceeds
  capacity.
- **Stale-if-error:** serve bounded stale data when freshness requirements
  permit it.

## Failure requirements

Every queue, lock, coalescing group, retry, and circuit must have a timeout or
bounded lifetime. Never create an unbounded wait queue for a cache refill.

Classify cache failures separately from origin failures. A cache outage should
normally skip the cache and use a protected database path; a database outage
should produce the application's defined error or stale response.

## Validation

Test many callers requesting the same missing key, many different missing keys,
cache backend outage, slow database, retry storms, and circuit recovery. Verify
that database concurrency stays within the declared limit.
