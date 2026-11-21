# Performance and Reliability Skills

A collection of installable Agent Skills for measured performance work,
evidence-led concurrent or asynchronous execution, resilience and error handling,
data integrity and lifecycle, business logic and input validation, application
security, architecture hygiene, observability, API contracts, and per-turn
prompt confidence gating. The skills use the standard `SKILL.md` format and are
compatible with Codex, Antigravity (`agy`), and other skills-compatible agents.

## Included skills

- `performance-and-resource-efficiency` — memory, allocation, algorithms,
  loops, I/O, concurrency, profiling, benchmarking, and cache reliability.
- `evidence-led-concurrency-and-delivery` — cancellation, failure isolation,
  leak prevention, join/wait behavior, shutdown, idempotency, transactions,
  ownership, visibility, durability, batching, backpressure, admission, and
  fairness with explicit evidence control.
- `resilience-and-error-handling` — error handling decisions (skip, retry,
  fallback, propagate), silent errors, degradation, fault isolation, failure
  propagation, recovery, and retry/timeout budgets with explicit evidence
  control.
- `data-integrity-and-lifecycle` — data integrity, cross-table/service/cache
  consistency, transaction safety, concurrent data mutations, mutation
  idempotency, and data lifecycle controls with explicit evidence control.
- `business-logic-and-input-validation` — business rules, boundary conditions,
  state transitions, domain invariants, calculation accuracy, and input
  validation/sanitization.
- `application-security-and-isolation` — authentication, authorization,
  multi-tenant isolation, injection resistance, secret exposure, information
  disclosure, and dependency CVE security.
- `architecture-and-config-hygiene` — package/module coupling, circular
  dependencies, abstraction quality, dead code, logic duplication, and
  configuration validation.
- `observability-and-audit-trail` — structured logging, monitoring, metrics and
  cardinality, distributed tracing, alerting, health checks, and append-only
  audit trails.
- `api-contracts-and-integrations` — API contract parity, backward/forward
  compatibility, serialization fidelity, and webhook reliability.
- `prompt-confidence-gate` — per-turn prompt clarity and candidate-intent
  evaluation workflow using `score_prompt.py` against a minimum confidence
  threshold from `AGENTS.md`, `GEMINI.md`, or user input.

## Repository layout

