from __future__ import annotations

from typing import Protocol
from uuid import uuid4

from memory_api.models import MemoryCreate, MemoryRecord, MemorySearchRequest, SearchResponse
from memory_api.services.embedding import DeterministicEmbedder


class InvalidSupersessionReferenceError(ValueError):
    pass


class PostgresStoreLike(Protocol):
    def init(self) -> None: ...
    def ping(self) -> None: ...
    def find_active_duplicate_memory(self, request: MemoryCreate) -> MemoryRecord | None: ...
    def create_memory(self, memory_id: str, request: MemoryCreate) -> MemoryRecord: ...
    def get_memory(self, memory_id: str, *, update_access_time: bool = False) -> MemoryRecord | None: ...
    def archive_memory(self, memory_id: str) -> MemoryRecord | None: ...
    def search(
        self,
        request: MemorySearchRequest,
        ids: list[str] | None = None,
        *,
        update_access_time: bool = False,
    ) -> list[MemoryRecord]: ...


class QdrantStoreLike(Protocol):
    def init(self) -> None: ...
    def ping(self) -> None: ...
    def search_memory_candidates(self, vector: list[float], *, limit: int) -> list[tuple[str, float]]: ...
    def upsert_memory(self, memory: MemoryRecord, vector: list[float]) -> None: ...


class MemoryService:
    def __init__(
        self,
        postgres: PostgresStoreLike,
        qdrant: QdrantStoreLike,
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
        self._validate_supersession_reference(request)
        existing_memory = self.postgres.find_active_duplicate_memory(request)
        if existing_memory is not None:
            return existing_memory

        memory = self.postgres.create_memory(str(uuid4()), request)
        self.qdrant.upsert_memory(memory, self.embedder.embed(memory.content))
        return memory

    def _validate_supersession_reference(self, request: MemoryCreate) -> None:
        if request.supersedes_memory_id is None:
            return

        superseded_memory = self.postgres.get_memory(request.supersedes_memory_id, update_access_time=False)
        if superseded_memory is None:
            msg = "supersedes_memory_id must reference an existing memory in the same namespace"
            raise InvalidSupersessionReferenceError(msg)
        if superseded_memory.namespace != request.namespace:
            msg = "supersedes_memory_id must reference an existing memory in the same namespace"
            raise InvalidSupersessionReferenceError(msg)

    def get_memory(self, memory_id: str) -> MemoryRecord | None:
        return self.postgres.get_memory(memory_id, update_access_time=True)

    def archive_memory(self, memory_id: str) -> MemoryRecord | None:
        memory = self.postgres.archive_memory(memory_id)
        if memory is None:
            return None
        self.qdrant.upsert_memory(memory, self.embedder.embed(memory.content))
        return memory

    def search(self, request: MemorySearchRequest) -> SearchResponse:
        if request.query is None:
            return SearchResponse(results=self.postgres.search(request, update_access_time=True))

        candidates = self.qdrant.search_memory_candidates(
            self.embedder.embed(request.query),
            limit=min(request.limit * 5, 500),
        )
        if not candidates:
            return SearchResponse(results=[])
        score_by_id = {memory_id: score for memory_id, score in candidates}
        results = self.postgres.search(
            request,
            ids=[memory_id for memory_id, _score in candidates],
            update_access_time=True,
        )
        results.sort(key=lambda memory: (-score_by_id[memory.id], -memory.updated_at.timestamp(), memory.id))
        return SearchResponse(results=results)
