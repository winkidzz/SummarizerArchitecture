#!/usr/bin/env bash
#
# Quick Start Script for Google ADK Web UI
#
# This script helps you launch the ADK web interface to query architecture patterns.
# It checks prerequisites and provides clear guidance.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

echo "=========================================="
echo "Google ADK Quick Start"
echo "=========================================="
echo ""

# Check Python version
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_CMD="python3"
    echo "✓ Python found: $PYTHON_VERSION"
elif command -v python >/dev/null 2>&1; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    PYTHON_CMD="python"
    echo "✓ Python found: $PYTHON_VERSION"
else
    echo "✗ Python not found. Please install Python 3.10+"
    exit 1
fi

# Check google-adk installation
echo ""
echo "Checking dependencies..."
if ! $PYTHON_CMD -c "import google.adk" 2>/dev/null; then
    echo "✗ google-adk not installed"
    echo ""
    echo "Installing google-adk..."
    pip install google-adk>=1.18.0
fi

# Check if ADK CLI is available
if ! command -v adk >/dev/null 2>&1; then
    echo "⚠  ADK CLI not in PATH"
    echo ""
    echo "Trying to find adk in Python scripts..."

    # Try to find adk in common Python script locations
    PYTHON_SCRIPTS_DIR=$(python3 -c "import sysconfig; print(sysconfig.get_path('scripts'))" 2>/dev/null || echo "")

    if [ -n "$PYTHON_SCRIPTS_DIR" ] && [ -f "$PYTHON_SCRIPTS_DIR/adk" ]; then
        export PATH="$PYTHON_SCRIPTS_DIR:$PATH"
        echo "✓ Found ADK CLI at: $PYTHON_SCRIPTS_DIR/adk"
    else
        echo "✗ Could not find ADK CLI"
        echo ""
        echo "Please ensure your Python scripts directory is in PATH:"
        echo "  export PATH=\"\$PATH:$PYTHON_SCRIPTS_DIR\""
        echo ""
        echo "Or reinstall google-adk:"
        echo "  pip install --upgrade --force-reinstall google-adk>=1.18.0"
        exit 1
    fi
fi

# Check GOOGLE_API_KEY
echo ""
if [ -z "${GOOGLE_API_KEY:-}" ]; then
    echo "⚠  GOOGLE_API_KEY not set"
    echo ""
    echo "You need a Google AI API key to use ADK."
    echo ""
    echo "Steps to get started:"
    echo "  1. Visit: https://aistudio.google.com/app/apikey"
    echo "  2. Create or copy your API key"
    echo "  3. Set it in your environment:"
    echo "     export GOOGLE_API_KEY='your-key-here'"
    echo ""
    echo "  Or create a .env file in the project root:"
    echo "     echo 'GOOGLE_API_KEY=your-key-here' > .env"
    echo ""
    read -p "Do you want to enter your API key now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your GOOGLE_API_KEY: " api_key
        export GOOGLE_API_KEY="$api_key"
        echo "✓ API key set for this session"
    else
        echo ""
        echo "Please set GOOGLE_API_KEY and run this script again."
        exit 1
    fi
else
    MASKED_KEY="${GOOGLE_API_KEY:0:8}...${GOOGLE_API_KEY: -4}"
    echo "✓ GOOGLE_API_KEY is set: $MASKED_KEY"
fi

# Check ChromaDB data
echo ""
if [ ! -f "data/chroma_db/chroma.sqlite3" ]; then
    echo "⚠  ChromaDB not populated"
    echo ""
    echo "The pattern database is empty. You need to ingest patterns first."
    echo ""
    echo "Run: python3 scripts/initialize_and_test.py"
    echo ""
    read -p "Do you want to populate the database now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Populating ChromaDB..."
        $PYTHON_CMD scripts/initialize_and_test.py
    else
        echo "Please populate the database and run this script again."
        exit 1
    fi
else
    echo "✓ ChromaDB found at: data/chroma_db/"
fi

# Check agent directory
echo ""
if [ ! -d ".adk/agents/gemini_agent" ]; then
    echo "⚠  ADK agent not configured"
    echo ""
    echo "Generating ADK agent configuration..."
    $PYTHON_CMD scripts/setup_adk_agent.py
fi

echo ""
echo "=========================================="
echo "All prerequisites met!"
echo "=========================================="
echo ""
echo "Starting ADK Web UI..."
echo ""
echo "  Web UI will be available at:"
echo "  http://127.0.0.1:8000"
echo ""
echo "  Press Ctrl+C to stop the server"
echo ""
echo "=========================================="
echo ""

# Launch the web UI
HOST="${ADK_WEB_HOST:-127.0.0.1}"
PORT="${ADK_WEB_PORT:-8000}"
ALLOW_ORIGINS="${ADK_ALLOW_ORIGINS:-*}"

adk web --host="$HOST" --port="$PORT" --allow_origins="$ALLOW_ORIGINS" .adk/agents
