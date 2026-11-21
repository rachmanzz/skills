# Idempotency and Data Lifecycle

## Idempotency Audit

Verify that repeated, retried, or concurrently replayed requests in the inspected
scope do not produce duplicate records, double charges, or unintended state
transitions.

### Mutation API & command idempotency

- **Idempotency key contract**: for non-idempotent creates/mutations (`POST`,
  webhooks, payments, state transitions), verify how a client or producer
  supplies an idempotency key and where that key is persisted atomically with
  the business mutation.
- **Payload mismatch protection**: verify that reusing an existing idempotency
  key with a different request payload or actor is rejected (e.g., `409`/`422`)
  rather than silently returning the earlier response.
- **Concurrent duplicate handling**: verify what happens when two identical
  requests arrive simultaneously before the first finishes (atomic unique claim
  or in-progress lock/status, never two parallel executions).
- **Failure and expiry semantics**: distinguish failed attempts that can be
  retried under the same key from completed results that must replay safely;
  define key retention/TTL aligned with client retry windows.
- **Natural idempotency**: for `PUT`/`DELETE`/state-machine transitions, verify
  conditional updates or unique constraints make repeats safe without relying on
  client honesty.

## Data Lifecycle Audit

Verify how records are created, updated, deactivated, archived, expired, and
permanently purged across their full lifetime.

### Create and update

- Verify auditability where required (`created_at`, `updated_at`, actor/version
  columns) and ensure immutable fields (owner, tenant, primary keys, historical
  snapshots) cannot be overwritten on `UPDATE`.

### Delete (soft vs hard) and cascades

- **Soft delete consistency**: if soft deletion (`deleted_at` / `is_deleted`) is
  used, verify that:
  - queries, joins, caches, and search indexes in scope filter deleted records
    consistently;
  - `UNIQUE` indexes account for soft-deleted rows (e.g., partial unique index
    `WHERE deleted_at IS NULL`) so re-creation is not blocked or leaked;
  - child records and references handle parent soft-delete predictably.
- **Hard delete & cascades**: verify foreign-key `ON DELETE` rules (`RESTRICT`,
  `CASCADE`, `SET NULL`) match domain safety so deleting a parent neither fails
  unexpectedly nor silently wipes critical audit/financial history.

### Archive, expiration, and retention

- **Archival boundaries**: verify cold/archived data moves atomically without
  duplication or loss, preserves referential links or snapshots, and cannot be
  mutated accidentally via active endpoints.
- **Expiration and purging**: verify TTLs, retention windows, scheduled cleanup
  jobs, and PII anonymization/deletion paths are bounded (batched to limit lock
  duration and escalation), respect legal/audit holds, and invalidate stale
  caches or search indexes when records expire or purge.
