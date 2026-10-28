# Security and Isolation

Cache correctness includes protecting data boundaries. A fast cache that returns
another tenant's or user's value is a security failure.

## Key and value requirements

- include tenant, identity, authorization scope, locale, and representation
  version when they affect the result;
- prevent user-controlled input from creating unsafe or unbounded key space;
- never use a shared key for values with different authorization outcomes;
- avoid storing secrets or sensitive values unless protection and retention are
  explicitly designed;
- define encryption, access control, and transport requirements for remote
  backends;
- validate deserialized values and reject incompatible schema versions.

## Validation

Test cross-tenant access, changed authorization, revoked access, key collisions,
cache poisoning, stale permissions, and deployment schema changes. Verify that
cache bypass and database fallback enforce the same authorization checks as a
cache hit.
