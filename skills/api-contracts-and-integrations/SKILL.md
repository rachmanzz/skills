---
name: api-contracts-and-integrations
description: Audit, design, or verify external and inter-service integration boundaries—covering API contract parity, backward/forward schema compatibility, serialization encoding/decoding fidelity, and webhook reliability. Use when reviewing OpenAPI/Protobuf/REST contracts, API versioning, JSON/binary marshaling, or inbound/outbound webhooks. For dependency timeouts/retries/degradation, use resilience-and-error-handling; for durable queue delivery, use evidence-led-concurrency-and-delivery.
metadata:
  short-description: Audit API contracts, compatibility, serialization, and webhook reliability
---

# API Contracts and Integrations

Use this skill to verify that service APIs, wire schemas, serializers, and
webhook integrations uphold strict contracts across versions and unreliable
networks.

This skill complements—and does not replace—the repository's adjacent skills:

- Use `resilience-and-error-handling` for **external dependency** resilience
  (timeouts, bounded retries, circuit breaking, degradation, and fault isolation).
- Use `evidence-led-concurrency-and-delivery` for **message delivery** durability
  (broker ack ordering, lease ownership, outbox mechanics, and queue backpressure).
- Use `application-security-and-isolation` for authentication, authorization,
  SSRF, and injection security at API endpoints.

Read only the references needed for the current task:

- Read [evidence-and-assumption-control.md](references/evidence-and-assumption-control.md)
  before claiming API parity, compatibility, serialization fidelity, or webhook
  reliability holds.
- Read [api-contracts-and-compatibility.md](references/api-contracts-and-compatibility.md)
  for spec parity, consistent error envelopes, pagination contracts, and
  additive backward/forward compatibility.
- Read [serialization-and-webhooks.md](references/serialization-and-webhooks.md)
  for JSON/Protobuf encoding fidelity (`int64`, `null` vs `[]`, timezones,
  unknown fields) and inbound/outbound webhook reliability.
- Read [validation-matrix.md](references/validation-matrix.md) when designing
  contract, round-trip, compatibility, or webhook replay/reordering tests.

## Non-negotiable rules

1. Classify important claims as `VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`,
   `PARTIAL`, `NOT_FOUND_IN_SCOPE`, or `UNKNOWN`. Never upgrade `UNKNOWN` to
   `VERIFIED_IN_SCOPE` because specs or DTOs look aligned, and keep verified
   wire behavior, proposed changes, test outputs, and inference visibly
   separate.
2. Treat OpenAPI/Swagger annotations, client SDK types, and mocks as hypotheses
   until verified against actual serialized wire payloads and live handler
   responses; never invent unstated partner webhook rules or consumer
   tolerances (record them as `UNKNOWN` in an assumption ledger).
3. Preserve backward and forward compatibility on shared APIs and events; never
   make breaking renames, type changes, or enum renumberings under an existing
   version.
4. Guard serialization boundaries for `int64` precision, `null` vs empty
   collections, explicit UTC timestamps, and unknown enum/field handling.
5. Verify inbound webhooks over the raw request body using the provider's
   cryptographic authentication (constant-time HMAC, asymmetric signature, or
   verified mTLS) and replay-window checks when applicable, enqueue/persist
   before heavy work, and deduplicate by stable event ID (or payload/header
   fingerprint if absent) while protecting against out-of-order events.

## Audit workflow

### 1. Map external contracts and wire boundaries

Identify all API specs, handlers, client DTOs, serializers, webhook endpoints/
dispatchers, and partner integration dependencies.

### 2. Build the evidence and assumption ledgers

Record material claims and unverified consumer/provider assumptions separately
using [evidence-and-assumption-control.md](references/evidence-and-assumption-control.md).

### 3. Audit API contracts and compatibility

Apply [api-contracts-and-compatibility.md](references/api-contracts-and-compatibility.md)
to check spec-to-handler parity, error envelopes, pagination determinism, and
evolution/versioning safety.

### 4. Audit serialization and webhooks

Apply [serialization-and-webhooks.md](references/serialization-and-webhooks.md)
to inspect marshaling/unmarshaling edge cases and inbound/outbound webhook
verification, deduplication, ordering, and fast-ACK boundaries.

### 5. Cross-check dependency resilience and message delivery

Verify that outbound HTTP/webhook calls apply `resilience-and-error-handling`
budgets and async event pipelines apply `evidence-led-concurrency-and-delivery`
durability rules.

### 6. Implement and validate

Apply minimal contract-preserving fixes and verify with contract, round-trip,
compatibility, and webhook replay/order tests using
[validation-matrix.md](references/validation-matrix.md).

## Required report shape

Include only applicable sections; mark non-applicable sections `OUT_OF_SCOPE`
with a short reason:

1. Scope, specs, serializers, and webhook endpoints inspected.
2. Evidence ledger for contract and integration claims.
3. API contract & compatibility findings.
4. Serialization findings.
5. Webhook reliability findings (and cross-links to resilience/delivery).
6. Validation performed and exact observed results.
7. Assumptions, uninspected external consumers/providers, and remaining risks.
