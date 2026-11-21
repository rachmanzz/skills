# Data Integrity and Consistency

## Data Integrity Audit

Verify that stored and transmitted data in the inspected scope is guarded
against silent corruption, loss, or persistence in invalid states.

### Schema and domain invariants

- **Database-enforced constraints**: verify `NOT NULL`, `UNIQUE`, `CHECK`, and
  foreign-key (`REFERENCES`) constraints exist in the schema/migrations rather
  than relying solely on application-layer validation.
- **Types, precision, and units**: check monetary values (decimal/integer minor
  units vs binary float), timestamps/timezones (UTC vs naive local time), enum
  boundaries, and string length/encoding limits so truncation or rounding never
  corrupts values silently.
- **Nullability and sentinel abuse**: distinguish missing/unset (`NULL`) from
  meaningful values (`0`, `""`, `false`); avoid magic sentinel strings/IDs.
- **Referential integrity and state invariants**: check whether child records
  can outlive deleted parents, whether state-machine transitions validate
  allowed predecessors, and whether multi-column invariants (e.g., `start <= end`)
  are enforced.
- **Schema evolution and migrations**: verify migrations are backward-safe for
  rolling deploys, handle existing rows/backfills without data loss, and
  preserve constraints during column/table refactors.

### Input and serialization boundaries

- Reject malformed or unknown critical fields instead of silently coercing or
  dropping them.
- Validate deserialized payloads from queues, caches, or external blobs against
  explicit schema/version expectations before trusting them.

## Data Consistency Audit

Verify agreement across tables, derived projections, services, and caches when
data is created, updated, or deleted.

### Cross-table consistency

- **Normalized vs denormalized copies**: identify duplicated summaries,
  counters, status mirrors, or snapshot columns in scope; verify how each is
  updated atomically or reconciled when source rows change.
- **Orphan and dangling state**: check multi-table writes or deletes for failure
  windows that can leave orphan child rows, dangling references, or mismatched
  totals.

### Cross-service consistency

- **Dual-write traps**: flag any path that writes to a local DB and then calls
  another service, broker, or object store without an atomic outbox, saga,
  compensation, or reconciliation job.
- **Eventual consistency contracts**: when asynchronous propagation is used,
  define ordering, idempotent consumers, staleness expectations, and repair
  mechanisms for dropped or out-of-order events.

### Cache-to-source consistency

- Verify write paths invalidate, version, or update affected cache entries after
  authoritative source writes (for cache-aside, write-through, and write-behind
  policies, apply `performance-and-resource-efficiency/references/cache-reliability-and-fallback/`).
- Check read-after-write flows so a user's immediate subsequent read does not
  observe stale cached or replica data when read-your-writes consistency is
  required.
- Bound staleness with explicit TTLs, versioned keys, or reconciliation when
  invalidation can fail.
