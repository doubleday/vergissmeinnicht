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

Run the smoke test against a running stack:

```bash
uv run python scripts/smoke_test.py
```

The smoke test creates a memory, fetches it, searches for it, restarts the Compose stack, and verifies the memory remains available afterward.

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
