## 1. Semantic Retrieval Plumbing

- [x] 1.1 Extend the Qdrant search integration so query embeddings can retrieve ranked candidate memory IDs for `POST /memories/search`.
- [x] 1.2 Update test doubles and supporting fixtures so search-path tests can model ranked Qdrant candidates independently from PostgreSQL records.

## 2. Query-Present Search Slice

- [x] 2.1 Update the service search flow so non-empty queries embed once, retrieve semantic candidates from Qdrant, and resolve them through PostgreSQL while preserving canonical response records.
- [x] 2.2 Extend PostgreSQL search support to constrain semantic candidate IDs with the existing namespace, scope, kind, tag, archived, and superseded rules while preserving deterministic final ordering.
- [x] 2.3 Preserve the existing query-less PostgreSQL browse path and ensure `last_accessed_at` behavior remains correct for returned canonical memories.

## 3. Verification

- [x] 3.1 Add targeted tests covering semantic matches without direct substring hits, filter preservation across semantic candidates, canonical record return behavior, and unchanged query-less browse search.
- [x] 3.2 Validate the change with the OpenSpec CLI and the targeted test suite before implementation is considered complete.
