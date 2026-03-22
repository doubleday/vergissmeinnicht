#!/usr/bin/env bash

set -euo pipefail

project_name="${COMPOSE_PROJECT_NAME:-vmn-it-$(date +%s)-$$}"
compose_files=(
  -f docker-compose.integration.yml
)
compose_cmd=(docker compose -p "$project_name" "${compose_files[@]}")

cleanup() {
  "${compose_cmd[@]}" down -v --remove-orphans >/dev/null 2>&1 || true
}

trap cleanup EXIT

echo "Using integration compose project: ${project_name}"

"${compose_cmd[@]}" build memory-api test-runner
"${compose_cmd[@]}" up -d postgres qdrant memory-api
"${compose_cmd[@]}" run --rm test-runner

prepare_output="$("${compose_cmd[@]}" run --rm -T test-runner uv run python scripts/smoke_test.py --mode prepare)"
memory_id="$(printf '%s' "$prepare_output" | uv run python -c 'import json, sys; print(json.load(sys.stdin)["memory_id"])')"
memory_title="$(printf '%s' "$prepare_output" | uv run python -c 'import json, sys; print(json.load(sys.stdin)["title"])')"
memory_content="$(printf '%s' "$prepare_output" | uv run python -c 'import json, sys; print(json.load(sys.stdin)["content"])')"

"${compose_cmd[@]}" restart memory-api
"${compose_cmd[@]}" run --rm -T test-runner \
  uv run python scripts/smoke_test.py \
  --mode verify \
  --memory-id "$memory_id" \
  --expected-title "$memory_title" \
  --expected-content "$memory_content"
