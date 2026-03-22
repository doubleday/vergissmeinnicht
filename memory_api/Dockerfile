FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml README.md /app/
COPY memory_api /app/memory_api
COPY scripts /app/scripts

RUN uv sync --no-dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "memory_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
