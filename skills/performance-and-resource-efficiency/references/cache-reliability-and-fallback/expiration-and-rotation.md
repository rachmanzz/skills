# Expiration and Rotation

Expiration is a correctness and capacity control, not only a performance
feature. Every cache needs a deliberate freshness boundary.

## Expiration strategies

- **TTL:** expire an entry after a fixed duration.
- **Absolute expiration:** expire at a known timestamp.
- **Sliding expiration:** extend lifetime on access, only when bounded by a
  hard maximum age.
- **Event invalidation:** remove or version entries after a source-of-truth
  write.
- **Stale-while-revalidate:** serve bounded stale data while one worker refreshes
  the entry.

Avoid unbounded sliding expiration. A frequently requested record must still be
replaced or revalidated eventually.

## Rotation

Use rotation when an entire logical group of entries must be replaced without
enumerating every key. A common pattern is a generation or namespace value:

```text
entity:{generation}:{id}
```

Advance the generation after a deployment, schema change, tenant reset, or
bulk data change. Keep old generations bounded with TTL and remove them only
when the backend supports safe cleanup.

## Stampede protection

Add TTL jitter, request coalescing, single-flight behavior, locking, or
stale-while-revalidate when many requests can expire the same key at once.
Ensure the protection itself has timeouts and does not become a deadlock.

## Refresh and invalidation

Cache population after a database read should be best effort by default. A
failed population must not erase a valid origin response. For writes, choose
and document one policy:

- invalidate after a successful origin write;
- update the cache after a successful origin write;
- use versioned keys and let old entries expire;
- use an event stream to invalidate asynchronously.
