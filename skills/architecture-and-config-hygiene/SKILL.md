---
name: architecture-and-config-hygiene
description: Audit, refactor, or harden codebase structure and configuration—covering package/module dependency coupling, circular dependencies, over- or mis-applied abstractions, dead code, logic duplication, and missing, invalid, or unsafe default configuration. Use when reviewing architecture boundaries, import cycles, code bloat, or startup config validation. For workload scalability, capacity bounds, and backpressure, use performance-and-resource-efficiency and evidence-led-concurrency-and-delivery.
metadata:
  short-description: Audit dependency coupling, cycles, abstractions, dead code, duplication, and config
---

# Architecture and Config Hygiene

Use this skill to keep module boundaries clean, acyclic, maintainable, and
fail-fast on configuration errors.

This skill complements—and does not replace—the repository's adjacent skills:

- Use `performance-and-resource-efficiency` and
  `evidence-led-concurrency-and-delivery` for **scalability** audits
  (complexity growth, resource bounds, backpressure, admission control, and
  capacity limits).
- Use `application-security-and-isolation` for dependency CVEs, hardcoded
  secrets, and security exposure.
- Use `business-logic-and-input-validation` when duplicated or misplaced logic
  violates domain rules or invariants.

Read only the references needed for the current task:

- Read [evidence-and-assumption-control.md](references/evidence-and-assumption-control.md)
  before claiming code is acyclic, unused, or config-safe.
- Read [dependency-and-modularity.md](references/dependency-and-modularity.md)
  for package/module coupling, layering rules, and static/runtime circular
  dependencies.
- Read [abstraction-and-code-hygiene.md](references/abstraction-and-code-hygiene.md)
  for premature/leaky abstractions, dead-code verification, and logic
  duplication.
- Read [configuration-hygiene.md](references/configuration-hygiene.md) for
  missing, invalid, and unsafe default configuration checks.
- Read [validation-matrix.md](references/validation-matrix.md) when designing
  startup config tests or verifying structural refactors.

## Non-negotiable rules

1. Classify important claims as `VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`,
   `PARTIAL`, `NOT_FOUND_IN_SCOPE`, or `UNKNOWN`. Never upgrade `UNKNOWN` to
   `VERIFIED_IN_SCOPE` because imports or config structs look clean, and keep
   verified observations, proposed refactors, and inference visibly separate.
2. Never assume deployment env vars or runtime DI bindings without inspecting
   them—mark uninspected environments `UNKNOWN` and record assumptions in an
   assumption ledger.
3. Never declare a symbol or module "dead code" from a plain text search or
   incomplete call graph alone; verify reflection, DI registration, route
   tables, interface dispatch, and public exports first.
4. Prefer breaking import/DI cycles by inverting dependencies or extracting
   leaf contracts rather than merging unrelated packages or suppressing linters.
5. Do not consolidate code that only looks superficially similar across
   unrelated domains; unify only shared rules with a single source of truth.
6. Require fail-fast startup validation for missing or invalid configuration;
   never allow silent fallbacks that turn invalid config or invalid `0` values
   (such as `TIMEOUT=0`) into defaults or substitute dev secrets/infinite
   timeouts.
7. Preserve behavior on every structural cleanup and verify with build, lint,
   and tests after edits.

## Audit workflow

### 1. Map packages, layers, and configuration loaders

Identify module/package boundaries, import direction, DI/startup wiring, and
all configuration sources (env vars, files, flags, defaults).

### 2. Build the evidence and assumption ledgers

Record material claims and unverified wiring/environment assumptions separately
using [evidence-and-assumption-control.md](references/evidence-and-assumption-control.md).

### 3. Audit dependency coupling and circular dependencies

Apply [dependency-and-modularity.md](references/dependency-and-modularity.md)
to locate layering violations, leaky boundary types, high fan-out hubs, and
static or runtime import/DI cycles.

### 4. Audit abstractions, dead code, and code duplication

Apply [abstraction-and-code-hygiene.md](references/abstraction-and-code-hygiene.md)
to review over-engineering vs missing boundaries, verify candidate dead code
across dynamic dispatch paths, and flag drifting duplicated logic.

### 5. Audit configuration hygiene

Apply [configuration-hygiene.md](references/configuration-hygiene.md) to check
missing-key startup behavior, unsafe defaults, invalid bounds/units, and schema
drift against deployment/example files.

### 6. Refactor safely and validate

Apply small behavior-preserving steps and verify builds, startup config tests,
and test suites using [validation-matrix.md](references/validation-matrix.md).

## Required report shape

Include only applicable sections; mark non-applicable sections `OUT_OF_SCOPE`
with a short reason:

1. Scope, module/layer map, and configuration sources.
2. Evidence ledger for structural and configuration claims.
3. Dependency coupling & circular dependency findings.
4. Abstraction, dead code & duplication findings.
5. Configuration hygiene findings (missing, invalid, unsafe defaults).
6. Validation performed and exact observed results.
7. Assumptions, uninspected environments/dispatch paths, and remaining risks.
