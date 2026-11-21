---
name: application-security-and-isolation
description: Audit, design, or harden application security—covering authentication, authorization (RBAC/IDOR/privilege escalation), multi-tenant isolation, injection (SQL/command/template/XSS/SSRF/path traversal), secret exposure, information disclosure in responses/logs, and vulnerable dependencies. Use when reviewing auth boundaries, user inputs reaching sinks, multi-tenant queries/caches, error disclosure, or supply-chain CVEs.
metadata:
  short-description: Audit auth, authz, tenant isolation, injection, secrets, info disclosure, and dependencies
---

# Application Security and Isolation

Use this skill to audit trust boundaries, identity enforcement, tenant
separation, injection resistance, secret management, disclosure hygiene, and
dependency security.

This skill complements—and does not replace—the repository's adjacent skills:

- Use `business-logic-and-input-validation` for non-security domain rules,
  calculation accuracy, state-machine completeness, and boundary math.
- Use `resilience-and-error-handling` for error propagation, degradation,
  timeouts, and retry budgets.
- Use `data-integrity-and-lifecycle` for database constraints, transactions,
  concurrent data races, and retention/deletion lifecycles.

Read only the references needed for the current task:

- Read [evidence-and-assumption-control.md](references/evidence-and-assumption-control.md)
  before claiming any security control holds.
- Read [authentication-and-authorization.md](references/authentication-and-authorization.md)
  for authentication checks, RBAC/ownership/IDOR prevention, and multi-tenant
  isolation.
- Read [injection-and-data-exposure.md](references/injection-and-data-exposure.md)
  for SQL/command/template/XSS/SSRF/path-traversal injection, secret exposure,
  and information disclosure in responses/logs.
- Read [dependency-security-and-hardening.md](references/dependency-security-and-hardening.md)
  for CVE scanning, lockfile pinning, and supply-chain checks.
- Read [validation-matrix.md](references/validation-matrix.md) when designing
  negative security tests or recording scan evidence.

## Non-negotiable rules

1. Treat middleware names, UI checks, and happy-path tests as hypotheses, not
   proof of enforcement.
2. Classify important claims as `VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`,
   `PARTIAL`, `NOT_FOUND_IN_SCOPE`, or `UNKNOWN`. Never upgrade `UNKNOWN` to
   `VERIFIED_IN_SCOPE` because middleware looks plausible, and preserve concrete
   bypasses or leaks as `CONTRADICTED_IN_SCOPE`.
3. Keep verified behavior, proposed remediations, observed negative tests, and
   inference visibly separate. Never assume uninspected gateways, WAFs, or
   network boundaries enforce missing checks—mark them `UNKNOWN` and record
   them in an assumption ledger.
4. Enforce default-deny authentication and resource-level authorization (never
   trust client-supplied user/role/tenant IDs over verified principal claims).
5. Scope every tenant-owned query, cache key, file path, queue payload, and
   cross-entity reference to the verified tenant (and explicitly justify any
   intentionally global/shared catalog data).
6. Require parameterization for values, strict allowlists for SQL identifiers,
   safe argument arrays, canonical path containment, and SSRF allowlists at
   all untrusted sinks.
7. Never permit hardcoded fallback secrets, unredacted credentials/PII in logs,
   or internal stack traces/SQL details in external error responses.
8. Never claim zero known CVEs in dependencies without running and observing
   the ecosystem vulnerability scanner against the lockfile (and qualify that
   clean scan output covers only known advisory-DB CVEs at scan time).

## Audit workflow

### 1. Map trust boundaries and assets

Identify external entry points, auth middleware, principal/tenant context
extraction, sensitive data/secrets, high-risk sinks (SQL, shell, templates,
filesystem, outbound HTTP), and dependency manifests/lockfiles.

### 2. Build the evidence and assumption ledgers

Record material claims and unverified trust assumptions separately using
[evidence-and-assumption-control.md](references/evidence-and-assumption-control.md).

### 3. Audit authentication, authorization, and tenant isolation

Apply [authentication-and-authorization.md](references/authentication-and-authorization.md)
to trace every protected route and verify token checks, RBAC/IDOR guards,
mass-assignment protection, and tenant scoping across DB/cache/storage.

### 4. Audit injection, secret exposure, and information disclosure

Apply [injection-and-data-exposure.md](references/injection-and-data-exposure.md)
to trace untrusted inputs to sinks, inspect secret handling and client bundles,
and check error responses, logs, and debug surfaces for leaks.

### 5. Audit dependency security

Apply [dependency-security-and-hardening.md](references/dependency-security-and-hardening.md)
to inspect lockfiles and run the ecosystem vulnerability scanner where
available.

### 6. Remediate and validate

Apply minimal boundary fixes and verify with negative security tests (401, 403,
cross-tenant, injection payloads, redacted error/log checks) using
[validation-matrix.md](references/validation-matrix.md).

## Required report shape

Include only applicable sections; mark non-applicable sections `OUT_OF_SCOPE`
with a short reason:

1. Scope, trust boundaries, and asset/sink map.
2. Evidence ledger for material security claims.
3. Authentication, authorization & tenant isolation findings.
4. Injection, secret exposure & information disclosure findings.
5. Dependency security findings & scanner output.
6. Validation performed and exact observed results.
7. Assumptions, uninspected layers, and remaining risks (`CONTRADICTED_IN_SCOPE`,
   `PARTIAL`, `NOT_FOUND_IN_SCOPE`, `UNKNOWN`).
