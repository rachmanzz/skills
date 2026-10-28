# Panic Recovery and Leak Prevention

## Failure boundaries

Place recovery at a boundary that can preserve the failed work item's identity,
original cause, cleanup result, and completion state. Recovery must not turn an
unhandled failure into a false success acknowledgement.

Distinguish:

- expected error returned by the task;
- panic or exception raised by the task;
- failure in cleanup;
- failure in acknowledgement or persistence;
- process-level failure that no local handler can contain.

Decide which failures retry, which are terminal, and which require operator
attention. Keep the original failure attached to the decision.

## Leak checklist

Inspect every path for:

- execution units with no owner or join path;
- queues or channels that can block forever;
- timers, watchers, subscriptions, or callbacks that are never stopped;
- locks or permits not released after failure;
- connections or file handles retained after cancellation;
- child work that outlives its parent unintentionally;
- recovery handlers that recursively create unbounded work.

Use explicit ownership and cleanup order. A cleanup call is not proof of cleanup
success; record and validate its result when it affects safety.

## Required observations

For leak-sensitive changes, measure or inspect:

- active execution count before and after the scenario;
- queue and permit counts;
- open resource count where observable;
- completion of child joins;
- repeated start/stop behavior;
- cancellation and panic paths;
- process or runtime leak diagnostics when available.

Report the measurement scope, observation window, and diagnostic limitations.
Say “no leak was observed during this scenario and observation window” when that
is what the evidence supports. Limited observations cannot rule out slow,
intermittent, or unmeasured leaks.
