## 1. Retrieval-eval scope

- [x] 1.1 Define the retrieval-eval boundary so it stays separate from unit tests and Docker-based integration tests.
- [x] 1.2 Define the narrow first-slice scope, including explicit non-goals such as reranking, hybrid retrieval redesign, and CI quality gates.

## 2. Retrieval-eval design

- [x] 2.1 Define the minimal frozen dataset shape for a hand-curated corpus and query judgments.
- [x] 2.2 Define the initial metric set as Hit@1, Recall@5, and MRR@5.
- [x] 2.3 Define how results should be reviewed, with emphasis on changed-query review rather than aggregate scores alone.
- [x] 2.4 Define when retrieval evals should run and record that early results remain provisional while the deterministic local embedder is still active.

## 3. Planning handoff

- [x] 3.1 Add or update documentation so the rationale from the exploration session is captured in-repo.
- [x] 3.2 Add a capability spec that can guide a later implementation change for the actual eval command and reporting output.
