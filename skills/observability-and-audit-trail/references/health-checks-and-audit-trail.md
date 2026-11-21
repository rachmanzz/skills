# Health Checks and Audit Trail

## Health Check Audit

Verify that health endpoints accurately represent service ability to serve
traffic without causing cascading restarts or slow probe hangs.

### Checklist

- **Liveness vs readiness separation**:
  - **Liveness** (`/livez` / `/healthz`): checks only whether the process event
    loop/runtime is alive and unblocked; **never** check external/soft
    dependencies (DB outages or slow third-party APIs must not kill and restart
    all pods).
  - **Readiness** (`/readyz`): checks required critical dependencies, schema/cache
    warmth, and shutdown draining state so load balancers stop routing traffic
    when the instance cannot serve safely.
  - **Startup probe**: give slow-booting migrations or model/cache preloads a
    dedicated startup window before liveness kicks in.
- **Deep check safety & bounds**: enforce strict short timeouts on dependency
  probes (e.g., `SELECT 1`, Redis `PING`), cache or rate-limit expensive deep
  checks to prevent probe amplification, and avoid leaking internal hostnames or
  secrets in unauthenticated health JSON.

## Audit Trail Audit

Verify that security-sensitive, financial, and administrative actions produce a
complete, durable, append-only activity history (and verify storage-level
tamper controls where claimed).

### Checklist

- **Coverage of critical events**: record authentication events, role/permission
  changes, API key/secret rotations, financial/balance mutations, exports,
  deletions, and admin overrides.
- **Required record fields**: include immutable timestamp (UTC), actor identity
  (user/service + impersonator if applicable), action, target resource type/ID,
  outcome (success/denied/failed), correlation/request ID, source IP/user-agent,
  and safe before/after diff or reason (redacting secrets/tokens).
- **Atomicity & durability**: persist audit records reliably (same DB transaction
  or durable append-only outbox/log) so critical mutations cannot succeed while
  their audit record is silently lost.
- **Append-only controls & retention**: verify audit tables/streams are
  append-only at the API layer (no user-facing `UPDATE`/`DELETE` endpoints) and
  check DB/storage write permissions, WORM storage, or cryptographic chaining
  when tamper-resistance is claimed, along with defined retention/export
  policies.
