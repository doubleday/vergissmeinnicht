## ADDED Requirements

### Requirement: Prevent Duplicate Active Memory Writes
The system MUST prevent duplicate create requests from producing multiple active canonical memory records when the requests are equivalent within the same namespace.

For this change, two create requests are equivalent when they have the same `namespace`, `scope`, `kind`, normalized `title`, and normalized `content`.

Normalization for duplicate checks MUST be deterministic and MUST treat differences in leading or trailing whitespace as non-meaningful.

#### Scenario: Return the existing active memory for a duplicate create
- **WHEN** a client submits a create-memory request that is equivalent to an existing active memory in the same namespace
- **THEN** the system returns the existing active canonical memory record
- **AND** the system does not create an additional active canonical record for that request

#### Scenario: Create a new memory when no active duplicate exists
- **WHEN** a client submits a valid create-memory request and no equivalent active memory exists in the same namespace
- **THEN** the system creates a new canonical memory record
- **AND** the returned record is available for later fetch and search operations

#### Scenario: Ignore archived memories for duplicate blocking
- **WHEN** a client submits a valid create-memory request that matches only archived memories
- **THEN** the system creates a new active canonical memory record
- **AND** archived records remain preserved for auditability

## MODIFIED Requirements

### Requirement: Create Explicit Memories

The system MUST provide an API operation that creates a memory record from explicit client input and persists the canonical memory data for later retrieval.

The create operation MUST incorporate duplicate checks defined by the duplicate-write requirements before inserting a new active memory.

#### Scenario: Create a valid memory

- **WHEN** a client submits a valid create-memory request with an allowed `kind`, `scope`, `namespace`, `title`, and `content`
- **THEN** the system stores a canonical memory record with a stable identifier and timestamps
- **AND** the stored record preserves any provided `tags`, `source.type`, `confidence`, and `metadata`
- **AND** the created record is marked `archived: false`
- **AND** the created memory is available for later fetch and search operations

#### Scenario: Return an existing record for an equivalent active write

- **WHEN** a client submits a valid create-memory request that is equivalent to an existing active memory under the duplicate-write rule
- **THEN** the system returns the existing canonical memory record
- **AND** the response preserves the existing record's stable identifier and lifecycle fields
- **AND** no additional active record is inserted

#### Scenario: Reject an invalid confidence value

- **WHEN** a client submits a create-memory request with `confidence` outside the inclusive range `0.0` to `1.0`
- **THEN** the system rejects the request with a validation error

#### Scenario: Reject an invalid source payload

- **WHEN** a client submits a create-memory request without `source.type`
- **THEN** the system rejects the request with a validation error
