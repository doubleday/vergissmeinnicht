## 1. Canonical Access Timestamp Contract

- [x] 1.1 Add `last_accessed_at` to the `memory-service-core` delta spec as part of the canonical record shape
- [x] 1.2 Define initialization behavior for new records and clarify duplicate-create behavior for existing records

## 2. Read Path Semantics

- [x] 2.1 Define fetch-by-id behavior to advance `last_accessed_at` on successful reads
- [x] 2.2 Define search behavior to advance `last_accessed_at` for memories returned in results
- [x] 2.3 Confirm archive responses preserve `last_accessed_at` unless another rule in the same request path updates it

## 3. Validation

- [x] 3.1 Validate the change with the OpenSpec CLI
- [x] 3.2 Review the slice against supersession and confirm no replacement-lifecycle semantics were introduced
