# C# Adapter

Configure in-process memory caches with explicit size limits, expiration, and
eviction behavior. A process-local cache is not shared automatically across
application instances.

For Redis, Memcached, or another shared backend, define cancellation/timeouts,
serialization, key namespaces, retry limits, and database fallback. Verify that
cache failure does not turn a valid database result into a false not-found
response.
