# Performance and Reliability Skills

A collection of installable Agent Skills for measured performance work and
evidence-led concurrent or asynchronous execution. The skills use the standard
`SKILL.md` format and are compatible with Codex, Antigravity (`agy`), and other
skills-compatible agents.

## Included skills

- `performance-and-resource-efficiency` — memory, allocation, algorithms,
  loops, I/O, concurrency, profiling, benchmarking, and cache reliability.
- `evidence-led-concurrency-and-delivery` — cancellation, failure isolation,
  leak prevention, join/wait behavior, shutdown, idempotency, transactions,
  ownership, visibility, durability, batching, backpressure, admission, and
  fairness with explicit evidence control.

## Repository layout

```text
.
├── LICENSE
├── package.json
├── tests/
│   ├── test_validate_evidence.py
│   └── test_validate_skill_package.py
├── .github/
│   └── workflows/
│       └── validate-skill.yml
└── skills/
    ├── performance-and-resource-efficiency/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        ├── scripts/
        │   ├── validate-evidence.py
        │   └── validate-skill-package.py
        └── references/
            ├── memory-efficiency.md
            ├── loop-and-algorithm-design.md
            ├── method-design.md
            ├── data-structures.md
            ├── io-and-database-efficiency.md
            ├── concurrency.md
            ├── profiling-and-benchmarking.md
            ├── evidence-and-assumption-control.md
            ├── evidence-ledger-template.md
            ├── cache-reliability-and-fallback/
            │   ├── cache-contract.md
            │   ├── consistency-and-write-policies.md
            │   ├── database-protection.md
            │   ├── expiration-and-rotation.md
            │   ├── fallback-flow.md
            │   ├── lru-capacity.md
            │   ├── observability.md
            │   ├── operational-controls.md
            │   ├── security-and-isolation.md
            │   ├── shared-cache-backends.md
            │   └── language-adapters/
            │       ├── csharp.md
            │       ├── go.md
            │       ├── java.md
            │       ├── javascript-typescript.md
            │       ├── python.md
            │       └── rust.md
            └── language-adapters/
                ├── javascript-typescript.md
                ├── python.md
                ├── go.md
                ├── java.md
                ├── rust.md
                └── csharp.md
    └── evidence-led-concurrency-and-delivery/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        └── references/
            ├── evidence-and-assumption-control.md
            ├── cancellation-and-failure-propagation.md
            ├── panic-recovery-and-leak-prevention.md
            ├── join-wait-and-shutdown.md
            ├── idempotency-and-transaction-boundaries.md
            ├── ownership-visibility-and-durable-storage.md
            ├── batching-backpressure-and-admission.md
            ├── fairness-and-scheduling.md
            └── validation-matrix.md
```

## Install from a Git repository

```bash
npx skills add owner/repository --skill performance-and-resource-efficiency
npx skills add owner/repository --skill evidence-led-concurrency-and-delivery
```

## Validate locally

```bash
python3 skills/performance-and-resource-efficiency/scripts/validate-skill-package.py
python3 skills/performance-and-resource-efficiency/scripts/validate-skill-package.py \
  skills/evidence-led-concurrency-and-delivery
python3 skills/performance-and-resource-efficiency/scripts/validate-evidence.py \
  skills/performance-and-resource-efficiency/references/evidence-ledger-template.md
python3 -m unittest discover -s tests -v
```

For a local test:

```bash
npx skills add . --skill performance-and-resource-efficiency --copy -y
npx skills add . --skill evidence-led-concurrency-and-delivery --copy -y
```

## Install in Google Antigravity

Install the skill bundle with the Antigravity CLI:

```bash
agy plugin install https://github.com/rachmanzz/skills.git
```

Antigravity discovers the skills under the workspace `.agents/skills/` directory
and exposes them as:

```text
/performance-and-resource-efficiency
/evidence-led-concurrency-and-delivery
```

No Antigravity-specific duplicate of `SKILL.md` is required.

## Install as an npm dependency

After publishing this package to npm, a consuming project can use the
experimental npm synchronization flow:

```bash
npm install -D skills performance-and-resource-efficiency-skills
npx skills experimental_sync -y
```

## License

MIT — see [LICENSE](LICENSE).
