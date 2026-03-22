from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

MemoryKind = Literal["rule", "example", "feedback", "correction", "preference"]
MemoryScope = Literal["global", "project", "agent"]


class Source(BaseModel):
    type: str
    name: str | None = None

    @field_validator("type")
    @classmethod
    def normalize_type(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            msg = "source.type must not be empty"
            raise ValueError(msg)
        return normalized

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class MemoryCreate(BaseModel):
    kind: MemoryKind
    scope: MemoryScope
    namespace: str = Field(min_length=1)
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    supersedes_memory_id: str | None = None
    tags: list[str] = Field(default_factory=list)
    source: Source
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryRecord(MemoryCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime
    archived: bool = False


class MemorySearchRequest(BaseModel):
    query: str | None = None
    namespace: str | None = None
    scope: MemoryScope | None = None
    kind: MemoryKind | None = None
    tags: list[str] = Field(default_factory=list)
    include_archived: bool = False
    exclude_superseded: bool = False
    limit: int = Field(default=10, ge=1, le=100)

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class SearchResponse(BaseModel):
    results: list[MemoryRecord]


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    checks: dict[str, str]


def utcnow() -> datetime:
    return datetime.now(UTC)
