# Ownership, Visibility, and Durable Storage

## Work-item state

Represent the meaningful states and transitions, for example:

```text
available -> claimed -> executing -> completed
                    ├-> retryable failure -> available
                    ├-> terminal failure -> retained or dead-lettered
                    └-> ownership expired -> recoverable
```

Use the actual system's states when known. Do not invent transitions merely to
complete the diagram; mark missing transitions as `UNKNOWN`.

## Ownership

For every claim, identify:

- owner identity;
- claim timestamp and expiry;
- renewal rules;
- acknowledgement authority;
- behavior after expiry;
- fencing or version check against stale owners;
- recovery when the owner disappears.

An identifier in a log is not proof of ownership. Look for and verify any state
transition, storage condition, or other protection against stale completion. Do
not assume one exists: if none is found within the searched boundary, report
that scope; if evidence is insufficient, mark the behavior `UNKNOWN`.

## Visibility

Separate visibility from ownership. A work item may be hidden from other
receivers without having a valid owner, or an owner may lose its visibility
period. Determine the behavior when the period expires during execution and
whether duplicate execution is handled safely. Report missing or unknown
protection rather than assuming a recovery mechanism exists.

## Durability

Classify state as:

- volatile and process-local;
- volatile but shared;
- recoverable from another source;
- durable across process restart;
- durable across machine or storage failure.

Use the weakest classification supported by evidence. A write call, successful
return, or replication setting alone does not prove recovery behavior. Validate
with restart, failure, or recovery tests appropriate to the claimed boundary.
