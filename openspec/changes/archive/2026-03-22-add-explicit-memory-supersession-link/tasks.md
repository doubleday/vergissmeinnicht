## 1. Canonical Supersession Contract

- [x] 1.1 Extend the canonical memory schema and API models with optional `supersedes_memory_id`
- [x] 1.2 Add create-time validation that any supplied `supersedes_memory_id` references an existing memory in the same namespace

## 2. Persistence And Duplicate Semantics

- [x] 2.1 Persist `supersedes_memory_id` in the PostgreSQL canonical store and return it through create, fetch, search, and archive responses
- [x] 2.2 Update duplicate-write matching so requests only dedupe when their `supersedes_memory_id` values also match

## 3. Verification

- [x] 3.1 Add service tests for successful supersession linkage, missing-reference rejection, and cross-namespace rejection
- [x] 3.2 Add duplicate-write tests covering matching versus differing `supersedes_memory_id` values
- [x] 3.3 Validate the change with the OpenSpec CLI and confirm it introduces no merge, restore, or automatic archival semantics
