#!/usr/bin/env bash

set -euo pipefail

project_name="${COMPOSE_PROJECT_NAME:-vmn-reval-$(date +%s)-$$}"
output_dir="${OUTPUT_DIR:-artifacts/retrieval-evals}"
compose_files=(
  -f docker-compose.integration.yml
)
compose_cmd=(docker compose -p "$project_name" "${compose_files[@]}")
result_path="${output_dir}/retrieval-eval-$(date +%Y%m%d-%H%M%S).json"

cleanup() {
  "${compose_cmd[@]}" down -v --remove-orphans >/dev/null 2>&1 || true
}

trap cleanup EXIT

mkdir -p "$output_dir"

echo "Using retrieval-eval compose project: ${project_name}"

export MEMORY_QDRANT_COLLECTION="${MEMORY_QDRANT_COLLECTION:-memories_retrieval_eval}"

"${compose_cmd[@]}" build memory-api test-runner
"${compose_cmd[@]}" up -d postgres qdrant memory-api
"${compose_cmd[@]}" run --rm -T test-runner \
  uv run python scripts/retrieval_eval.py run --output-format json > "$result_path"

echo "Saved retrieval-eval result: ${result_path}"
uv run python scripts/retrieval_eval.py summary --input "$result_path"
