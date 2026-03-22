## Context

The service now stores explicit supersession intent through `supersedes_memory_id`, but that linkage is informational only. Search still returns both the older and newer memories, and archive only toggles a single record's `archived` flag without any documented relationship to supersession.

This slice needs to stay smaller than a full replacement workflow. The current API boundary remains `create`, `search`, `get by id`, and `archive`, PostgreSQL remains the canonical lifecycle store, and the codebase currently executes search directly against PostgreSQL filters rather than a separate semantic merge pipeline.

## Goals / Non-Goals

**Goals:**

- Add one narrow search-time control that lets clients hide superseded memories
- Define that superseded filtering is based on active superseding memories in the same namespace
- Clarify that archive remains record-local even when supersession links exist
- Preserve current behavior for create, fetch, duplicate detection, and default search requests

**Non-Goals:**

- Automatically archiving superseded memories
- Restoring or unarchiving related memories
- Traversing supersession chains or exposing reverse-link APIs
- Choosing a canonical winner among multiple active superseding memories
- Changing ranking or introducing Qdrant-based supersession logic

## Decisions

Add an optional search flag named `exclude_superseded`, defaulting to `false`.
Rationale: this is the smallest additive API change. It lets clients opt into cleaner search results without breaking the current contract or forcing all callers to adopt supersession-aware behavior immediately.

Treat a memory as suppressed only when another active memory in the same namespace points to it through `supersedes_memory_id`.
Rationale: namespace is the existing tenant boundary, and active-only suppression keeps archive semantics simple. If the newer memory is archived, the older memory becomes visible again under `exclude_superseded` without needing restore rules or extra state.

Implement suppression in the PostgreSQL canonical search query with a `NOT EXISTS` check.
Rationale: PostgreSQL already owns lifecycle fields and exact relationship metadata. Query-time filtering is smaller and safer than introducing derived flags, background jobs, or Qdrant payload coordination for this slice.

Document archive as a record-local mutation with no cascade and no link rewrites.
Rationale: the current implementation already updates only the targeted row. Making that behavior explicit closes the policy gap without expanding the archive endpoint into lineage management.

## Risks / Trade-offs

[The search API gains another boolean flag] -> Mitigation: keep the name narrow and default it to `false` so existing callers remain unchanged.

[Multiple active memories can supersede the same older memory] -> Mitigation: treat suppression as existential. If any active superseding memory exists in the same namespace, the older memory is excluded when requested.

[Future semantic retrieval may not run purely in PostgreSQL] -> Mitigation: define the behavior at the contract level now and implement it in PostgreSQL for the current codebase. A later retrieval pipeline can preserve the same rule as a post-filter.

## Migration Plan

Add `exclude_superseded` as an optional search request field with a default of `false`, so existing clients continue to validate and behave the same.

Update the PostgreSQL search query to apply superseded filtering only when that flag is enabled.

No data migration is required because the existing `supersedes_memory_id` field already stores the needed linkage.

## Open Questions

None for this slice. Automatic archival, reverse traversal, merge behavior, and ranking changes remain intentionally deferred.
