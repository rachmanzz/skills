# Dependency Coupling and Circular Dependencies

## Dependency Audit (Coupling)

Measure and review how tightly packages, modules, and layers depend on one
another's concrete internals rather than stable boundaries.

### Checklist

- **Layering & direction violations**: flag domain/core modules importing
  transport (HTTP/gRPC), persistence drivers, or UI layers directly instead of
  depending on narrow contracts.
- **Concrete & temporal coupling**: flag callers reaching into internal mutable
  fields, global singletons, or implicit call-order assumptions across modules.
- **High fan-in / fan-out hubs**: identify unrelated-concern aggregator
  modules (`utils`/`helpers` buckets or "god packages" crossing multiple
  domain boundaries) where edits cause wide rebuilds or regressions.
- **Leaky boundary types**: flag public APIs exposing internal ORM entities,
  transport structs, or vendor SDK errors directly across module borders.

## Circular Dependency Audit

Detect both compile-time import cycles and runtime/initialization cycles.

### Checklist

- **Static package/module cycles**: map the import graph (`A -> B -> A` or
  `A -> B -> C -> A`); verify build tools or module-graph analyzers do not
  suppress or hide cycles via barrels/re-exports.
- **Runtime & DI initialization cycles**: check lazy imports, constructor/DI
  provider graphs, event-bus feedback loops, and `init()` side-effect ordering
  for circular initialization or runtime `undefined`/null-reference traps.
- **Shared-state / callback cycles**: check mutual callbacks or reciprocal
  service calls (`Service A -> Service B -> Service A`) that can also create
  re-entrant state corruption or call-stack/deadlock loops.
- **Cycle-breaking strategy**: break cycles cleanly by inverting ownership with
  an interface at the consumer boundary, extracting shared value types into a
  leaf contract package, or splitting bidirectional responsibilities.
