# Validation Matrix

Use this matrix to test business rules, boundary inputs, state machines,
invariants, calculations, and input validation. A happy-path test does not
establish edge-case or invariant safety.

| Area | Scenario | Expected invariant | Evidence to record |
| --- | --- | --- | --- |
| Business Logic | Alternate entry points (API, job, admin) execute same rule | Outcomes and eligibility decisions match the authoritative rule across every path | Code paths compared and test results |
| Boundary Condition | `0`, negative, empty, `max+1`, `NaN`/`Infinity`, oversized `limit` | Inputs at or past boundaries are rejected or clamped safely without overflow or panic | Boundary input table and observed outputs |
| State Transition | Skip intermediate state or mutate terminal state | Transition guard rejects illegal jump with explicit error and leaves state unchanged | Current/target state test and persisted state |
| Invariant | `PATCH` partial update violating cross-field invariant | Merged post-update state is checked and rejected before write | Update payload and rejected error/DB state |
| Calculation Accuracy | Proration, split rounding, multi-currency, zero denominator | Exact decimal/minor-unit arithmetic preserves `sum(parts) == total` for partitioned totals where contracted; zero divisor is handled safely | Input values, expected vs actual output, and rounding rule |
| Input Validation | Malformed type, oversized string/file, unknown enum, encoding bypass | Validation rejects with clear 4xx/validation error before domain mutation | Rejected payload, status code, and validation error |

For each executed scenario record:

- exact input shape, rule source, and expected result;
- test command and observed output;
- inspected scope and uninspected entry points;
- claim status (`VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`, `PARTIAL`, `NOT_FOUND_IN_SCOPE`, or `UNKNOWN`).