```text
.
├── .gitignore
├── LICENSE
├── README.md
├── package.json
├── plugin.json
├── tests/
│   ├── test_plugin_manifest.py
│   ├── test_score_prompt.py
│   ├── test_validate_evidence.py
│   └── test_validate_skill_package.py
├── .github/
│   └── workflows/
│       └── validate-skill.yml
└── skills/
    ├── performance-and-resource-efficiency/
    │   ├── SKILL.md
    │   ├── agents/
    │   │   └── openai.yaml
    │   ├── scripts/
    │   │   ├── validate-evidence.py
    │   │   └── validate-skill-package.py
    │   └── references/
    │       ├── memory-efficiency.md
    │       ├── loop-and-algorithm-design.md
    │       ├── method-design.md
    │       ├── data-structures.md
    │       ├── io-and-database-efficiency.md
    │       ├── concurrency.md
    │       ├── profiling-and-benchmarking.md
    │       ├── evidence-and-assumption-control.md
    │       ├── evidence-ledger-template.md
    │       ├── validation-matrix.md
    │       ├── cache-reliability-and-fallback/
    │       │   ├── cache-contract.md
    │       │   ├── consistency-and-write-policies.md
    │       │   ├── database-protection.md
    │       │   ├── expiration-and-rotation.md
    │       │   ├── fallback-flow.md
    │       │   ├── lru-capacity.md
    │       │   ├── observability.md
    │       │   ├── operational-controls.md
    │       │   ├── security-and-isolation.md
    │       │   ├── shared-cache-backends.md
    │       │   └── language-adapters/
    │       │       ├── csharp.md
    │       │       ├── go.md
    │       │       ├── java.md
    │       │       ├── javascript-typescript.md
    │       │       ├── python.md
    │       │       └── rust.md
    │       └── language-adapters/
    │           ├── javascript-typescript.md
    │           ├── python.md
    │           ├── go.md
    │           ├── java.md
    │           ├── rust.md
    │           └── csharp.md
    ├── evidence-led-concurrency-and-delivery/
    │   ├── SKILL.md
    │   ├── agents/
    │   │   └── openai.yaml
    │   └── references/
    │       ├── evidence-and-assumption-control.md
    │       ├── cancellation-and-failure-propagation.md
    │       ├── panic-recovery-and-leak-prevention.md
    │       ├── join-wait-and-shutdown.md
    │       ├── idempotency-and-transaction-boundaries.md
    │       ├── ownership-visibility-and-durable-storage.md
    │       ├── batching-backpressure-and-admission.md
    │       ├── fairness-and-scheduling.md
    │       └── validation-matrix.md
    ├── prompt-confidence-gate/
    │   ├── SKILL.md
    │   ├── agents/
    │   │   └── openai.yaml
    │   ├── scripts/
    │   │   └── score_prompt.py
    │   └── references/
    │       ├── confidence-rubric.md
    │       └── evidence-and-assumption-control.md
    ├── resilience-and-error-handling/
    │   ├── SKILL.md
    │   ├── agents/
    │   │   └── openai.yaml
    │   └── references/
    │       ├── evidence-and-assumption-control.md
    │       ├── error-handling-and-silent-errors.md
    │       ├── degradation-and-fault-isolation.md
    │       ├── failure-propagation-and-recovery.md
    │       ├── retry-and-timeout-budgets.md
    │       └── validation-matrix.md
    ├── data-integrity-and-lifecycle/
    │   ├── SKILL.md
    │   ├── agents/
    │   │   └── openai.yaml
    │   └── references/
    │       ├── evidence-and-assumption-control.md
    │       ├── integrity-and-consistency.md
    │       ├── transactions-and-concurrency.md
    │       ├── idempotency-and-lifecycle.md
    │       └── validation-matrix.md
    ├── business-logic-and-input-validation/
    │   ├── SKILL.md
    │   ├── agents/
    │   │   └── openai.yaml
    │   └── references/
    │       ├── evidence-and-assumption-control.md
    │       ├── business-logic-and-invariants.md
    │       ├── boundary-conditions-and-calculations.md
    │       ├── state-transitions-and-validation.md
    │       └── validation-matrix.md
    ├── application-security-and-isolation/
    │   ├── SKILL.md
    │   ├── agents/
    │   │   └── openai.yaml
    │   └── references/
    │       ├── evidence-and-assumption-control.md
    │       ├── authentication-and-authorization.md
    │       ├── injection-and-data-exposure.md
    │       ├── dependency-security-and-hardening.md
    │       └── validation-matrix.md
    ├── architecture-and-config-hygiene/
    │   ├── SKILL.md
    │   ├── agents/
    │   │   └── openai.yaml
    │   └── references/
    │       ├── evidence-and-assumption-control.md
    │       ├── dependency-and-modularity.md
    │       ├── abstraction-and-code-hygiene.md
    │       ├── configuration-hygiene.md
    │       └── validation-matrix.md
    ├── observability-and-audit-trail/
    │   ├── SKILL.md
    │   ├── agents/
    │   │   └── openai.yaml
    │   └── references/
    │       ├── evidence-and-assumption-control.md
    │       ├── logging-and-tracing.md
    │       ├── monitoring-metrics-and-alerting.md
    │       ├── health-checks-and-audit-trail.md
    │       └── validation-matrix.md
    └── api-contracts-and-integrations/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        └── references/
            ├── evidence-and-assumption-control.md
            ├── api-contracts-and-compatibility.md
            ├── serialization-and-webhooks.md
            └── validation-matrix.md
```

## Install from a Git repository

```bash
npx skills add rachmanzz/skills --skill performance-and-resource-efficiency
npx skills add rachmanzz/skills --skill evidence-led-concurrency-and-delivery
npx skills add rachmanzz/skills --skill resilience-and-error-handling
npx skills add rachmanzz/skills --skill data-integrity-and-lifecycle
npx skills add rachmanzz/skills --skill business-logic-and-input-validation
npx skills add rachmanzz/skills --skill application-security-and-isolation
npx skills add rachmanzz/skills --skill architecture-and-config-hygiene
npx skills add rachmanzz/skills --skill observability-and-audit-trail
npx skills add rachmanzz/skills --skill api-contracts-and-integrations
npx skills add rachmanzz/skills --skill prompt-confidence-gate
```

## Install in Google Antigravity

The repository is also an Antigravity plugin: `plugin.json` at the root declares
the manifest, and the `skills/` layout supplies the skills. Install it with the
Antigravity CLI:

```bash
agy plugin install https://github.com/rachmanzz/skills.git
```

The plugin installs as `rachmanzz` with all ten skills:

```text
/rachmanzz:performance-and-resource-efficiency
/rachmanzz:evidence-led-concurrency-and-delivery
/rachmanzz:resilience-and-error-handling
/rachmanzz:data-integrity-and-lifecycle
/rachmanzz:business-logic-and-input-validation
/rachmanzz:application-security-and-isolation
/rachmanzz:architecture-and-config-hygiene
/rachmanzz:observability-and-audit-trail
/rachmanzz:api-contracts-and-integrations
/rachmanzz:prompt-confidence-gate
```

Alternatively, install manually by placing the plugin directory either in
`.agents/plugins/` at a workspace root (project scope) or in
`~/.gemini/config/plugins/` (global scope). No Antigravity-specific duplicate of
`SKILL.md` is required.

## License

MIT — see [LICENSE](LICENSE).
