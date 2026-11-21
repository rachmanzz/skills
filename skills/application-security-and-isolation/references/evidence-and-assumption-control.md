# Evidence and Assumption Control

Use this reference before claiming an endpoint is authenticated, authorized,
tenant-isolated, injection-safe, or free of exposed secrets and vulnerable
dependencies.

## Claim statuses

| Status | Meaning |
| --- | --- |
| `VERIFIED_IN_SCOPE` | A specifically scoped security claim is supported by direct inspection of handlers, middleware, queries, configs, or dependency scanners plus observed negative/exploit-path tests within that boundary. |
| `CONTRADICTED_IN_SCOPE` | Direct evidence or a concrete bypass/exposure path refutes the stated security property within its named scope. Preserve the exact bypass condition. |
| `PARTIAL` | The control holds only for identified routes, roles, sinks, or environments. |
| `NOT_FOUND_IN_SCOPE` | A named scope was searched and no auth check, tenant filter, parameterization, or redaction control was found there. This does not prove global absence. |
| `UNKNOWN` | Runtime configuration, upstream gateway auth, key management, or scanner output was not inspected or could not be verified. |

Never upgrade `UNKNOWN` to `VERIFIED_IN_SCOPE` because middleware, decorators,
or libraries look plausible. Keep verified behavior, proposed fixes, test
observation, and inference visibly separate. Do not infer security from
middleware registration names, route comments, test names, or happy-path 200 OK
tests, and do not convert `NOT_FOUND_IN_SCOPE` into global absence. Negative
tests (unauthenticated, wrong role, cross-tenant ID, malformed token, injection
payload) must actually run and be observed to claim enforcement.

## Claim ledger

| Claim | Evidence | Status | Validation |
| --- | --- | --- | --- |
| Security property and exact route/component scope | File, line, query, config, or scanner output | One status above | Negative test or tool command |

## Assumption ledger

Record assumptions separately and never assume an uninspected gateway, WAF, or
IAM layer enforces missing app-level controls:

| Assumption | Impact if false | Validation | Fallback |
| --- | --- | --- | --- |
| Upstream gateway, WAF, or runtime trust assumption | Bypass or data exposure path | Gateway/config inspection | Enforce check in application boundary |

An assumption is not a fact. If it materially affects trust boundaries or data
exposure, verify it directly or label the posture as conditional.

## Completion gate

Before saying “hardened against [tested vector]”, “authorized”, “isolated”, or
“protected”, qualify the statement with its exact inspected scope and test
limits (never claim unconditionally “secure” from static review and tests
alone), and require:

1. trust boundaries, routes, queries, sinks, and dependencies in scope were
   inspected;
2. the inspected boundary is stated explicitly;
3. negative authorization/tenant/injection/exposure checks ran and were
   observed (or gaps reported as `NOT_FOUND_IN_SCOPE`/`UNKNOWN`);
4. error and log paths were checked for secret/PII leakage;
5. uninspected layers (gateway, infra, IAM) are disclosed.

If any item is missing, use “proposed”, “partially verified”, “not observed”,
or “requires validation”.
