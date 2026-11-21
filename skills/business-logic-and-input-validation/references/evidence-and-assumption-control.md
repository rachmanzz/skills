# Evidence and Assumption Control

Use this reference before claiming that business rules hold, calculations are
accurate, state transitions are complete, or inputs are safely validated.

## Claim statuses

| Status | Meaning |
| --- | --- |
| `VERIFIED_IN_SCOPE` | A specifically scoped claim is supported by direct code and specification inspection plus observed tests or edge-case checks within that boundary. |
| `CONTRADICTED_IN_SCOPE` | Direct evidence or a concrete counterexample input refutes the stated rule or invariant within its named scope. Preserve the counterexample. |
| `PARTIAL` | The rule holds only for identified handlers, input shapes, states, or calculation paths. |
| `NOT_FOUND_IN_SCOPE` | A named scope was searched and no rule, validation, guard, or transition check was found there. This does not prove global absence. |
| `UNKNOWN` | The authoritative business requirement, rounding policy, or caller validation behavior is unstated or unverified. |

State the exact boundary for each claim: handler, service function, domain
entity, specification source, and test inputs. Never upgrade `UNKNOWN` to
`VERIFIED_IN_SCOPE` because validation or math looks plausible. Keep verified
behavior, proposed design, test observation, and inference visibly separate.
Happy-path unit tests do not prove boundary safety, overflow protection, or
state-machine completeness, and test names or assertions are not evidence until
the test actually ran and its output was observed. Do not convert
`NOT_FOUND_IN_SCOPE` into global absence.

If the expected business rule or rounding convention is not documented in the
repository, mark the requirement `UNKNOWN` rather than inventing a rule.

## Claim ledger

| Claim | Evidence | Status | Validation |
| --- | --- | --- | --- |
| What is asserted, including scope | Spec, code path, line, or test case | One status above | How the status was or will be checked |

## Assumption ledger

Record assumptions separately and never invent unstated domain rules, rounding
policies, or cutoff thresholds:

| Assumption | Impact if false | Validation | Fallback |
| --- | --- | --- | --- |
| Assumed business rule or input guarantee | Which calculation or workflow breaks | Spec check or boundary test | Fail closed or reject invalid input |

An assumption is not a fact. If it materially changes domain behavior or
financial calculations, obtain evidence or label the design as conditional.

## Completion gate

Before saying “valid”, “accurate”, “enforced”, or “tested successfully”, qualify
the statement with its scope and require:

1. the relevant domain handlers, validators, calculators, and state transitions
   in scope were inspected;
2. for domain-correctness claims (“valid”, “accurate”, “enforced”), the
   authoritative business rule or requirement source was checked;
3. negative, boundary, invalid-state, and precision tests in scope ran and were
   observed;
4. for enforcement claims (“enforced”, “valid”), bypass paths across alternate
   entry points in scope were checked;
5. unresolved assumptions and uninspected entry points are disclosed.

If any item is missing, use “proposed”, “partially verified”, “not observed”,
or “requires validation”.
