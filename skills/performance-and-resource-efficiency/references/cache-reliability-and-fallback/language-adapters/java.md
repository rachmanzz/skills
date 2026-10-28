# Java Adapter

Use a bounded in-process cache implementation when local caching is appropriate
and configure maximum size, weight, expiration, and removal behavior explicitly.

For Redis, Memcached, or another shared backend, define client timeouts,
serialization compatibility, retry policy, namespace versioning, and fallback
behavior. Verify that an eviction or backend exception reaches the database
path rather than becoming an empty response.
