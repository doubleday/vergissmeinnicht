## Context

The current query-present search flow always embeds the query, asks Qdrant for candidate memory IDs, and resolves those IDs through PostgreSQL. That makes semantic retrieval real, but it also creates a brittle edge: if Qdrant returns no candidates, the search returns an empty result even when PostgreSQL still contains obvious substring matches. If Qdrant raises a transient error, the whole query search fails even though the canonical store is still available.

This slice is intentionally smaller than a hybrid retrieval redesign. The goal is not to fuse semantic and lexical ranking. The goal is to keep the existing search endpoint useful and deterministic when the retrieval index is empty or temporarily unavailable.

## Goals / Non-Goals

**Goals:**

- Preserve semantic retrieval as the primary path for query-present searches when Qdrant returns candidates successfully.
- Fall back to the existing PostgreSQL lexical search path when Qdrant returns no candidates for a non-empty query.
- Fall back to the existing PostgreSQL lexical search path when Qdrant query-time retrieval raises a temporary error.
- Keep the API shape, canonical response records, filter semantics, and query-less browse path unchanged.

**Non-Goals:**

- Adding new endpoints, request flags, response fields, or adapter-specific behavior.
- Blending lexical and semantic result sets when Qdrant already returns candidates.
- Adding background reindexing, retry workers, or broader startup/lifecycle redesign.
- Changing create-time or archive-time Qdrant behavior in this slice.

## Decisions

Fall back only in the query-present search path, not in write operations.
Rationale: the motivating gap is real search usability and search-path reliability. Keeping the slice search-only avoids broadening into write durability or lifecycle redesign.
Alternative considered: also tolerate Qdrant failures during create and archive. Rejected because that expands the slice into write-path consistency decisions and likely needs a broader replay or repair story.

Treat both "no semantic candidates" and "semantic retrieval exception" as reasons to use the existing PostgreSQL query search.
Rationale: both cases leave the semantic path unable to produce query results, and the existing PostgreSQL path already provides a deterministic canonical search behavior with the same filters and response shape.
Alternative considered: only fall back on retrieval exceptions, while preserving empty results for zero candidates. Rejected because an empty vector result can still hide obvious title/content matches and weakens real search behavior unnecessarily.

Keep the fallback ordering entirely in PostgreSQL rather than adding a service-layer merge.
Rationale: the lexical fallback should behave exactly like the existing query-aware PostgreSQL search path, including its deterministic ordering and `last_accessed_at` handling.
Alternative considered: pull fallback matches into Python and merge them with semantic results. Rejected because this slice is not a hybrid ranking project and does not need a second ordering system.

Preserve semantic rank ordering whenever Qdrant returns candidates successfully.
Rationale: the fallback is a safety net, not a replacement for semantic retrieval. If Qdrant produced candidates, the current semantic-first behavior should remain intact.
Alternative considered: always union semantic and lexical results. Rejected because it changes ranking semantics, increases scope, and moves this slice toward a broader retrieval redesign.

## Risks / Trade-offs

[Lexical fallback can return weaker matches than the semantic path would have found] -> Mitigation: keep semantic retrieval primary when it succeeds and use fallback only when the semantic path produces no usable candidate list.

[Catching overly broad exceptions could hide deeper retrieval bugs] -> Mitigation: constrain the fallback to query-time semantic retrieval and keep readiness checks unchanged so Qdrant health issues still surface operationally.

[Different ordering rules between semantic and fallback results may be visible across requests] -> Mitigation: document the distinction explicitly in the spec and reuse the existing deterministic PostgreSQL ordering for fallback behavior.

## Migration Plan

No API migration is required because the request and response schema stay unchanged.

Implementation should adjust the service search orchestration so query-present requests attempt semantic retrieval first and then delegate to the existing PostgreSQL query search when semantic retrieval returns no candidates or raises an exception.

Rollback is straightforward: restore the current semantic-only query-present flow while leaving the underlying PostgreSQL search path and Qdrant indexing intact.

## Open Questions

None for this slice. Hybrid retrieval, partial semantic-plus-lexical unions, and write-path retry/repair behavior remain intentionally deferred.
