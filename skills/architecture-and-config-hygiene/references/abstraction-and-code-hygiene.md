# Abstraction, Dead Code, and Code Duplication

## Abstraction Audit

Evaluate whether abstractions clarify change boundaries or add indirection
without value.

### Checklist

- **Premature / speculative generality**: flag single-implementation interfaces,
  empty pass-through wrappers, and plugin/strategy hierarchies with only one
  concrete behavior when they serve no layering/dependency-inversion,
  testability, or extension requirement.
- **Wrong abstraction boundary**: flag abstractions that couple unrelated
  domains together merely because their current code looks similar, forcing
  boolean flags (`isAdmin`, `skipValidation`, `mode`) to pile up over time.
- **Leaky abstractions**: flag interfaces whose signatures expose backend
  implementation details (SQL cursors, Redis-specific options, framework request
  objects).
- **God interfaces & oversized functions**: split wide interfaces into small
  consumer-owned contracts and extract coherent helpers with shallow nesting.

## Dead Code Audit

Identify unused, unreachable, or obsolete code paths safely without deleting
live dynamic entry points.

### Checklist

- **Unreachable control flow**: code after unconditional `return`/`throw`,
  always-true/false conditions, and shadowed switch/if branches.
- **Unused symbols & modules**: unreferenced files, functions, classes, types,
  routes, feature flags, config keys, and unused dependencies in manifests.
- **Dynamic-dispatch verification**: before declaring a symbol unused, verify
  reflection, interface implementations, framework decorators/annotations,
  dependency injection containers, event subscribers, and dynamic imports.

## Code Duplication Audit

Identify duplicated business logic, validation, or orchestration that risks
divergent bug fixes.

### Checklist

- **Rule & invariant drift**: flag duplicated calculations, authorization
  checks, error-mapping blocks, or query filters across endpoints/jobs where a
  fix in one place misses the copy.
- **Intentional vs accidental duplication**: keep decoupled copies separate when
  two bounded contexts only resemble each other coincidentally; extract a shared
  helper only when they share the exact same single source of truth.
