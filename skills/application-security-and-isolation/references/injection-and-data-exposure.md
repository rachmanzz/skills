# Injection, Secret Exposure, and Information Disclosure

## Injection Audit

Trace untrusted data from source (request, header, file, DB, webhook) to
execution sink.

### Checklist

- **SQL / NoSQL injection**: require bound/parameterized queries for all
  values; flag string concatenation/interpolation in SQL, dynamic `ORDER BY` /
  column / table names without strict identifier allowlists, and raw query
  operators (`$where`, unvalidated filter objects).
- **Command & code injection**: forbid shell invocation (`sh -c`, `shell=True`)
  with user input; pass fixed binaries with argument arrays and strict input
  allowlists.
- **Template, XSS & HTML injection**: verify context-aware escaping in HTML/SVG/
  templates, safe `Content-Security-Policy` / sanitization for rich text, and
  no unsafe server-side template compilation of user strings.
- **SSRF & path traversal**: validate outbound URLs against scheme/host/CIDR
  allowlists and verify resolved socket/connect IPs against loopback, link-local,
  metadata IPs (`169.254.169.254`), IPv6 ULA/loopback/IPv4-mapped ranges, and
  unsafe redirects (mitigating DNS rebinding/TOCTOU). Canonicalize file paths,
  verify containment using path-segment/separator-aware checks (not naive string
  prefixes), and guard against symlinks (`O_NOFOLLOW`/open-relative checks).

## Secret Exposure Audit

Prevent credentials, signing keys, and tokens from leaking in code, builds,
configs, or client surfaces.

### Checklist

- **No hardcoded secrets**: flag API keys, private keys, JWT signing secrets,
  DB passwords, or webhook secrets committed in source, tests using real
  secrets, or default fallbacks (`secret || "dev-secret"`).
- **Client/frontend & artifact boundary**: verify server secrets never enter
  frontend env bundles, SSR props, public config endpoints, or error payloads.
- **Rotation & scoping**: verify separate keys per environment, least-privilege
  scopes, and support for key rotation without downtime.

## Information Disclosure Audit

Prevent internal system details, sensitive metadata, and PII from leaking via
responses or logs.

### Checklist

- **Error responses**: never return stack traces, SQL errors, internal hostnames,
  file paths, or dependency versions to external callers; map internal errors
  to safe opaque messages + correlation IDs.
- **Logs & telemetry**: redact passwords, Authorization/Cookie headers, session
  tokens, OTPs, payment data, and sensitive PII before logging or tracing.
- **Debug/introspection surfaces**: verify debug endpoints (`/debug/pprof`,
  GraphQL introspection, Swagger/Actuator/metrics) are disabled or strictly
  authenticated/network-restricted outside local dev.
