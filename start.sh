#!/bin/bash
# Start MCP Toolkit server with Cloudflare tunnel for claude.ai access
# Usage: ./start.sh [--no-tunnel]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=8100
PYTHON="/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"

# Kill any existing instances
kill $(lsof -ti:$PORT) 2>/dev/null || true
sleep 1

echo "Starting MCP Toolkit server on port $PORT..."
cd "$SCRIPT_DIR"
$PYTHON -m fastmcp run server.py -t streamable-http --host 0.0.0.0 --port $PORT &
SERVER_PID=$!
sleep 3

echo "Server running (PID $SERVER_PID)"
echo "  Local:  http://localhost:$PORT/mcp"

if [ "$1" != "--no-tunnel" ]; then
    echo ""
    echo "Starting Cloudflare tunnel..."
    cloudflared tunnel --url http://localhost:$PORT 2>&1 | tee /tmp/mcp-toolkit-tunnel.log &
    TUNNEL_PID=$!
    sleep 8

    TUNNEL_URL=$(grep -o 'https://[^ ]*trycloudflare.com' /tmp/mcp-toolkit-tunnel.log | head -1)
    echo ""
    echo "============================================"
    echo "MCP Toolkit is live!"
    echo "============================================"
    echo ""
    echo "Claude Desktop: configured (restart Desktop app)"
    echo "Claude Code:    claude mcp add mcp-toolkit -- python3 -m fastmcp run $SCRIPT_DIR/server.py"
    echo ""
    echo "claude.ai URL:  ${TUNNEL_URL}/mcp"
    echo ""
    echo "Add as MCP integration in claude.ai:"
    echo "  Settings > Integrations > Add > Custom MCP"
    echo "  URL: ${TUNNEL_URL}/mcp"
    echo ""
    echo "Press Ctrl+C to stop all servers"

    trap "kill $SERVER_PID $TUNNEL_PID 2>/dev/null; exit 0" INT TERM
    wait
else
    echo ""
    echo "No tunnel. Server available locally only."
    echo "Press Ctrl+C to stop"
    trap "kill $SERVER_PID 2>/dev/null; exit 0" INT TERM
    wait
fi
