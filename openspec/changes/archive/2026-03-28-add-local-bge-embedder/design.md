## Context

The service already has a single embedding integration point in the request path, but the runtime is effectively hard-coded to `deterministic-local`. That was sufficient for functional tests and early retrieval wiring, yet it now limits the usefulness of the manual retrieval-eval workflow because the active embeddings are not semantically meaningful.

This change introduces the first real local embedding provider while preserving the current test posture. The design needs to stay narrow, but it also needs to avoid baking `bge-small-en-v1.5` directly into the service in a way that would force another refactor when the project wants to try a different local model later.

## Goals / Non-Goals

**Goals:**

- Add a stable embedding-runtime seam so `memory-api` can select an embedder from configuration rather than hard-coded construction.
- Support two runtime modes in this slice: `deterministic-local` and a local sentence-transformer model, initially `BAAI/bge-small-en-v1.5`.
- Keep tests and default local fallback on `deterministic-local`.
- Make later model changes low-friction by treating model name and embedding dimensions as configuration, not code-level constants.
- Keep the search API, retrieval flow shape, and eval workflow entry points unchanged.

**Non-Goals:**

- Multiple real providers beyond the first local sentence-transformer path.
- Automated reindex or backfill from PostgreSQL into Qdrant.
- Reranking, hybrid retrieval, or search-policy changes.
- Provider-specific readiness checks that depend on external model download state after startup.
- Performance tuning for GPU execution, batching, or embedding caches.

## Decisions

### Introduce a small `Embedder` runtime interface and factory

`MemoryService` should depend on an embedding protocol instead of `DeterministicEmbedder` directly. Application startup should select the concrete implementation from settings and pass it into the service.

Rationale:

- This is the smallest change that removes the current hard-coded provider decision from service wiring.
- It makes later model swaps primarily a configuration change plus, at most, a targeted provider implementation change.
- It avoids a broader plugin architecture before the project has real evidence that multiple provider families are needed.

Alternatives considered:

- Keep the current direct dependency and just branch in `main.py`. Rejected because it still couples the service type signature to one provider class.
- Build a generic provider registry with dynamic discovery. Rejected because it adds abstraction weight before there is more than one real provider family.

### Use a local sentence-transformer provider with model name in configuration

The first real provider should use a local sentence-transformer-compatible implementation, with `BAAI/bge-small-en-v1.5` as the documented default model for that provider. The model name should remain configurable so later local-model experiments do not require another runtime refactor.

Rationale:

- It satisfies the local-first goal without introducing a hosted dependency.
- It keeps the first real-provider slice concrete enough to implement and verify.
- Making the model name configurable now addresses the expected future need to try different local embedding models.

Alternatives considered:

- Add an OpenAI embeddings provider first. Rejected for this slice because it would improve retrieval signal, but it moves the project away from the local-first direction.
- Hard-code `BAAI/bge-small-en-v1.5` into the provider class. Rejected because it would reintroduce the same kind of coupling at the model level.

### Validate embedding configuration at startup, not lazily during the first search

The application should validate provider selection and initialize the configured embedder during startup. Unsupported providers, invalid model configuration, or incompatible dimension settings should fail startup visibly rather than waiting for the first write or search request.

Rationale:

- It keeps operational failures close to deploy/startup time.
- It avoids partial success where the API looks healthy but semantic search fails only on demand.
- It makes model-switch mistakes more obvious during local development and eval runs.

Alternatives considered:

- Lazy initialization on first use. Rejected because it hides configuration failures until runtime traffic reaches the embedding path.

### Keep Qdrant collection compatibility as an explicit operator boundary

Changing embedding provider, model, or dimensions should be treated as a Qdrant collection compatibility boundary. This slice should document that developers must use a clean collection or separate collection name when they switch embedding shape, rather than introducing automatic migration logic.

Rationale:

- Qdrant collections have a fixed vector size, and old vectors embedded under a different provider/model are not meaningfully comparable to new vectors.
- PostgreSQL remains canonical, so the project can safely defer reindex tooling without risking primary data loss.
- Documentation is enough for this first slice and keeps the change focused.

Alternatives considered:

- Add automatic reindex from PostgreSQL. Rejected because it is a separate migration feature and broadens the scope materially.
- Allow mixed vectors in one collection when dimensions happen to match. Rejected because that would produce misleading retrieval behavior.

### Keep tests deterministic and evals opt-in for real embeddings

Unit tests and integration tests should continue to default to `deterministic-local`. Retrieval evals can opt into the local real provider through environment configuration without changing their invocation shape.

Rationale:

- Hermetic tests remain fast and stable.
- Retrieval evals become more informative without turning every test environment into an ML runtime environment.
- The same documented runtime seam can be exercised in both deterministic and real-provider modes.

Alternatives considered:

- Switch all integration tests to the real local model immediately. Rejected because it would make the default verification loop heavier and more variable.

## Risks / Trade-offs

- [Local model dependencies increase environment weight] -> Mitigation: keep `deterministic-local` as the default path and document the real-provider path as opt-in for semantic evaluation.
- [Model downloads or ML backend setup may fail on some developer machines] -> Mitigation: validate at startup with clear failure modes and preserve the deterministic fallback path.
- [Changing provider/model/dimensions can invalidate the existing Qdrant collection] -> Mitigation: document provider/model switches as a fresh-collection boundary in local and eval workflows.
- [A generic model name setting can invite unsupported combinations] -> Mitigation: keep the runtime seam narrow, validate supported providers explicitly, and scope this change to one sentence-transformer-backed local provider family.
- [BGE-specific retrieval guidance such as query instructions could improve quality later] -> Mitigation: treat this as a later tuning concern and keep the first slice focused on provider realism rather than retrieval optimization.

## Migration Plan

1. Add the configurable embedding runtime seam and local sentence-transformer provider.
2. Extend environment-backed settings and local docs to cover provider name, model name, device, and embedding dimensions.
3. Keep default test and local settings on `deterministic-local`.
4. Document a real-provider local/eval configuration that uses a separate or clean Qdrant collection.
5. If the local provider path proves stable, future changes can add model swaps or migration tooling without changing the search contract.

Rollback:

- Revert runtime configuration to `deterministic-local`.
- Start with a deterministic-compatible Qdrant collection if the previous collection was created for another vector shape.

## Open Questions

- Whether the first local provider implementation should use `sentence-transformers` directly or a slightly lower-level `transformers` path for tighter dependency control.
- Whether the local provider should expose a configurable query prefix from day one or defer all query-instruction tuning until retrieval-quality iteration after this slice.
