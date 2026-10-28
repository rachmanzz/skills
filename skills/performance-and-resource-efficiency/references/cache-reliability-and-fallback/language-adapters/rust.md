# Rust Adapter

Choose a cache implementation with explicit ownership, synchronization, size,
and expiration semantics. Do not use an unbounded map as a production cache
without a documented capacity policy.

For async remote backends, set operation deadlines and classify timeout,
connection, serialization, miss, and expiration outcomes separately. Preserve
the database fallback when a cache future fails.
