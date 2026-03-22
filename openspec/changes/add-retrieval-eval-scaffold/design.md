## Context

The repository already has a clear testing split. Unit tests in `tests/` cover deterministic service behavior. Docker-based integration tests in `tests_integration/` cover the live FastAPI, PostgreSQL, and Qdrant stack. Those layers answer functional questions such as whether the API behaves correctly, whether filters and archive behavior still work, and whether query fallback remains wired correctly.

What they do not answer is whether semantic retrieval results are useful. That is now a separate concern because query-present search already uses embeddings plus Qdrant candidate retrieval before PostgreSQL filtering and canonical record resolution.

The important constraint is that the current runtime still uses the deterministic local embedder. That means the repository is ready for eval scaffolding, but not yet ready to treat retrieval-eval metrics as strong evidence about real semantic quality.

## Goals / Non-Goals

**Goals:**
- Define a lightweight retrieval-eval workflow that is clearly separate from functional and integration testing.
- Keep the initial dataset small enough to curate by hand and review manually.
- Pick a minimal first metric set that is easy to interpret.
- Make future retrieval changes easier to compare once a real embedding provider exists.
- Record that early eval numbers are provisional while the deterministic placeholder embedder remains active.

**Non-Goals:**
- Shipping reranking, hybrid retrieval, or ranking-policy changes.
- Introducing broad search-tuning work or changing the public API.
- Adding CI gates or mandatory eval runs on every pull request in this slice.
- Designing a large benchmark corpus or a graded relevance system immediately.

## Decisions

### Separate retrieval evals from unit and integration tests

Retrieval evals will be treated as their own workflow rather than being folded into normal tests.

Rationale:
- Unit and integration tests should stay focused on correctness and service wiring.
- Relevance judgments are inherently different from deterministic pass/fail contracts.
- Mixing ranking expectations into normal tests would make the core test suite brittle and harder to maintain.

Alternative considered:
- Add semantic quality assertions directly into integration tests. Rejected because those tests should verify observable correctness, not broader relevance quality.

### Start with a small frozen offline dataset

The first eval dataset will be a hand-curated frozen corpus plus query judgments.

Rationale:
- A small fixed dataset is enough to make retrieval changes reviewable.
- Hand curation keeps the initial maintenance burden low.
- Frozen inputs make baseline comparisons straightforward.

Alternative considered:
- Wait for a large real-world dataset before adding evals. Rejected because the workflow itself is valuable before scale exists.

### Use binary relevance labels first

Queries will initially map to relevant memory ids without graded labels.

Rationale:
- Binary relevance is simple to author and review.
- The repository does not yet need the complexity of multi-level judgments.
- This is sufficient for first metrics such as Hit@1, Recall@5, and MRR@5.

Alternative considered:
- Start immediately with graded relevance and nDCG. Rejected because it adds annotation cost before the workflow has proven its value.

### Keep the first metric set intentionally small

The first metric set will be Hit@1, Recall@5, and MRR@5.

Rationale:
- These metrics answer the first practical questions: did the system find a relevant result, and how high did it rank it.
- They are easy to explain during review.
- A minimal set reduces the risk of false precision in a small early dataset.

Alternative considered:
- Include a broader metric suite from the start. Rejected because more metrics would add noise before the project has a stable dataset and a real embedding provider.

### Review changed queries, not just aggregate metrics

Eval results should emphasize changed-query review alongside overall metrics.

Rationale:
- Aggregate metrics can hide sharp regressions on a small number of important queries.
- Per-query diffs make it easier to reason about why a retrieval change helped or hurt.
- Manual review is appropriate at this scale and matches the lightweight goal of the change.

Alternative considered:
- Rely only on a single aggregate score. Rejected because it would make the early workflow less actionable.

### Run evals manually first, with optional CI later

The first eval workflow should be manual and targeted, not part of every default test run.

Rationale:
- Retrieval evals are slower and more interpretive than core correctness tests.
- The project should preserve a fast inner loop for unit work and a separate integration workflow for live-stack verification.
- Manual runs are enough until retrieval changes become more frequent or a real embedder makes the signals more actionable.

Alternative considered:
- Run evals on every pull request as a hard gate. Rejected because the current embedder and small dataset do not justify that operational cost yet.

## Risks / Trade-offs

- [Early scores may be over-interpreted] -> Mitigation: document explicitly that the active embedder is still deterministic and that early eval numbers are provisional.
- [A very small curated dataset may miss regressions] -> Mitigation: treat the first dataset as a starter set and expand it only when real failure modes emerge.
- [Manual review may feel subjective] -> Mitigation: keep judgments frozen, metrics simple, and changed-query reporting concrete.
- [The repository could add docs without ever implementing the workflow] -> Mitigation: define a narrow follow-up implementation scope and keep the change small enough to complete later.

## Migration Plan

1. Document the retrieval-eval boundary and first workflow shape.
2. Add a new retrieval-evaluation capability spec describing dataset shape, metrics, result review, and intended run cadence.
3. Use that spec to guide a later implementation slice for the actual eval command and reporting output.

Rollback is simple because this slice is planning and documentation only. If the project decides evals are premature, the change can be dropped without affecting runtime behavior.

## Open Questions

- Should the first implementation run directly against service classes, a local API process, or an isolated stack?
- Should the starter dataset live as JSONL, YAML, or another simple text format?
- Should fallback-driven lexical matches be reported distinctly in the first eval output, or only reflected in ranked results?
