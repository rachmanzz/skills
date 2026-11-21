# Evidence and Assumption Control

Use this reference before claiming an API matches its specification, a schema
change is backward-compatible, serialization is lossless, or webhook handling
is reliable.

## Claim statuses

| Status | Meaning |
| --- | --- |
| `VERIFIED_IN_SCOPE` | A specifically scoped contract claim is supported by direct spec/schema/handler inspection and observed contract, serialization, or webhook tests within that boundary. |
| `CONTRADICTED_IN_SCOPE` | Direct evidence or a payload counterexample shows spec drift, breaking schema changes, precision/encoding corruption, or missing webhook replay/signature checks. |
| `PARTIAL` | The contract holds only for identified endpoints, versions, or payload shapes. |
| `NOT_FOUND_IN_SCOPE` | A named scope was searched and no schema validation, signature check, deduplication, or compatibility rule was found there. |
| `UNKNOWN` | Downstream consumer behavior, external provider webhook retry rules, or unpublished schema specs were not inspected. |

Never upgrade `UNKNOWN` to `VERIFIED_IN_SCOPE` because OpenAPI annotations,
generated types, or mocks look consistent. Keep verified contract behavior,
proposed schema edits, observed test payloads, and inference visibly separate,
and do not convert `NOT_FOUND_IN_SCOPE` into global absence. Do not infer API
contract compliance from handler type names, outdated OpenAPI/Swagger docs, or
test names alone. Compare the live serialized response, status codes, and error
envelopes against the declared contract.

## Claim ledger

| Claim | Evidence | Status | Validation |
| --- | --- | --- | --- |
| Contract or integration property and scope | Spec file, DTO/serializer, handler, or contract test | One status above | Contract/round-trip/webhook test |

## Assumption ledger

Record assumptions separately and never invent unstated partner webhook
retry/ordering behavior or consumer field tolerance:

| Assumption | Impact if false | Validation | Fallback |
| --- | --- | --- | --- |
| Assumed consumer tolerance or provider webhook ordering | Client breakage or missed/duplicate events | Consumer/provider contract check | Additive evolution + idempotent handler |

An assumption is not a fact. If it materially affects wire compatibility or
event ordering, verify it against consumer/provider specs or mark it conditional.

## Completion gate

Before saying “compatible”, “contract-compliant”, or “webhook-safe”, qualify
the statement with its scope and require:

1. schema/OpenAPI/Protobuf definitions and actual handlers/serializers were
   inspected;
2. breaking-change rules and wire edge cases (`null` vs `[]`, `int64`, dates,
   unknown fields) were checked;
3. if webhooks are in scope, webhook signature, timestamp window, and event-ID
   deduplication were verified;
4. contract and round-trip tests ran and were observed;
5. uninspected consumers or external providers are disclosed as `UNKNOWN`.

If any item is missing, use “proposed”, “partially verified”, “not observed”,
or “requires validation”.
