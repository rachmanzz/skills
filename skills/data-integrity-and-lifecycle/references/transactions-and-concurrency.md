# Transaction Safety and Concurrent Mutations

## Transaction Safety Audit

Verify that multi-step state changes uphold atomicity, isolation, and clean
failure recovery without partial commits.

### Atomicity and boundaries

- **Single logical unit**: group coupled reads-for-update and multi-table writes
  inside one database transaction when they share one storage engine.
- **Rollback completeness**: verify every error, panic, or early return inside a
  transaction rolls back cleanly and never commits partial state on `finally` or
  cleanup paths (noting that abrupt process termination such as `SIGKILL` or OOM
  relies on database connection-drop rollback rather than in-process `finally`
  handlers).
- **No external I/O inside DB transactions**: flag HTTP/gRPC calls, slow queue
  publishes, or external locks held open inside an active database transaction
  (which causes long lock holds, pool exhaustion, and uncertain commit vs
  rollback outcomes).
- **Non-transactional side effects**: when an operation spans a database and an
  external service, file store, or separate database, map the failure window
  explicitly (outbox, two-phase state machine, or compensating action).

### Partial commit and batch safety

- For multi-item or multi-table updates, verify whether partial success is
  forbidden (all-or-nothing transaction) or explicitly modeled per item with
  observable outcomes.
- Verify transaction propagation across helper functions so nested helpers do not
  accidentally open separate auto-committed connections outside the caller's
  transaction.

## Concurrency Audit (Mutations & Locking)

Verify how concurrent requests or jobs mutating the same data prevent lost
updates, double spending/allocation, and constraint races, and handle or bound
deadlocks safely.

### Race conditions and lost updates

- **Read-modify-write races**: flag any pattern that reads a row/value, computes
  a new state in application memory, and writes it back without:
  - atomic conditional update (`UPDATE ... WHERE version = ?` or `balance >= ?`),
  - pessimistic row lock (`SELECT ... FOR UPDATE`), or
  - `SERIALIZABLE` conflict handling with bounded retry (noting that `REPEATABLE READ` /
    snapshot isolation alone prevents lost updates on the same row but does not
    prevent multi-row/cross-table write skew).
- **Check-then-act (TOCTOU) races**: verify uniqueness, quota, and balance
  checks are enforced atomically in the write/constraint itself (`INSERT ... ON
  CONFLICT` / unique index), not by a preceding `SELECT` check alone.
- **In-process vs multi-instance locking**: do not treat process-local mutexes
  as sufficient protection for data shared across multiple app instances.

### Isolation levels and deadlocks

- Verify the configured transaction isolation level matches the invariant being
  protected (e.g., `READ COMMITTED` does not prevent non-repeatable reads or
  phantom writes without explicit row locks or unique constraints).
- **Deadlock prevention**: check lock acquisition order across multi-row or
  multi-table transactions; enforce a consistent canonical ordering (e.g., sort
  account IDs before locking) and set lock/statement timeouts.
- Verify serialization failures or deadlock errors are either surfaced clearly or
  retried safely only when the entire transaction block is idempotent.
