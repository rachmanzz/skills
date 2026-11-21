# Validation Matrix

Use this matrix to verify authentication, authorization, tenant isolation,
injection defenses, secret/information redaction, and dependency security.

| Area | Scenario | Expected invariant | Evidence to record |
| --- | --- | --- | --- |
| Authentication | Missing, expired, tampered, or `alg=none` token | Request is rejected (401) before handler execution | Token test cases and returned status |
| Authorization | Low-privilege user calls admin action or foreign resource ID | Access is denied (403/404) without mutating or leaking resource existence | Cross-role/IDOR test results and DB state |
| Tenant Isolation | Request supplies another `tenant_id` in body/query/ID | Mismatched `tenant_id` is rejected (403/404) or ignored in favor of verified principal tenant per contract; zero cross-tenant rows/cache/files returned | Cross-tenant negative test and query/cache trace |
| Injection | SQLi, shell metacharacters, `../` path, metadata SSRF URL | Parameterization/allowlist/canonicalization blocks payload cleanly | Payload inputs and execution/query logs |
| Secret Exposure | Search source, env templates, build outputs, client bundles | No live credentials, fallback signing keys, or server secrets exposed | Scan command output and inspected files |
| Information Disclosure | Trigger 500/validation/auth error and inspect response + logs | External response hides stack/SQL/paths; logs redact tokens, headers, and PII | Captured error response and log line |
| Dependency Security | Run ecosystem CVE audit against committed lockfile | Scanner exit status and any reachable CVEs reported with exact severity/remediation | Scanner command, lockfile scope, and output |

For each executed check record:

- exact route, query, config, or scanner command;
- observed response, log output, or advisory report;
- claim status (`VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`, `PARTIAL`, `NOT_FOUND_IN_SCOPE`, or `UNKNOWN`).
