#
# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md /app/

FROM base AS runtime-deps

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

FROM runtime-deps AS runtime

COPY evals /app/evals
COPY memory_api /app/memory_api
COPY scripts /app/scripts

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "memory_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS test-deps

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --dev --no-install-project

FROM test-deps AS test-runner

ENV MEMORY_API_BASE_URL=http://memory-api:8000

COPY evals /app/evals
COPY memory_api /app/memory_api
COPY scripts /app/scripts
COPY tests /app/tests
COPY tests_integration /app/tests_integration

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --dev

CMD ["/app/.venv/bin/pytest", "tests_integration"]
