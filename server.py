#!/usr/bin/env python3
"""
MCP Toolkit Server — Unified MCP server combining:
  - UI/UX Pro Max (design intelligence)
  - Claude Command Suite (216+ dev commands, 120+ agents)
  - Superpowers (composable development skills)

Run:
  fastmcp run server.py                          # stdio (Claude Desktop / Claude Code)
  fastmcp run server.py -t sse --port 8100       # SSE (claude.ai via tunnel)
  fastmcp run server.py -t streamable-http --port 8100  # Streamable HTTP
"""

import sys
from pathlib import Path

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Paths — resolve relative to this file so it works from any cwd
# ---------------------------------------------------------------------------
BASE = Path(__file__).resolve().parent
UIUX_SCRIPTS = BASE / "uiux_scripts"
UIUX_DATA = BASE / "uiux_data"
COMMANDS_DIR = BASE / "commands"
AGENTS_DIR = BASE / "agents"
SKILLS_DIR = BASE / "skills"

# Patch the UI/UX scripts so core.py finds the data directory here
sys.path.insert(0, str(UIUX_SCRIPTS))

# Patch DATA_DIR in core before design_system imports it
import core as _core
_core.DATA_DIR = UIUX_DATA

# Now import design_system — it will pick up the patched DATA_DIR from core
import design_system as _ds
# Also patch design_system's own reference (it does `from core import DATA_DIR`)
_ds.DATA_DIR = UIUX_DATA

from core import CSV_CONFIG, AVAILABLE_STACKS, search, search_stack
from design_system import generate_design_system

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "MCP Toolkit",
    instructions=(
        "Unified toolkit: UI/UX Pro Max design intelligence, "
        "Claude Command Suite (216+ commands, 120+ agents), "
        "and Superpowers development skills."
    ),
)

DOMAINS = list(CSV_CONFIG.keys())

# ===== UI/UX Pro Max Tools =================================================

@mcp.tool()
def uiux_search(query: str, domain: str = "", max_results: int = 5) -> str:
    """Search the UI/UX Pro Max design database for styles, colors, typography, UX patterns, and more.

    Args:
        query: Search query (e.g. "glassmorphism", "dark mode dashboard", "e-commerce checkout")
        domain: Domain to search. Options: style, color, chart, landing, product, ux, typography,
                icons, react, web, google-fonts, prompt. Leave empty for auto-detect.
        max_results: Number of results (default 5)
    """
    result = search(query, domain=domain or None, max_results=max_results)
    if "error" in result:
        return f"Error: {result['error']}"
    lines = [f"## UI/UX Pro Max — {result.get('domain', 'auto')} results for '{result['query']}'",
             f"**Source:** {result['file']} | **Found:** {result['count']} results\n"]
    for i, row in enumerate(result["results"], 1):
        lines.append(f"### Result {i}")
        for k, v in row.items():
            val = str(v)[:500]
            lines.append(f"- **{k}:** {val}")
        lines.append("")
    return "\n".join(lines)


@mcp.tool()
def uiux_design_system(query: str, project_name: str = "") -> str:
    """Generate a complete design system (colors, typography, spacing, components, guidelines).

    Args:
        query: Project description (e.g. "SaaS analytics dashboard", "luxury e-commerce store")
        project_name: Optional project name
    """
    return generate_design_system(query, project_name=project_name or None,
                                  output_format="markdown", persist=False)


@mcp.tool()
def uiux_stack_guidelines(query: str, stack: str = "react-native", max_results: int = 5) -> str:
    """Search stack-specific UI/UX guidelines (do/don't patterns, code examples).

    Args:
        query: Search query (e.g. "navigation patterns", "list performance")
        stack: Tech stack (currently: react-native)
        max_results: Number of results (default 5)
    """
    result = search_stack(query, stack=stack, max_results=max_results)
    if "error" in result:
        return f"Error: {result['error']}"
    lines = [f"## Stack: {result.get('stack', stack)} — '{result['query']}'",
             f"**Found:** {result['count']} results\n"]
    for i, row in enumerate(result["results"], 1):
        lines.append(f"### Result {i}")
        for k, v in row.items():
            lines.append(f"- **{k}:** {str(v)[:500]}")
        lines.append("")
    return "\n".join(lines)


