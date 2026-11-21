# I/O and Database Efficiency

I/O often dominates CPU improvements. Optimize the number, size, and timing of
database, filesystem, network, and serialization operations.

## Review checklist

- Are queries repeated inside loops?
- Can reads be batched, joined, paginated, or streamed?
- Are only required columns and fields selected?
- Are indexes aligned with actual filters and sort order?
- Are connection pools, timeouts, and retries bounded?
- Is serialization performed more than once?
- Are remote calls made sequentially when safe parallelism is possible?
- Is backpressure applied when the consumer is slower than the producer?

Avoid batching that creates unbounded request or memory size. Avoid parallel I/O
that overwhelms the dependency. Preserve authorization and transaction
boundaries when changing query or request shape.

## Connection pools

Configure and verify every database and remote-client pool explicitly:

- **Pool bounds**: set maximum open connections relative to instance count and
  downstream capacity, and bound pool-acquisition wait timeouts so saturation
  fails fast instead of piling up blocked callers.
- **Idle connection limits**: set explicit minimum/maximum idle connection counts
  to avoid holding excessive unused connections while preventing constant
  connect/TLS churn under steady load.
- **Idle timeout and max lifetime**: expire idle connections and rotate long-lived
  connections before upstream NAT, firewall, or database idle-kill deadlines.
- **Stale idle handling**: validate or safely evict broken idle connections so
  dead sockets do not fail live requests after quiet periods.

When caching is considered, use the cache references and prove that cache miss,
expiration, outage, and invalidation behavior are correct.
