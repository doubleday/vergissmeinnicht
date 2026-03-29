## Purpose

Define the retrieval-evaluation workflow for semantic search quality, separate from functional and integration testing.

## Requirements

### Requirement: Retrieval Evaluation Workflow Can Be Run Manually

The system MUST provide a manual retrieval-evaluation workflow for semantic search quality.

The workflow MUST remain separate from the default unit-test and integration-test commands.

The workflow MUST exercise the public search behavior used by clients rather than relying on a separate evaluation-only search implementation.

The local workflow MUST support reuse of a dedicated retrieval-eval runtime rather than requiring a newly created disposable stack on every run.

#### Scenario: Run retrieval eval separately from normal tests

- **WHEN** a developer invokes the documented retrieval-eval entry point
- **THEN** the system runs retrieval evaluation as a separate workflow
- **AND** the default unit-test and Docker integration-test commands remain unchanged

#### Scenario: Eval workflow uses the normal search surface

- **WHEN** the retrieval-eval workflow executes representative queries
- **THEN** it evaluates the same externally observable search behavior that normal clients use
- **AND** it does not rely on a separate evaluation-only search contract

#### Scenario: Local eval runs reuse dedicated runtime by default

- **WHEN** a developer runs retrieval evals repeatedly in the local workflow
- **THEN** the workflow can reuse a dedicated retrieval-eval runtime between runs
- **AND** it does not require a newly named disposable Docker project for each ordinary local run

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

#### Scenario: Starter dataset is versioned in the repository

- **WHEN** the retrieval-eval workflow is reviewed or updated
- **THEN** the dataset files are available in the repository
- **AND** changes to the corpus or judgments can be inspected through normal code review

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

### Requirement: Retrieval Evaluation Uses Isolated Runtime Data

The retrieval-eval workflow MUST avoid relying on a developer's long-lived local stack data.

The workflow MUST load the starter dataset into an isolated runtime environment or other clean evaluation context owned by the eval run.

The local workflow MAY satisfy this requirement through a reusable dedicated eval runtime, provided it supports a documented clean reset path for eval data.

#### Scenario: Eval run avoids polluting long-lived local data

- **WHEN** a developer runs the retrieval-eval workflow
- **THEN** the starter dataset is loaded into an isolated or clean evaluation context for that run
- **AND** the workflow does not require polluting the developer's normal persisted data as a prerequisite

#### Scenario: Reusable eval runtime can be reset to a clean state

- **WHEN** a developer uses the reusable local eval runtime
- **THEN** the workflow provides a documented way to restore a clean evaluation state before the next run
- **AND** the isolated retrieval-eval data boundary remains intact

### Requirement: Retrieval Evaluation Results Preserve Runtime Provenance

The retrieval-eval workflow MUST preserve enough runtime provenance in its saved result to support intentional comparison across embedding runtimes.

The saved result MUST identify the active embedding provider and SHOULD include model or collection identifiers when they are available to the eval process.

#### Scenario: Eval result captures embedding runtime metadata

- **WHEN** a developer saves a retrieval-eval result
- **THEN** the result records the active embedding provider
- **AND** optional runtime identifiers such as model name or collection name are included when available
- **AND** deterministic and real-provider runs can be distinguished during later review

### Requirement: Retrieval Evaluation Documentation Explains Its Role

The project MUST document how to run the retrieval-eval workflow and how it differs from unit tests and integration tests.

#### Scenario: Developer can distinguish evals from tests

- **WHEN** a developer reads the project documentation
- **THEN** the documentation identifies the retrieval-eval entry point
- **AND** it explains that retrieval evals measure search quality rather than functional correctness
