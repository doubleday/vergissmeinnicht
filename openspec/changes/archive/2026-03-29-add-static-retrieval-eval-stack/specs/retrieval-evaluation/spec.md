## MODIFIED Requirements

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
