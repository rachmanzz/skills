# Evidence and Assumption Control

Use this reference before describing existing behavior, claiming a fix is
complete, or stating that a reliability guarantee holds.

## Claim statuses

| Status | Meaning |
| --- | --- |
| `VERIFIED_IN_SCOPE` | A specifically scoped claim is supported by direct evidence, and the relevant validation produced the stated observation within that boundary. |
| `CONTRADICTED_IN_SCOPE` | Direct evidence or a valid counterexample refutes the stated claim within its named scope. Preserve the counterexample and its conditions. |
| `PARTIAL` | The claim holds only for identified paths, inputs, configurations, or failure modes. |
| `NOT_FOUND_IN_SCOPE` | A named scope was searched and no supporting implementation or evidence was found there. This does not prove global absence. |
| `UNKNOWN` | Available evidence is insufficient, unresolved, stale, or not runtime-confirmed for the claim being made. |

State the actual evidence boundary for each claim: relevant paths, versions,
configuration, inputs, environment, scenario, and observation window where
applicable. A passing test establishes only what it observed under its tested
conditions; do not extend it to untested paths, schedules, failures, or runtime
environments. Code inspection can establish what code specifies in the inspected
path without establishing that it ran or that the system behaved as intended.

For conflicting evidence, check whether the observations concern the same
version, configuration, and claimed scope. If a valid counterexample refutes
the claim, use `CONTRADICTED_IN_SCOPE` even if other scenarios passed. Reserve
`UNKNOWN` for conflicts that cannot be resolved from the available evidence.
Use `PARTIAL` for limited positive support with unverified coverage, not to hide
a demonstrated failure. A narrower claim may be verified separately without
erasing the original contradiction.

Do not use `NOT_FOUND_IN_SCOPE` merely because a search term failed. Name the
inspected boundary and search the relevant symbols, state transitions,
configuration, tests, generated behavior, dependencies, and operational hooks
that are available in that boundary. Use `UNKNOWN` when the boundary or runtime
evidence is incomplete. Never convert `NOT_FOUND_IN_SCOPE` into a claim that the
capability cannot exist elsewhere.

## Claim ledger

Create a ledger for material claims:

| Claim | Evidence | Status | Validation |
| --- | --- | --- | --- |
| What is asserted, including its scope | File, symbol, configuration, test, command, or runtime signal | One status above | How the status was or will be checked |

Examples of precise wording:

- “The code requests cancellation through the parent context.”
- “The test verifies that the caller observes a timeout.”
- “The inspected path does not prove that the underlying operation stopped.”
- “Duplicate handling is `UNKNOWN` because the side-effect boundary was not inspected.”

Avoid converting these into stronger claims such as “the task is cancelled” or
“the system is exactly-once” without evidence of the stronger property.

## Assumption ledger

Record assumptions separately:

| Assumption | Impact if false | Validation | Fallback |
| --- | --- | --- | --- |
| What must be true for the proposal | What behavior or safety property changes | Test, inspection, or runtime signal | Safe bounded behavior |

An assumption is not a fact. If it materially changes the design, either obtain
evidence or label the resulting design as conditional.

## Completion gate

Before saying “implemented”, “fixed”, “working”, “safe”, “durable”, “leak-free”,
or “tested successfully”, qualify the statement with its scope and require:

1. the relevant code or configuration was inspected;
2. the claim's scope is stated;
3. a relevant validation was run and observed;
4. failure and boundary conditions were considered;
5. unresolved assumptions are disclosed.

If any item is missing, use “proposed”, “partially verified”, “not observed”,
or “requires validation”.
