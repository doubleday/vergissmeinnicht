## Why

The explicit supersession link now records replacement intent, but search still returns both the older and newer memories unless a caller post-processes results. The next smallest useful Milestone C slice is to let clients opt out of superseded records in search while keeping archive and fetch semantics simple and local to individual records.

## What Changes

- Add an optional `exclude_superseded` search flag that filters out memories explicitly superseded by another active memory in the same namespace.
- Define superseded-search filtering in terms of active superseding memories only, so archiving the newer record removes that suppression without adding restore or chain traversal rules.
- Clarify that archive remains record-local: archiving a superseding or superseded memory does not cascade to related memories and does not mutate supersession links.
- Leave create, fetch-by-id, duplicate-write, merge, and lineage traversal semantics unchanged in this slice.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `memory-service-core`: extend search and archive requirements with a narrow superseded-memory visibility rule.

## Impact

- Introduces a delta spec under [`openspec/changes/add-superseded-memory-search-filter/specs/memory-service-core/spec.md`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/openspec/changes/add-superseded-memory-search-filter/specs/memory-service-core/spec.md)
- Affects the search request model, PostgreSQL search query semantics, and service tests around superseded-memory visibility
- Preserves the existing four-endpoint API boundary and avoids merge, restore, reverse-link, or automatic archival workflows
