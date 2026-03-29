from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from pydantic import ValidationError

from memory_api.client import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    MemoryApiClient,
    MemoryApiResponseError,
    MemoryApiTransportError,
)
from memory_api.models import MemoryCreate, MemorySearchRequest, Source


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interact with the memory API.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Base URL for the memory API.",
    )
    common.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="Request timeout in seconds.",
    )

    create = subparsers.add_parser("create", parents=[common], help="Create a memory.")
    create.add_argument("--kind", required=True)
    create.add_argument("--scope", required=True)
    create.add_argument("--namespace", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--content", required=True)
    create.add_argument("--supersedes-memory-id")
    create.add_argument("--tag", action="append", default=[])
    create.add_argument("--source-type", required=True)
    create.add_argument("--source-name")
    create.add_argument("--confidence", type=float, default=0.5)
    create.add_argument(
        "--metadata-json",
        default="{}",
        help="JSON object for metadata.",
    )
    create.set_defaults(handler=_handle_create)

    search = subparsers.add_parser("search", parents=[common], help="Search memories.")
    search.add_argument("--query")
    search.add_argument("--namespace")
    search.add_argument("--scope")
    search.add_argument("--kind")
    search.add_argument("--tag", action="append", default=[])
    search.add_argument("--include-archived", action="store_true")
    search.add_argument("--exclude-superseded", action="store_true")
    search.add_argument("--limit", type=int, default=10)
    search.set_defaults(handler=_handle_search)

    get_parser = subparsers.add_parser("get", parents=[common], help="Fetch a memory by id.")
    get_parser.add_argument("memory_id")
    get_parser.set_defaults(handler=_handle_get)

    archive = subparsers.add_parser("archive", parents=[common], help="Archive a memory by id.")
    archive.add_argument("memory_id")
    archive.set_defaults(handler=_handle_archive)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.handler(args)
    except ValidationError as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 2
    except MemoryApiResponseError as exc:
        print(f"api error [{exc.status_code}]: {exc}", file=sys.stderr)
        return 1
    except MemoryApiTransportError as exc:
        print(f"transport error: {exc}", file=sys.stderr)
        return 1


def _handle_create(args: argparse.Namespace) -> int:
    metadata = _parse_metadata_json(args.metadata_json)
    payload = MemoryCreate(
        kind=args.kind,
        scope=args.scope,
        namespace=args.namespace,
        title=args.title,
        content=args.content,
        supersedes_memory_id=args.supersedes_memory_id,
        tags=args.tag,
        source=Source(type=args.source_type, name=args.source_name),
        confidence=args.confidence,
        metadata=metadata,
    )
    with _build_client(args) as client:
        created = client.create_memory(payload)
    _print_json(created.model_dump(mode="json", exclude_none=True))
    return 0


def _handle_search(args: argparse.Namespace) -> int:
    payload = MemorySearchRequest(
        query=args.query,
        namespace=args.namespace,
        scope=args.scope,
        kind=args.kind,
        tags=args.tag,
        include_archived=args.include_archived,
        exclude_superseded=args.exclude_superseded,
        limit=args.limit,
    )
    with _build_client(args) as client:
        response = client.search_memories(payload)
    _print_json(response.model_dump(mode="json", exclude_none=True))
    return 0


def _handle_get(args: argparse.Namespace) -> int:
    with _build_client(args) as client:
        record = client.get_memory(args.memory_id)
    _print_json(record.model_dump(mode="json", exclude_none=True))
    return 0


def _handle_archive(args: argparse.Namespace) -> int:
    with _build_client(args) as client:
        record = client.archive_memory(args.memory_id)
    _print_json(record.model_dump(mode="json", exclude_none=True))
    return 0


def _build_client(args: argparse.Namespace) -> MemoryApiClient:
    return MemoryApiClient(base_url=args.base_url, timeout=args.timeout)


def _parse_metadata_json(raw_metadata: str) -> dict[str, Any]:
    try:
        metadata = json.loads(raw_metadata)
    except json.JSONDecodeError as exc:
        raise ValueError(f"metadata-json must be valid JSON: {exc.msg}") from exc
    if not isinstance(metadata, dict):
        raise ValueError("metadata-json must decode to an object")
    return metadata


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