@mcp.tool()
def uiux_list_domains() -> str:
    """List all searchable UI/UX domains and available stacks."""
    info = {
        "style": "UI styles (glassmorphism, minimalism, brutalism) + CSS keywords",
        "color": "Color palettes by product type with hex values",
        "typography": "Font pairings with Google Fonts imports",
        "product": "Product type recommendations (SaaS, e-commerce, portfolio)",
        "landing": "Page structure and CTA strategies",
        "chart": "Chart types and library recommendations",
        "ux": "UX best practices and anti-patterns",
        "icons": "Icon library recommendations",
        "react": "React component patterns",
        "web": "Web design patterns",
        "google-fonts": "Google Fonts search and pairing",
        "prompt": "AI prompt templates for UI generation",
    }
    lines = ["## UI/UX Pro Max — Domains\n"]
    for d, desc in info.items():
        tag = "✓" if d in DOMAINS else "✗"
        lines.append(f"- [{tag}] **{d}**: {desc}")
    lines.append(f"\n## Stacks: {', '.join(AVAILABLE_STACKS) or '(none)'}")
    return "\n".join(lines)


# ===== Command Suite Tools ==================================================

def _get_namespaces() -> dict[str, list[str]]:
    ns = {}
    if not COMMANDS_DIR.exists():
        return ns
    for item in sorted(COMMANDS_DIR.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            cmds = [str(md.relative_to(COMMANDS_DIR)).replace("/", ":").removesuffix(".md")
                    for md in sorted(item.rglob("*.md")) if md.name != "README.md"]
            if cmds:
                ns[item.name] = cmds
    return ns


def _get_agents() -> list[dict]:
    agents = []
    if not AGENTS_DIR.exists():
        return agents
    skip = {"README.md", "ATTRIBUTION.md", "WORKFLOW_EXAMPLES.md", "TASK-STATUS-PROTOCOL.md"}
    for md in sorted(AGENTS_DIR.rglob("*.md")):
        if md.name in skip:
            continue
        content = md.read_text(errors="replace")
        desc = ""
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                for line in content[3:end].split("\n"):
                    if line.strip().startswith("description:"):
                        desc = line.split(":", 1)[1].strip().strip('"\'')
                        break
        if not desc:
            for line in content.split("\n"):
                l = line.strip()
                if l and not l.startswith("#") and not l.startswith("---"):
                    desc = l[:150]
                    break
        agents.append({"name": str(md.relative_to(AGENTS_DIR)).removesuffix(".md"),
                       "description": desc})
    return agents


@mcp.tool()
def list_commands(namespace: str = "") -> str:
    """List Claude Command Suite slash commands. Filter by namespace or see all.

    Args:
        namespace: Filter (e.g. "dev", "test", "deploy", "security", "project"). Empty = show all.
    """
    namespaces = _get_namespaces()
    if namespace:
        ns = namespace.lower()
        if ns not in namespaces:
            return f"Namespace '{ns}' not found. Available: {', '.join(sorted(namespaces))}"
        lines = [f"## /{ns} commands\n"]
        for cmd in namespaces[ns]:
            lines.append(f"- `/{cmd}`")
        return "\n".join(lines)
    lines = ["## Command Suite — All Namespaces\n"]
    total = 0
    for ns, cmds in sorted(namespaces.items()):
        lines.append(f"- **{ns}** — {len(cmds)} commands")
        total += len(cmds)
    lines.append(f"\n**Total: {total} commands**\nUse `list_commands(namespace='dev')` to drill in.")
    return "\n".join(lines)


@mcp.tool()
def get_command(command_name: str) -> str:
    """Get the full content/prompt of a slash command.

    Args:
        command_name: e.g. "dev:code-review", "test:write-tests", "deploy:prepare-release"
    """
    name = command_name.lstrip("/")
    path = COMMANDS_DIR / (name.replace(":", "/") + ".md")
    if not path.exists():
        path = COMMANDS_DIR / (name + ".md")
    if not path.exists():
        return f"Command '{command_name}' not found. Use list_commands() or search_commands()."
    return f"## /{name}\n\n{path.read_text(errors='replace')}"


@mcp.tool()
def search_commands(query: str) -> str:
    """Search across all commands and agents by keyword.

    Args:
        query: e.g. "debug", "security audit", "deployment", "test coverage"
    """
    q = query.lower()
    results = []
    if COMMANDS_DIR.exists():
        for md in COMMANDS_DIR.rglob("*.md"):
            if md.name == "README.md":
                continue
            name = str(md.relative_to(COMMANDS_DIR)).replace("/", ":").removesuffix(".md")
            content = md.read_text(errors="replace")
            if q in name.lower() or q in content.lower():
                desc = ""
                for line in content.split("\n"):
                    l = line.strip()
                    if l and not l.startswith("#") and not l.startswith("---"):
                        desc = l[:150]; break
                results.append(("cmd", name, desc))
    for a in _get_agents():
        if q in a["name"].lower() or q in a["description"].lower():
            results.append(("agent", a["name"], a["description"]))
    if not results:
        return f"No results for '{query}'."
    lines = [f"## Search: '{query}' — {len(results)} matches\n"]
    cmds = [r for r in results if r[0] == "cmd"]
    if cmds:
        lines.append(f"### Commands ({len(cmds)})")
        for _, n, d in cmds[:25]:
            lines.append(f"- `/{n}` — {d}")
        if len(cmds) > 25:
            lines.append(f"  _+{len(cmds)-25} more_")
    ags = [r for r in results if r[0] == "agent"]
    if ags:
        lines.append(f"\n### Agents ({len(ags)})")
        for _, n, d in ags[:25]:
            lines.append(f"- **{n}** — {d}")
    return "\n".join(lines)


@mcp.tool()
def list_agents(category: str = "") -> str:
    """List AI agents. Optionally filter by category.

    Args:
        category: e.g. "development", "security", "business", "quality-testing". Empty = all.
    """
    agents = _get_agents()
    if category:
        filtered = [a for a in agents if category.lower() in a["name"].lower()]
        if not filtered:
            return f"No agents in '{category}'. Use list_agents() for all."
        lines = [f"## Agents: {category} ({len(filtered)})\n"]
        for a in filtered:
            lines.append(f"- **{a['name']}** — {a['description']}")
        return "\n".join(lines)
    lines = [f"## All Agents ({len(agents)})\n"]
    for a in agents:
        lines.append(f"- **{a['name']}** — {a['description']}")
    return "\n".join(lines)


@mcp.tool()
def get_agent(agent_name: str) -> str:
    """Get full agent definition (role, expertise, constraints).

    Args:
        agent_name: e.g. "code-auditor", "development/frontend-developer", "release-manager"
    """
    path = AGENTS_DIR / (agent_name + ".md")
    if not path.exists():
        for md in AGENTS_DIR.rglob("*.md"):
            if md.stem == agent_name or str(md.relative_to(AGENTS_DIR)).removesuffix(".md") == agent_name:
                path = md; break
    if not path.exists():
        return f"Agent '{agent_name}' not found. Use list_agents()."
    return f"## Agent: {agent_name}\n\n{path.read_text(errors='replace')}"


# ===== Superpowers Tools ====================================================

SUPERPOWERS = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()}


