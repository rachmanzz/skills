# Evidence and Assumption Control

Use this reference before describing existing schema guarantees, stating that
data is consistent or atomic, or claiming a concurrency, idempotency, or
lifecycle fix is complete.

## Claim statuses

| Status | Meaning |
| --- | --- |
| `VERIFIED_IN_SCOPE` | A specifically scoped claim is supported by direct schema, migration, query, or code inspection and observed test or runtime evidence within that boundary. |
| `CONTRADICTED_IN_SCOPE` | Direct evidence or a valid counterexample refutes the stated claim within its named scope. Preserve the counterexample and its conditions. |
| `PARTIAL` | The claim holds only for identified tables, endpoints, isolation levels, or mutation paths. |
| `NOT_FOUND_IN_SCOPE` | A named scope was searched and no supporting constraint, transaction, lock, or lifecycle rule was found there. This does not prove global absence. |
| `UNKNOWN` | Available evidence is insufficient, unresolved, stale, or not confirmed against the real database engine or runtime configuration. |

State the actual evidence boundary for each claim: inspected migrations,
schemas, queries, models, isolation settings, cache policies, and tests. Never
upgrade `UNKNOWN` to `VERIFIED_IN_SCOPE` because code or ORM annotations look
plausible. Keep verified behavior, proposed design, test observation, and
inference visibly separate. A test on an in-memory mock or SQLite does not
establish locking, isolation, or constraint behavior on PostgreSQL, MySQL, or
distributed storage. Do not turn a test name, migration filename, or configured
pool/isolation setting into proof of runtime safety until the scenario actually
ran against the target behavior.

For conflicting evidence, preserve valid counterexamples as
`CONTRADICTED_IN_SCOPE` even when happy-path CRUD tests pass. Do not use
`PARTIAL` to mask a demonstrated race condition, partial commit, or orphan
state.

Do not report `NOT_FOUND_IN_SCOPE` merely because a search term failed. Check
migrations, ORM/SQL definitions, triggers, middleware, application hooks, and
background jobs in the inspected scope.

## Claim ledger

Record material claims in a structured ledger:

| Claim | Evidence | Status | Validation |
| --- | --- | --- | --- |
| What is asserted, including scope | Migration, schema, query, code, or test | One status above | How the status was or will be checked |

Examples of precise wording:

- “`orders.user_id` has a foreign-key constraint in migration `0004`, verified against schema.”
- “Concurrent `POST /transfers` updates read balance outside the transaction (`CONTRADICTED_IN_SCOPE` in `transfer.go:44-62`).”
- “Cross-service inventory sync is `UNKNOWN` because the consumer service repository was not inspected.”

## Assumption ledger

Record assumptions separately and never invent unstated retention, cascade, or
consistency guarantees—mark missing contracts `UNKNOWN`:

| Assumption | Impact if false | Validation | Fallback |
| --- | --- | --- | --- |
| What must be true for correctness | Which integrity or consistency invariant breaks | Schema check, concurrency test, or query | Safe bounded behavior |

An assumption is not a fact. If it materially changes data safety or
durability, obtain evidence or label the design as conditional.

## Completion gate

Before saying “atomic”, “consistent”, “idempotent”, “no race observed in
tested schedule”, or “data-safe within scope”, qualify the statement with its
scope and require:

1. the relevant schema, migrations, queries, and mutation code were inspected;
2. the inspected boundary is stated explicitly;
3. relevant concurrency, rollback, constraint, or lifecycle validation ran and was observed;
4. partial-failure, duplicate-request, and stale-cache windows were checked;
5. unresolved assumptions and uninspected storage/services are disclosed.

If any item is missing, use “proposed”, “partially verified”, “not observed”,
or “requires validation”.
