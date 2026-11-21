# API Contracts and Compatibility

## API Contract Audit

Verify that inspected HTTP/REST, gRPC, or GraphQL endpoints match their
documented schemas and behave consistently with caller expectations.

### Checklist

- **Spec-to-implementation parity**: compare routes, HTTP methods, query/path
  parameters, request/response fields, required vs optional nullability, and
  status codes (`200`/`201`/`204`/`400`/`404`/`409`/`422`/`5xx`) against
  OpenAPI/Protobuf/GraphQL definitions.
- **Consistent error envelope**: verify error responses use one documented
  shape (`code`, `message`, `details`, `request_id`) across validation, auth,
  and unhandled failure middleware rather than leaking raw framework errors.
- **Pagination, filtering & sorting**: verify deterministic ordering (tie-breaker
  on unique ID), bounded `limit`, cursor/page semantics, and consistent empty
  page responses (`items: []` rather than `null`, unless a legacy contract
  explicitly documents nullable `items`).
- **Content-Type, method semantics & version routing**: check strict
  `Content-Type` / `Accept` handling, charset (`UTF-8`), side-effect-free `GET`/
  `HEAD` semantics, explicit version routing (path/header), and required
  correlation/idempotency headers.

## Compatibility Audit

Verify that schema, payload, and endpoint changes preserve safe interoperability
across rolling deploys and independent client versions.

### Checklist

- **Backward & forward compatibility**:
  - keep changes **additive** (new optional fields, new endpoints/versions);
  - never rename, remove, or change types/meanings of existing fields in-place
    under the same API version;
  - never reuse Protobuf field numbers or change enum numeric meanings;
  - ensure clients/consumers (and rolling-deploy servers receiving additive
    fields from newer clients) tolerate unknown fields and new enum variants
    gracefully instead of crashing on deserialization.
- **Nullability & constraint changes**: flag making a previously non-null
  response field nullable or omitted (weakening caller guarantees), or making a
  previously optional request field required without a version bump or safe
  server default.
- **Deprecation lifecycle**: verify deprecated fields/endpoints emit explicit
  deprecation headers/docs and have a measured removal window rather than
  silent breaking removal.
