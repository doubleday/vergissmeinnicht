## 1. Duplicate Create Contract

- [x] 1.1 Define the duplicate-equivalence rule for create requests in the `memory-service-core` delta spec
- [x] 1.2 Define the observable API behavior when a request matches an existing active memory

## 2. Canonical Persistence Updates

- [x] 2.1 Implement canonical-store lookup logic that checks for duplicates before insert
- [x] 2.2 Return the existing active record instead of creating a new one when the duplicate rule matches
- [x] 2.3 Verify archived memories do not block new writes in this change

## 3. Validation

- [x] 3.1 Add or update tests for unique create, duplicate create, and archived-record edge cases
- [x] 3.2 Validate the change with the OpenSpec CLI before implementation review
