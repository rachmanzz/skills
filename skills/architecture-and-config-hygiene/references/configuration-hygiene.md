# Configuration Hygiene Audit

Verify how application configuration is loaded, defaulted, validated, and
documented across environments.

### Checklist

- **Missing required config (fail-fast)**: verify missing required variables
  (database DSN, signing keys, external base URLs, critical feature limits)
  fail immediately at startup with a clear error identifying the missing key—never
  at request time hours later.
- **Unsafe silent defaults**: flag dangerous fallback defaults such as:
  - hardcoded development secrets, default passwords, or permissive tokens;
  - wildcard CORS (`*`) with credentials, `0.0.0.0` unintended exposure, or
    debug/profiling flags enabled by default;
  - `0` / infinite timeouts, unbounded retries, or disabled TLS verification.
- **Invalid values & unit mismatches**: validate types, numeric bounds (`> 0`,
  `min <= max`), enum sets, URL formats, and duration units (seconds vs
  milliseconds—explicitly suffix or parse typed durations).
- **Silent parse fallback**: flag patterns like `parseInt(env.TIMEOUT) || 5000`
  where `0` or `"abc"` silently turns into `5000` instead of surfacing invalid
  configuration.
- **Environment drift & unused keys**: compare `.env.example` / config schemas,
  code readers, and deployment manifests so renamed or dead config keys are
  caught early.
- **Hot-reload & schema validation**: validate all active config fields
  together via one startup schema pass (scoping subcommand or optional-module
  fields to their enabled mode), and verify hot-reloaded configs/secrets either
  apply atomically or avoid mixed old/new credential states.
