# Cache Contract

Define a cache contract before choosing a library or backend. A cache contract
describes what may be stored, how fresh it must be, and what happens when it is
not available.

## Required decisions

For each cache entry, specify:

- key format and namespace;
- value schema and serialization format;
- source of truth;
- freshness requirement;
- TTL or invalidation rule;
- maximum stale period, if stale reads are allowed;
- behavior for missing, empty, negative, or deleted values;
- fallback source;
- privacy and authorization boundaries;
- versioning strategy for schema or deployment changes.

## Cache is normally not the source of truth

Unless explicitly stated otherwise, treat the database or origin system as the
authoritative source. A cached value is a performance optimization and may be
missing, expired, evicted, stale, corrupted, or unavailable.

## Key safety

Keys must include every input that affects the result, including tenant,
locale, authorization scope, feature version, and data version where relevant.
Never allow a key to bypass authorization or tenant isolation.

## Negative caching

If the system caches “not found” results, define a shorter TTL and invalidate
the negative entry when the record can be created. Do not make negative caching
an accidental side effect of serializing a missing database result.
