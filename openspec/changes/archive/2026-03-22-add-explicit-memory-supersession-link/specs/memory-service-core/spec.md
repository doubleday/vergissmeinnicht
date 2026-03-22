## MODIFIED Requirements

### Requirement: Canonical Memory Record Shape

The system MUST expose a canonical memory representation for create, fetch, search, and archive operations.

The canonical memory record MUST contain:

- `id`: a stable service-generated identifier
- `kind`: an allowed memory taxonomy value
- `scope`: an allowed scope taxonomy value
- `namespace`: a client-provided namespace string
- `title`: a short human-readable label
- `content`: the canonical memory text
- `tags`: a list of zero or more string tags
- `source`: an object that includes at least `type`
- `confidence`: a numeric confidence value from `0.0` to `1.0`
- `metadata`: a free-form object for client-supplied structured metadata
- `supersedes_memory_id`: an optional identifier of an earlier memory explicitly superseded by this memory
- `created_at`: the creation timestamp
- `updated_at`: the most recent mutation timestamp
- `last_accessed_at`: the most recent observed access timestamp
- `archived`: a lifecycle flag indicating whether the memory is archived

#### Scenario: Return a canonical memory record after create

- **WHEN** a client submits a valid create-memory request
- **THEN** the system returns the created memory in the canonical representation
- **AND** the response includes a service-generated `id`
- **AND** the response includes `supersedes_memory_id`, `created_at`, `updated_at`, `last_accessed_at`, and `archived`

#### Scenario: Reject a create request missing canonical required fields

- **WHEN** a client submits a create-memory request without `kind`, `scope`, `namespace`, `title`, or `content`
- **THEN** the system rejects the request with a validation error
- **AND** no partial memory record is created

### Requirement: Create Explicit Memories

The system MUST provide an API operation that creates a memory record from explicit client input and persists the canonical memory data for later retrieval.

The create operation MUST incorporate duplicate checks defined by the duplicate-write requirements before inserting a new active memory.

The create operation MUST accept an optional `supersedes_memory_id` that explicitly links the new memory to an existing memory in the same namespace.

#### Scenario: Create a valid memory

- **WHEN** a client submits a valid create-memory request with an allowed `kind`, `scope`, `namespace`, `title`, and `content`
- **THEN** the system stores a canonical memory record with a stable identifier and timestamps
- **AND** the stored record preserves any provided `tags`, `source.type`, `confidence`, `metadata`, and `supersedes_memory_id`
- **AND** the created record is marked `archived: false`
- **AND** the created memory is available for later fetch and search operations

#### Scenario: Create a memory that explicitly supersedes an earlier memory

- **WHEN** a client submits a valid create-memory request with `supersedes_memory_id` set to an existing memory in the same namespace
- **THEN** the system stores the new canonical memory record with that `supersedes_memory_id`
- **AND** the superseded memory remains independently fetchable and searchable unless a separate archive action changes its lifecycle state

#### Scenario: Return an existing record for an equivalent active write

- **WHEN** a client submits a valid create-memory request that is equivalent to an existing active memory under the duplicate-write rule
- **THEN** the system returns the existing canonical memory record
- **AND** the response preserves the existing record's stable identifier and lifecycle fields
- **AND** no additional active record is inserted

#### Scenario: Reject an invalid supersession reference

- **WHEN** a client submits a create-memory request with `supersedes_memory_id` that does not identify an existing memory in the same namespace
- **THEN** the system rejects the request with a validation error
- **AND** no partial memory record is created

#### Scenario: Reject an invalid confidence value

- **WHEN** a client submits a create-memory request with `confidence` outside the inclusive range `0.0` to `1.0`
- **THEN** the system rejects the request with a validation error

#### Scenario: Reject an invalid source payload

- **WHEN** a client submits a create-memory request without `source.type`
- **THEN** the system rejects the request with a validation error

### Requirement: Prevent Duplicate Active Memory Writes

The system MUST prevent duplicate create requests from producing multiple active canonical memory records when the requests are equivalent within the same namespace.

For this change, two create requests are equivalent when they have the same `namespace`, `scope`, `kind`, normalized `title`, normalized `content`, and the same `supersedes_memory_id` value.

Normalization for duplicate checks MUST be deterministic and MUST treat differences in leading or trailing whitespace as non-meaningful.

#### Scenario: Return the existing active memory for a duplicate create

- **WHEN** a client submits a create-memory request that is equivalent to an existing active memory in the same namespace
- **THEN** the system returns the existing active canonical memory record
- **AND** the system does not create an additional active canonical record for that request

#### Scenario: Create a new memory when no active duplicate exists

- **WHEN** a client submits a valid create-memory request and no equivalent active memory exists in the same namespace
- **THEN** the system creates a new canonical memory record
- **AND** the returned record is available for later fetch and search operations

#### Scenario: Create a new memory when supersession intent differs

- **WHEN** a client submits a valid create-memory request that matches an existing active memory on `namespace`, `scope`, `kind`, normalized `title`, and normalized `content` but has a different `supersedes_memory_id`
- **THEN** the request is not treated as an equivalent duplicate
- **AND** the system creates a distinct canonical memory record for that lineage

#### Scenario: Ignore archived memories for duplicate blocking

- **WHEN** a client submits a valid create-memory request that matches only archived memories
- **THEN** the system creates a new active canonical memory record
- **AND** archived records remain preserved for auditability
