## Why

The repository now has a real separation between functional correctness and retrieval quality, but it still lacks an actual eval workflow for semantic search. Unit tests and Docker-based integration tests already cover API behavior, filtering, fallback behavior, and live PostgreSQL/Qdrant wiring. What is still missing is a lightweight way to compare retrieval quality over time.

This is the right next slice because semantic search is already part of the runtime architecture, yet the project still has no frozen retrieval dataset, no agreed first metrics, and no repeatable review workflow. At the same time, the current embedder is still the deterministic local placeholder, so this change should establish eval scaffolding without pretending that early scores represent mature semantic quality.

## What Changes

- Define a small retrieval-eval capability for semantic search quality that is separate from unit and integration testing.
- Establish the first frozen dataset shape for a lightweight offline eval workflow.
- Define a minimal initial metric set and a simple human review workflow for changed retrieval results.
- Document when retrieval evals should run and what they should not be used for.
- Non-goal: implement production retrieval improvements, reranking, hybrid fusion, or CI gating in this slice.

## Capabilities

### New Capabilities
- `retrieval-evaluation`: A lightweight workflow for assessing semantic retrieval quality independently from functional and integration tests.

### Modified Capabilities
- None.

## Impact

- Affects evaluation and verification documentation for semantic search.
- Establishes the intended shape of later retrieval-eval tooling and datasets.
- Creates a narrow planning surface for future implementation without changing the current API, storage design, or search behavior.
