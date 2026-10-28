# Python Adapter

Do not treat an unbounded dictionary or a function memoization decorator as a
production cache without checking capacity, expiration, concurrency, and
process scope. Select a bounded cache implementation that matches the runtime
and workload.

For async applications, use async-compatible clients and deadlines. For sync
applications, ensure that a slow shared-cache call cannot block the entire
request pool indefinitely.

Define how workers share or do not share local cache state, and test database
fallback after local eviction and shared-backend failure.
