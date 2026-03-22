# Retrieval Evals Notes

This is a lightweight starting point for how semantic search quality might be evaluated later. It is intentionally incomplete and should be treated as working notes rather than a finalized plan.

## Functional Tests Versus Evals

Functional tests answer:

- Does the API behave correctly?
- Do PostgreSQL and Qdrant work together through the live stack?
- Do filters, archiving, and fallback behavior still work?

Evals answer:

- Are the returned memories relevant?
- Is semantic search getting better or worse over time?
- Did a model, embedding, or ranking change improve usefulness?

The practical split for this project is:

- Unit tests: deterministic behavior of isolated code paths
- Integration tests: correctness of the live HTTP API and backing-service wiring
- Retrieval evals: quality of semantic search results

## Why Semantic Search Quality Needs Evals

Semantic retrieval is not just a software-correctness problem. Once the question becomes "are these results useful?" the project is in eval territory rather than ordinary functional testing.

Even when the embedding provider is deterministic, relevance quality should be measured with retrieval-oriented metrics and review workflows instead of strict result-order assertions in normal tests.

## Possible Evaluation Shape

One reasonable approach would be to create a small frozen evaluation set:

- A curated memory corpus
- A set of representative search queries
- Expected relevant memory ids for each query
- Optional graded relevance such as high, medium, or irrelevant

That set could then be used to compare search behavior over time.

## Possible Metrics

Useful retrieval metrics to consider later:

- Recall@k
- Precision@k
- Mean Reciprocal Rank (MRR)
- nDCG

The exact metric mix does not need to be decided yet. The main point is that semantic quality should be evaluated with ranking or retrieval metrics, not only with pass/fail API tests.

## Sensible Early Strategy

A pragmatic first version could look like this:

1. Keep unit and integration tests focused on correctness and live-stack wiring.
2. Add a separate offline evaluation script for semantic search quality.
3. Use a small frozen dataset and report a few retrieval metrics.
4. Add lightweight human review for changed queries when search behavior shifts noticeably.

## What Not To Do

- Do not treat exact semantic ranking order as a stable unit-test contract.
- Do not assume one or two hand-written example queries are enough to measure quality.
- Do not mix relevance judgments into normal integration tests unless the expectation is very narrow and deterministic.

## Future Questions

- What corpus size is enough to catch regressions without creating heavy maintenance?
- Should the project use binary relevance labels or graded relevance?
- When should evals run: manually, in CI, or only before larger search changes?
- How should model or embedding-version changes be compared over time?
