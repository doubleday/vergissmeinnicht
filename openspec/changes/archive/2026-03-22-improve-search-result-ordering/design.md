## Context

The current search path applies exact filters in PostgreSQL and optionally narrows results with a simple `ILIKE` condition across `title` and `content`. After filtering, it orders rows by `updated_at DESC` and applies the limit. That is stable enough for chronology, but it is weak as a relevance policy: a recent memory with only a loose content hit can outrank an older memory with an exact title match.

Milestone C is about keeping the store usable after repeated writes. In this codebase, the smallest useful result-quality improvement is to make search ordering more intentional while staying inside the current API contract and data model. The service already stores `confidence`, `title`, `content`, `updated_at`, and `id`, so no new lifecycle concept or retrieval backend is required.

## Goals / Non-Goals

**Goals:**

- Improve `POST /memories/search` result selection with a minimal deterministic ordering rule
- Prefer stronger text matches over weaker ones when a query is present
- Use existing `confidence` as a secondary signal without introducing a new request field
- Preserve the four current endpoints and the existing filter semantics

**Non-Goals:**

- Adding new endpoints, search flags, or lifecycle operations
- Introducing semantic reranking, vector score fusion, or Qdrant-specific behavior
- Weighting results by `source.type` or inferring trust from metadata
- Adding merge, restore, delete, supersession-chain traversal, or automatic extraction semantics
- Redefining duplicate detection or archive behavior

## Decisions

Apply a query-aware ordering policy only when `request.query` is present.
Rationale: this is the smallest behavior change with clear value. Query-less search stays a browse-like path rather than turning into an implicit ranking feature.

Rank query matches with a deterministic priority tuple:
1. exact case-insensitive title match
2. title substring match
3. content substring match
4. `confidence` descending
5. `updated_at` descending
6. `id` ascending
Rationale: this keeps the policy explainable and testable. Exact title hits are the clearest signal in the current schema, title hits are usually stronger than content hits, `confidence` is already stored on the canonical record, and the final tie-breakers make results stable.

For searches without a query, preserve the existing browse semantics and order by `updated_at DESC, id ASC`.
Rationale: this avoids semantic overreach while removing nondeterministic ties.

Implement the ordering in the PostgreSQL search query rather than in a second-pass Python sort.
Rationale: PostgreSQL already owns the filtered candidate set and limit application. Keeping ordering there preserves the current architecture and avoids adding service-layer search orchestration.

## Risks / Trade-offs

[Older high-confidence memories may outrank newer weaker matches] -> Mitigation: keep `updated_at` in the ordering tuple after match quality and `confidence`, and limit the change to query-present searches only.

[Simple substring classes may still be weaker than future semantic search needs] -> Mitigation: define this as a narrow interim policy for the current codebase. Later semantic retrieval can replace the internal ordering while preserving the same endpoint.

[Confidence can be user-supplied and imperfect] -> Mitigation: use it only as a secondary tie-breaker after observable textual match categories, not as the primary ranking signal.

## Open Questions

None for this slice. Source weighting, semantic reranking, and broader retrieval-policy work remain explicitly deferred.
