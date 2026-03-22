## Why

`POST /memories/search` now depends on Qdrant whenever a query is present. That makes semantic retrieval real, but it also means a query can return no results, or fail outright, even when PostgreSQL still contains obvious lexical matches. The next bounded slice should keep real search usable when the retrieval index is empty or temporarily unavailable.

## What Changes

- Add a query-present fallback path for `POST /memories/search` that reuses the existing PostgreSQL lexical search when semantic retrieval returns no candidates.
- Extend the same fallback to temporary Qdrant search failures so query search degrades to canonical PostgreSQL matching instead of failing closed.
- Preserve the current request and response schema, the four-endpoint API boundary, and the existing browse-style path for searches without a query.
- Preserve current semantic ordering when Qdrant returns candidates successfully; fallback ordering should use the existing PostgreSQL query-aware ordering.
- Define explicit non-goals for this slice: no new endpoints or flags, no hybrid score blending, no reranking experiments, no background reindex jobs, no write-path redesign, and no adapter/client work.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `memory-service-core`: refine query-present search requirements so search can fall back to canonical PostgreSQL matching when semantic retrieval yields no candidates or is temporarily unavailable.

## Impact

- Introduces a delta spec under [`openspec/changes/add-query-search-fallback/specs/memory-service-core/spec.md`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/openspec/changes/add-query-search-fallback/specs/memory-service-core/spec.md).
- Affects query search orchestration in [`memory_service.py`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/memory_api/src/memory_api/services/memory_service.py) and targeted search-path tests in [`test_memory_service.py`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/tests/test_memory_service.py).
- Preserves the current API boundary and avoids introducing broader retrieval, lifecycle, or operational workflows.
