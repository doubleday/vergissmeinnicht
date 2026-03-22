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

## Verification

Run the fast unit tests:

```bash
uv run pytest
```

Run the isolated integration suite:

```bash
./scripts/run_integration_tests.sh
```

The integration workflow starts a dedicated Docker Compose project from [`docker-compose.integration.yml`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/docker-compose.integration.yml), runs the live-stack tests from an internal `test-runner` container, restarts `memory-api` inside that isolated project, and tears the whole environment down with `down -v` when finished. It does not require the default local stack to be running and does not reuse its fixed ports or persistent volumes.

Run the manual smoke test against an already running stack:

```bash
uv run python scripts/smoke_test.py
```

The smoke test creates a memory, fetches it, searches for it, restarts the target stack, and verifies the memory remains available afterward. It remains useful as a manual check when you want to verify an existing environment directly.

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
