# Evidence and Assumption Control

Use this reference before claiming a module is decoupled, cycle-free, free of
dead code, free of duplication, or safely configured.

## Claim statuses

| Status | Meaning |
| --- | --- |
| `VERIFIED_IN_SCOPE` | A specifically scoped claim is supported by direct import/graph/call-site/config inspection and observed static-analysis, build, or startup-validation output within that boundary. |
| `CONTRADICTED_IN_SCOPE` | Direct evidence or a concrete cycle, duplicated rule, unused path, or unsafe config fallback refutes the claim within its named scope. |
| `PARTIAL` | The property holds only for identified packages, modules, or environments. |
| `NOT_FOUND_IN_SCOPE` | A named scope was searched and no dependency violation, cycle, or validation check was found there. This does not prove global absence. |
| `UNKNOWN` | Dynamic dispatch, reflection, DI wiring, or deployment environment config was not inspected or verified. |

Never upgrade `UNKNOWN` to `VERIFIED_IN_SCOPE` because imports or config structs
look clean. Keep verified behavior, proposed refactors, tool output, and
inference visibly separate. Do not mark a symbol as dead code purely from a
naive text search or single static-call-graph miss when reflection, interface
dispatch, framework routing, or dynamic imports exist. Verify dynamic
registration tables, routes, CLI wiring, and public package exports before
recommending deletion, and do not convert `NOT_FOUND_IN_SCOPE` into global
absence.

## Claim ledger

| Claim | Evidence | Status | Validation |
| --- | --- | --- | --- |
| Architectural or config property and scope | Package graph, file/line, config loader, or test | One status above | Static check, build, or startup test |

## Assumption ledger

Record assumptions separately and never invent deployment environment values or
runtime DI bindings:

| Assumption | Impact if false | Validation | Fallback |
| --- | --- | --- | --- |
| Assumed runtime wiring or env provisioning | Startup failure, cycle, or silent misconfig | Startup/DI test or env schema check | Fail fast on invalid/missing config |

An assumption is not a fact. If it materially affects runtime wiring or
startup behavior, obtain evidence or label the finding conditional.

## Completion gate

Before saying “decoupled”, “acyclic in inspected scope”, “unused in inspected
scope”, or “config-validated”, qualify the statement with its scope and require:

1. actual module imports, DI wiring, call sites, and config loaders in scope
   were inspected;
2. if dead code is in scope, dynamic/reflection/framework entry points were
   checked before flagging unused symbols;
3. if config is in scope, startup missing/invalid config behavior was verified;
4. build, lint, or unit tests ran after any refactor or cleanup;
5. uninspected environments, external consumers, or lazy/conditional wiring are
   disclosed.

If any item is missing, use “proposed”, “partially verified”, “not observed”,
or “requires validation”.
