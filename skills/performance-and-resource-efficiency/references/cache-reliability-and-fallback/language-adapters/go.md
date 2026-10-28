# Go Adapter

Choose a concurrency-safe bounded cache for shared access within a process.
Define context deadlines for Redis, Memcached, or other remote clients.

Do not assume that a process-local cache is shared across replicas. Make the
fallback function explicit and avoid recursive cache lookups. Test behavior
when a cache client returns an error, a stale value, or a serialization failure.
