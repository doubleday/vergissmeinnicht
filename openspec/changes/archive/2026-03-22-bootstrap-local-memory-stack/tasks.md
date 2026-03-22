## 1. Local Stack Bootstrap

- [x] 1.1 Add the initial repository structure and dependencies required to run `memory-api`, `postgres`, and `qdrant` locally
- [x] 1.2 Create the Docker Compose configuration, persistent volumes, and shared network for the three-service stack
- [x] 1.3 Add documented environment-backed configuration for database, Qdrant, and embedding-related settings used by the local stack

## 2. API Runtime Wiring

- [x] 2.1 Implement the minimal FastAPI application bootstrap and configuration loading for local development
- [x] 2.2 Wire the API startup path to PostgreSQL and Qdrant so dependency connectivity is established through configured settings
- [x] 2.3 Add health and readiness endpoints that distinguish process health from dependency availability

## 3. Verification and Developer Operability

- [x] 3.1 Add a smoke test or scripted verification flow that brings the stack up and confirms readiness
- [x] 3.2 Verify that data written through the API remains present after a container restart for both PostgreSQL and Qdrant
- [x] 3.3 Document how to start the stack, inspect backing store data directly, and troubleshoot failed readiness checks
