# Authentication, Authorization, and Tenant Isolation

## Authentication Audit

Verify how caller identity is established and validated across every protected
entry point.

### Checklist

- **Verification completeness**: verify signature, issuer (`iss`), audience
  (`aud`), expiration (`exp`/`nbf`), and algorithm pinning (`alg`, rejecting
  `none` or key-confusion) on tokens/JWTs.
- **Session and credential lifecycle**: check secure cookie flags (`HttpOnly`,
  `Secure`, `SameSite`), token revocation/rotation on logout or password change,
  constant-time secret/HMAC comparisons, and strong password hashing (`argon2`/
  `bcrypt`/`scrypt` with safe cost).
- **Brute-force & bypass paths**: check rate limiting/lockout on login/OTP/reset
  endpoints, default-deny middleware ordering, and absence of dev/test backdoor
  bypass flags in production paths.
- **CSRF & CORS boundaries**: on cookie-authenticated state-changing endpoints,
  verify CSRF tokens or origin/fetch-metadata checks, and forbid wildcard CORS
  (`*`) or unvalidated origin reflection paired with `Allow-Credentials: true`.

## Authorization Audit

Verify that authenticated callers can only perform actions and access resources
permitted to their identity and role.

### Checklist

- **Default deny**: verify every route/resolver/RPC enforces explicit
  authorization rather than relying on client UI hiding or opt-in decorators.
- **Object-level ownership (IDOR / BOLA)**: verify resource lookups scope by
  authorized owner/principal (`WHERE id = ? AND user_id = ?`), not just by
  object ID alone.
- **Function-level & privilege escalation**: verify admin/internal actions,
  role changes, and mass-assignment bindings (`req.body` bound directly into
  ORM structs) cannot elevate roles, flags, or ownership fields.

## Tenant Isolation Audit

Verify strict data and execution separation across tenants in multi-tenant
systems.

### Checklist

- **Authoritative tenant source**: derive `tenant_id` strictly from the
  verified auth principal/session—never trust a `tenant_id` supplied in request
  body, query string, or unverified header unless verified against principal
  membership.
- **Every data layer scoped**: verify SQL queries, ORM global scopes, cache keys
  (`tenant:{id}:...`), object-storage paths, search indexes, background job
  payloads, and WebSocket/pub-sub channels include tenant boundaries.
- **Cross-tenant reference checks**: when linking foreign IDs (e.g., attaching a
  file or item to an order), verify referenced IDs belong to the same tenant.
