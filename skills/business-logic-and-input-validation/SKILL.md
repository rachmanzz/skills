---
name: business-logic-and-input-validation
description: Audit, design, or fix domain correctness and input safety—covering business logic alignment, boundary conditions (min/max/empty/overflow), state transitions, domain invariants, calculation accuracy (rounding/precision), and input validation/sanitization. Use when reviewing domain rules, pricing/ledger math, workflows, or request validation. For DB constraints and concurrent mutations, use data-integrity-and-lifecycle; for security exploits, use application-security-and-isolation.
metadata:
  short-description: Audit business rules, boundaries, state transitions, invariants, calculations, and inputs
---

# Business Logic and Input Validation

Use this skill to verify that domain rules, edge-case boundaries, state
machines, invariants, calculations, and input validation behave accurately and
consistently across all application entry points.

This skill complements—and does not replace—the repository's adjacent skills:

- Use `data-integrity-and-lifecycle` when the primary concern is database
  constraints, migrations, transaction isolation, concurrent DB mutations, API
  idempotency, or archival/retention lifecycles.
- Use `application-security-and-isolation` when the primary concern is
  authentication, authorization, tenant isolation, injection exploits, or
  secret/information exposure.
- Use `api-contracts-and-integrations` when the primary concern is wire schema
  contracts, versioning compatibility, webhooks, or serialization encoding.

Read only the references needed for the current task:

- Read [evidence-and-assumption-control.md](references/evidence-and-assumption-control.md)
  before claiming business rules, calculations, or validations hold.
- Read [business-logic-and-invariants.md](references/business-logic-and-invariants.md)
  for domain rule fidelity, cross-field invariants, and partial-update safety.
- Read [boundary-conditions-and-calculations.md](references/boundary-conditions-and-calculations.md)
  for min/max/empty/overflow checks, date/DST edges, rounding, and precision.
- Read [state-transitions-and-validation.md](references/state-transitions-and-validation.md)
  for state-machine guards, terminal states, and allowlist input validation.
- Read [validation-matrix.md](references/validation-matrix.md) when designing
  negative, boundary, precision, or state-transition tests.

## Non-negotiable rules

1. Treat UI validation, comments, and happy-path tests as hypotheses, not proof
   of domain or boundary correctness.
2. Classify important claims as `VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`,
   `PARTIAL`, `NOT_FOUND_IN_SCOPE`, or `UNKNOWN`. Never upgrade `UNKNOWN` to
   `VERIFIED_IN_SCOPE` because logic looks plausible, and preserve counterexample
   inputs as `CONTRADICTED_IN_SCOPE`.
3. Keep verified behavior, proposed changes, test observations, and inference
   visibly separate. Never invent unstated business rules, thresholds, or
   rounding modes—mark missing specifications `UNKNOWN` and record them in an
   assumption ledger.
4. Never rely on binary floating-point arithmetic for monetary or exact decimal
   calculations unless a documented domain specification explicitly permits
   approximate float precision.
5. Enforce state-machine transitions via explicit `(from_state -> to_state)`
   guards; reject unrecognized states and terminal-state mutations fail-closed.
6. Re-validate cross-field and aggregate invariants against the merged post-edit
   state on partial updates.
7. Validate and canonicalize untrusted inputs at every entry point (HTTP, RPC,
   CLI, queue consumers, webhooks) before executing business logic.

## Audit workflow

### 1. Map domain rules and entry points

List the authoritative business rules, state machines, calculations, and all
entry points that can trigger or mutate them. Mark unstated business rules or
rounding policies as `UNKNOWN` instead of guessing.

### 2. Build the evidence and assumption ledgers

Record material claims and unverified assumptions separately using
[evidence-and-assumption-control.md](references/evidence-and-assumption-control.md).

### 3. Audit business logic and invariants

Apply [business-logic-and-invariants.md](references/business-logic-and-invariants.md)
to verify rule parity across entry points, temporal/actor checks, and merged
cross-field invariants.

### 4. Audit boundary conditions and calculations

Apply [boundary-conditions-and-calculations.md](references/boundary-conditions-and-calculations.md)
to check zero/empty/min/max/overflow cases, pagination/date boundaries, exact
decimal/minor-unit math, rounding, remainder allocation, and zero-division
guards.

### 5. Audit state transitions and input validation

Apply [state-transitions-and-validation.md](references/state-transitions-and-validation.md)
to verify transition guards, terminal-state protection, canonicalization-before-validation,
allowlists, and payload bounds.

### 6. Implement and validate

Fix findings at the authoritative domain/entry boundary and verify with
boundary, precision, invalid-state, and negative input tests from
[validation-matrix.md](references/validation-matrix.md).

## Required report shape

Include only applicable sections; mark non-applicable sections `OUT_OF_SCOPE`
with a short reason:

1. Scope, authoritative rule sources, and entry points inspected.
2. Evidence ledger for material correctness claims.
3. Business logic & invariant findings.
4. Boundary condition & calculation accuracy findings.
5. State transition & input validation findings.
6. Validation performed and exact observed results.
7. Assumptions, uninspected paths, and remaining risks (`CONTRADICTED_IN_SCOPE`,
   `PARTIAL`, `NOT_FOUND_IN_SCOPE`, `UNKNOWN`).