def _skill_info(name: str) -> dict | None:
    skill_md = SKILLS_DIR / name / "SKILL.md"
    if not skill_md.exists():
        return None
    content = skill_md.read_text(errors="replace")
    info = {"name": name, "description": "", "content": content}
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            for line in content[3:end].split("\n"):
                if line.strip().startswith("description:"):
                    info["description"] = line.split(":", 1)[1].strip().strip('"\'')
    info["files"] = [str(f.relative_to(SKILLS_DIR / name))
                     for f in sorted((SKILLS_DIR / name).rglob("*.md")) if f.name != "SKILL.md"]
    return info


@mcp.tool()
def list_skills() -> str:
    """List all Superpowers development skills."""
    lines = ["## Superpowers Skills\n"]
    for name in sorted(SUPERPOWERS):
        info = _skill_info(name)
        if info:
            lines.append(f"- **{name}** — {info['description'][:120] or '(no desc)'}")
    lines.append(f"\n**Total: {len(SUPERPOWERS)} skills**")
    return "\n".join(lines)


@mcp.tool()
def get_skill(skill_name: str) -> str:
    """Get full skill methodology and guidelines.

    Args:
        skill_name: e.g. "systematic-debugging", "brainstorming", "test-driven-development"
    """
    info = _skill_info(skill_name)
    if not info:
        return f"Skill '{skill_name}' not found. Use list_skills()."
    lines = [f"## Skill: {skill_name}"]
    if info["description"]:
        lines.append(f"**Description:** {info['description']}\n")
    lines.append(info["content"])
    if info["files"]:
        lines.append(f"\n---\n### Supporting files: {', '.join(info['files'])}")
    return "\n".join(lines)


