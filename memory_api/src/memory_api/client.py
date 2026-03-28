from __future__ import annotations

from typing import Any

import httpx

from memory_api.models import MemoryCreate, MemoryRecord, MemorySearchRequest, SearchResponse


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_TIMEOUT = 10.0


class MemoryApiError(Exception):
    """Base error for memory API client failures."""


class MemoryApiTransportError(MemoryApiError):
    """Raised when the client cannot reach the memory API."""

    def __init__(self, message: str, *, cause: Exception) -> None:
        super().__init__(message)
        self.__cause__ = cause


class MemoryApiResponseError(MemoryApiError):
    """Raised when the memory API returns a non-success HTTP response."""

    def __init__(self, status_code: int, message: str, *, response: httpx.Response) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class MemoryApiClient:
    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        transport: httpx.BaseTransport | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        if transport is not None and http_client is not None:
            msg = "transport and http_client are mutually exclusive"
            raise ValueError(msg)

        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            transport=transport,
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> MemoryApiClient:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def create_memory(self, payload: MemoryCreate) -> MemoryRecord:
        response = self._request("POST", "/memories", json=payload.model_dump(exclude_none=True))
        return MemoryRecord.model_validate(response.json())

    def search_memories(self, payload: MemorySearchRequest) -> SearchResponse:
        response = self._request("POST", "/memories/search", json=payload.model_dump(exclude_none=True))
        return SearchResponse.model_validate(response.json())

    def get_memory(self, memory_id: str) -> MemoryRecord:
        response = self._request("GET", f"/memories/{memory_id}")
        return MemoryRecord.model_validate(response.json())

    def archive_memory(self, memory_id: str) -> MemoryRecord:
        response = self._request("POST", f"/memories/{memory_id}/archive")
        return MemoryRecord.model_validate(response.json())

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        try:
            response = self._client.request(method, path, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            raise MemoryApiResponseError(
                exc.response.status_code,
                self._build_response_error_message(exc.response),
                response=exc.response,
            ) from exc
        except httpx.HTTPError as exc:
            raise MemoryApiTransportError(f"memory API request failed: {exc}", cause=exc) from exc

    @staticmethod
    def _build_response_error_message(response: httpx.Response) -> str:
        payload = response.text
        try:
            data = response.json()
        except ValueError:
            pass
        else:
            if isinstance(data, dict) and "detail" in data:
                payload = str(data["detail"])
            else:
                payload = str(data)
        return f"memory API returned {response.status_code}: {payload}"
