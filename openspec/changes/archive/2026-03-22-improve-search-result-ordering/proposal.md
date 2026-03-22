## Why

Search currently returns filtered memories ordered only by `updated_at DESC`. That keeps the implementation simple, but it does not reliably put the best textual match first when multiple active memories satisfy the same search request. The next narrow Milestone C slice should improve result quality without expanding the API surface or introducing broader retrieval semantics.

## What Changes

- Add a deterministic query-aware ordering policy to the existing `POST /memories/search` operation.
- When a query is present, order matching memories by text match strength first, then use stored `confidence` and stable tie-breakers to keep result selection predictable.
- When no query is present, preserve the current non-semantic search behavior apart from making tie-breaking deterministic.
- Leave create, fetch-by-id, archive, supersession behavior, and retrieval backends unchanged in this slice.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `memory-service-core`: refine search result ordering so filtered memories are returned in a deterministic, query-aware order.

## Impact

- Introduces a delta spec under [`openspec/changes/improve-search-result-ordering/specs/memory-service-core/spec.md`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/openspec/changes/improve-search-result-ordering/specs/memory-service-core/spec.md)
- Affects the search request handling and PostgreSQL-backed search query ordering
- Adds targeted tests around exact title matches, title-vs-content matches, confidence tie-breaking, and stable ordering
- Preserves the current four-endpoint API boundary and avoids merge, restore, delete, chain traversal, source weighting, or automatic extraction semantics
