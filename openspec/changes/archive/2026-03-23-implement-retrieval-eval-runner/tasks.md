## 1. Eval runner foundation

- [x] 1.1 Add a manual retrieval-eval entry point that runs separately from the default unit and integration test commands.
- [x] 1.2 Reuse or extend the repository's isolated-stack workflow so retrieval evals run in a clean environment rather than against long-lived local data.

## 2. Starter dataset and reporting

- [x] 2.1 Add the frozen starter dataset files for the eval corpus and query judgments.
- [x] 2.2 Implement corpus loading through the normal create-memory flow and query execution through the normal search flow.
- [x] 2.3 Compute and report Hit@1, Recall@5, and MRR@5 from the eval run.
- [x] 2.4 Emit per-query output that makes found and missed relevant ids reviewable.

## 3. Documentation and usage

- [x] 3.1 Document how to run the retrieval-eval workflow locally.
- [x] 3.2 Document how retrieval evals differ from unit tests and Docker-based integration tests.
- [x] 3.3 Record any initial limitations of the workflow, including that early results remain provisional while the deterministic local embedder is active.
