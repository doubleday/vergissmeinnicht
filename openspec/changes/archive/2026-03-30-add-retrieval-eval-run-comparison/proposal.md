## Why

The retrieval-eval workflow now saves stable JSON artifacts with per-query results and runtime provenance, but the review loop still stops at single-run inspection. The docs already say reviewers should look for queries whose results changed relative to a prior baseline, yet the current tooling provides no first-class way to compare two saved runs. In practice that means every retrieval-setting, embedder, or runtime experiment still depends on manual JSON diffing.

This is the next smallest useful eval-focused slice because it improves comparison and review before any further retrieval-logic changes. It uses the artifacts already being saved, stays separate from search redesign, and avoids broad automation or provider-matrix orchestration.

## What Changes

- Add a retrieval-eval comparison workflow for two saved eval result artifacts.
- Report aggregate metric deltas and per-query retrieval changes in a human-reviewable format.
- Detect and surface dataset or runtime-provenance mismatches so accidental apples-to-oranges comparisons are obvious.
- Document how to use comparison output for deterministic regression checks and intentional real-provider or search-setting reviews.
- Non-goal: change retrieval behavior, add ranking logic, add CI quality gates, or build automatic multi-provider benchmark orchestration.

## Capabilities

### Modified Capabilities
- `retrieval-evaluation`: extend the eval workflow so saved retrieval-eval artifacts can be compared intentionally across runs.

## Impact

- Affects retrieval-eval CLI or script surface, saved-artifact review workflow, and eval documentation.
- Builds directly on the existing per-query JSON output and runtime metadata.
- Makes embedding-runtime and search-setting experiments easier to review without changing the retrieval contract itself.
