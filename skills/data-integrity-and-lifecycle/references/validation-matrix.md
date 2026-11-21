# Validation Matrix

Use this matrix as a starting point when reviewing or testing data integrity,
consistency, transactions, concurrency, idempotency, and data lifecycle paths.
Remove irrelevant rows and add domain-specific invariants. A passing test on a
mock or single-threaded fixture does not prove multi-connection safety.

| Area | Scenario | Expected invariant | Evidence to record |
| --- | --- | --- | --- |
| Data Integrity | Invalid types, out-of-range precision, NULL, or broken foreign key | Persistence rejects invalid state at DB constraint as well as app validation; no silent truncation or orphan row | Migration/constraint DDL and negative test result |
| Data Integrity | Rolling schema migration with existing rows | Existing data remains valid and readable by old and new code without constraint loss | Migration script, backfill check, and compatibility test |
| Data Consistency | Multi-table write or denormalized summary update fails mid-way | Either all coupled tables roll back atomically or reconciliation repairs drift cleanly | Transaction scope, error test, and post-failure DB state |
| Data Consistency | Source mutation with cache or secondary store | Affected cache keys invalidate/version or bound staleness; read-after-write returns fresh authoritative state when required | Cache invalidation trace and read-after-write test |
| Transaction Safety | Error or panic midway through multi-step transaction | All uncommitted writes roll back; no partial commit and no external I/O left inconsistent | Rollback test output and table row counts before/after |
| Transaction Safety | Helper called inside parent transaction | Helper participates in the caller's transaction instead of opening a separate auto-committed connection | Connection/tx propagation trace and rollback test |
| Concurrency | Two concurrent read-modify-write mutations on same record | No lost update; enforced by atomic conditional update, row lock, or version conflict retry | Parallel test (N goroutines/threads) and final balance/version |
| Concurrency | Concurrent duplicate creates racing past a `SELECT` check | Unique DB constraint prevents duplicates; loser receives clean conflict or idempotent replay | Concurrent create test and DB row count (= 1) |
| Concurrency | Opposite-order multi-row updates | Canonical lock order prevents deadlock, or deadlock timeout + safe retry resolves cleanly | Concurrent cross-order test and DB deadlock logs |
| Idempotency | Same `Idempotency-Key` sent concurrently or after completion | Only 1 side effect executes; identical replay returns stored result; different payload or actor with same key is rejected (409/422) | Request replay trace, DB side-effect count, and conflict test |
| Data Lifecycle | Soft-deleted parent or unique-key re-creation | Soft-deleted rows are excluded from active reads/caches/indexes and do not break legitimate re-creation | Query/index inspection and soft-delete + recreate test |
| Data Lifecycle | Archival, expiration, or retention purge job | Records move/expire/purge in bounded batches without locking active traffic or leaving dangling cache/index entries | Batch size/bounds, residual row check, and cache state |

For each executed scenario record:

- exact database engine, isolation level, and configuration;
- concurrency level, command, or test executed;
- observed database state, constraints triggered, or error outputs;
- inspected scope and limitations (e.g., SQLite vs production PostgreSQL);
- claim status (`VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`, `PARTIAL`, `NOT_FOUND_IN_SCOPE`, or `UNKNOWN`);
- unresolved assumptions.
