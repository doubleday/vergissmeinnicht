## Context

The current retrieval-eval workflow has reached a useful first plateau:

- frozen starter corpus and queries
- expected-empty queries
- false-positive reporting through `unexpected_ids`
- aggregate metrics including expected-empty success and precision@5
- saved runtime provenance in each artifact
- a reusable static local runtime for repeated runs

That is enough to create comparable artifacts, but not enough to review them efficiently. The main eval questions now are comparative:

- Did a run improve or degrade against the prior baseline?
- Which specific queries moved?
- Did false positives shrink or grow?
- Are we actually comparing the same dataset and compatible runtime context?

Today those questions require hand-inspecting JSON under `artifacts/retrieval-evals/`. That is workable once, but it does not scale to repeated iteration across embedding runtimes or search-setting changes.

## Goals / Non-Goals

**Goals:**
- Compare two saved retrieval-eval artifacts without rerunning the stack.
- Show metric deltas and per-query changes in a compact review format.
- Make runtime or dataset mismatches explicit before humans over-interpret the diff.
- Keep the comparison workflow manual and lightweight.

**Non-Goals:**
- Running multiple providers automatically.
- Defining a persistent blessed baseline registry or CI gate.
- Changing retrieval metrics, dataset judgments, or search behavior.
- Adding broad experiment-management infrastructure.

## Decisions

### Compare saved artifacts rather than orchestrating new eval runs

The comparison flow should take two existing JSON artifacts as input.

Rationale:
- The artifacts already contain the information needed for review.
- This keeps the change narrow and avoids coupling compare logic to Docker runtime orchestration.
- It works equally for deterministic runs, real-provider runs, and search-setting experiments.

Alternative considered:
- Add a runner that executes baseline and candidate automatically. Rejected because it expands the scope into automation and runtime management.

### Treat compatibility checks as first-class review output

The comparison workflow should check, at minimum:

- dataset name
- corpus path and query path
- top-k
- embedding provider
- model, dimensions, device, and collection metadata when available

Rationale:
- Provenance only helps if the review workflow uses it.
- The likely failure mode is accidental comparison across different provider or collection setups.
- A visible compatibility section is smaller and safer than silently diffing incomparable runs.

Alternative considered:
- Leave compatibility checking to documentation only. Rejected because it keeps the most important review guardrail manual and easy to miss.

### Highlight review-relevant per-query changes, not raw JSON deltas

Per-query comparison should focus on human-meaningful shifts such as:

- relevant id moved up or down
- relevant id dropped out of top-k
- expected-empty query started or stopped returning ids
- unexpected ids increased, decreased, appeared, or disappeared
- returned top-k list changed even if aggregate metrics stayed flat

Rationale:
- Reviewers care about behavioral changes, not structural diffs.
- Aggregate metrics alone can hide meaningful query-level movement.
- This keeps the output aligned with the existing documentation’s “changed queries” review loop.

Alternative considered:
- Emit only metric deltas. Rejected because retrieval iteration depends on seeing which queries changed and how.

### Keep comparison output lightweight and manual

The result should be a human-readable summary, with machine-readable output optional only if it comes nearly for free.

Rationale:
- The immediate need is reviewability in the local loop.
- The repo already saves raw JSON artifacts; the missing piece is a readable compare view.
- Keeping the default output textual reduces design overhead.

Alternative considered:
- Introduce a richer report format or dashboard. Rejected as too broad for the current need.

## Proposed Result Shape

```text
Retrieval Eval Comparison
- Baseline: artifacts/retrieval-evals/retrieval-eval-...
- Candidate: artifacts/retrieval-evals/retrieval-eval-...

Compatibility
- dataset: match
- top_k: match
- embedding_provider: match
- memory_qdrant_collection: differs (baseline=..., candidate=...)

Metric deltas
- Hit@1: 0.750 -> 0.875 (+0.125)
- Expected-empty: 0.000 -> 0.500 (+0.500)
- Precision@5: 0.150 -> 0.225 (+0.075)

Changed queries
- q2: relevant id m2 moved rank 1 -> 3
- q7: expected-empty failed -> passed
- q8: unexpected ids 5 -> 2
- q5: returned ids changed, relevance unchanged
```

The exact wording can stay simple. The important point is that comparison is anchored in metrics plus query-level behavioral shifts.

## Risks / Trade-offs

- [Different providers may legitimately use different collections] -> Mitigation: treat mismatches as explicit review context, not necessarily hard failure.
- [Small metric changes may hide query churn] -> Mitigation: always include a changed-query section, not only metric deltas.
- [Output can become noisy if every returned-id change is shown] -> Mitigation: prioritize queries with rank movement, expected-empty state changes, missing relevant ids, or unexpected-id count changes.

## Migration Plan

1. Add a comparison command over saved retrieval-eval artifacts.
2. Compute compatibility information and metric deltas from the existing artifact schema.
3. Summarize changed queries in a review-oriented format.
4. Document when comparisons are meaningful for deterministic-local runs versus real-provider or search-setting experiments.

Rollback is straightforward because the change is additive to eval tooling and docs.
