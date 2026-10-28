# Shared Cache Backends

Choose the backend from the required scope, consistency, latency, durability,
and operational model. Do not silently substitute one backend for another.

## Local process cache

Use for very low-latency, disposable data. It is isolated per process and
usually disappears on restart or deployment. It cannot by itself guarantee
cross-process consistency.

## Redis

Use when shared access, richer data structures, coordination, or explicit
server-side controls are required. Define network timeouts, serialization,
namespace isolation, authentication, memory policy, failure handling, and what
happens during reconnects or failover.

## Memcached

Use for simple shared key-value caching when its eviction and durability model
fits the workload. Treat entries as disposable and define behavior when the
cluster evicts or loses data.

## Other distributed stores

For any other backend, document:

- availability and timeout behavior;
- consistency model;
- maximum value size;
- serialization and compatibility;
- memory and eviction controls;
- tenant and namespace isolation;
- observability and operational ownership;
- database fallback during outages.

The application must remain correct when the shared cache is empty or
unreachable unless the user explicitly designs the cache as authoritative.
