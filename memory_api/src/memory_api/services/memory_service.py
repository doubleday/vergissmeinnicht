from __future__ import annotations

from uuid import uuid4

from memory_api.models import MemoryCreate, MemoryRecord, MemorySearchRequest, SearchResponse
from memory_api.services.embedding import DeterministicEmbedder
from memory_api.services.postgres import PostgresStore
from memory_api.services.qdrant_store import QdrantStore


class MemoryService:
    def __init__(
        self,
        postgres: PostgresStore,
        qdrant: QdrantStore,
        embedder: DeterministicEmbedder,
    ) -> None:
        self.postgres = postgres
        self.qdrant = qdrant
        self.embedder = embedder

    def initialize(self) -> None:
        self.postgres.init()
        self.qdrant.init()

    def readiness_checks(self) -> dict[str, str]:
        checks: dict[str, str] = {}
        try:
            self.postgres.ping()
            checks["postgres"] = "ok"
        except Exception:
            checks["postgres"] = "error"
        try:
            self.qdrant.ping()
            checks["qdrant"] = "ok"
        except Exception:
            checks["qdrant"] = "error"
        return checks

    def create_memory(self, request: MemoryCreate) -> MemoryRecord:
        memory = self.postgres.create_memory(str(uuid4()), request)
        self.qdrant.upsert_memory(memory, self.embedder.embed(memory.content))
        return memory

    def get_memory(self, memory_id: str) -> MemoryRecord | None:
        return self.postgres.get_memory(memory_id)

    def archive_memory(self, memory_id: str) -> MemoryRecord | None:
        memory = self.postgres.archive_memory(memory_id)
        if memory is None:
            return None
        self.qdrant.upsert_memory(memory, self.embedder.embed(memory.content))
        return memory

    def search(self, request: MemorySearchRequest) -> SearchResponse:
        return SearchResponse(results=self.postgres.search(request))
