# LRU and Capacity

LRU means least recently used eviction. It is a policy for choosing what to
remove when a cache is full; it does not define where the cache is stored.

## Capacity must be explicit

Set one or more of:

- maximum entry count;
- maximum total bytes;
- weighted item size;
- maximum row or record count;
- per-tenant or per-namespace quota;
- TTL or idle timeout;
- maximum serialized value size.

An entry-count limit alone may be unsafe when values vary substantially in
size. Prefer weighted capacity or a memory budget when records are large or
unpredictable.

## LRU is not always the best policy

Use workload evidence to choose between LRU, LFU, FIFO, TinyLFU, segmented
policies, or a custom admission policy. Consider frequency, recency, item
cost, scan resistance, and the cost of refilling from the database.

## Required behavior on eviction

Eviction is expected. A later request for an evicted key must follow the
configured fallback chain and repopulate the cache when appropriate. It must
not be treated as proof that the database is missing the record.

## Capacity observability

Track entry count, estimated bytes, eviction count, eviction reason, refill
rate, and the database load caused by eviction. If an LRU causes excessive
refills, adjust capacity or policy using measurements rather than removing the
bound.

## Backend distinction

A local LRU is process-local and is lost during restart. Redis or Memcached may
provide shared storage, but their eviction policies, memory limits, persistence,
replication, and failure modes are backend-specific. Configure and verify the
actual backend instead of assuming that the word “LRU” guarantees a behavior.
