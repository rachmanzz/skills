# Serialization and Webhook Reliability

## Serialization Audit

Audit encoding and decoding boundaries across JSON, Protobuf, MessagePack, CSV,
and external payloads for silent data loss or misinterpretation.

### Checklist

- **Numeric & precision fidelity**: flag 64-bit integers (`int64`/Snowflake IDs)
  serialized as raw JSON numbers consumed by JavaScript clients (precision loss
  above `2^53 - 1`), and floats used for exact decimal values.
- **Null vs omitted vs empty**: verify consistent handling of `null`, omitted
  fields, zero values (`0`, `false`, `""`), and empty arrays (`[]` vs `null`) on
  both marshal and unmarshal paths.
- **Time, timezone & encoding**: standardize timestamps (e.g., RFC3339/ISO-8601
  UTC with explicit offset) and verify UTF-8/base64/URL-safe encoding without
  double-encoding or silent invalid-UTF-8 replacement.
- **Strict vs tolerant decoding**: reject unexpected unknown fields only on
  strict versioned command DTOs where rolling-deploy N-1/N+1 additive skew is
  controlled and silent typos cause bugs; allow tolerant unknown-field skipping
  when consuming forward-compatible payloads or across rolling deploys.
- **Case & enum mapping**: verify explicit struct/JSON tags and enum string vs
  integer representations so serializer defaults never silently map unknown enums
  to zero values.

## Webhook Reliability Audit

Verify both **outbound webhook producers** and **inbound webhook consumers**
against real-world network retries, delays, and reordering.

### Checklist (Inbound Consumers)

- **Signature & replay window**: verify cryptographic signature (e.g., HMAC-SHA256)
  over the **raw unparsed body** using constant-time comparison, plus a bounded
  timestamp tolerance window to block replay attacks.
- **Fast ACK & async handoff**: verify the endpoint validates signature, persists
  or enqueues the event durably, and returns `2xx` within the provider's timeout
  instead of doing slow downstream work inline (which triggers retry storms).
- **Idempotent event deduplication**: persist provider `event_id` (or
  documented unique delivery key) atomically so replayed/retried deliveries are
  safely ignored (safe `2xx` no-op) without duplicate side effects.
- **Out-of-order & late events**: check timestamps/sequence versions so an older
  delayed event (e.g., `order.pending` arriving after `order.paid`) cannot
  overwrite newer state.

### Checklist (Outbound Producers)

- **Signing, event ID & timestamp**: include stable `event_id`, `created_at`,
  schema version, and cryptographic signature headers (e.g., HMAC or asymmetric
  signature) on every delivery.
- **Bounded delivery & DLQ**: pair with `resilience-and-error-handling` (bounded
  jittered retry, strict per-delivery timeout, SSRF-safe target URLs) and
  `evidence-led-concurrency-and-delivery` (durable outbox/queue & DLQ inspection).
