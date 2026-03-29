# Vergissmeinnicht

Local memory service foundation for coding agents and automation.

## Requirements

- `uv`
- Docker Desktop or another Docker daemon compatible with `docker compose`

## Quick Start

1. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

2. Sync Python dependencies with `uv`:

   ```bash
   uv sync
   ```

3. Start the stack:

   ```bash
   docker compose up --build -d
   ```

4. Check readiness:

   ```bash
   curl http://127.0.0.1:8000/readyz
   ```

## Python Client

The first Milestone D adapter slice is a thin typed Python client over the existing four memory endpoints. It stays at the current API boundary and is intended to be the shared base for later CLI and MCP work.

```python
from memory_api import MemoryApiClient
from memory_api.models import MemoryCreate, MemorySearchRequest

with MemoryApiClient(base_url="http://127.0.0.1:8000") as client:
    created = client.create_memory(
        MemoryCreate(
            kind="rule",
            scope="project",
            namespace="demo",
            title="Keep responses concise",
            content="Prefer direct answers unless more detail is requested.",
            tags=["style"],
            source={"type": "manual"},
        )
    )
    fetched = client.get_memory(created.id)
    results = client.search_memories(
        MemorySearchRequest(query="direct answers", namespace="demo", scope="project")
    )
    archived = client.archive_memory(created.id)
```

The client intentionally does not include readiness calls, retries, MCP behavior, or CLI-oriented helper methods.

## CLI

The next Milestone D adapter slice is a thin CLI over the shared Python client. It exposes the same four memory operations for manual inspection and debugging and does not add new backend behavior.

```bash
memory-cli create \
  --kind rule \
  --scope project \
  --namespace demo \
  --title "Keep responses concise" \
  --content "Prefer direct answers unless more detail is requested." \
  --tag style \
  --source-type manual

memory-cli search --query "direct answers" --namespace demo --scope project
memory-cli get <memory-id>
memory-cli archive <memory-id>
```

The CLI prints structured JSON to stdout, uses the shared client for all four operations, and supports `--base-url` plus `--timeout` on each command.

## Verification

Run the fast unit tests:

```bash
uv run pytest
```

Run the isolated integration suite:

```bash
./scripts/run_integration_tests.sh setup
./scripts/run_integration_tests.sh run
```

The integration workflow uses a reusable isolated Docker Compose project from [`docker-compose.integration-static.yml`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/docker-compose.integration-static.yml). It restores clean PostgreSQL and Qdrant state before each run, executes the live-stack tests from an internal `test-runner` container, restarts `memory-api` inside that isolated project, and runs the smoke verification flow. It does not require the default local stack to be running and does not reuse its fixed ports or persistent volumes.

Available lifecycle commands:

```bash
./scripts/run_integration_tests.sh setup
./scripts/run_integration_tests.sh start
./scripts/run_integration_tests.sh reset
./scripts/run_integration_tests.sh run
./scripts/run_integration_tests.sh cleanup
```

Use `setup` the first time or after Dockerfile/dependency changes, `run` for ordinary isolated integration verification, `reset` when you want to reestablish a clean deterministic test state without rebuilding images, and `cleanup` when you want to remove the reusable integration stack entirely.

Run the manual smoke test against an already running stack:

```bash
uv run python scripts/smoke_test.py
```

The smoke test creates a memory, fetches it, searches for it, restarts the target stack, and verifies the memory remains available afterward. It remains useful as a manual check when you want to verify an existing environment directly.

Run the manual retrieval-eval workflow:

```bash
./scripts/run_retrieval_evals.sh setup
./scripts/run_retrieval_evals.sh run
```

The retrieval-eval workflow uses a reusable local Docker Compose project instead of a fresh timestamped project on every run. It loads the frozen starter dataset from [`evals/retrieval/starter/`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/evals/retrieval/starter), exercises the live HTTP search API, and saves a machine-readable result under `artifacts/retrieval-evals/` before printing a human-readable summary. It is separate from unit tests and integration tests because it measures retrieval quality rather than functional correctness.

Available lifecycle commands:

```bash
./scripts/run_retrieval_evals.sh setup
./scripts/run_retrieval_evals.sh start
./scripts/run_retrieval_evals.sh reset
./scripts/run_retrieval_evals.sh run
./scripts/run_retrieval_evals.sh cleanup
```

Use `setup` the first time or after Dockerfile/dependency changes, `run` for ordinary eval iterations, `reset` when you want a fresh isolated eval data state before the next run, and `cleanup` when you want to remove the reusable eval stack entirely.

The starter query set now includes both positive-match queries and explicit expected-non-match queries. The saved result reports `unexpected_ids`, expected-empty success, and `precision@k` so false positives are visible even when a relevant hit still ranks first.

By default, the stack still uses `deterministic-local`, which keeps unit tests, integration tests, and zero-dependency local runs hermetic. Retrieval-eval scores from that mode are useful for workflow establishment and regression comparison, but they should not be treated as strong evidence of real semantic quality.

Each saved retrieval-eval result also records embedding runtime metadata such as provider, model name, dimensions, device, and collection name. Use that metadata to compare like-for-like runs rather than mixing deterministic and real-provider outputs implicitly.

The reusable retrieval-eval stack stays isolated from the default local `docker compose up` stack through its own Compose file, project name, volumes, and eval-specific Qdrant collection. It is meant for repeatable quality runs, not general manual API work.

To run a local real-embedding configuration, set:

```bash
EMBEDDING_PROVIDER=sentence-transformer-local
EMBEDDING_MODEL_NAME=BAAI/bge-small-en-v1.5
EMBEDDING_DIMENSIONS=384
EMBEDDING_DEVICE=cpu
```

When switching provider, model, or vector dimensions, use a clean Qdrant collection or a different collection name such as `memories_bge_small`. Existing vectors from another embedding runtime are not a supported mixed-runtime steady state.

## OpenSpec Change Naming

Active OpenSpec changes under `openspec/changes/` use plain kebab-case slugs such as `add-memory-cli`.

Archived changes under `openspec/changes/archive/` use a date-prefixed form such as `2026-03-29-add-memory-cli`.

To catch accidental date-prefixed active changes, run:

```bash
uv run python scripts/check_openspec_change_names.py
```

## Inspect Backing Stores

Inspect PostgreSQL rows:

```bash
docker compose exec postgres psql -U "${POSTGRES_USER:-memory}" -d "${POSTGRES_DB:-memory}" -c "select id, namespace, archived from memories;"
```

Inspect Qdrant collections:

```bash
curl http://127.0.0.1:6333/collections | jq
```

Inspect Qdrant points:

```bash
curl -X POST http://127.0.0.1:6333/collections/${MEMORY_QDRANT_COLLECTION:-memories}/points/scroll \
  -H 'Content-Type: application/json' \
  -d '{"limit": 10, "with_payload": true, "with_vector": false}'
```

## Troubleshooting

- If `docker compose up` fails immediately, ensure the Docker daemon is running.
- If `/readyz` returns `"degraded"`, inspect `docker compose logs memory-api`.
- If PostgreSQL or Qdrant health checks fail, wait for their containers to finish initialization before retrying the smoke test.
- If the integration workflow fails, inspect the project-specific containers with `docker compose -p <reported-project-name> -f docker-compose.integration.yml logs`.
