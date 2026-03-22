## 1. Confidence Contract

- [x] 1.1 Update the `memory-service-core` delta spec to define deterministic canonical confidence normalization for stored memory records
- [x] 1.2 Confirm the slice preserves the existing four-endpoint API boundary and does not introduce broader retrieval or lifecycle semantics

## 2. Confidence Normalization Implementation

- [x] 2.1 Update the create-path validation/normalization logic so in-range `confidence` values are normalized deterministically before persistence
- [x] 2.2 Ensure PostgreSQL persistence and returned canonical records preserve the normalized confidence value for create, fetch, search, archive, and duplicate-create responses
- [x] 2.3 Keep duplicate detection, search filtering, archive behavior, and endpoint surface unchanged

## 3. Verification

- [x] 3.1 Add targeted tests covering deterministic normalization of high-precision confidence inputs
- [x] 3.2 Add tests confirming create, fetch, search, archive, and duplicate-create responses expose the stored normalized confidence value consistently
- [x] 3.3 Run the relevant OpenSpec validation and targeted test suite before implementation is considered complete
