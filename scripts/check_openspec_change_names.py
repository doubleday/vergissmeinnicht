from __future__ import annotations

import re
import sys
from pathlib import Path


ACTIVE_CHANGES_DIR = Path("openspec/changes")
DATE_PREFIX_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}-")


def main() -> int:
    if not ACTIVE_CHANGES_DIR.exists():
        print(f"missing directory: {ACTIVE_CHANGES_DIR}", file=sys.stderr)
        return 1

    invalid_names: list[str] = []
    for path in sorted(ACTIVE_CHANGES_DIR.iterdir()):
        if not path.is_dir() or path.name == "archive":
            continue
        if DATE_PREFIX_PATTERN.match(path.name):
            invalid_names.append(path.name)

    if not invalid_names:
        print("OpenSpec active change names look valid.")
        return 0

    print("Invalid OpenSpec active change names:", file=sys.stderr)
    for name in invalid_names:
        print(f"- {name}", file=sys.stderr)
    print(
        "Active changes must use plain kebab-case slugs under openspec/changes/. "
        "Date prefixes are reserved for archived changes under openspec/changes/archive/.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
