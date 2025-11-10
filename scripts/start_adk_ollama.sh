#!/usr/bin/env bash
# Launch the Google ADK web UI using local Ollama models.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENTS_DIR="${ROOT_DIR}/.adk/agents"
HOST="${ADK_WEB_HOST:-127.0.0.1}"
PORT="${ADK_WEB_PORT:-8000}"
ALLOW_ORIGINS="${ADK_ALLOW_ORIGINS:-*}"
OLLAMA_MODEL="${OLLAMA_MODEL:-qwen3:14b}"

echo "=========================================="
echo "ADK Web UI with Local Ollama"
echo "=========================================="
echo ""
echo "Configuration:"
echo "  Model: $OLLAMA_MODEL"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Agents: ollama_agent"
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "⚠️  Warning: Ollama server doesn't appear to be running"
  echo ""
  echo "Please start Ollama:"
  echo "  - macOS: Open the Ollama app"
  echo "  - Linux: ollama serve"
  echo ""
  read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
fi

# Check if ADK CLI is available
if ! command -v adk >/dev/null 2>&1; then
  echo "Error: the 'adk' CLI is not on PATH. Install google-adk first." >&2
  exit 1
fi

# Check if ollama_agent exists
if [ ! -d "${AGENTS_DIR}/ollama_agent" ]; then
  echo "Error: ${AGENTS_DIR}/ollama_agent does not exist." >&2
  echo "The agent should have been created. Please check the .adk/agents directory." >&2
  exit 1
fi

echo "Starting ADK web UI on ${HOST}:${PORT}"
echo "Using Ollama model: ${OLLAMA_MODEL}"
echo ""
echo "Web UI will be available at: http://${HOST}:${PORT}"
echo "Press Ctrl+C to stop."
echo ""

cd "${ROOT_DIR}"

# Set environment for Ollama
export OLLAMA_MODEL="${OLLAMA_MODEL}"
export OLLAMA_BASE_URL="http://localhost:11434/v1"

# Launch ADK web with ollama_agent
adk web --host="${HOST}" --port="${PORT}" --allow_origins="${ALLOW_ORIGINS}" "${AGENTS_DIR}/ollama_agent"
