# Evidence, Assumptions, and Claim Control

This reference prevents the agent from turning intent, plausible code, or
partial inspection into an overconfident claim.

## Evidence hierarchy

Use the strongest available evidence:

1. observed runtime behavior, passing integration test, benchmark, profile, or
   deployment check;
2. code path plus relevant configuration and a passing focused test;
3. code and configuration inspection without runtime validation;
4. dependency or package metadata showing capability may be available;
5. user statement, issue description, or design intention;
6. model inference or common practice.

Levels 1 and 2 can support `VERIFIED` for a narrowly scoped claim. Level 3
usually supports `PARTIAL` or a carefully bounded implementation claim. Levels
4 through 6 do not prove that a runtime feature exists or works.

## Claim statuses

- `VERIFIED`: direct evidence supports the exact claim and scope.
- `PARTIAL`: evidence supports only some paths, environments, or conditions.
- `ABSENT`: the relevant scope was inspected and the capability was not found.
- `UNKNOWN`: evidence is insufficient to decide.

Do not use `ABSENT` when only one file or one search pattern was checked. Do
not use `VERIFIED` because a library is installed, a function has the right
name, or a configuration key appears to be enabled.

## Evidence gate

Before claiming that something exists, is implemented, is fixed, is faster, or
has passed validation:

1. State the exact claim and its scope.
2. Inspect the relevant code, configuration, dependencies, tests, and runtime
   signals.
3. Record the evidence source, such as a path and line, command output, test
   name, benchmark result, or trace.
4. Assign `VERIFIED`, `PARTIAL`, `ABSENT`, or `UNKNOWN`.
5. If the evidence is incomplete, state the assumption and its impact.
6. Define the next validation step or ask the user when the missing information
   materially changes the implementation.

## Assumption ledger

For material assumptions, use this format:

```text
Assumption: Redis is the shared cache backend.
Evidence: configuration file names Redis, but no connectivity test was found.
Status: UNKNOWN.
Impact: backend-specific timeout and serialization behavior may be wrong.
Validation: inspect deployment configuration and run the integration test.
```

Do not hide assumptions inside definitive language. If an assumption is low
risk, proceed with it explicitly. If it changes architecture, data safety,
correctness, or external side effects, ask or stop at the decision point.

## Claim wording

Prefer:

- “The repository contains a cache initialization, but the read path is not
  verified.”
- “I changed the fallback branch; the integration test still needs to run.”
- “The proposed design uses a bounded LRU.”
- “Memory improvement is unknown until a baseline and benchmark are available.”

Avoid:

- “The cache is already working” when only a library is installed;
- “Fixed” when the code changed but the failure path was not tested;
- “Faster” without before-and-after measurements;
- “Supports Redis” when only a generic interface or dependency exists;
- “Tested successfully” when a test was not actually executed.

## Final review

Before finalizing, check every sentence that describes current state, completed
work, compatibility, performance, correctness, or validation. Each sentence
must either have evidence, be marked as an assumption/proposal, or be rewritten
as an explicit unknown.
