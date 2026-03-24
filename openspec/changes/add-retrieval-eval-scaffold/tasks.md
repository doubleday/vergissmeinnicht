## 1. Retrieval-eval scope

- [ ] 1.1 Define the retrieval-eval boundary so it stays separate from unit tests and Docker-based integration tests.
- [ ] 1.2 Define the narrow first-slice scope, including explicit non-goals such as reranking, hybrid retrieval redesign, and CI quality gates.

## 2. Retrieval-eval design

- [ ] 2.1 Define the minimal frozen dataset shape for a hand-curated corpus and query judgments.
- [ ] 2.2 Define the initial metric set as Hit@1, Recall@5, and MRR@5.
- [ ] 2.3 Define how results should be reviewed, with emphasis on changed-query review rather than aggregate scores alone.
- [ ] 2.4 Define when retrieval evals should run and record that early results remain provisional while the deterministic local embedder is still active.

## 3. Planning handoff

- [ ] 3.1 Add or update documentation so the rationale from the exploration session is captured in-repo.
- [ ] 3.2 Add a capability spec that can guide a later implementation change for the actual eval command and reporting output.
