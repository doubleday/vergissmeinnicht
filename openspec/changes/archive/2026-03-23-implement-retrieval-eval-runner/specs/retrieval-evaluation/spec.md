## ADDED Requirements

### Requirement: Retrieval Evaluation Workflow Can Be Run Manually

The system MUST provide a manual retrieval-evaluation workflow for semantic search quality.

The workflow MUST remain separate from the default unit-test and integration-test commands.

The workflow MUST exercise the public search behavior used by clients rather than relying on a separate evaluation-only search implementation.

#### Scenario: Run retrieval eval separately from normal tests

- **WHEN** a developer invokes the documented retrieval-eval entry point
- **THEN** the system runs retrieval evaluation as a separate workflow
- **AND** the default unit-test and Docker integration-test commands remain unchanged

#### Scenario: Eval workflow uses the normal search surface

- **WHEN** the retrieval-eval workflow executes representative queries
- **THEN** it evaluates the same externally observable search behavior that normal clients use
- **AND** it does not rely on a separate evaluation-only search contract

### Requirement: Retrieval Evaluation Uses A Frozen Starter Dataset

The retrieval-eval workflow MUST use a frozen starter dataset that includes:

- a curated memory corpus
- representative search queries
- expected relevant memory ids for each query

The starter dataset MUST be stored in repository-managed files that are easy to inspect and update.

#### Scenario: Starter dataset includes corpus and query judgments

- **WHEN** a developer inspects the retrieval-eval dataset
- **THEN** the dataset provides stored-memory examples and representative queries
- **AND** each query identifies the expected relevant memory ids for that query

#### Scenario: Starter dataset is versioned in the repository

- **WHEN** the retrieval-eval workflow is reviewed or updated
- **THEN** the dataset files are available in the repository
- **AND** changes to the corpus or judgments can be inspected through normal code review

### Requirement: Retrieval Evaluation Reports Starter Metrics

The retrieval-eval workflow MUST report the starter retrieval metrics:

- Hit@1
- Recall@5
- MRR@5

The workflow MUST compute those metrics from the frozen dataset results produced during the run.

#### Scenario: Eval run reports agreed starter metrics

- **WHEN** a retrieval-eval run completes
- **THEN** the output includes Hit@1, Recall@5, and MRR@5 for that run

### Requirement: Retrieval Evaluation Produces Reviewable Per-Query Results

The retrieval-eval workflow MUST produce per-query results that support human review in addition to aggregate metrics.

The per-query output MUST make it possible to determine which results were returned for a given query and whether any expected relevant ids were missing from the reported top results.

#### Scenario: Eval output supports query-level inspection

- **WHEN** a developer reviews retrieval-eval results
- **THEN** the output includes per-query retrieval details
- **AND** the developer can inspect which expected relevant ids were found or missed for each query

### Requirement: Retrieval Evaluation Uses Isolated Runtime Data

The retrieval-eval workflow MUST avoid relying on a developer's long-lived local stack data.

The workflow MUST load the starter dataset into an isolated runtime environment or other clean evaluation context owned by the eval run.

#### Scenario: Eval run avoids polluting long-lived local data

- **WHEN** a developer runs the retrieval-eval workflow
- **THEN** the starter dataset is loaded into an isolated or clean evaluation context for that run
- **AND** the workflow does not require polluting the developer's normal persisted data as a prerequisite

### Requirement: Retrieval Evaluation Documentation Explains Its Role

The project MUST document how to run the retrieval-eval workflow and how it differs from unit tests and integration tests.

#### Scenario: Developer can distinguish evals from tests

- **WHEN** a developer reads the project documentation
- **THEN** the documentation identifies the retrieval-eval entry point
- **AND** it explains that retrieval evals measure search quality rather than functional correctness
