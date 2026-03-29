## Context

The repository now has a working retrieval-eval runner, a frozen starter dataset, and basic retrieval metrics. That workflow is useful for proving the eval loop exists, but it still cannot distinguish a clean retrieval result from a result list padded with unrelated memories.

The evidence is already visible in saved eval artifacts: the current starter queries all score perfectly on Hit@1, Recall@5, and MRR@5 even though each query also returns several unrelated ids in the rest of the top-5 list. The roadmap now identifies false-positive detection and expected non-matches as the immediate priority. The next slice should therefore sharpen the eval signal rather than guessing at search fixes.

## Goals / Non-Goals

**Goals:**
- Let the retrieval eval express that some queries should return no memories.
- Make false positives visible in both per-query output and aggregate metrics.
- Preserve the current hermetic deterministic eval workflow.
- Make optional real-provider runs comparable by recording runtime metadata, without turning provider comparison into a large new workflow.

**Non-Goals:**
- Changing retrieval thresholds, fallback behavior, or ranking policy.
- Introducing graded relevance, nDCG, reranking, or hybrid-retrieval redesign.
- Building a provider matrix runner or automatic multi-provider benchmarking.
- Folding retrieval evals into the default unit or integration test commands.

## Decisions

### Add an explicit query mode for expected non-matches

The dataset should support queries whose correct outcome is no returned memories in the reported top-k.

Rationale:
- The current failure mode is specifically about unrelated queries returning a memory.
- Encoding that expectation in the dataset is smaller and more direct than inferring it from absent relevant ids alone.
- Reviewers should be able to tell whether a query is intended to find something or intentionally expected to return nothing.

Alternative considered:
- Treat `relevant_ids: []` as sufficient without any explicit marker. Rejected because it is ambiguous during review and easier to mis-author accidentally.

### Report unexpected ids for every query

Per-query results should show not only `found_ids` and `missing_ids`, but also `unexpected_ids` for returned results that were not judged relevant.

Rationale:
- False positives need to be inspectable, not hidden behind aggregate scores.
- This keeps the result format simple while making the current issue obvious in every run.
- It improves changed-query review because reviewers can see whether a change reduced or increased unrelated tail results.

Alternative considered:
- Only add new aggregate metrics. Rejected because aggregate scores alone make it harder to diagnose which specific wrong results were returned.

### Add one expected-empty metric and one ranking-noise metric

The narrowest useful metric expansion is:

- expected-empty success rate: fraction of expected-non-match queries that return no ids in top-k
- precision@k: fraction of returned top-k ids that are judged relevant across all queries

Rationale:
- Expected-empty success rate directly measures the observed manual-testing failure mode.
- Precision@k captures unrelated tail results even when a relevant id is still ranked first.
- This keeps the metric set small and interpretable without jumping to graded-relevance metrics.

Alternative considered:
- Add only expected-empty success rate. Rejected because it would miss false-positive padding on positive queries.
- Add nDCG or graded metrics. Rejected because the dataset and judgment model are still intentionally binary.

### Keep MRR and Recall for positives

The existing hit and ranking metrics should remain for positive queries rather than being replaced.

Rationale:
- The eval still needs to measure whether relevant results are found and how highly they rank.
- The new metrics complement rather than replace the current positive-query view.

Alternative considered:
- Replace the old metrics with false-positive-aware metrics only. Rejected because it would lose continuity with the current baseline and make ranking regressions harder to spot.

### Record embedding runtime metadata in the saved result

Each eval result should capture the active embedding provider and key runtime identifiers when available.

Rationale:
- Hermetic deterministic runs should stay available for workflow validation and local regression checks.
- Real-provider runs are still valuable, but their results need clear provenance to avoid accidental apples-to-oranges comparison.
- Recording metadata is much smaller than building a multi-provider orchestration layer.

Alternative considered:
- Build a first-class comparison runner that executes multiple providers automatically. Rejected because it is a broader workflow than needed for the next eval slice.

## Result Shape

The dataset and output can stay close to the current structure:

```text
query:
  query_id
  query
  relevant_ids
  expected_empty
  notes

result:
  query_id
  returned_ids
  found_ids
  missing_ids
  unexpected_ids
  expected_empty
  expected_empty_pass
  reciprocal_rank
```

This keeps authoring simple and preserves backward familiarity.

## Runtime Comparison Stance

The project should treat retrieval evals as two related but different uses:

- deterministic-local runs: hermetic workflow validation and regression comparison
- real-provider runs: higher-signal retrieval-quality checks before or during search iteration

The workflow should not yet try to merge these into a single scorecard. The smaller step is to preserve both paths and label them clearly in the saved output and docs.

## Risks / Trade-offs

- [Precision@k may look harsh on a small dataset with sparse judgments] -> Mitigation: keep it as an informative metric, pair it with per-query `unexpected_ids`, and avoid hard thresholds in this slice.
- [Expected-empty queries can overfit to tiny datasets] -> Mitigation: add only a small number of clearly unrelated starter queries and treat the dataset as curated rather than exhaustive.
- [Runtime metadata may be incomplete if environment variables are missing] -> Mitigation: record what is available and document the expected fields for intentional comparison runs.

## Migration Plan

1. Extend the retrieval-eval dataset format with explicit expected-non-match cases.
2. Update the runner and saved result schema to expose unexpected ids and the new metrics.
3. Update docs so developers know how to interpret deterministic versus optional real-provider runs.

Rollback is straightforward because the change only affects eval tooling and documentation.
