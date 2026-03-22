## ADDED Requirements

### Requirement: Search Uses Deterministic Query-Aware Ordering

The search operation MUST return results in a deterministic order.

When a query is present, the system MUST order matching memories using the following priority, from strongest to weakest:

1. exact case-insensitive title matches
2. title substring matches
3. content substring matches
4. higher `confidence`
5. more recent `updated_at`
6. lexicographically smaller `id`

When no query is present, the system MUST preserve browse-style ordering by `updated_at` descending and `id` ascending.

#### Scenario: Exact title matches rank ahead of weaker matches

- **WHEN** a client searches with query text that exactly matches one memory title and only partially matches other memories
- **THEN** the exact title match appears before title-substring and content-only matches in the returned results

#### Scenario: Title matches rank ahead of content-only matches

- **WHEN** a client searches with query text that appears in one memory title and in another memory content only
- **THEN** the title match appears before the content-only match in the returned results

#### Scenario: Confidence breaks ties within the same match tier

- **WHEN** multiple memories match the same query at the same textual match tier
- **THEN** memories with higher `confidence` appear earlier in the returned results

#### Scenario: Non-query searches stay chronological with deterministic ties

- **WHEN** a client searches without query text
- **THEN** the system orders matching memories by `updated_at` descending
- **AND** uses `id` ascending to break ties deterministically
