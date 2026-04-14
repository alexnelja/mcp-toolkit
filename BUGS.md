# Known Bugs — MCP Toolkit

Last reviewed: 2026-04-14

## Shipped tool code (server.py)

- None identified. All 14 `@mcp.tool()` functions have explicit not-found branches and use `errors="replace"` on file reads.

## Deployment / infrastructure

- **`SUPERPOWERS` set built at import time** (`server.py:311`). If `skills/` is missing or empty, the module fails to import before FastMCP can surface a useful error. Low priority — repo ships with 31 skills.
- **`start.sh` hardcoded Python path**: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`. Breaks on any other machine. Replace with a venv or `$(command -v python3)`.
- **`start.sh` tunnel-URL race**: fixed `sleep 8` then greps `/tmp/mcp-toolkit-tunnel.log` for a `trycloudflare.com` URL. On slow startups `TUNNEL_URL` ends up empty and the printed integration URL is `https:///mcp`.
- **Public tunnel has no auth**. Anyone with the `trycloudflare.com` URL can call every tool.

## Not bugs (intentional)

- `TODO` markers in `commands/skills/scripts/init_skill.py` and `commands/skills/scripts/quick_validate.py` are template placeholders used by the skill-builder to scaffold new skills. `quick_validate.py` actively flags excess TODOs in generated skills; this is a feature.
