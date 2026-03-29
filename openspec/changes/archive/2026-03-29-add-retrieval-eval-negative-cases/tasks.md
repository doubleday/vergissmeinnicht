## 1. Dataset coverage

- [x] 1.1 Extend the starter retrieval dataset with a small set of explicit expected-non-match queries.
- [x] 1.2 Keep the existing positive queries and annotate the new dataset shape clearly enough for hand editing and review.

## 2. Eval reporting

- [x] 2.1 Update per-query retrieval-eval output to report `unexpected_ids` alongside found and missing relevant ids.
- [x] 2.2 Add aggregate metrics for expected-empty success and false-positive-sensitive ranking quality while preserving Hit@1, Recall@5, and MRR@5.
- [x] 2.3 Record embedding-runtime metadata in the saved eval result for later comparison across deterministic and optional real-provider runs.

## 3. Documentation

- [x] 3.1 Document how expected-non-match queries are represented and reviewed.
- [x] 3.2 Document how to use deterministic-local runs for hermetic regression checks and real-provider runs for higher-signal quality comparison without introducing provider-matrix automation.
