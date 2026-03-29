## 1. Artifact comparison workflow

- [x] 1.1 Add a retrieval-eval comparison entry point that accepts two saved eval result artifacts without rerunning the retrieval stack.
- [x] 1.2 Report aggregate metric deltas for the existing starter metric set.

## 2. Query-level review output

- [x] 2.1 Summarize per-query behavioral changes, including rank movement for relevant ids, expected-empty pass or fail changes, and unexpected-id changes.
- [x] 2.2 Keep unchanged queries out of the default compare summary unless needed for context.

## 3. Provenance and docs

- [x] 3.1 Surface dataset and runtime compatibility information prominently in the comparison output.
- [x] 3.2 Document how to use saved-artifact comparison for deterministic regression checks and intentional real-provider or search-setting review.
