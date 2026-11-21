# Evidence and Assumption Control

Use this reference before describing existing error behavior, claiming a
resilience fix is complete, or stating that degradation, isolation, or recovery
guarantees hold.

## Claim statuses

| Status | Meaning |
| --- | --- |
| `VERIFIED_IN_SCOPE` | A specifically scoped claim is supported by direct code or configuration inspection and observed test, fault-injection, or runtime evidence within that boundary. |
| `CONTRADICTED_IN_SCOPE` | Direct evidence or a valid counterexample refutes the stated claim within its named scope. Preserve the counterexample and its conditions. |
| `PARTIAL` | The claim holds only for identified paths, dependencies, error classes, or configurations. |
| `NOT_FOUND_IN_SCOPE` | A named scope was searched and no supporting implementation or evidence was found there. This does not prove global absence. |
| `UNKNOWN` | Available evidence is insufficient, unresolved, stale, or not runtime-confirmed for the claim being made. |

State the actual evidence boundary for each claim: inspected files, symbols,
dependency boundaries, configuration, inputs, and test or fault-injection
conditions. Never upgrade `UNKNOWN` to `VERIFIED_IN_SCOPE` because an
implementation looks plausible. Keep verified behavior, proposed design, test
observation, and inference visibly separate. A unit test with mocked errors
establishes only how the caller behaves under that mock; do not extend it to
real network timeouts, partial failures, or untested error classes. Do not turn
a test name, mock, configured timeout/retry limit, or expected assertion into
runtime evidence until the fault scenario actually ran and its output was
observed.

For conflicting evidence, check whether observations concern the same code path
and configuration. If a counterexample refutes the claim, record
`CONTRADICTED_IN_SCOPE` even when happy-path tests pass. Use `PARTIAL` only
when coverage is genuinely limited to a subset of paths, never to mask a
demonstrated failure.

Do not report `NOT_FOUND_IN_SCOPE` merely because a single keyword search failed.
Inspect the actual call chain, middleware, interceptors, client wrappers,
configuration defaults, and fallback handlers in that boundary.

## Claim ledger

Record material claims in a structured ledger:

| Claim | Evidence | Status | Validation |
| --- | --- | --- | --- |
| What is asserted, including scope | File, symbol, config, test, or runtime signal | One status above | How the status was or will be checked |

Examples of precise wording:

- “The HTTP client sets a 5s request timeout, but no overall handler deadline was observed in the inspected path.”
- “`catch` block in `syncOrder` logs the error and returns `null`; caller impact is `PARTIAL` because only `fetchOrder` handles `null`.”
- “Retry amplification across gateway and client is `UNKNOWN` because upstream gateway config was not inspected.”

## Assumption ledger

Record assumptions separately and never invent unstated retry, timeout, or
fallback requirements—mark missing contracts `UNKNOWN`:

| Assumption | Impact if false | Validation | Fallback |
| --- | --- | --- | --- |
| What must be true for the design | Which safety or resilience property fails | Inspection, fault test, or metric | Safe bounded behavior |

An assumption is not a fact. If it materially changes safety or error
semantics, obtain evidence or label the design as conditional.

## Completion gate

Before saying “resilient”, “fixed”, “isolated”, “recoverable”, or “tested
successfully”, qualify the statement with its scope and require:

1. the relevant error, fallback, retry, timeout, and recovery paths were inspected;
2. the inspected boundary is stated explicitly;
3. relevant fault, timeout, or failure-path validation was run and observed;
4. silent-error and cascading-failure conditions were checked;
5. unresolved assumptions and uninspected layers are disclosed.

If any item is missing, use “proposed”, “partially verified”, “not observed”,
or “requires validation”.
