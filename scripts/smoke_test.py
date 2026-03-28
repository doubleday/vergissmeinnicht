from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from uuid import uuid4

import httpx

from memory_api.client import MemoryApiClient
from memory_api.models import MemoryCreate, MemorySearchRequest, Source


BASE_URL = os.environ.get("MEMORY_API_BASE_URL", "http://127.0.0.1:8000")
DEFAULT_RESTART_COMMAND = os.environ.get("MEMORY_API_RESTART_COMMAND", "docker compose restart memory-api")


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


def restart_stack(command: str) -> None:
    subprocess.run(shlex.split(command), check=True)


def create_memory() -> dict:
    suffix = uuid4().hex[:8]
    with MemoryApiClient(base_url=BASE_URL) as client:
        created = client.create_memory(
            MemoryCreate(
                kind="rule",
                scope="project",
                namespace="smoke-test",
                title=f"Smoke Test {suffix}",
                content=f"Persistent memory verification payload {suffix}",
                tags=["smoke", "persistence"],
                source=Source(type="manual"),
                confidence=0.9,
                metadata={"test_run": suffix},
            )
        )
    return created.model_dump(mode="json", exclude_none=True)


def fetch_memory(memory_id: str) -> dict:
    with MemoryApiClient(base_url=BASE_URL) as client:
        memory = client.get_memory(memory_id)
    return memory.model_dump(mode="json", exclude_none=True)


def search_memory(query: str) -> list[dict]:
    with MemoryApiClient(base_url=BASE_URL) as client:
        response = client.search_memories(
            MemorySearchRequest(query=query, namespace="smoke-test", scope="project")
        )
    return [result.model_dump(mode="json", exclude_none=True) for result in response.results]


def ensure_memory_visible(memory: dict) -> None:
    fetched_memory = fetch_memory(memory["id"])
    if fetched_memory["id"] != memory["id"]:
        raise RuntimeError("fetch did not return the expected memory")

    search_results = search_memory(memory["content"])
    if not any(item["id"] == memory["id"] for item in search_results):
        raise RuntimeError("search did not return the expected memory")


def prepare_restart_verification() -> dict:
    wait_until_ready()
    created = create_memory()
    ensure_memory_visible(created)
    return {
        "memory_id": created["id"],
        "title": created["title"],
        "content": created["content"],
        "ready_url": f"{BASE_URL}/readyz",
        "status": "prepared",
    }


def verify_restart(memory_id: str, expected_title: str, expected_content: str) -> dict:
    wait_until_ready()
    fetched_after = fetch_memory(memory_id)
    if fetched_after["title"] != expected_title:
        raise RuntimeError(
            "memory title changed after restart: "
            f"expected {expected_title!r}, got {fetched_after['title']!r}"
        )
    if fetched_after["content"] != expected_content:
        raise RuntimeError(
            "memory content changed after restart: "
            f"expected {expected_content!r}, got {fetched_after['content']!r}"
        )

    search_results = search_memory(expected_content)
    if not any(item["id"] == memory_id for item in search_results):
        raise RuntimeError("search after restart did not return the created memory")

    return {
        "memory_id": memory_id,
        "title": expected_title,
        "ready_url": f"{BASE_URL}/readyz",
        "status": "ok",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify the live memory API stack.")
    parser.add_argument(
        "--mode",
        choices=("full", "prepare", "verify"),
        default="full",
        help="Verification mode to run.",
    )
    parser.add_argument(
        "--restart-command",
        default=DEFAULT_RESTART_COMMAND,
        help="Command used for restart during full-mode verification.",
    )
    parser.add_argument("--memory-id", help="Existing memory id to verify after restart.")
    parser.add_argument("--expected-title", help="Expected title for verify mode.")
    parser.add_argument("--expected-content", help="Expected content for verify mode.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.mode == "prepare":
        print(json.dumps(prepare_restart_verification()))
        return 0

    if args.mode == "verify":
        if not args.memory_id or not args.expected_title or not args.expected_content:
            raise RuntimeError("verify mode requires --memory-id, --expected-title, and --expected-content")
        print(json.dumps(verify_restart(args.memory_id, args.expected_title, args.expected_content)))
        return 0

    prepared = prepare_restart_verification()
    restart_stack(args.restart_command)
    print(
        json.dumps(
            verify_restart(
                prepared["memory_id"],
                prepared["title"],
                prepared["content"],
            )
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"smoke test failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
