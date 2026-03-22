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
- `source`: an object with a required normalized `type` string and an optional normalized `name` string
- `confidence`: a numeric confidence value from `0.0` to `1.0`
- `metadata`: a free-form object for client-supplied structured metadata
- `supersedes_memory_id`: an optional identifier of an earlier memory explicitly superseded by this memory
- `created_at`: the creation timestamp
- `updated_at`: the most recent mutation timestamp
- `last_accessed_at`: the most recent observed access timestamp
- `archived`: a lifecycle flag indicating whether the memory is archived

Canonical source normalization MUST be deterministic:

- `source.type` MUST treat leading and trailing whitespace as non-meaningful
- `source.type` MUST be returned in lowercase canonical form
- `source.name`, when present, MUST treat leading and trailing whitespace as non-meaningful
- `source.name` MUST be omitted from the canonical record when its normalized value would be empty

#### Scenario: Return a canonical memory record after create

- **WHEN** a client submits a valid create-memory request
- **THEN** the system returns the created memory in the canonical representation
- **AND** the response includes a service-generated `id`
- **AND** the response includes `source.type` in normalized canonical form
- **AND** the response includes `source.name` only when a non-empty normalized name was provided
- **AND** the response includes `supersedes_memory_id`, `created_at`, `updated_at`, `last_accessed_at`, and `archived`

#### Scenario: Return the same canonical source shape across endpoints

- **WHEN** a client creates, fetches, searches, or archives a memory
- **THEN** each returned canonical memory record includes the same normalized `source` shape for that stored memory
- **AND** the record does not require endpoint-specific source interpretation

#### Scenario: Reject a create request missing canonical required fields

- **WHEN** a client submits a create-memory request without `kind`, `scope`, `namespace`, `title`, or `content`
- **THEN** the system rejects the request with a validation error
- **AND** no partial memory record is created

### Requirement: Create Explicit Memories

The system MUST provide an API operation that creates a memory record from explicit client input and persists the canonical memory data for later retrieval.

The create operation MUST incorporate duplicate checks defined by the duplicate-write requirements before inserting a new active memory.

The create operation MUST accept an optional `supersedes_memory_id` that explicitly links the new memory to an existing memory in the same namespace.

The create operation MUST normalize the stored canonical `source` envelope before persistence.

#### Scenario: Create a valid memory

- **WHEN** a client submits a valid create-memory request with an allowed `kind`, `scope`, `namespace`, `title`, and `content`
- **THEN** the system stores a canonical memory record with a stable identifier and timestamps
- **AND** the stored record preserves any provided `tags`, normalized `source.type`, normalized `source.name`, `confidence`, `metadata`, and `supersedes_memory_id`
- **AND** the created record is marked `archived: false`
- **AND** the created memory is available for later fetch and search operations

#### Scenario: Omit a blank source name from the stored record

- **WHEN** a client submits a valid create-memory request whose `source.name` is absent or normalizes to an empty string
- **THEN** the system stores the canonical memory record without `source.name`
- **AND** later fetch, search, and archive responses omit `source.name` for that memory

#### Scenario: Create a memory that explicitly supersedes an earlier memory

- **WHEN** a client submits a valid create-memory request with `supersedes_memory_id` set to an existing memory in the same namespace
- **THEN** the system stores the new canonical memory record with that `supersedes_memory_id`
- **AND** the superseded memory remains independently fetchable and searchable unless a separate archive action changes its lifecycle state

#### Scenario: Return an existing record for an equivalent active write

- **WHEN** a client submits a valid create-memory request that is equivalent to an existing active memory under the duplicate-write rule
- **THEN** the system returns the existing canonical memory record
- **AND** the response preserves the existing record's stable identifier and lifecycle fields
- **AND** the response preserves the stored record's normalized canonical `source` shape
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

