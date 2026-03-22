## 1. Canonical Source Contract

- [x] 1.1 Update the `memory-service-core` delta spec to define a minimal canonical `source` shape with normalized `type` and optional normalized `name`
- [x] 1.2 Validate that the change preserves the existing four-endpoint API boundary and does not introduce broader provenance or lifecycle semantics

## 2. Source Normalization Implementation

- [x] 2.1 Update the memory API models to support `source.name` and normalize `source.type`/`source.name` deterministically in the canonical create path
- [x] 2.2 Ensure PostgreSQL persistence stores the normalized `source` envelope and returned records preserve that shape for create, fetch, search, archive, and duplicate-create responses
- [x] 2.3 Keep duplicate-write rules, supersession behavior, archive behavior, and search ordering unchanged

## 3. Verification

- [x] 3.1 Add targeted tests for trimmed and lowercased `source.type`
- [x] 3.2 Add targeted tests for optional `source.name` trimming and omission when blank
- [x] 3.3 Add targeted tests confirming returned records keep the same normalized source shape across create, fetch, search, archive, and duplicate-create paths
- [x] 3.4 Run the relevant OpenSpec validation and targeted test suite before implementation is considered complete
