# Business Logic and Domain Invariants

## Business Logic Audit

Verify that implemented behavior matches the actual business rules across every
entry point (API handlers, background jobs, CLI/admin actions, webhooks).

### Checklist

- **Rule completeness and drift**: compare code conditions, thresholds,
  eligibility checks, and workflows against documented business rules. Flag
  divergent copies of the same rule across multiple endpoints or services.
- **Temporal & actor rules**: verify effective dates, expirations, cutoff
  times, actor roles/states, and approval prerequisites are evaluated in the
  intended order and timezone.
- **Branch & default-path safety**: inspect `else` / `default` branches so
  unrecognized cases fail closed instead of falling through to permissive
  behavior.
- **Side-effect ordering**: confirm business eligibility and preconditions are
  checked before irreversible side effects (payments, emails, state commits).

## Invariant Audit

Identify domain conditions that must **always** hold true before and after an
operation (for example, `available + reserved == total`, `discount <= subtotal`,
`end_at > start_at`, `refunded_amount <= captured_amount`).

### Checklist

- **Enforced at mutation boundaries**: verify invariants are checked inside
  domain constructors, state mutators, and service boundaries—not only in UI
  forms or one controller.
- **Cross-field & aggregate invariants**: verify multi-field relationships
  (e.g., percentage sums = 100%, min <= max, currency match across line items)
  are validated together whenever any constituent field changes.
- **No partial-update bypass**: ensure `PATCH` / update endpoints re-check
  cross-field invariants against the merged post-update state rather than only
  validating the single incoming field.
