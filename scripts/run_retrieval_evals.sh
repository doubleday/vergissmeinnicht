#!/usr/bin/env bash

set -euo pipefail

project_name="${COMPOSE_PROJECT_NAME:-vmn-retrieval-eval}"
output_dir="${OUTPUT_DIR:-artifacts/retrieval-evals}"
compose_files=(
  -f docker-compose.retrieval-eval.yml
)
compose_cmd=(docker compose -p "$project_name" "${compose_files[@]}")

mkdir -p "$output_dir"
export MEMORY_QDRANT_COLLECTION="${MEMORY_QDRANT_COLLECTION:-memories_retrieval_eval}"
command="${1:-run}"
if [[ $# -gt 0 ]]; then
  shift
fi

python_cmd=()
if command -v uv >/dev/null 2>&1; then
  python_cmd=(uv run python)
elif [[ -x ".venv/bin/python" ]]; then
  python_cmd=(.venv/bin/python)
else
  echo "Missing Python runner. Install uv or create .venv/bin/python." >&2
  exit 1
fi

usage() {
  cat <<'EOF'
Usage: ./scripts/run_retrieval_evals.sh [setup|start|reset|run|compare|cleanup]

Commands:
  setup    Build the reusable retrieval-eval images.
  start    Start the reusable retrieval-eval stack without rebuilding images.
  reset    Recreate retrieval-eval data volumes and restart the stack without rebuilding images.
  run      Start the stack if needed, run the eval, save a JSON artifact, and print a summary.
  compare  Compare two saved retrieval-eval JSON artifacts.
  cleanup  Remove the reusable retrieval-eval containers, volumes, and images.
EOF
}

require_built_images() {
  if ! docker image inspect vergissmeinnicht-retrieval-eval-memory-api:latest >/dev/null 2>&1; then
    echo "Missing retrieval-eval images. Run './scripts/run_retrieval_evals.sh setup' first." >&2
    exit 1
  fi
  if ! docker image inspect vergissmeinnicht-retrieval-eval-test-runner:latest >/dev/null 2>&1; then
    echo "Missing retrieval-eval images. Run './scripts/run_retrieval_evals.sh setup' first." >&2
    exit 1
  fi
}

start_stack() {
  require_built_images
  "${compose_cmd[@]}" up --no-build -d postgres qdrant memory-api
}

run_eval() {
  local result_path
  result_path="${output_dir}/retrieval-eval-$(date +%Y%m%d-%H%M%S).json"
  start_stack
  "${compose_cmd[@]}" run --rm --no-deps -T test-runner \
    /app/.venv/bin/python scripts/retrieval_eval.py run --output-format json > "$result_path"
  echo "Saved retrieval-eval result: ${result_path}"
  "${python_cmd[@]}" scripts/retrieval_eval.py summary --input "$result_path"
}

compare_eval() {
  if [[ $# -ne 2 ]]; then
    echo "Usage: ./scripts/run_retrieval_evals.sh compare <baseline.json> <candidate.json>" >&2
    exit 1
  fi
  "${python_cmd[@]}" scripts/retrieval_eval.py compare --baseline "$1" --candidate "$2"
}

echo "Using retrieval-eval compose project: ${project_name}"

case "$command" in
  setup)
    "${compose_cmd[@]}" build memory-api test-runner
    ;;
  start)
    start_stack
    ;;
  reset)
    require_built_images
    "${compose_cmd[@]}" down -v --remove-orphans
    start_stack
    ;;
  run)
    run_eval
    ;;
  compare)
    compare_eval "$@"
    ;;
  cleanup)
    "${compose_cmd[@]}" down -v --remove-orphans --rmi local
    docker image rm -f \
      vergissmeinnicht-retrieval-eval-memory-api:latest \
      vergissmeinnicht-retrieval-eval-test-runner:latest >/dev/null 2>&1 || true
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    usage >&2
    exit 1
    ;;
esac
