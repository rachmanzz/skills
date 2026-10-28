# Performance and Resource Efficiency Skills

A practical Agent Skill for finding, explaining, and fixing performance
bottlenecks in memory usage, loops, methods, data structures, I/O, concurrency,
profiling, and caching.

## Repository layout

```text
.
├── package.json
├── .github/
│   └── workflows/
│       └── validate-skill.yml
└── skills/
    └── performance-and-resource-efficiency/
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
            ├── evidence-and-assumption-control.md
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
            │   └── shared-cache-backends.md
            └── language-adapters/
                ├── javascript-typescript.md
                ├── python.md
                ├── go.md
                ├── java.md
                ├── rust.md
                └── csharp.md
```

## Install from a Git repository

```bash
npx skills add owner/repository --skill performance-and-resource-efficiency
```

## Validate locally

```bash
python3 skills/performance-and-resource-efficiency/scripts/validate-skill-package.py
python3 skills/performance-and-resource-efficiency/scripts/validate-evidence.py \
  skills/performance-and-resource-efficiency/references/evidence-ledger-template.md
```

For a local test:

```bash
npx skills add . --skill performance-and-resource-efficiency --copy -y
```

## Install as an npm dependency

After publishing this package to npm, a consuming project can use the
experimental npm synchronization flow:

```bash
npm install -D skills performance-and-resource-efficiency-skills
npx skills experimental_sync -y
```
