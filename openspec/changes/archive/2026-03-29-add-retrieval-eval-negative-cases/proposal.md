## Why

The current retrieval-eval workflow can report a perfect score even when most returned results are unrelated. The starter dataset contains only exact-positive queries, and the current metrics only ask whether at least one relevant memory appeared near the top. That means the eval loop cannot yet measure the main failure mode observed in manual testing: clearly unrelated queries still returning a memory.

This is the next smallest high-value slice because it improves the eval signal before any search-behavior change. It keeps the existing runner, isolated stack, and deterministic baseline intact while making false positives and expected non-matches visible in a repeatable way.

## What Changes

- Extend the starter retrieval-eval dataset to include explicit expected-non-match queries.
- Extend per-query eval output so reviewers can see unexpected returned ids, not only missed relevant ids.
- Add a small false-positive-aware metric set for the eval workflow, with emphasis on expected-empty success and precision of returned top-k results.
- Record embedding-runtime metadata in eval output so deterministic runs remain hermetic while optional real-provider runs can be compared intentionally.
- Document how deterministic and real-provider retrieval-eval runs should be interpreted and compared.
- Non-goal: change search behavior, add thresholds, redesign fallback, add MCP work, or build a broad provider-matrix automation workflow in this slice.

## Capabilities

### Modified Capabilities
- `retrieval-evaluation`: broaden the retrieval-eval workflow so it can measure expected non-matches and false positives in addition to positive-hit retrieval.

## Impact

- Affects retrieval-eval dataset shape, metrics, result reporting, and docs.
- Preserves the current manual isolated-stack workflow.
- Makes the current manual-testing failure mode measurable without changing the search contract.
