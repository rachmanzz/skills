# Cache Fallback Flow

Use a cache-aside flow unless the application has a documented alternative.

```text
request
  -> build safe cache key
  -> read configured cache layers
      -> fresh hit: return value
      -> miss, expired, evicted, or invalid: continue
      -> timeout or backend error: record error and continue
  -> read database or origin
      -> success: return value and best-effort populate cache
      -> failure: return the application's defined origin error
```

## Important distinctions

- A cache miss means the layer answered successfully but did not contain a
  usable value.
- A cache error means the layer could not reliably answer.
- An expired value is not a fresh hit. It may be used only under an explicit
  stale-read policy.
- An eviction is normal bounded-cache behavior, not an application failure.

The default outcome for all four cases is to continue to the next configured
layer or the database.

## Multiple layers

If both local and shared caches exist, use a deliberate order such as:

```text
local LRU -> Redis/Memcached -> database
```

On a shared-cache hit, optionally populate the local cache. On a database hit,
populate the appropriate cache layers without making the response depend on a
successful cache write unless fail-closed behavior is required.

## Avoid fallback loops

The origin/database function must not call the cache lookup function again. Keep
the fallback boundary explicit and make cache bypass possible for repair jobs,
migrations, and emergency operations.

## Failure policy

Define separately:

- maximum cache operation timeout;
- whether one failed layer is skipped;
- whether all cache failures are sampled or rate-limited in logs;
- whether stale data may be served;
- whether database overload triggers throttling, backoff, or request coalescing.
