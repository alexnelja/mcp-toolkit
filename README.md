# MCP Toolkit

Unified MCP server combining three powerful AI development toolkits:

- **UI/UX Pro Max** — Design intelligence: 50+ styles, 161 color palettes, 57 font pairings, 99 UX guidelines
- **Claude Command Suite** — 216+ slash commands and 120+ AI agents for dev, test, deploy, security
- **Superpowers** — Composable development skills: TDD, debugging, brainstorming, code review, planning

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run for Claude Desktop (stdio)
fastmcp run server.py

# Run for claude.ai (SSE with tunnel)
fastmcp run server.py -t sse --port 8100
```

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-toolkit": {
      "command": "python3",
      "args": ["-m", "fastmcp", "run", "/path/to/mcp-toolkit/server.py"]
    }
  }
}
```

## Claude Code

```bash
claude mcp add mcp-toolkit -- python3 -m fastmcp run /path/to/server.py
```

## Available Tools

| Tool | Description |
|------|-------------|
| `uiux_search` | Search styles, colors, typography, UX patterns |
| `uiux_design_system` | Generate complete design system |
| `uiux_stack_guidelines` | Stack-specific UI/UX guidelines |
| `uiux_list_domains` | List all searchable domains |
| `list_commands` | Browse 216+ slash commands by namespace |
| `get_command` | Get full command content |
| `search_commands` | Search commands and agents |
| `list_agents` | Browse 120+ AI agents |
| `get_agent` | Get agent definition |
| `list_skills` | List Superpowers skills |
| `get_skill` | Get skill methodology |
| `search_skills` | Search skills by keyword |
| `get_workflow` | Get multi-skill workflows |
