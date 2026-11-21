# Validation Matrix

Use this matrix to verify API contracts, backward/forward compatibility,
serialization fidelity, and webhook reliability.

| Area | Scenario | Expected invariant | Evidence to record |
| --- | --- | --- | --- |
| API Contract | Valid, invalid, empty-list, and error responses vs OpenAPI/Proto spec | Routes, status codes, field types, pagination, and error envelopes match documented spec | Contract test output and captured payloads |
| Compatibility | Old client payload sent to new server; new optional fields/enums sent to old reader | Additive fields and unknown enum/field cases decode without breaking either side | Cross-version payload test results |
| Serialization | `int64 > 2^53-1`, empty slice `[]`, `null` vs omitted, UTC timestamp, unknown field | Precision, empty vs null semantics, timezone offset, and strict/tolerant decoding match contract | Round-trip encode/decode test output |
| Webhook (Security) | Invalid HMAC signature, modified raw body, or expired timestamp | Handler rejects (401/403) before processing or persisting event | Negative signature/replay test |
| Webhook (Reliability) | Duplicate `event_id` and out-of-order older event after newer state | Duplicate returns safe 2xx with 1 side effect; stale out-of-order event does not regress newer state | Event replay/reordering test and DB state |

For each check record exact payload/spec scope, command or test executed,
observed output, and claim status (`VERIFIED_IN_SCOPE`, `CONTRADICTED_IN_SCOPE`,
`PARTIAL`, `NOT_FOUND_IN_SCOPE`, or `UNKNOWN`).
