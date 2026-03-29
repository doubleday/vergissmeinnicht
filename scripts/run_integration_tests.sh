#!/usr/bin/env bash

set -euo pipefail

project_name="${COMPOSE_PROJECT_NAME:-vmn-integration-test}"
compose_files=(
  -f docker-compose.integration-static.yml
)
compose_cmd=(docker compose -p "$project_name" "${compose_files[@]}")
command="${1:-run}"
if [[ $# -gt 0 ]]; then
  shift
fi

usage() {
  cat <<'EOF'
Usage: ./scripts/run_integration_tests.sh [setup|start|reset|run|cleanup]

Commands:
  setup    Build the reusable integration-test images.
  start    Start the reusable integration stack without rebuilding images.
  reset    Recreate integration data volumes and restart the stack without rebuilding images.
  run      Reset to a clean state, start the stack, run integration tests, and run smoke verification.
  cleanup  Remove the reusable integration containers, volumes, and images.
EOF
}

require_built_images() {
  if ! docker image inspect vergissmeinnicht-integration-memory-api:latest >/dev/null 2>&1; then
    echo "Missing integration images. Run './scripts/run_integration_tests.sh setup' first." >&2
    exit 1
  fi
  if ! docker image inspect vergissmeinnicht-integration-test-runner:latest >/dev/null 2>&1; then
    echo "Missing integration images. Run './scripts/run_integration_tests.sh setup' first." >&2
    exit 1
  fi
}

start_stack() {
  require_built_images
  "${compose_cmd[@]}" up --no-build -d postgres qdrant memory-api
}

reset_stack() {
  require_built_images
  "${compose_cmd[@]}" down -v --remove-orphans
  start_stack
}

run_integration_suite() {
  local prepare_output memory_id memory_title memory_content
  reset_stack
  "${compose_cmd[@]}" run --rm test-runner

  prepare_output="$("${compose_cmd[@]}" run --rm -T test-runner /app/.venv/bin/python scripts/smoke_test.py --mode prepare)"
  memory_id="$(printf '%s' "$prepare_output" | uv run python -c 'import json, sys; print(json.load(sys.stdin)["memory_id"])')"
  memory_title="$(printf '%s' "$prepare_output" | uv run python -c 'import json, sys; print(json.load(sys.stdin)["title"])')"
  memory_content="$(printf '%s' "$prepare_output" | uv run python -c 'import json, sys; print(json.load(sys.stdin)["content"])')"

  "${compose_cmd[@]}" restart memory-api
  "${compose_cmd[@]}" run --rm -T test-runner \
    /app/.venv/bin/python scripts/smoke_test.py \
    --mode verify \
    --memory-id "$memory_id" \
    --expected-title "$memory_title" \
    --expected-content "$memory_content"
}

echo "Using integration compose project: ${project_name}"

case "$command" in
  setup)
    "${compose_cmd[@]}" build memory-api test-runner
    ;;
  start)
    start_stack
    ;;
  reset)
    reset_stack
    ;;
  run)
    run_integration_suite
    ;;
  cleanup)
    "${compose_cmd[@]}" down -v --remove-orphans --rmi local
    docker image rm -f \
      vergissmeinnicht-integration-memory-api:latest \
      vergissmeinnicht-integration-test-runner:latest >/dev/null 2>&1 || true
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    usage >&2
    exit 1
    ;;
esac
