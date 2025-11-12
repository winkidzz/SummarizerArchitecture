# ADK Gemini Agent Setup Guide

This guide explains how to configure and run the pattern-query-app with Google Gemini API.

## Configuration

The application is now configured to use Google Gemini API through environment variables in the `.env` file.

### Environment Variables

Add these to your `.env` file:

```bash
# Google Gemini API Key
# Get your key from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your-api-key-here

# Google Gemini Configuration for ADK Agent
# Model to use for Gemini agent (default: gemini-2.0-flash-exp)
# Options: gemini-2.0-flash-exp, gemini-1.5-pro, gemini-1.5-flash, etc.
GEMINI_MODEL=gemini-2.0-flash-exp

# ADK Agent Configuration (used by ADK framework)
ADK_MODEL=gemini-2.0-flash-exp
```

## Available Models

You can configure any Gemini model by changing the `GEMINI_MODEL` parameter in `.env`:

- `gemini-2.0-flash-exp` - Latest experimental flash model (fastest, recommended)
- `gemini-1.5-pro` - Most capable model
- `gemini-1.5-flash` - Fast, balanced model
- `gemini-1.0-pro` - Production-ready model

## Starting the ADK Agent

### Option 1: Using the Startup Script (Recommended)

```bash
cd pattern-query-app
./scripts/start_adk_gemini.sh
```

The script will:
1. Load configuration from `.env`
2. Verify `GEMINI_API_KEY` is set
3. Display configuration (model, API key)
4. Start ADK web server on http://127.0.0.1:8000

### Option 2: Manual Start

```bash
cd pattern-query-app

# Load .env variables
export $(grep -v '^#' .env | xargs)

# Set ADK environment
export ADK_MODEL="$GEMINI_MODEL"
export GOOGLE_API_KEY="$GEMINI_API_KEY"

# Start ADK
../venv312/bin/adk web \
    --host=127.0.0.1 \
    --port=8000 \
    --allow_origins="*" \
    .adk/agents/gemini_agent
```

## Accessing the Agent

Once started, access the ADK UI at:
- **Web UI**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **OpenAPI Schema**: http://127.0.0.1:8000/openapi.json

## Agent Capabilities

The Gemini agent can:

1. **Query Architecture Patterns** - Search and retrieve information from 116+ architecture pattern documents in ChromaDB
2. **Get Store Information** - View metadata about the vector database

### Example Queries

Try these queries in the ADK web UI:

- "What is Basic RAG?"
- "Compare RAPTOR RAG with HyDE RAG"
- "Show me healthcare summarization patterns with HIPAA compliance"
- "Give me a comparison table of all RAG patterns as CSV"

## Switching Between Ollama and Gemini

### To Use Gemini (Current Configuration)
```bash
./scripts/start_adk_gemini.sh
```

### To Use Local Ollama
```bash
./scripts/start_adk_ollama.sh
```

## Configuration Files

- **`.env`** - Main configuration file with API keys and model settings
- **`.adk/agents/gemini_agent/agent.py`** - Gemini agent implementation
- **`scripts/start_adk_gemini.sh`** - Startup script for Gemini agent
- **`scripts/start_adk_ollama.sh`** - Startup script for Ollama agent

## Troubleshooting

### API Key Not Found

Error: `❌ Error: GEMINI_API_KEY not set in .env file`

Solution:
1. Get your API key from: https://aistudio.google.com/app/apikey
2. Add it to `.env`: `GEMINI_API_KEY=your-key-here`

### Invalid API Key

Error: `Failed to initialize Gemini agent`

Solution:
1. Verify your API key is valid
2. Check you have API quota remaining
3. Ensure the key has Gemini API access enabled

### Port Already in Use

Error: `Address already in use`

Solution:
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill $(lsof -ti:8000)

# Restart
./scripts/start_adk_gemini.sh
```

### Model Not Found

Error: `Model not found: gemini-xyz`

Solution:
- Check available models at: https://ai.google.dev/models/gemini
- Update `GEMINI_MODEL` in `.env` with a valid model name

## Performance Comparison

| Agent Type | Model | Speed | Cost | Best For |
|------------|-------|-------|------|----------|
| Gemini | gemini-2.0-flash-exp | Very Fast (1-2s) | Low | Production, evaluation |
| Gemini | gemini-1.5-pro | Fast (2-4s) | Medium | Complex queries |
| Ollama | qwen3:14b | Slow (10-30s) | Free | Offline development |

## Related Documentation

- **EVALUATION_CONFIGURATION.md** - Configure RAG evaluation with Gemini or Ollama
- **START_HERE.md** - General project setup guide
- **ADK_QUICKSTART.md** - ADK framework overview

## Current Status

✅ **Gemini Agent Running**
- Model: `gemini-2.0-flash-exp`
- Port: `8000`
- Status: Active
- API Key: Configured from `.env`

Access at: http://127.0.0.1:8000