@mcp.tool()
def get_skill_file(skill_name: str, file_path: str) -> str:
    """Read a supporting file from a skill (technique docs, templates).

    Args:
        skill_name: e.g. "systematic-debugging"
        file_path: Relative path, e.g. "root-cause-tracing.md"
    """
    full = SKILLS_DIR / skill_name / file_path
    if not full.exists() or not full.is_relative_to(SKILLS_DIR / skill_name):
        return f"File '{file_path}' not found in skill '{skill_name}'."
    return f"## {skill_name}/{file_path}\n\n{full.read_text(errors='replace')}"


@mcp.tool()
def search_skills(query: str) -> str:
    """Search Superpowers skills by keyword.

    Args:
        query: e.g. "debug", "test", "review", "plan", "parallel"
    """
    q = query.lower()
    results = []
    for name in sorted(SUPERPOWERS):
        info = _skill_info(name)
        if not info:
            continue
        if q in name or q in info["description"].lower() or q in info["content"].lower():
            count = info["content"].lower().count(q)
            results.append((name, info["description"], count))
    results.sort(key=lambda x: x[2], reverse=True)
    if not results:
        return f"No skills match '{query}'."
    lines = [f"## Skills matching '{query}' ({len(results)})\n"]
    for n, d, c in results:
        lines.append(f"- **{n}** ({c} mentions) — {d[:120]}")
    return "\n".join(lines)


@mcp.tool()
def get_workflow(workflow: str) -> str:
    """Get a recommended multi-skill workflow.

    Args:
        workflow: "feature" | "bugfix" | "refactor" | "review"
    """
    wfs = {
        "feature": ("Feature Development", [
            ("brainstorming", "Explore requirements and design"),
            ("writing-plans", "Create implementation plan"),
            ("test-driven-development", "Write tests first, then implement"),
            ("requesting-code-review", "Get reviewed"),
            ("verification-before-completion", "Verify everything"),
            ("finishing-a-development-branch", "Merge or PR"),
        ]),
        "bugfix": ("Bug Fix", [
            ("systematic-debugging", "Investigate root cause"),
            ("test-driven-development", "Write regression test, fix"),
            ("verification-before-completion", "Verify fix"),
        ]),
        "refactor": ("Refactoring", [
            ("requesting-code-review", "Review current quality"),
            ("writing-plans", "Plan approach"),
            ("test-driven-development", "Ensure tests exist"),
            ("verification-before-completion", "Verify nothing broke"),
        ]),
        "review": ("Code Review", [
            ("requesting-code-review", "Request structured review"),
            ("receiving-code-review", "Process feedback"),
            ("verification-before-completion", "Verify changes"),
        ]),
    }
    if workflow not in wfs:
        return f"Unknown workflow. Available: {', '.join(wfs)}"
    title, steps = wfs[workflow]
    lines = [f"## Workflow: {title}\n"]
    for i, (skill, desc) in enumerate(steps, 1):
        info = _skill_info(skill)
        lines.append(f"**Step {i}: {desc}**")
        lines.append(f"  Skill: `{skill}` ({'✓' if info else '✗'})")
        if info and info["description"]:
            lines.append(f"  _{info['description'][:150]}_")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
