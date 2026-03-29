## MODIFIED Requirements

### Requirement: Retrieval Evaluation Produces Reviewable Per-Query Results

The retrieval-eval workflow MUST produce per-query results that support human review in addition to aggregate metrics.

The per-query output MUST make it possible to determine:

- which results were returned for a given query
- whether any expected relevant ids were missing from the reported top results
- which returned ids were unexpected for that query
- whether an expected-non-match query incorrectly returned any results

The workflow MUST also support intentional comparison of two saved retrieval-eval results so reviewers can identify metric and per-query behavioral changes between runs.

#### Scenario: Eval output exposes false positives per query

- **WHEN** a developer reviews retrieval-eval results
- **THEN** the output includes per-query retrieval details
- **AND** the developer can inspect which expected relevant ids were found or missed
- **AND** the developer can inspect which returned ids were unexpected
- **AND** the developer can tell whether an expected-empty query passed or failed

#### Scenario: Saved eval results can be compared for review

- **WHEN** a developer compares two saved retrieval-eval results
- **THEN** the workflow reports aggregate metric differences between the runs
- **AND** it highlights queries whose returned top results or review-relevant status changed
- **AND** it makes runtime and dataset provenance visible enough to judge whether the comparison is intentional
