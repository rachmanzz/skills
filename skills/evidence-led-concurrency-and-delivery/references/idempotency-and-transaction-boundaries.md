# Idempotency and Transaction Boundaries

## Idempotency

Idempotency is a property of an operation and its side effects, not a label on a
retry loop. Define:

- the idempotency key or equivalent identity;
- the scope and lifetime of deduplication;
- which side effects are protected;
- what happens after a partial side effect;
- how concurrent duplicates are serialized or rejected;
- how expired deduplication state is handled.

If the side effect cannot be repeated safely, evaluate durable deduplication,
atomic state transitions, compensation, or an explicit terminal failure policy
against the requirements. None alone guarantees safety: map failure windows
before, during, and after the side effect and its recorded state, especially
when they span systems. Verify how concurrent duplicates, crashes, uncertain
outcomes, and failed compensation are handled. If a gap remains, report it and
the resulting guarantee. Do not claim exactly-once execution merely because
duplicates are uncommon or a retry count is limited.

## Transaction boundaries

Map each transaction separately:

- work-item persistence;
- ownership claim;
- business state change;
- outbox or inbox record;
- external side effect;
- completion acknowledgement;
- retry or dead-letter state.

State which operations are atomic together and which are not. A transaction in
one storage system does not automatically include another storage system,
network call, process, or delivery backend.

## Ordering questions

For each applicable path, establish the actual order between persistence and
acknowledgement, claim and execution, commit and publication, side effect and
idempotency state, and recovery and ownership release. Treat these as questions,
not universal orderings. For each possible crash or uncertain result between
steps, determine whether work can be lost, duplicated, or left incomplete and
how the chosen contract addresses it. In particular, performing a side effect
before marking its idempotency key complete can permit a duplicate on retry;
marking it complete first can lose the effect. Establish an appropriate atomic
boundary or explicitly document the remaining risk and recovery strategy.

When an atomic boundary is unavailable, document the failure window and any
evidenced recovery mechanism; if none is found or it is unknown, say so instead
of hiding the gap behind a stronger claim.
