# Environment Setup Guide

This guide explains how to configure environment variables for the Semantic Pattern Query App, including the Gemini API key.

## Quick Setup

Run the setup script:

```bash
cd semantic-pattern-query-app
./scripts/setup_env.sh
```

This will:
1. Create a `.env` file from `.env.example`
2. Prompt you for your Gemini API key
3. Configure all environment variables

## Manual Setup

### 1. Create `.env` File

Copy the example file:

```bash
cd semantic-pattern-query-app
cp .env.example .env
```

### 2. Edit `.env` File

Open `.env` and set your Gemini API key:

```bash
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-actual-api-key-here
```

### 3. Get Gemini API Key

1. Visit https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it into your `.env` file

## Environment Variables

### Required for Gemini

- **`GEMINI_API_KEY`**: Your Google Gemini API key (required for Gemini queries)
- **`GEMINI_EMBEDDING_MODEL`**: Gemini embedding model (default: `models/embedding-001`)

### Optional Configuration

- **`OLLAMA_MODEL`**: Ollama model name (default: `qwen3:14b`)
- **`OLLAMA_BASE_URL`**: Ollama API URL (default: `http://localhost:11434`)
- **`QDRANT_URL`**: Qdrant server URL (default: `http://localhost:6333`)
- **`ELASTICSEARCH_URL`**: Elasticsearch server URL (default: `http://localhost:9200`)
- **`REDIS_HOST`**: Redis host (default: `localhost`)
- **`REDIS_PORT`**: Redis port (default: `6380`)
- **`PATTERN_LIBRARY_PATH`**: Path to pattern library (default: `../pattern-library`)

## Using Environment Variables

The application automatically loads `.env` file when:
- Starting the API server (`python src/api_server.py`)
- Using the orchestrator directly
- Running any script that imports the modules

### Alternative: Export Variables

You can also export environment variables directly:

```bash
export GEMINI_API_KEY=your-api-key-here
export GEMINI_EMBEDDING_MODEL=models/embedding-001
```

### Verify Configuration

Check if your environment variables are loaded:

```python
import os
from dotenv import load_dotenv
load_dotenv()

print(f"GEMINI_API_KEY: {'Set' if os.getenv('GEMINI_API_KEY') else 'Not set'}")
```

## Security Notes

⚠️ **Important Security Practices:**

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Share `.env.example`** - This is safe to commit (no real keys)
3. **Rotate keys regularly** - If a key is exposed, regenerate it
4. **Use different keys** - Use separate keys for development and production

## Troubleshooting

### "GEMINI_API_KEY environment variable is required"

**Solution**: Make sure you've:
1. Created a `.env` file
2. Set `GEMINI_API_KEY=your-key` in the file
3. Restarted your application/server

### "Invalid API key"

**Solution**: 
1. Verify the key is correct (no extra spaces)
2. Check if the key is active at https://makersuite.google.com/app/apikey
3. Ensure you're using the correct key format

### Environment variables not loading

**Solution**:
1. Check `.env` file is in the project root (`semantic-pattern-query-app/.env`)
2. Verify `python-dotenv` is installed: `pip install python-dotenv`
3. Make sure `load_dotenv()` is called before using `os.getenv()`

## Testing Gemini Integration

After setting up your API key, test it:

```bash
# Test with curl
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAPTOR RAG?",
    "query_embedder_type": "gemini"
  }'
```

Or in Python:

```python
from src.document_store.orchestrator import SemanticPatternOrchestrator

orchestrator = SemanticPatternOrchestrator()
result = orchestrator.query(
    "What is RAPTOR RAG?",
    query_embedder_type="gemini"
)
print(result["answer"])
```

## Next Steps

Once your environment is configured:

1. **Start services**: `docker-compose up -d`
2. **Ingest patterns**: `python scripts/ingest_patterns.py`
3. **Start API server**: `python src/api_server.py`
4. **Query with Gemini**: Use `query_embedder_type: "gemini"` in API requests

