#!/bin/bash
# Setup script for environment variables

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_DIR/.env"
ENV_EXAMPLE="$PROJECT_DIR/.env.example"

echo "🔧 Setting up environment variables for Semantic Pattern Query App"
echo ""

# Check if .env already exists
if [ -f "$ENV_FILE" ]; then
    echo "⚠️  .env file already exists at: $ENV_FILE"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file"
        exit 0
    fi
fi

# Create .env from .env.example if it doesn't exist
if [ ! -f "$ENV_EXAMPLE" ]; then
    echo "Creating .env.example template..."
    cat > "$ENV_EXAMPLE" << 'EOF'
# Semantic Pattern Query App - Environment Configuration

# ============================================================================
# Google Gemini API Configuration
# ============================================================================
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_EMBEDDING_MODEL=models/embedding-001

# ============================================================================
# Ollama Configuration
# ============================================================================
OLLAMA_MODEL=qwen3:14b
OLLAMA_BASE_URL=http://localhost:11434

# ============================================================================
# Service URLs
# ============================================================================
QDRANT_URL=http://localhost:6333
ELASTICSEARCH_URL=http://localhost:9200
REDIS_HOST=localhost
REDIS_PORT=6380

# ============================================================================
# Pattern Library Path
# ============================================================================
PATTERN_LIBRARY_PATH=../pattern-library

# ============================================================================
# Embedding Configuration
# ============================================================================
EMBEDDING_ALIGNMENT_MATRIX_PATH=alignment_matrix.npy
EOF
fi

# Copy .env.example to .env
cp "$ENV_EXAMPLE" "$ENV_FILE"
echo "✅ Created .env file from .env.example"

# Prompt for Gemini API key
echo ""
echo "📝 Please provide your Gemini API key"
echo "   Get it from: https://makersuite.google.com/app/apikey"
read -p "GEMINI_API_KEY (press Enter to skip): " GEMINI_KEY

if [ -n "$GEMINI_KEY" ]; then
    # Update .env file with the API key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|GEMINI_API_KEY=.*|GEMINI_API_KEY=$GEMINI_KEY|" "$ENV_FILE"
    else
        # Linux
        sed -i "s|GEMINI_API_KEY=.*|GEMINI_API_KEY=$GEMINI_KEY|" "$ENV_FILE"
    fi
    echo "✅ Updated GEMINI_API_KEY in .env file"
else
    echo "⚠️  GEMINI_API_KEY not set. You can set it later in .env file"
fi

echo ""
echo "✅ Environment setup complete!"
echo ""
echo "📄 .env file location: $ENV_FILE"
echo ""
echo "To set GEMINI_API_KEY manually, edit: $ENV_FILE"
echo "Or export it: export GEMINI_API_KEY=your-key-here"

