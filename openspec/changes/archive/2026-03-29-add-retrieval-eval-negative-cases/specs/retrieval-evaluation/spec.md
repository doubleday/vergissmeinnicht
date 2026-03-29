## MODIFIED Requirements

### Requirement: Retrieval Evaluation Uses A Frozen Starter Dataset

The retrieval-eval workflow MUST use a frozen starter dataset that includes:

- a curated memory corpus
- representative search queries
- expected relevant memory ids for each positive-match query
- an explicit indication when a query is expected to return no memories in the reported top results

The starter dataset MUST be stored in repository-managed files that are easy to inspect and update.

#### Scenario: Starter dataset includes positive and expected-empty queries

- **WHEN** a developer inspects the retrieval-eval dataset
- **THEN** the dataset provides stored-memory examples and representative queries
- **AND** positive-match queries identify the expected relevant memory ids for that query
- **AND** expected-non-match queries explicitly indicate that no memories should be returned

### Requirement: Retrieval Evaluation Reports Starter Metrics

The retrieval-eval workflow MUST report the starter retrieval metrics:

- Hit@1
- Recall@5
- MRR@5

The workflow MUST also report false-positive-aware metrics that include:

- expected-empty success rate for queries whose correct outcome is no returned result
- precision@k over the reported top-k results

The workflow MUST compute those metrics from the frozen dataset results produced during the run.

#### Scenario: Eval run reports positive and false-positive-aware metrics

- **WHEN** a retrieval-eval run completes
- **THEN** the output includes Hit@1, Recall@5, MRR@5, expected-empty success rate, and precision@k for that run

### Requirement: Retrieval Evaluation Produces Reviewable Per-Query Results

The retrieval-eval workflow MUST produce per-query results that support human review in addition to aggregate metrics.

The per-query output MUST make it possible to determine:

- which results were returned for a given query
- whether any expected relevant ids were missing from the reported top results
- which returned ids were unexpected for that query
- whether an expected-non-match query incorrectly returned any results

#### Scenario: Eval output exposes false positives per query

- **WHEN** a developer reviews retrieval-eval results
- **THEN** the output includes per-query retrieval details
- **AND** the developer can inspect which expected relevant ids were found or missed
- **AND** the developer can inspect which returned ids were unexpected
- **AND** the developer can tell whether an expected-empty query passed or failed

### Requirement: Retrieval Evaluation Results Preserve Runtime Provenance

The retrieval-eval workflow MUST preserve enough runtime provenance in its saved result to support intentional comparison across embedding runtimes.

The saved result MUST identify the active embedding provider and SHOULD include model or collection identifiers when they are available to the eval process.

#### Scenario: Eval result captures embedding runtime metadata

- **WHEN** a developer saves a retrieval-eval result
- **THEN** the result records the active embedding provider
- **AND** optional runtime identifiers such as model name or collection name are included when available
- **AND** deterministic and real-provider runs can be distinguished during later review
