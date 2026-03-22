from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from memory_api.models import MemoryCreate, MemoryRecord, MemorySearchRequest, utcnow


def normalize_duplicate_text(value: str) -> str:
    return value.strip()


class PostgresStore:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    def connect(self) -> psycopg.Connection:
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def init(self) -> None:
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS memories (
                        id TEXT PRIMARY KEY,
                        kind TEXT NOT NULL,
                        scope TEXT NOT NULL,
                        namespace TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        supersedes_memory_id TEXT,
                        tags JSONB NOT NULL DEFAULT '[]'::jsonb,
                        source JSONB NOT NULL,
                        confidence DOUBLE PRECISION NOT NULL,
                        metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL,
                        updated_at TIMESTAMPTZ NOT NULL,
                        last_accessed_at TIMESTAMPTZ,
                        archived BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute(
                    """
                    ALTER TABLE memories
                    ADD COLUMN IF NOT EXISTS supersedes_memory_id TEXT
                    """
                )
                cur.execute(
                    """
                    ALTER TABLE memories
                    ADD COLUMN IF NOT EXISTS last_accessed_at TIMESTAMPTZ
                    """
                )
                cur.execute(
                    """
                    UPDATE memories
                    SET last_accessed_at = created_at
                    WHERE last_accessed_at IS NULL
                    """
                )
                cur.execute(
                    """
                    ALTER TABLE memories
                    ALTER COLUMN last_accessed_at SET NOT NULL
                    """
                )
            conn.commit()

    def ping(self) -> None:
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()

    def create_memory(self, memory_id: str, request: MemoryCreate) -> MemoryRecord:
        now = utcnow()
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO memories (
                        id, kind, scope, namespace, title, content, supersedes_memory_id, tags, source,
                        confidence, metadata, created_at, updated_at, last_accessed_at, archived
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE)
                    RETURNING *
                    """,
                    (
                        memory_id,
                        request.kind,
                        request.scope,
                        request.namespace,
                        request.title,
                        request.content,
                        request.supersedes_memory_id,
                        Jsonb(request.tags),
                        Jsonb(request.source.model_dump()),
                        request.confidence,
                        Jsonb(request.metadata),
                        now,
                        now,
                        now,
                    ),
                )
                row = cur.fetchone()
            conn.commit()
        return MemoryRecord.model_validate(row)

    def find_active_duplicate_memory(self, request: MemoryCreate) -> MemoryRecord | None:
        normalized_title = normalize_duplicate_text(request.title)
        normalized_content = normalize_duplicate_text(request.content)

        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM memories
                    WHERE namespace = %s
                      AND scope = %s
                      AND kind = %s
                      AND archived = FALSE
                      AND btrim(title) = %s
                      AND btrim(content) = %s
                      AND supersedes_memory_id IS NOT DISTINCT FROM %s
                    ORDER BY updated_at DESC
                    LIMIT 1
                    """,
                    (
                        request.namespace,
                        request.scope,
                        request.kind,
                        normalized_title,
                        normalized_content,
                        request.supersedes_memory_id,
                    ),
                )
                row = cur.fetchone()

        if row is None:
            return None
        return MemoryRecord.model_validate(row)

    def get_memory(self, memory_id: str, *, update_access_time: bool = False) -> MemoryRecord | None:
        with self.connect() as conn:
            with conn.cursor() as cur:
                if update_access_time:
                    cur.execute(
                        """
                        UPDATE memories
                        SET last_accessed_at = %s
                        WHERE id = %s
                        RETURNING *
                        """,
                        (utcnow(), memory_id),
                    )
                else:
                    cur.execute("SELECT * FROM memories WHERE id = %s", (memory_id,))
                row = cur.fetchone()
            if update_access_time and row is not None:
                conn.commit()
        if row is None:
            return None
        return MemoryRecord.model_validate(row)

    def archive_memory(self, memory_id: str) -> MemoryRecord | None:
        now = utcnow()
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE memories
                    SET archived = TRUE, updated_at = %s
                    WHERE id = %s
                    RETURNING *
                    """,
                    (now, memory_id),
                )
                row = cur.fetchone()
            conn.commit()
        if row is None:
            return None
        return MemoryRecord.model_validate(row)

    def search(
        self,
        request: MemorySearchRequest,
        ids: Iterable[str] | None = None,
        *,
        update_access_time: bool = False,
    ) -> list[MemoryRecord]:
        filters: list[sql.Composed] = []
        params: list[Any] = []

        if ids is not None:
            filters.append(sql.SQL("id = ANY(%s)"))
            params.append(list(ids))
        if request.namespace:
            filters.append(sql.SQL("namespace = %s"))
            params.append(request.namespace)
        if request.scope:
            filters.append(sql.SQL("scope = %s"))
            params.append(request.scope)
        if request.kind:
            filters.append(sql.SQL("kind = %s"))
            params.append(request.kind)
        if request.tags:
            filters.append(sql.SQL("tags @> %s::jsonb"))
            params.append(Jsonb(request.tags))
        if not request.include_archived:
            filters.append(sql.SQL("archived = FALSE"))
        if request.exclude_superseded:
            filters.append(
                sql.SQL(
                    """
                    NOT EXISTS (
                        SELECT 1
                        FROM memories AS superseding
                        WHERE superseding.supersedes_memory_id = memories.id
                          AND superseding.namespace = memories.namespace
                          AND superseding.archived = FALSE
                    )
                    """
                )
            )
        if request.query:
            filters.append(sql.SQL("(title ILIKE %s OR content ILIKE %s)"))
            pattern = f"%{request.query}%"
            params.extend([pattern, pattern])

        where_clause = sql.SQL("")
        if filters:
            where_clause = sql.SQL("WHERE ") + sql.SQL(" AND ").join(filters)

        query = sql.SQL(
            "SELECT * FROM memories {where_clause} ORDER BY updated_at DESC LIMIT %s"
        ).format(where_clause=where_clause)
        params.append(request.limit)

        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
                if update_access_time and rows:
                    access_time = utcnow()
                    memory_ids = [row["id"] for row in rows]
                    cur.execute(
                        """
                        UPDATE memories
                        SET last_accessed_at = %s
                        WHERE id = ANY(%s)
                        RETURNING *
                        """,
                        (access_time, memory_ids),
                    )
                    updated_rows = cur.fetchall()
                    row_by_id = {row["id"]: row for row in updated_rows}
                    rows = [row_by_id.get(row["id"], row) for row in rows]
                    conn.commit()

        return [MemoryRecord.model_validate(row) for row in rows]
