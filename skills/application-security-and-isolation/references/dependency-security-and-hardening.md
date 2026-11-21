# Dependency Security Audit

Verify third-party packages, transitive dependencies, lockfiles, and build/run
supply-chain hygiene.

### Checklist

- **Known vulnerabilities (CVEs)**: check whether ecosystem scanners (`govulncheck`,
  `npm audit` / `pnpm audit`, `pip-audit`, `cargo audit`, `mvn`/`gradle`
  dependency checks, `dotnet list package --vulnerable`) are run against the
  actual lockfile and inspect reachable/high-severity advisories.
- **Lockfile & pinning integrity**: verify lockfiles (`go.sum`,
  `package-lock.json`/`pnpm-lock.yaml`, `Cargo.lock`, `poetry.lock`/`uv.lock`)
  exist, are committed, and are enforced in CI (`--frozen-lockfile` / `npm ci` /
  `-mod=readonly`).
- **Deprecated, unmaintained, or suspicious packages**: flag abandoned security-critical
  libraries (crypto, auth, parsers), typo-squatted names, and unverified
  pre/post-install lifecycle scripts.
- **Minimal attack surface**: flag unnecessary dependencies carrying heavy
  native/network parsers or overly broad runtime privileges (container running
  as root, wide IAM/DB roles).

Do not report clean dependency status (no known CVEs) without actually running
the appropriate ecosystem scanner and recording its exact scope, date, and
output—and qualify that clean scanner output covers only known advisory-DB
entries at scan time (not zero-days, native/OS packages, or uninspected files).
If no scanner was run or the advisory DB was unavailable, mark dependency
vulnerability status `UNKNOWN`.
