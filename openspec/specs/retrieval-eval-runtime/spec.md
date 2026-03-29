## Purpose

Define the reusable local runtime workflow for retrieval evals, including setup, reset, run, and cleanup operations.

## Requirements

### Requirement: Retrieval Eval Runtime Supports Explicit Lifecycle Operations

The system MUST provide a reusable local retrieval-eval runtime with explicit lifecycle operations for setup, startup, reset, eval execution, and cleanup.

The lifecycle operations MUST be documented entry points rather than an implicit side effect of a single all-in-one command.

#### Scenario: First-time setup builds reusable eval runtime

- **WHEN** a developer prepares the retrieval-eval runtime for first use
- **THEN** the system builds or otherwise initializes the required runtime resources
- **AND** the resulting runtime can be reused by later eval runs without generating a new timestamped project by default

#### Scenario: Repeated eval run reuses existing runtime

- **WHEN** a developer runs retrieval evals repeatedly without changing the runtime definition
- **THEN** the system reuses the existing local eval runtime
- **AND** the workflow does not require rebuilding a fresh project-specific image set for each run

### Requirement: Retrieval Eval Runtime Remains Isolated From Default Local Stack

The reusable retrieval-eval runtime MUST remain separate from the developer's normal local stack used for manual API work.

#### Scenario: Eval runtime does not share default stack resources implicitly

- **WHEN** a developer runs the retrieval-eval workflow
- **THEN** the workflow uses its own runtime context for eval data and services
- **AND** the developer's default local stack is not treated as the retrieval-eval target by default

### Requirement: Retrieval Eval Runtime Supports Clean Reset And Cleanup

The reusable retrieval-eval runtime MUST support a clean reset for eval data and a full cleanup for local resources.

#### Scenario: Reset prepares a clean eval state without full rebuild

- **WHEN** a developer requests a retrieval-eval reset
- **THEN** the workflow restores a clean eval data state for the next run
- **AND** it does not require rebuilding the reusable runtime images if the runtime definition has not changed

#### Scenario: Cleanup removes reusable eval runtime resources

- **WHEN** a developer requests retrieval-eval cleanup
- **THEN** the workflow removes the reusable eval runtime resources it created
- **AND** later eval use can recreate them through the documented setup path
