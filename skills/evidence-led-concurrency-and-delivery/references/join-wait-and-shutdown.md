# Join, Wait, and Graceful Shutdown

## Join and wait contracts

Define:

- which work is included in the join;
- whether new work may be admitted while waiting;
- whether waiting is idempotent;
- how the first or aggregate error is chosen;
- how cancellation interacts with waiting;
- what happens when a child never returns;
- whether a wait timeout leaves work running.

If repeated wait calls are supported, verify that they do not duplicate cleanup,
change the original result, or hide the first failure. If they are not
supported, document the single-owner rule.

## Shutdown phases

A bounded graceful shutdown commonly has these phases:

1. announce stopping and stop new admission;
2. preserve or persist work that cannot start;
3. request cancellation of active work;
4. wait for owned child work and cleanup;
5. record unresolved ownership and defer settlement to a recovery path with
   verified authority;
6. close resources in dependency order;
7. report complete or incomplete shutdown with the cause.

The exact sequence may vary, but ownership and ordering must be explicit. A
deadline expiry means the deadline expired. It does not prove that handlers,
threads, processes, or external operations stopped.

Before acknowledging, requeueing, releasing a claim, or changing recovery state,
verify authority for that specific transition using the delivery contract and
current claim or recovery credentials. Uncertain ownership alone authorizes no
such mutation. If authority cannot be established, report the unresolved state
and the applicable expiry or reconciliation path, if one is known.

Keep capacity charged while work still uses the resource. Release it only when
use has ended or accounting ownership has verifiably transferred. After a wait
timeout, identify resources still in use before closing them; report incomplete
shutdown and any explicit force-stop policy rather than assuming cleanup ran.

## Validation cases

Test shutdown with:

- no active work;
- active work that completes normally;
- active work that returns an error;
- active work that panics or raises an exception;
- active work that ignores cancellation;
- queued work not yet admitted;
- child work still running;
- cleanup or acknowledgement failure;
- repeated shutdown calls.

Record the final state, remaining work, recovery path, and observed deadline
behavior.
