## Context

The repository now has a planning-level retrieval-eval change that defines the boundary between functional verification and retrieval-quality evaluation. What is still missing is a runnable workflow that can load a frozen dataset, execute representative queries, and produce reviewable retrieval metrics.

The current project already has a useful pattern for disposable live-stack verification: the Docker-based integration workflow starts `memory-api`, PostgreSQL, and Qdrant in an isolated environment and runs tests through the public HTTP API. That existing shape is a strong fit for the first retrieval-eval implementation because semantic search quality depends on the real embedding, indexing, filtering, and fallback path rather than on a mocked or partially reconstructed code path.

The main constraint is to keep this first implementation lightweight. It should be good enough to create a repeatable eval baseline without broadening into ranking experiments, CI gates, or production search changes.

## Goals / Non-Goals

**Goals:**
- Add a manual retrieval-eval runner that exercises the real search path.
- Keep the eval environment isolated so starter data does not pollute a developer's normal local stack.
- Add a small frozen starter dataset with a curated corpus and representative queries.
- Produce both summary metrics and per-query output that support human review.
- Keep the workflow simple enough to run locally before or after retrieval-focused changes.

**Non-Goals:**
- Changing the memory API, search semantics, ranking behavior, or fallback policy.
- Adding reranking, hybrid retrieval, or broader search-tuning logic.
- Making retrieval evals part of the default unit or integration test commands.
- Introducing CI quality gates or multi-model comparison infrastructure in this slice.

## Decisions

### Run the first eval workflow against a disposable live stack through the public HTTP API

The first retrieval-eval runner will exercise `memory-api` over HTTP against an isolated stack rather than calling service classes directly.

Rationale:
- The eval should reflect the real runtime path, including memory creation, embedding generation, Qdrant indexing, candidate retrieval, PostgreSQL filtering, and fallback behavior.
- Reusing the live API avoids creating a second evaluation-only execution path that could drift from production behavior.
- The repository already has a disposable Docker integration pattern that can be reused instead of inventing a new environment story.

Alternative considered:
- Run the eval directly against service classes in-process. Rejected because it would be smaller in code but less faithful to the actual runtime path and easier to let drift from the public system behavior.

### Reuse isolated-stack conventions rather than the developer's default local stack

The eval runner will use disposable infrastructure rather than writing the starter dataset into a developer's normal persisted environment.

Rationale:
- Eval data should not pollute long-lived PostgreSQL rows or Qdrant collections.
- A clean environment makes results more repeatable.
- This keeps the eval workflow aligned with the repository's existing isolation-first verification story.

Alternative considered:
- Require a developer to run evals against their already-running local stack. Rejected because it weakens repeatability and creates avoidable data-contamination risk.

### Store the starter dataset as simple JSONL files

The first implementation will store the corpus and query judgments in simple text files, one record per line.

Rationale:
- JSONL is easy to read, diff, extend, and process with small Python scripts.
- It matches the starter dataset shape already described in the retrieval-eval notes.
- Separate corpus and query files keep authoring straightforward.

Alternative considered:
- Use YAML or a single large nested JSON file. Rejected because JSONL is easier to append to and simpler to process incrementally.

### Use API writes to load the eval corpus

The eval workflow will create the starter corpus through the normal create-memory API rather than seeding backing stores directly.

Rationale:
- This guarantees that the same indexing and canonical-write path is exercised as in normal operation.
- It avoids duplicating persistence rules in the eval tooling.
- It ensures later retrieval reflects the real stored records rather than an eval-only shortcut.

Alternative considered:
- Seed PostgreSQL and Qdrant directly. Rejected because that would be faster but would bypass important runtime behavior and add maintenance burden.

### Report both machine-readable results and a compact human-readable summary

The first runner will produce structured results plus a review-oriented summary that highlights the initial metrics and per-query outcomes.

Rationale:
- Machine-readable output enables future comparisons and tooling.
- Human-readable output is necessary for the immediate manual review workflow.
- Changed-query inspection is more useful when the raw per-query results are preserved.

Alternative considered:
- Emit only terminal text. Rejected because it would make later baseline comparison and automation harder.

### Keep baseline comparison lightweight and optional

The first implementation may compare against a prior saved result if one is provided, but baseline comparison should not become a required workflow dependency.

Rationale:
- Manual use should stay simple.
- The first value is in running the eval and inspecting results, not in enforcing a formal baseline-management system.
- Optional comparison leaves room for later refinement without blocking the initial implementation.

Alternative considered:
- Require checked-in golden result files and strict pass/fail thresholds. Rejected because that would overengineer the first slice.

## Risks / Trade-offs

- [A disposable live-stack eval will be slower than an in-process script] -> Mitigation: keep the starter dataset small and the workflow manual.
- [Using the deterministic local embedder limits how meaningful the first scores are] -> Mitigation: preserve the explicit documentation that early results are provisional and primarily useful for workflow establishment.
- [HTTP-based corpus loading can make eval setup noisier than direct store seeding] -> Mitigation: keep the dataset compact and let the runner own setup end-to-end.
- [Optional baseline comparison may reduce consistency across reviewers] -> Mitigation: make the structured output stable so saved result files can be compared consistently when desired.

## Migration Plan

1. Add the starter dataset files and result schema.
2. Add the retrieval-eval runner that creates the corpus, runs the queries, computes the agreed starter metrics, and writes reviewable output.
3. Add a manual entry point that starts or reuses isolated infrastructure for the eval workflow.
4. Update documentation so developers know when to use retrieval evals versus unit and integration tests.

Rollback is straightforward because this change adds a separate evaluation workflow. If it proves too heavy or premature, the eval files and commands can be removed without affecting the memory API or storage behavior.

## Open Questions

- Should the first manual entry point wrap Docker lifecycle itself, or should it assume the isolated environment is already started by a companion script?
- Should baseline comparison be included in the first runner or deferred until after the initial report format stabilizes?
- Should the per-query output include raw returned ids only, or also rank positions and notes about missing relevant hits?
