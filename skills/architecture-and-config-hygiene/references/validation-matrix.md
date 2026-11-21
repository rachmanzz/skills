# Validation Matrix

Use this matrix to verify modularity, cycle freedom, dead-code safety,
duplication fixes, and configuration validation.

| Area | Scenario | Expected invariant | Evidence to record |
| --- | --- | --- | --- |
| Dependency Coupling | Inspect cross-package imports and boundary types | Domain logic depends on narrow contracts, not transport/driver internals | Import list and dependency map |
| Circular Dependency | Check package import graph and DI startup graph | Zero static package cycles in the inspected scope and zero observed DI/startup initialization cycles | Explicit cycle-check/lint/build output and DI boot test |
| Abstraction | Review wrappers, interfaces, and flag-driven helpers | Abstractions isolate real variation without pass-through bloat or boolean-flag sprawl | Inspected interfaces/callers |
| Dead Code | Trace unreferenced symbols across inspected static and dynamic entry points | No callers found across inspected static, DI, reflection, and export surfaces; build and tests pass | Call-site search, dynamic-entry check, and test run |
| Code Duplication | Extract shared rule/helper where logic drifted | Single shared implementation preserves edge cases across all callers | Diff and callers' unit tests |
| Configuration (Missing) | Boot app with a required env/config key unset | Process fails fast at startup naming the missing key | Startup test stderr/exit code |
| Configuration (Invalid) | Boot app with malformed type, negative bound, or invalid URL | Process rejects invalid config at startup instead of silently falling back | Startup test stderr/exit code |
| Configuration (Defaults) | Boot app with only required keys set | All defaults are explicit, safe for production, and typed with unambiguous units | Inspected config defaults table |

For each check record exact commands, inspected scope, observed output, and
claim status (`VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`, `PARTIAL`,
`NOT_FOUND_IN_SCOPE`, or `UNKNOWN`).
