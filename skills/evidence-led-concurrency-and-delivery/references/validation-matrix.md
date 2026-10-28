# Validation Matrix

Use this matrix as a starting point. Add scenarios that match the actual
contract and remove scenarios that are irrelevant. A passing test supports only
the tested scope.

| Area | Scenario | Expected invariant | Evidence to record |
| --- | --- | --- | --- |
| Cancellation | Cancel before admission | Observed admission behavior matches the declared cancellation contract | State transition and returned result |
| Cancellation | Cancel during execution | Propagation, remaining work, and recovery match the declared contract | Cause, timing, and remaining work |
| Capacity | Work continues after cancellation or timeout | Resources still in use remain accounted for; release follows ended use or verified accounting transfer without duplicate release | Active work, reservation owner, and permit or budget counts |
| Failure | Panic/exception in one task | Observed containment or fail-fast behavior matches the declared failure boundary; completion is not falsely acknowledged | Original cause and sibling or process behavior |
| Leak | Repeated start/stop | Resource behavior matches the declared lifecycle baseline within the observation window | Counts, handles, or runtime diagnostics |
| Join | Child task fails | Join behavior matches the declared error policy; non-detached children do not lose ownership | Join result, child states, and detached-work owner |
| Shutdown | Deadline expires | Incomplete shutdown is reported; no claim that work stopped | Deadline, active work, and recovery path |
| Cleanup | Cleanup fails, blocks, or cannot run after abrupt termination | Cleanup outcome and residual state are reported; recovery follows the declared contract where available | Cleanup result, remaining resources, and recovery evidence |
| Idempotency | Duplicate delivery | Protected side effect occurs according to the contract | Key, dedupe state, and side-effect count |
| Transaction | Failure between two state changes | The outcome matches the declared recovery or accepted-loss policy, and the failure window remains visible | Transaction boundary and recovery or loss result |
| Ownership | Stale owner acknowledges | Stale completion is handled according to the declared ownership and idempotency contract | Owner/version/idempotency evidence |
| Ownership | Authority cannot be established during shutdown | Uncertainty alone triggers no acknowledgement, requeue, claim release, or recovery mutation | Attempted transitions, authority checks, and unresolved state |
| Visibility | Ownership period expires during execution | Duplicate/recovery behavior matches the contract | Expiry event and resulting states |
| Durability | Process or storage restart | Claimed durability boundary is preserved | Before/after state and recovery evidence |
| Batch | Batch exceeds normal size | Memory, time, and partial-failure limits remain bounded | Peak resource and item outcomes |
| Backpressure | Capacity is exhausted | The defined wait/reject/shed/degrade behavior occurs | Admission decision and queue depth |
| Admission | Reservation cannot be fulfilled | Reserved resources are released and work is not falsely accepted | Reservation state and result |
| Fairness | Sustained competing load | Service distribution and starvation behavior match the declared fairness policy within the stated scope | Wait-time and service distribution |

For each scenario record:

- exact configuration and input shape;
- command or test executed;
- observed output or runtime signal;
- scope and limitations;
- claim status;
- unresolved assumptions.

When a valid observation refutes a stated claim, record it as
`CONTRADICTED_IN_SCOPE` with the counterexample, configuration, and observed
result. Passing scenarios elsewhere do not remove that contradiction.

Do not turn a test name, configured limit, or expected assertion into evidence
until the test actually ran and its result was observed.
