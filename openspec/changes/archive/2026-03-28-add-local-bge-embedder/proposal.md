## Why

The repository now has a real semantic-retrieval path and a real retrieval-eval workflow, but the active runtime embedder is still `deterministic-local`. That keeps tests hermetic, but it also means retrieval-eval results are still weak evidence about real semantic quality.

This is the right next slice because it can materially improve retrieval signal without changing the API or ranking contract. The change should stay narrow: add one real local embedding provider now, while introducing a small embedding-runtime seam so later model swaps do not require another service-level refactor.

## What Changes

- Add a configurable embedding runtime that selects the active embedder from environment-backed settings instead of hard-coding `deterministic-local`.
- Add one real local embedding option based on `BAAI/bge-small-en-v1.5` for higher-signal semantic retrieval and retrieval-eval runs.
- Preserve `deterministic-local` as the default provider for unit tests, integration tests, and zero-dependency local fallback.
- Define configuration and startup expectations for provider selection, model selection, and embedding dimensions so later model changes can be made through configuration rather than service rewrites.
- Document the operational boundary that changing embedding provider, model, or dimensions requires a clean or separate Qdrant collection unless a later migration workflow is introduced.
- Non-goal: add reindex tooling, reranking, hybrid retrieval, multiple real providers, provider-specific health checks, or public API changes in this slice.

## Capabilities

### New Capabilities
- `embedding-runtime`: A configurable embedding runtime that supports a deterministic fallback provider and a real local embedding provider behind a stable service seam.

### Modified Capabilities
- `local-memory-foundation`: Extend environment-driven runtime configuration to cover model-selectable embedding runtime settings and startup expectations for local embedding providers.

## Impact

- Affects embedding service wiring, application startup, environment configuration, and local runtime documentation.
- Adds local ML runtime dependencies needed to run `BAAI/bge-small-en-v1.5`.
- Improves the usefulness of manual retrieval evals without changing the current public API or search/filtering contract.
- Establishes a narrow abstraction boundary so later embedding model changes can be introduced primarily through configuration and targeted provider additions rather than broad refactoring.
