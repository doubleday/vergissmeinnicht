from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request

from memory_api.config import settings
from memory_api.models import HealthResponse, MemoryCreate, MemoryRecord, MemorySearchRequest, SearchResponse
from memory_api.services.embedding import DeterministicEmbedder
from memory_api.services.memory_service import MemoryService
from memory_api.services.postgres import PostgresStore
from memory_api.services.qdrant_store import QdrantStore


def build_service() -> MemoryService:
    return MemoryService(
        postgres=PostgresStore(settings.postgres_dsn),
        qdrant=QdrantStore(settings.qdrant_url, settings.memory_qdrant_collection, settings.embedding_dimensions),
        embedder=DeterministicEmbedder(settings.embedding_dimensions),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    service = build_service()
    service.initialize()
    app.state.memory_service = service
    yield


app = FastAPI(title="memory-api", version="0.1.0", lifespan=lifespan)


def get_service(request: Request) -> MemoryService:
    return request.app.state.memory_service


@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok", checks={"api": "ok"})


@app.get("/readyz", response_model=HealthResponse)
def readyz(request: Request) -> HealthResponse:
    checks = get_service(request).readiness_checks()
    status = "ok" if all(value == "ok" for value in checks.values()) else "degraded"
    return HealthResponse(status=status, checks=checks)


@app.post("/memories", response_model=MemoryRecord)
def create_memory(request: Request, payload: MemoryCreate) -> MemoryRecord:
    return get_service(request).create_memory(payload)


@app.get("/memories/{memory_id}", response_model=MemoryRecord)
def get_memory(request: Request, memory_id: str) -> MemoryRecord:
    memory = get_service(request).get_memory(memory_id)
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@app.post("/memories/{memory_id}/archive", response_model=MemoryRecord)
def archive_memory(request: Request, memory_id: str) -> MemoryRecord:
    memory = get_service(request).archive_memory(memory_id)
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@app.post("/memories/search", response_model=SearchResponse)
def search_memories(request: Request, payload: MemorySearchRequest) -> SearchResponse:
    return get_service(request).search(payload)
