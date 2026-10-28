# Consistency and Write Policies

Cache reads and writes must agree on what happens after the source of truth
changes. Choose a policy explicitly rather than mixing behaviors accidentally.

## Cache-aside

The application reads the cache first and reads the origin on a miss. After a
successful origin write, invalidate or update the affected cache key. This is a
common default, but it requires a plan for invalidation failure and concurrent
read/write races.

## Write-through

The write path updates the cache and origin as one logical operation. Define
ordering, retry, rollback, and partial-failure behavior. Do not describe this
as atomic unless the actual backend and transaction model provide that
guarantee.

## Write-behind

The cache accepts writes before the origin is updated. This requires a durable
queue, replay behavior, ordering guarantees, conflict handling, and a clear
data-loss policy. It must not be introduced as a simple performance tweak.

## Mutation rules

For create, update, and delete, specify:

- which write is authoritative;
- when the cache is invalidated or populated;
- what happens if invalidation fails;
- how stale readers are bounded;
- how concurrent writes are ordered;
- how schema or representation versions change;
- how repair or reconciliation is performed.

If the system cannot guarantee immediate invalidation, use versioned keys,
shorter TTL, event replay, or another documented mechanism to bound staleness.
