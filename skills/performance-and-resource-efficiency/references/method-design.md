# Method and Function Design

Method boundaries affect performance, allocation, testability, and correctness.
Design methods around clear ownership and work contracts.

## Review checklist

- Is the method doing one coherent operation?
- Does it make hidden I/O, cache access, allocation, or mutation explicit?
- Does it repeatedly fetch or transform the same data?
- Are inputs copied unnecessarily?
- Is the return value materialized when a stream or iterator would fit?
- Are errors, cancellation, and timeouts propagated correctly?
- Does recursion have a bounded depth and memory cost?
- Is memoization safe for the method's inputs, authorization, and freshness?

Avoid splitting code into many methods solely to optimize call syntax. Avoid
large methods that hide repeated work or make resource ownership impossible to
see. Keep performance-sensitive contracts documented at the boundary.

## Side effects

Separate pure transformation from I/O and mutation where practical. This makes
it easier to benchmark computation independently and to verify that retries do
not duplicate writes or invalidate the wrong cache entry.
