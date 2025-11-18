#!/bin/bash
# Start the RAG API Server with standardized port configuration

# Load port configuration
if [ -f .ports ]; then
    source .ports
    export API_PORT=${API_PORT:-8000}
else
    export API_PORT=8000
fi

# Activate virtual environment
if [ -d venv ]; then
    source venv/bin/activate
else
    echo "Error: venv directory not found. Please create a virtual environment first."
    exit 1
fi

# Check if port is available
if lsof -ti:${API_PORT} > /dev/null 2>&1; then
    echo "⚠️  Port ${API_PORT} is already in use. Attempting to free it..."
    lsof -ti:${API_PORT} | xargs kill -9 2>/dev/null
    sleep 1
fi

# Start the server
echo "🚀 Starting RAG API Server on port ${API_PORT}..."
python src/api_server.py

