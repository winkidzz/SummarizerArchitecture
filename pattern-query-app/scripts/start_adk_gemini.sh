#!/bin/bash
# Start Google ADK with Gemini agent
# Loads configuration from .env file

set -e

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "========================================"
echo "Starting Google ADK with Gemini Agent"
echo "========================================"
echo "Project root: $PROJECT_ROOT"
echo ""

# Load environment variables from .env
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "Loading environment variables from .env..."
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
    echo "✓ Loaded configuration"
else
    echo "⚠️  Warning: .env file not found at $PROJECT_ROOT/.env"
    echo "   Using default configuration"
fi

# Verify GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY not set in .env file"
    echo "   Please add your Gemini API key to .env"
    echo "   Get your key from: https://aistudio.google.com/app/apikey"
    exit 1
fi

# Use GEMINI_MODEL from .env or default
GEMINI_MODEL="${GEMINI_MODEL:-gemini-2.0-flash-exp}"
ADK_MODEL="${ADK_MODEL:-$GEMINI_MODEL}"

echo ""
echo "Configuration:"
echo "  Model: $ADK_MODEL"
echo "  API Key: ${GEMINI_API_KEY:0:10}...${GEMINI_API_KEY: -4}"
echo "  Agents directory: $PROJECT_ROOT/.adk/agents"
echo "  Available agents: gemini_agent (active), ollama_agent"
echo ""

# Set environment variables for ADK
export ADK_MODEL="$ADK_MODEL"
export GOOGLE_API_KEY="$GEMINI_API_KEY"  # ADK uses GOOGLE_API_KEY

# Navigate to project root
cd "$PROJECT_ROOT"

# Start ADK web server
echo "Starting ADK web server..."
echo "Access the UI at: http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Use venv312 python
# Point to .adk/agents directory to discover all agents (gemini_agent and ollama_agent)
../venv312/bin/adk web \
    --host=127.0.0.1 \
    --port=8000 \
    --allow_origins="*" \
    .adk/agents
