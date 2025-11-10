#!/bin/bash
# Bash script to install dependencies
# Extends existing requirements.txt approach

echo "Installing dependencies for AI Summarization Reference Architecture..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "ERROR: Python not found. Please install Python 3.8 or higher."
    exit 1
fi

echo "Using Python: $PYTHON_CMD"

# Upgrade pip
echo ""
echo "Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip

# Install core dependencies
echo ""
echo "Installing core dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt

# Verify installations
echo ""
echo "Verifying installations..."
packages=("docling" "chromadb" "sentence-transformers" "duckduckgo-search" "ollama")
for pkg in "${packages[@]}"; do
    if $PYTHON_CMD -m pip show "$pkg" &> /dev/null; then
        echo "  ✓ $pkg installed"
    else
        echo "  ✗ $pkg not found"
    fi
done

echo ""
echo "Installation complete!"
echo "Note: Google ADK will need to be installed separately when available."
echo "Note: Ollama service must be running separately (ollama serve)"

