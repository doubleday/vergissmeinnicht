## Why

The repository now has a documented retrieval-eval direction, but it still has no runnable workflow for actually evaluating semantic search quality. The current test suite already covers functional correctness, live-stack integration, filtering, and fallback behavior. What is missing is a concrete way to load a frozen eval dataset, execute representative search queries, compute the agreed starter metrics, and review changed query results.

This is the right next slice because the eval scaffold change already established the intended boundary, dataset shape, metric set, and review approach. The implementation now needs to make that workflow real without broadening into ranking experiments, reranking, CI gates, or search-contract changes.

## What Changes

- Add a first manual retrieval-eval runner for semantic search quality.
- Add a small frozen starter dataset for retrieval evaluation.
- Report the initial agreed metrics: Hit@1, Recall@5, and MRR@5.
- Emit per-query results in a reviewable format, including enough detail to inspect changed queries across runs.
- Document how to run the eval workflow and how it differs from unit and integration tests.
- Non-goal: change retrieval behavior, add reranking, redesign fallback, or introduce CI quality gates in this slice.

## Capabilities

### New Capabilities
- `retrieval-evaluation`: A runnable workflow for evaluating semantic search quality against a frozen starter dataset.

### Modified Capabilities
- None.

## Impact

- Affects evaluation tooling, starter eval data, and retrieval-quality documentation.
- Adds the first concrete command or script for semantic search evaluation.
- Creates the baseline output format that later retrieval changes can compare against.
- Does not change the public memory API, canonical storage design, or current search semantics.
