# Project Roadmap

## Milestone A - Local Foundation

Outcome: a local stack that starts with one command and persists memory across restarts.

Deliverables:

- Docker Compose for `memory-api`, `postgres`, and `qdrant`
- Environment configuration for database and embedding provider settings, including a deterministic local provider for tests and fallback plus optional real-provider runtime settings for semantic evaluation
- Basic health and startup checks

Success criteria:

- A memory can be created, searched, fetched by id, and archived
- PostgreSQL rows and Qdrant payloads are inspectable directly
- Data survives container restarts

## Milestone B - Stable API Contract

Outcome: a typed and framework-agnostic memory API that can be called from agents or scripts.

Deliverables:

- Request and response schemas for the four core endpoints
- Validation for memory kinds, scopes, namespaces, and archived behavior
- Search flow that merges exact filters with semantic retrieval results

Success criteria:

- API behavior is documented and testable
- Search results are filtered predictably by namespace and scope
- Internal persistence details remain hidden behind the API

## Milestone C - Memory Quality Controls

Outcome: the store stays usable after repeated real-world writes.

Deliverables:

- Deduplication checks on write
- Confidence and source tracking
- `last_accessed_at` and optional supersession support

Success criteria:

- Repeated runs do not flood the store with near-duplicates
- Old or invalid memories can be archived without losing auditability

## Milestone D - Shared Adapters

Outcome: multiple tools can use the same backend without app-specific storage logic.

Deliverables:

- MCP wrapper
- Python SDK or thin client
- CLI for manual inspection and debugging

Success criteria:

- Claude, Codex, and local automation all talk to the same primitives
- Memory behavior is consistent regardless of the client protocol

## Deferred Until After Real Usage

- Automatic memory extraction from conversations
- Aggressive ranking and reranking logic
- Mem0 as a production dependency or public contract
- Production-grade backup, HA, or multi-tenant concerns

## Testing And Evals

- Unit and integration tests cover functional correctness, API behavior, and service wiring.
- Retrieval evaluation exists as a separate manual workflow and should remain outside the default unit-test and integration-test commands.
- While the active runtime embedder is `deterministic-local`, retrieval-eval results are useful for workflow validation and regression comparison but should not be treated as strong evidence of real semantic quality.
- The next meaningful retrieval-quality milestone is support for a real embedding provider while preserving deterministic embeddings for hermetic tests and local fallback.
