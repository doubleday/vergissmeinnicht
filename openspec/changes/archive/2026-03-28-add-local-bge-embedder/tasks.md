## 1. Embedding Runtime Seam

- [x] 1.1 Introduce a shared embedder interface and provider-selection factory so `memory-api` no longer depends directly on `DeterministicEmbedder`.
- [x] 1.2 Add startup-time embedding configuration validation for provider selection, model initialization, and vector-dimension compatibility.

## 2. Local BGE Provider

- [x] 2.1 Add the local sentence-transformer-backed embedder implementation with `BAAI/bge-small-en-v1.5` as the documented default model.
- [x] 2.2 Extend environment-backed settings and runtime wiring for provider name, model name, device, and embedding dimensions.

## 3. Verification And Documentation

- [x] 3.1 Add unit coverage for provider selection, deterministic-runtime behavior, and local-provider startup validation with mocked model loading.
- [x] 3.2 Update local stack and retrieval-eval documentation to explain deterministic defaults, opt-in local BGE usage, and the clean-Qdrant-collection expectation when provider, model, or dimensions change.
