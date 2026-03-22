FROM python:3.12-slim AS base

COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md /app/
COPY memory_api /app/memory_api
COPY scripts /app/scripts

FROM base AS runtime

RUN uv sync --no-dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "memory_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS test-runner

ENV MEMORY_API_BASE_URL=http://memory-api:8000

COPY tests /app/tests
COPY tests_integration /app/tests_integration

RUN uv sync --dev

CMD ["uv", "run", "pytest", "tests_integration"]
