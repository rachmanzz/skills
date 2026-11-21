# Boundary Conditions and Calculation Accuracy

## Boundary Condition Audit

Check every numeric, string, collection, pagination, and date/time boundary
where edge inputs frequently trigger bugs or silent wraparound.

### Checklist

- **Empty, zero, and null**: verify behavior on `0`, `-0`, `""`, whitespace-only
  strings, `[]`, `{}` and missing/null fields (distinguishing `0` from unset).
- **Min/max and off-by-one**: check inclusive vs exclusive bounds (`<` vs `<=`,
  `>` vs `>=`), single-element ranges, and zero-length slices.
- **Numeric overflow and underflow**: check integer addition/multiplication
  overflow (especially unit conversions, timestamps, counters, and quantities),
  negative quantities/amounts, `NaN`, and `Infinity`.
- **Pagination and batch bounds**: verify `page <= 0`, `limit <= 0`, oversized
  `limit`, and empty result sets do not panic, return unbounded results, or
  skip records.
- **Date, time, and DST**: check leap years, month-end arithmetic, timezone
  offsets, daylight-saving transitions, clock-skew tolerance, and monotonic vs
  wall-clock usage for elapsed durations versus absolute calendar deadlines.

## Calculation Accuracy Audit

Audit financial, billing, quota, scoring, and scientific computations for
precision loss, rounding drift, and order-of-operations defects.

### Checklist

- **Exact representation**: flag binary floating-point (`float`/`double`/`number`)
  used for money, tax, ledger balances, or exact decimal rates; require integer
  minor units or fixed-point/decimal arithmetic unless a documented domain
  specification explicitly permits approximate float precision.
- **Rounding rules**: verify the rounding mode (half-up, half-even, floor,
  ceil) and precision scale are explicit and match business/regulatory rules.
- **Order of operations and remainder allocation**: check whether multiplying
  before dividing avoids truncation loss (while guarding against intermediate
  integer overflow via wider types or checked arithmetic), and whether
  partitioned/prorated totals preserve exact sum (`sum(parts) == total` via
  remainder allocation) where the business rule requires whole-allocation parity.
- **Unit & currency consistency**: verify explicit unit/currency tags and
  exchange/conversion rates so mixed units or currencies cannot be added
  without conversion.
- **Division by zero**: verify denominators (`count`, `total`, `weight`,
  `duration`) are guarded before division.
