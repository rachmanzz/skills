---
name: data-integrity-and-lifecycle
description: Audit, design, or fix data persistence and mutation safety—covering data integrity (constraints, types, migrations), cross-table/service/cache data consistency, transaction safety (atomicity, rollback, partial commit), concurrent data mutations (races, locking, deadlocks), mutation idempotency, and data lifecycle (create, update, delete, archive, expiration). Use when reviewing schemas, queries, transactions, or CRUD/mutation endpoints. For async worker lifecycles and delivery durability, use evidence-led-concurrency-and-delivery.
metadata:
  short-description: Audit data integrity, consistency, transactions, concurrency, idempotency, and lifecycle
---

# Data Integrity and Lifecycle

Use this skill to audit, design, or harden data correctness across schemas,
migrations, queries, transactions, mutation APIs, caches, and lifecycle jobs.

This skill complements—and does not replace—the repository's adjacent skills:

- Use `evidence-led-concurrency-and-delivery` when the primary concern is
  asynchronous/concurrent execution lifecycles, worker leaks, lease/visibility
  ownership, queue backpressure, or durable message delivery ordering.
- Use `performance-and-resource-efficiency` when the primary concern is
  profiling, algorithmic complexity, query indexing/N+1 speedups, or cache
  sizing, LRU capacity, eviction/write policies, and fallback mechanics.
- Use `resilience-and-error-handling` when the primary concern is error
  classification, silent errors, circuit breaking, blast-radius isolation, or
  retry/timeout budgets.
- Use `business-logic-and-input-validation` when the primary concern is domain
  business rules, boundary/calculation math, state-machine workflows, or
  request input sanitization.
- Use `observability-and-audit-trail` when the primary concern is append-only
  activity audit trails, telemetry, or health checks.

Read only the references needed for the current task:

- Read [evidence-and-assumption-control.md](references/evidence-and-assumption-control.md)
  before making claims about schema guarantees, atomicity, concurrency safety,
  idempotency, or lifecycle behavior.
- Read [integrity-and-consistency.md](references/integrity-and-consistency.md)
  for database constraints, types/precision, safe migrations, cross-table and
  cross-service consistency, and cache-to-source agreement.
- Read [transactions-and-concurrency.md](references/transactions-and-concurrency.md)
  for transaction boundaries, rollback safety, partial commits, read-modify-write
  races, isolation levels, locking, and deadlock prevention.
- Read [idempotency-and-lifecycle.md](references/idempotency-and-lifecycle.md)
  for mutation API idempotency contracts and full data lifecycle controls
  (create, update, soft/hard delete, archive, expiration, retention).
- Read [validation-matrix.md](references/validation-matrix.md) when designing
  concurrency, rollback, constraint, or lifecycle tests.

## Non-negotiable rules

1. Treat ORM validations, application-layer `if` checks, and helper names as
   hypotheses, not proof of database integrity or concurrency safety.
2. Classify important claims as `VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`,
   `PARTIAL`, `NOT_FOUND_IN_SCOPE`, or `UNKNOWN`. Never upgrade `UNKNOWN` to
   `VERIFIED_IN_SCOPE` because an ORM model or helper looks plausible, and
   preserve counterexamples as `CONTRADICTED_IN_SCOPE`.
3. Keep verified behavior, proposed fixes, test observations, and inference
   visibly separate. Never turn mocks, test names, or single-threaded tests
   into proof of concurrent/production safety, and never invent unstated
   retention, cascade, or isolation guarantees (mark `UNKNOWN` and log in an
   assumption ledger).
4. Enforce critical invariants (`NOT NULL`, `UNIQUE`, `CHECK`, foreign keys,
   atomic conditional updates) in the persistence layer—never rely solely on
   preceding `SELECT` checks or process-local locks for data shared across
   instances.
5. Never hold slow external network/HTTP I/O inside an active database
   transaction, and never describe multi-system dual writes as atomic without an
   outbox, saga, or verified compensation contract.
6. Verify transaction propagation and rollback paths on every error or early
   return so partial commits cannot escape silently.
7. Require explicit idempotency contracts (key binding, payload and actor
   mismatch rejection, concurrent duplicate handling) on non-idempotent mutation
   APIs.
8. Verify soft-delete filtering, partial unique indexes, foreign-key cascades,
   archival boundaries, and bounded purge/expiration behavior across inspected
   queries and caches.
9. Distinguish test engines (e.g., mocks or SQLite) from production storage
   isolation and locking semantics; never extrapolate single-threaded tests to
   concurrent safety.

## Audit workflow

### 1. Map data stores, schemas, and mutation paths

Identify all tables, collections, caches, derived projections, migrations, and
create/update/delete/archive endpoints or jobs in scope. Note the database
engine, configured isolation level, and multi-instance deployment topology.

### 2. Build the evidence and assumption ledgers

Record material claims and unverified assumptions separately using
[evidence-and-assumption-control.md](references/evidence-and-assumption-control.md).
Inspect actual DDL/migrations, SQL/ORM queries, transaction wrappers, and cache
hooks—not just model classes or happy-path unit tests.

### 3. Audit data integrity and consistency

Apply [integrity-and-consistency.md](references/integrity-and-consistency.md) to
verify schema constraints, numeric/time precision, safe migrations, cross-table
denormalization sync, dual-write failure windows, and cache-to-source agreement.

### 4. Audit transaction safety and concurrent mutations

Apply [transactions-and-concurrency.md](references/transactions-and-concurrency.md)
to verify transaction boundaries, rollback behavior, helper tx propagation,
absence of external I/O inside transactions, protection against lost updates /
TOCTOU races, isolation levels, and canonical lock ordering.

### 5. Audit idempotency and data lifecycle

Apply [idempotency-and-lifecycle.md](references/idempotency-and-lifecycle.md) to
verify mutation idempotency keys, payload-conflict rejection, concurrent
duplicate protection, immutable fields, soft/hard delete consistency, archival,
and bounded expiration/purging.

### 6. Implement and validate

Apply the smallest targeted fix per boundary and validate with constraint tests,
rollback/partial-failure injection, concurrent race tests, duplicate replay
tests, and lifecycle checks using [validation-matrix.md](references/validation-matrix.md).

## Required report shape

Include only applicable sections; mark non-applicable sections `OUT_OF_SCOPE`
with a short reason:

1. Scope, storage engines, isolation settings, and mutation/schema map.
2. Evidence ledger for material data-safety claims.
3. Data integrity & consistency findings (schema, cross-table, service, cache).
4. Transaction safety & concurrent mutation findings.
5. Idempotency & data lifecycle findings (create, update, delete, archive, expiry).
6. Validation performed and exact observed results.
7. Assumptions, uninspected stores/services, and remaining risks (`CONTRADICTED_IN_SCOPE`,
   `PARTIAL`, `NOT_FOUND_IN_SCOPE`, `UNKNOWN`).
