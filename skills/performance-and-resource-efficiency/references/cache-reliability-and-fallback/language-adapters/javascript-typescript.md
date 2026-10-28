# JavaScript and TypeScript Adapter

Apply the core cache contract first. Choose a bounded in-process cache library
only when process-local behavior is acceptable. The `lru-cache` package is one
possible implementation of LRU; it is not a substitute for a shared backend or
database fallback.

Verify asynchronous cache clients with explicit operation timeouts. A rejected
cache promise must continue to the configured fallback rather than becoming an
unhandled rejection or silently returning an empty result.

For Redis or Memcached clients, define serialization, connection lifecycle,
retry limits, namespace handling, and behavior during reconnects. Test both a
local LRU miss and a remote-cache outage.
