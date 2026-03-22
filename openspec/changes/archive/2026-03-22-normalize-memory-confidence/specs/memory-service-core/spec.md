## ADDED Requirements

### Requirement: Confidence Is Canonicalized Deterministically

The canonical memory record MUST store `confidence` in a deterministic normalized form.

For this slice, confidence normalization MUST:

- preserve the existing inclusive valid range of `0.0` to `1.0`
- round to exactly three decimal places using deterministic decimal rounding
- apply before persistence when a valid create-memory request produces a new canonical memory record

The system MUST return the stored normalized `confidence` value for that memory in create, fetch, search, and archive responses.

#### Scenario: Normalize an in-range confidence value before storing it

- **WHEN** a client submits a valid create-memory request with `confidence` containing more than three decimal places
- **THEN** the system stores the memory with `confidence` rounded to the canonical three-decimal representation
- **AND** the create response returns that normalized stored value

#### Scenario: Preserve canonical confidence across endpoints

- **WHEN** a memory has been stored with normalized `confidence`
- **THEN** fetch, search, and archive responses for that memory return the same normalized `confidence` value
- **AND** endpoint-specific confidence interpretation is not required

#### Scenario: Return the existing stored confidence for a duplicate create

- **WHEN** a client submits a create-memory request that resolves to an existing active memory under the duplicate-write rule
- **THEN** the system returns the existing canonical memory record
- **AND** the response preserves that stored record's normalized `confidence` value
