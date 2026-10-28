# Cancellation and Failure Propagation

## Model cancellation precisely

Distinguish these states:

- cancellation was requested;
- the task observed cancellation;
- child work received cancellation;
- the operation returned because of cancellation;
- external side effects stopped or were compensated.

They are not interchangeable. A timeout or cancellation signal establishes only
what the observing component emitted or received. Verify whether the request
propagated, was observed by the target, and caused execution or side effects to
stop.

Identify whether the runtime supports cooperative cancellation, preemptive
interruption, or only a deadline. Design the task so blocking operations can
observe the chosen mechanism and so non-cancellable work has a bounded exit or
explicit recovery policy.

## Propagation rules

- Define the parent-child relationship for every spawned operation.
- Propagate the original cancellation cause where the runtime permits it.
- Decide whether one child failure cancels siblings, only the parent, or neither.
- Do not let a child silently outlive the owner unless it has an explicit owner
  and recovery contract.
- Preserve the distinction between cancellation, timeout, dependency failure,
  and application error.
- Arrange and verify cleanup on success, error, cancellation, and recoverable
  panic/exception paths supported by the runtime. Identify abrupt termination
  or fatal paths where cleanup cannot be assumed to run.
- Record cleanup failures, blocking, deadlines, and residual resources. Tie
  permit or budget release to ended resource use or verified accounting
  transfer; requesting cancellation does not establish either condition.

## Validation cases

Check cancellation:

1. before admission;
2. while waiting for capacity;
3. while blocked on I/O or a dependency;
4. after a side effect starts;
5. while child work is active;
6. during shutdown;
7. after the deadline expires.

For each case, record what stopped, what continued, what was acknowledged, and
what recovery is required. Do not claim that all work stopped unless the runtime
and observation prove it.
