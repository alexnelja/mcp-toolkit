# Roadmap — MCP Toolkit

## Near-term

- [ ] **More stacks in `uiux_stack_guidelines`** — currently only `react-native`. Add React, Next.js, Vue, Svelte, SwiftUI, Flutter, Tailwind, shadcn/ui, HTML/CSS (data already implied by the UI/UX Pro Max skill description).
- [ ] **Cache directory walks** — `_get_namespaces`, `_get_agents`, and `_skill_info` re-read the filesystem on every tool invocation. Memoize at startup; invalidate on file-mtime change.
- [ ] **Fix `start.sh` portability** — replace hardcoded `/Library/Frameworks/Python.framework/…` with venv activation or `$(command -v python3)`.
- [ ] **Tunnel-URL robustness** — poll cloudflared log until URL appears (with timeout) instead of fixed `sleep 8`.

## Medium-term

- [ ] **Auth for remote tunnel** — bearer token or basic auth in front of the FastMCP streamable-http endpoint before exposing via `trycloudflare.com`.
- [ ] **MCP resources (not just tools)** — expose the agent catalog, skill catalog, and UI/UX CSVs as resources so clients can subscribe/list without wrapping everything in tool calls.
- [ ] **Lazy skill loading** — don't build `SUPERPOWERS` at import time.
- [ ] **Workflow expansion** — `get_workflow` currently ships 4 recipes (feature/bugfix/refactor/review). Add: architecture-review, incident-response, release, migration, onboarding.
- [ ] **Test suite** — no tests exist. Add pytest coverage for each `@mcp.tool()` happy-path + not-found branches, plus golden-file tests for `uiux_design_system` output.

## Longer-term

- [ ] **Multi-user / remote deployment** — persistent host (not local cloudflared) with per-user API keys.
- [ ] **Agent / skill versioning** — pin known-good revisions, show diffs when the upstream Command-Suite or Superpowers repos update.
- [ ] **Write-side tools** — scaffold new skills / commands / agents from within the MCP session (reuse `commands/skills/scripts/init_skill.py`).
- [ ] **Telemetry** — which tools, domains, skills, and namespaces are actually used; prune dead content.

## Not planned

- Rewriting in TypeScript. Python + FastMCP is the stated stack.
