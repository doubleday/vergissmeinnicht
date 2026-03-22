## 1. Query Search Fallback Contract

- [x] 1.1 Keep the query-present search API unchanged while defining fallback behavior for zero semantic candidates and temporary query-time retrieval failures
- [x] 1.2 Preserve semantic-first ordering when candidates exist and PostgreSQL query-aware ordering when fallback is used

## 2. Query Search Implementation

- [x] 2.1 Update the service search flow so non-empty queries fall back to the existing PostgreSQL query search when Qdrant returns no candidates
- [x] 2.2 Handle temporary Qdrant query-time retrieval failures by reusing the same PostgreSQL fallback path without changing non-query browse behavior

## 3. Verification

- [x] 3.1 Add targeted tests covering lexical fallback on zero semantic candidates, fallback on temporary Qdrant search failure, and preserved semantic-first behavior when candidates exist
- [x] 3.2 Validate the change with the OpenSpec CLI and the targeted test suite before implementation is considered complete
