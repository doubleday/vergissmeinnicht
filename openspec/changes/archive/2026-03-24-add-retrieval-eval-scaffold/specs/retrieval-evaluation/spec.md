## ADDED Requirements

### Requirement: Retrieval Quality Evaluation Is Separate From Functional Verification

The project MUST treat retrieval quality evaluation as a separate workflow from unit tests and integration tests.

Unit tests and integration tests MUST remain focused on functional correctness, API behavior, storage integration, filtering behavior, and fallback behavior.

Retrieval evals MUST be used to assess the quality of semantic search results rather than to define deterministic ranking contracts for the normal test suite.

#### Scenario: Functional verification remains separate from relevance evaluation

- **WHEN** the project verifies search behavior through unit tests or Docker-based integration tests
- **THEN** those checks validate correctness, filtering, fallback behavior, and live-service wiring
- **AND** they do not serve as the primary workflow for judging semantic retrieval quality

#### Scenario: Retrieval evals assess search usefulness rather than API correctness

- **WHEN** the project runs retrieval evals
- **THEN** the workflow evaluates whether returned memories are relevant to representative queries
- **AND** the workflow remains separate from the normal functional test commands

### Requirement: Retrieval Evals Use A Small Frozen Starter Dataset

The retrieval-eval workflow MUST support a small frozen starter dataset for repeatable comparisons.

The starter dataset MUST include:

- a curated memory corpus
- representative search queries
- expected relevant memory ids for each query

The starter dataset MAY include lightweight notes for query intent, but it MUST NOT require graded relevance labels in the first version.

#### Scenario: Starter dataset captures corpus and query judgments

- **WHEN** a developer prepares the first retrieval-eval dataset
- **THEN** the dataset includes stored-memory examples plus representative queries
- **AND** each query identifies the memory ids considered relevant for that query

#### Scenario: First dataset stays small enough for manual curation

- **WHEN** the project defines its initial retrieval-eval dataset
- **THEN** the dataset remains intentionally small and hand-curated
- **AND** the workflow does not require a large benchmark corpus before retrieval evals can begin

### Requirement: Retrieval Evals Report A Minimal First Metric Set

The first retrieval-eval workflow MUST report a minimal metric set that is easy to interpret.

The initial metric set MUST include:

- Hit@1
- Recall@5
- MRR@5

The first workflow SHOULD avoid broader metric suites unless the dataset and judgment model become more mature.

#### Scenario: Eval run reports the agreed starter metrics

- **WHEN** a retrieval-eval run completes
- **THEN** the reported results include Hit@1, Recall@5, and MRR@5

### Requirement: Retrieval Eval Review Includes Changed-Query Inspection

The retrieval-eval workflow MUST support human review of changed queries in addition to aggregate metrics.

The workflow SHOULD make it easy to inspect queries whose top results or relevant-hit positions changed between runs.

#### Scenario: Review workflow highlights changed queries

- **WHEN** a developer compares retrieval-eval results over time
- **THEN** the workflow surfaces queries whose ranked results changed
- **AND** the developer can review those changes alongside the aggregate metrics

### Requirement: Retrieval Evals Start As A Manual Workflow

The first retrieval-eval workflow MUST be suitable for manual execution when retrieval behavior changes.

The first workflow MUST NOT require inclusion in the default unit-test command or the default integration-test command.

The project MAY add CI execution later, but the first slice MUST treat evals as a separate targeted workflow.

#### Scenario: Run evals during retrieval-focused work

- **WHEN** a developer changes retrieval logic, embedding behavior, ranking behavior, candidate oversampling, or fallback behavior
- **THEN** the retrieval-eval workflow can be run separately to review quality impact
- **AND** the default unit and integration test commands remain unchanged

### Requirement: Early Retrieval Evals Remain Provisional While The Placeholder Embedder Is Active

The project MUST document that early retrieval-eval results are provisional while the deterministic local embedder remains the active embedding provider.

The workflow MUST be used to establish comparison structure and review habits without overstating the meaning of early scores.

#### Scenario: Early eval results are interpreted cautiously

- **WHEN** the project runs retrieval evals before adopting a real semantic embedding provider
- **THEN** the results are treated as provisional indicators
- **AND** the project does not use those scores alone as strong evidence of production semantic quality
