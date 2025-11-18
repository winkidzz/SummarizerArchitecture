#!/bin/bash
# Stop the RAG API Server

# Load port configuration
if [ -f .ports ]; then
    source .ports
    export API_PORT=${API_PORT:-8000}
else
    export API_PORT=8000
fi

echo "🛑 Stopping RAG API Server on port ${API_PORT}..."

# Kill processes using the API port
if lsof -ti:${API_PORT} > /dev/null 2>&1; then
    echo "  Killing process on port ${API_PORT}..."
    lsof -ti:${API_PORT} | xargs kill -9
    sleep 1
    echo "✅ Server stopped"
else
    echo "  No server running on port ${API_PORT}"
fi

# Also kill by process name
if pgrep -f "api_server.py" > /dev/null; then
    echo "  Killing api_server.py processes..."
    pkill -f "api_server.py"
    sleep 1
    echo "✅ All api_server.py processes stopped"
fi

echo "✅ Done"
