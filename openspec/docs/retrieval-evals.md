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

## Current Readiness

The repository is already in a good place to define a retrieval-eval workflow, dataset shape, and review process.

Reasons:

- The project already separates unit tests, Docker-based integration tests, and search quality notes.
- The query-present search path already performs retrieval through embeddings plus Qdrant candidate search before PostgreSQL filtering.
- The current verification stack already covers correctness, fallback behavior, and live-service wiring separately from ranking quality.

However, the repository is not yet in a good place to treat retrieval-eval scores as strong evidence about real semantic quality.

Current limitation:

- The active embedder is still the deterministic local placeholder rather than a real semantic embedding provider.

Practical implication:

- It is useful to start eval scaffolding now.
- It is not useful to over-interpret the resulting scores yet.
- The first milestone should establish workflow and reviewability, not claim that the current search stack is semantically strong.

## Possible Evaluation Shape

One reasonable approach would be to create a small frozen evaluation set:

- A curated memory corpus
- A set of representative search queries
- Expected relevant memory ids for each query
- Optional graded relevance such as high, medium, or irrelevant

That set could then be used to compare search behavior over time.

## Recommended First Strategy

The first eval strategy for this repository should stay deliberately small:

1. Keep unit and integration tests focused on functional correctness and live-stack behavior.
2. Add a separate retrieval-eval workflow for search quality.
3. Use a small frozen offline dataset rather than trying to judge relevance inside normal tests.
4. Review changed queries manually when retrieval behavior shifts.

The goal of this first slice is not advanced ranking science. The goal is to make future retrieval changes easier to compare and discuss.

## Minimal Dataset Shape

A practical first dataset can use two simple files:

- `corpus.jsonl`
- `queries.jsonl`

Suggested `corpus.jsonl` shape:

```json
{"id":"m1","namespace":"eval","scope":"project","kind":"rule","title":"Prefer concise answers","content":"Answer directly and avoid filler.","tags":["style"]}
{"id":"m2","namespace":"eval","scope":"project","kind":"rule","title":"Use bullets for lists","content":"Use bullets when enumerating distinct items.","tags":["format"]}
```

Suggested `queries.jsonl` shape:

```json
{"query_id":"q1","query":"brief replies","relevant_ids":["m1"],"notes":"semantic paraphrase"}
{"query_id":"q2","query":"list formatting","relevant_ids":["m2"],"notes":"concept match"}
```

Recommended first scale:

- 20 to 40 corpus items
- 10 to 20 queries
- 1 to 3 relevant ids per query

This is large enough to catch obvious regressions and still small enough to curate by hand.

## Possible Metrics

Useful retrieval metrics to consider later:

- Recall@k
- Precision@k
- Mean Reciprocal Rank (MRR)
- nDCG

The exact metric mix does not need to be decided yet. The main point is that semantic quality should be evaluated with ranking or retrieval metrics, not only with pass/fail API tests.

## Recommended First Metrics

The first metric set should stay minimal:

- Hit@1
- Recall@5
- Mean Reciprocal Rank at 5 (MRR@5)

Why this mix:

- Hit@1 is easy to reason about during manual review.
- Recall@5 shows whether relevant memories are being found at all.
- MRR@5 shows whether the first relevant result is near the top.

Metrics to defer for now:

- Precision@k
- nDCG
- Composite or weighted rollup scores

Those become more useful later, especially if the project adopts graded relevance labels.

## Sensible Early Strategy

A pragmatic first version could look like this:

1. Keep unit and integration tests focused on correctness and live-stack wiring.
2. Add a separate retrieval-eval workflow for semantic search quality.
3. Use a small frozen dataset and report a few retrieval metrics.
4. Add lightweight human review for changed queries when search behavior shifts noticeably.

## How Results Should Be Reviewed

The first review loop should be human-readable and lightweight.

Each eval run should report:

- Overall metrics
- Per-query result summaries
- Queries whose results changed relative to a prior baseline

Good review questions:

- Did any query lose all relevant hits?
- Did top-1 get worse for important queries?
- Are failures caused by retrieval quality or by functional behavior such as filtering or fallback?
- Did the change alter only one or two queries, or did it broadly shift the ranking profile?

Example result shape:

```text
Overall
- Hit@1: 6/12
- Recall@5: 10/12
- MRR@5: 0.63

Changed queries
- q1 "brief replies": m1 moved from rank 1 to rank 4
- q4 "meeting reminders": no relevant hit in top 5
- q7 "archived note search": unchanged, still uses fallback behavior
```

This keeps review anchored in concrete query behavior instead of abstract averages alone.

## When Evals Should Run

Retrieval evals should not run as part of every fast test cycle.

Recommended trigger points:

- Manual local runs when retrieval logic changes
- Manual local runs when embedding behavior changes
- Manual local runs when ranking, candidate oversampling, or fallback logic changes
- Optional CI runs for changes that directly affect semantic retrieval behavior

They should not initially be:

- part of the default unit-test command
- part of the default Docker integration-test command
- hard quality gates on every pull request

That keeps the workflow lightweight while preserving the existing testing split.

## Current Starter Workflow

The repository now includes a first manual retrieval-eval workflow:

```bash
./scripts/run_retrieval_evals.sh
```

Current implementation shape:

- uses a disposable Docker Compose project rather than the default local stack
- loads a frozen starter dataset from `evals/retrieval/starter/`
- creates memories through the normal create-memory API
- executes representative queries through the normal search API
- saves machine-readable JSON output under `artifacts/retrieval-evals/`
- prints a compact human-readable summary for review

This keeps retrieval evals grounded in the real live-stack behavior while preserving separation from ordinary tests.

## What Not To Do

- Do not treat exact semantic ranking order as a stable unit-test contract.
- Do not assume one or two hand-written example queries are enough to measure quality.
- Do not mix relevance judgments into normal integration tests unless the expectation is very narrow and deterministic.
- Do not treat early scores from the deterministic placeholder embedder as strong evidence about real semantic quality.

## Recommended Scope For A First Change

If this work is formalized as an OpenSpec change, the first slice should stay narrow:

- define the frozen dataset shape
- define the first metric set
- define the result-review workflow
- add a manual eval entry point later
- explicitly document that early scores are provisional until a real embedding provider exists

That first slice should not include:

- reranking
- hybrid retrieval redesign
- production retrieval tuning
- CI quality gates
- graded relevance labels
- model comparison automation

## Future Questions

- What corpus size is enough to catch regressions without creating heavy maintenance?
- Should the project use binary relevance labels or graded relevance?
- When should evals run: manually, in CI, or only before larger search changes?
- How should model or embedding-version changes be compared over time?
