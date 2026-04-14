# MCP Toolkit

## Overview

A unified Python MCP (Model Context Protocol) server built on FastMCP that exposes three integrated toolkits to Claude Desktop, Claude Code, and claude.ai: **UI/UX Pro Max** design intelligence, **Claude Command Suite** (slash commands + AI agents), and **Superpowers** development skills. One server, one config, 14 tools spanning design-system generation, stack-specific UI guidelines, browsable command/agent libraries, and composable development skills (TDD, debugging, code review, planning).

## Status

**Working** — server runs via stdio, SSE, or streamable-HTTP; `start.sh` publishes it through a Cloudflare tunnel for claude.ai integration.

**14 tools exposed:**

| Group | Tools |
|-------|-------|
| UI/UX Pro Max | `uiux_search`, `uiux_design_system`, `uiux_stack_guidelines`, `uiux_list_domains` |
| Command Suite | `list_commands`, `get_command`, `search_commands`, `list_agents`, `get_agent` |
| Superpowers | `list_skills`, `get_skill`, `get_skill_file`, `search_skills`, `get_workflow` |

**Content inventory:**
- Commands: 26 namespaces (dev, test, deploy, security, project, rust, svelte, simulation, docs, team, performance, memory, reasoning, wfgy, etc.)
- Agents: 40+ specialized agents (code-auditor, test-engineer, release-manager, svelte-*, swift-macos-expert, wfgy, skill-builder, data-ai, infrastructure, …)
- Skills: 31 Superpowers SKILL.md folders (brainstorming, systematic-debugging, test-driven-development, writing-plans, frontend-design, mcp-builder, webapp-testing, …)
- UI/UX data: CSVs for styles, 161 color palettes, typography pairings, charts, product types, UX guidelines, React/web patterns, Google Fonts, prompt templates — plus `react-native` stack guidelines

## Setup & Run

```bash
# Install (only FastMCP required)
pip install -r requirements.txt
```

### Claude Desktop (stdio)

```bash
fastmcp run server.py
```

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-toolkit": {
      "command": "python3",
      "args": ["-m", "fastmcp", "run", "/absolute/path/to/mcp-toolkit/server.py"]
    }
  }
}
```

### Claude Code

```bash
claude mcp add mcp-toolkit -- python3 -m fastmcp run /absolute/path/to/server.py
```

### claude.ai (remote via Cloudflare tunnel)

```bash
./start.sh              # server on :8100 + cloudflared tunnel (prints trycloudflare.com URL)
./start.sh --no-tunnel  # local-only
```

Then in claude.ai: Settings → Integrations → Add Custom MCP → paste the `https://…trycloudflare.com/mcp` URL.

Manual alternative: `fastmcp run server.py -t sse --port 8100` or `-t streamable-http`.

## Architecture

```
mcp-toolkit/
├── server.py          # FastMCP server, 14 @mcp.tool() definitions (UIUX / Commands / Skills)
├── start.sh           # Boots streamable-http server + Cloudflare tunnel, prints public URL
├── requirements.txt   # fastmcp>=3.0.0
├── agents/            # 40+ agent .md files (flat + subdirs: development, security, business, …)
├── commands/          # 26 namespaces of slash-command .md files (dev, test, deploy, rust, svelte, …)
├── skills/            # 31 Superpowers skills, each a folder with SKILL.md + supporting files
├── uiux_data/         # CSVs: styles, colors, typography, charts, products, UX, stacks
└── uiux_scripts/      # core.py, design_system.py, search.py — imported by server.py
```

**Wiring note:** `server.py` patches `sys.path` and `core.DATA_DIR` so the bundled `uiux_scripts/` modules resolve `uiux_data/` regardless of cwd.

**Tool surface:**
- `uiux_search(query, domain, max_results)` — 12 domains auto-detected
- `uiux_design_system(query, project_name)` — full design-system markdown (colors/typography/spacing/components)
- `uiux_stack_guidelines(query, stack)` — currently `react-native`
- `list_commands` / `get_command` / `search_commands` — walk `commands/<ns>/*.md`
- `list_agents` / `get_agent` — walk `agents/**/*.md`, parse frontmatter `description:`
- `list_skills` / `get_skill` / `get_skill_file` / `search_skills` — walk `skills/*/SKILL.md`
- `get_workflow(workflow)` — curated multi-skill recipes for `feature | bugfix | refactor | review`

## Roadmap

- [ ] Expand `uiux_stack_guidelines` beyond `react-native` (React, Next.js, Vue, Svelte, SwiftUI, Flutter, Tailwind, shadcn/ui, HTML/CSS)
- [ ] Cache `_get_agents()` / `_get_namespaces()` / `SUPERPOWERS` walks — currently re-scan disk on every tool call
- [ ] Make `SUPERPOWERS` set construction lazy; it runs at import time and will crash if `skills/` is ever missing
- [ ] Replace hardcoded Python path in `start.sh` (`/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`) with a venv or `$(command -v python3)`
- [ ] Auth / access control for the public Cloudflare tunnel endpoint
- [ ] Health check + reconnect logic in `start.sh` (currently fixed `sleep 8` for tunnel URL parse)
- [ ] Add MCP resources (not just tools) for large static content — design-system CSVs, agent/skill catalogs
- [ ] Tests — no test suite exists yet

## Known Bugs

- None identified in shipped tool code. (TODO markers found in `commands/skills/scripts/init_skill.py` and `quick_validate.py` are intentional template scaffolding for the skill-builder, not defects.)
- Minor: `SUPERPOWERS = {…}` at module top-level will raise `FileNotFoundError` if `skills/` is absent — deployment-time concern only.
- Minor: `start.sh` parses the tunnel URL after a fixed 8-second sleep; slow cloudflared startups may leave `TUNNEL_URL` empty.
