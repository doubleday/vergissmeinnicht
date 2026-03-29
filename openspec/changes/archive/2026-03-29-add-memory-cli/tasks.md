## 1. CLI Surface

- [x] 1.1 Add a thin typed CLI module inside the installed package with one command per public memory endpoint: create, search, get, and archive.
- [x] 1.2 Add the narrow command configuration and failure surface needed for base URL selection, timeout control, structured stdout output, and predictable non-zero exits.

## 2. Verification And Documentation

- [x] 2.1 Add tests covering CLI argument parsing, typed request construction through the shared client, success output, and failure presentation without requiring new backend behavior.
- [x] 2.2 Document the CLI as the manual inspection and debugging adapter that follows the shared Python client and remains separate from MCP.
