from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from uuid import uuid4

import httpx


BASE_URL = os.environ.get("MEMORY_API_BASE_URL", "http://127.0.0.1:8000")


def wait_until_ready(timeout_seconds: int = 90) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            response = httpx.get(f"{BASE_URL}/readyz", timeout=5.0)
            data = response.json()
            if response.status_code == 200 and data["status"] == "ok":
                return
        except httpx.HTTPError:
            pass
        time.sleep(2)
    raise RuntimeError("memory-api did not become ready in time")


def restart_stack() -> None:
    subprocess.run(["docker", "compose", "restart"], check=True)


def create_memory() -> dict:
    suffix = uuid4().hex[:8]
    response = httpx.post(
        f"{BASE_URL}/memories",
        json={
            "kind": "rule",
            "scope": "project",
            "namespace": "smoke-test",
            "title": f"Smoke Test {suffix}",
            "content": f"Persistent memory verification payload {suffix}",
            "tags": ["smoke", "persistence"],
            "source": {"type": "manual"},
            "confidence": 0.9,
            "metadata": {"test_run": suffix},
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()


def fetch_memory(memory_id: str) -> dict:
    response = httpx.get(f"{BASE_URL}/memories/{memory_id}", timeout=10.0)
    response.raise_for_status()
    return response.json()


def search_memory(query: str) -> list[dict]:
    response = httpx.post(
        f"{BASE_URL}/memories/search",
        json={"query": query, "namespace": "smoke-test", "scope": "project"},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()["results"]


def main() -> int:
    wait_until_ready()
    created = create_memory()
    fetched_before = fetch_memory(created["id"])
    if fetched_before["id"] != created["id"]:
        raise RuntimeError("fetch before restart did not return the created memory")

    search_results = search_memory(created["title"])
    if not any(item["id"] == created["id"] for item in search_results):
        raise RuntimeError("search before restart did not return the created memory")

    restart_stack()
    wait_until_ready()

    fetched_after = fetch_memory(created["id"])
    if fetched_after["content"] != created["content"]:
        raise RuntimeError("memory content changed after restart")

    summary = {
        "memory_id": created["id"],
        "title": created["title"],
        "ready_url": f"{BASE_URL}/readyz",
        "status": "ok",
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"smoke test failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
