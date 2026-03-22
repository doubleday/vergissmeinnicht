## 1. Search Ordering Contract

- [x] 1.1 Add a spec delta for deterministic query-aware search ordering within the existing `memory-service-core` capability
- [x] 1.2 Keep non-query searches on the current browse path while defining stable tie-breakers

## 2. Search Ordering Implementation

- [x] 2.1 Update the PostgreSQL-backed search query to order query-present results by match strength, `confidence`, and stable tie-breakers
- [x] 2.2 Preserve the existing four endpoints and current filter semantics without adding new search fields or lifecycle behavior

## 3. Verification

- [x] 3.1 Add tests covering exact title matches ahead of weaker matches, title hits ahead of content-only hits, and confidence-based ordering within the same match tier
- [x] 3.2 Add tests confirming query-less searches remain chronological with deterministic ties
- [x] 3.3 Validate the change artifacts and run the targeted test suite before implementation is considered complete
