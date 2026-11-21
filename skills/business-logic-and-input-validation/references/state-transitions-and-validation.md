# State Transitions and Input Validation

## State Transition Audit

Verify that stateful entities follow an explicit, enforced lifecycle without
illegal jumps or skipped preconditions.

### Checklist

- **Allowed transition table**: check that every status update validates `(from_state, event) -> to_state` rather than blindly assigning `status = req.Status`.
- **Terminal & backwards transitions**: confirm terminal states (`completed`,
  `cancelled`, `refunded`, `archived`) reject unexpected re-opening or
  mutation.
- **Preconditions per transition**: verify required fields, approvals, or
  child-entity states exist before advancing state (e.g., cannot ship an unpaid
  order unless COD contract allows it).
- **Unknown state handling**: verify unrecognized enum/status values fail closed
  rather than matching a permissive fallback branch.

*(For database row locking and concurrent transition races, pair with
`data-integrity-and-lifecycle`.)*

## Input Validation Audit

Verify that untrusted inputs from HTTP/RPC requests, headers, query params,
files, and external payloads are validated and normalized at every entry point.

### Checklist

- **Allowlist validation**: enforce expected types, formats, lengths, ranges,
  enums, and character sets using strict allowlists rather than brittle
  blocklists.
- **Normalize before validate**: canonicalize Unicode (typically NFC rather than
  compatibility-altering NFKC unless required), trim/normalize paths and case
  where appropriate, and decode once before running validation so encoding
  tricks cannot bypass checks—while preserving raw bytes for passwords,
  cryptographic secrets, and signed payloads.
- **Reject unexpected fields/shapes**: verify whether unknown fields, duplicate
  keys, trailing garbage, or unexpected nesting depth are rejected cleanly on
  strict input DTOs (while noting forward-compatible external payload tolerances
  per `api-contracts-and-integrations`).
- **Upload & payload bounds**: enforce size limits, MIME/magic-byte validation
  (not only filename extensions), and decompression limits.
- **Sanitization context**: separate validation (rejecting invalid domain
  values) from output encoding/escaping for the target sink (SQL, shell, HTML,
  CSV formula injection).
