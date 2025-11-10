# Google ADK Quick Start Guide

## Overview

This guide shows you how to use Google's Agent Development Kit (ADK) to query your AI architecture patterns through an interactive web interface.

**What you'll get:**
- 🌐 Web-based chat interface to query patterns
- 🤖 AI agent with access to your entire pattern library
- 🔍 Semantic search across all RAG patterns, vendor guides, and use cases
- 📊 Structured responses with source citations

## Prerequisites

| Requirement | Version | Notes |
|------------|---------|-------|
| Python | 3.10+ | Python 3.9 works but has warnings |
| google-adk | 1.18.0+ | Installed via requirements.txt |
| GOOGLE_API_KEY | - | Get from [AI Studio](https://aistudio.google.com/app/apikey) |
| ChromaDB | - | Auto-configured, patterns must be ingested |

## Quick Start (Recommended)

### Option 1: Automated Setup

```bash
# Run the quick start script - it checks everything and launches the UI
./scripts/quick_start_adk.sh
```

The script will:
1. ✓ Check Python and dependencies
2. ✓ Verify GOOGLE_API_KEY (prompts if missing)
3. ✓ Check ChromaDB data (offers to populate if needed)
4. ✓ Configure ADK agent
5. ✓ Launch web UI at http://127.0.0.1:8000

### Option 2: Manual Setup

If you prefer manual control:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Google AI API key
export GOOGLE_API_KEY='your-api-key-here'
# Get key from: https://aistudio.google.com/app/apikey

# 3. Populate ChromaDB (if not already done)
python3 scripts/initialize_and_test.py

# 4. Generate ADK agent configuration
python3 scripts/setup_adk_agent.py

# 5. Launch the web UI
./scripts/start_adk_default_ui.sh
```

## Using the Web Interface

Once the web UI is running at http://127.0.0.1:8000:

### Example Queries

Try asking:

**Pattern Discovery:**
- "What RAG patterns are available for healthcare?"
- "Explain Contextual Retrieval and when to use it"
- "Compare RAPTOR RAG vs basic RAG"

**Vendor-Specific:**
- "How do I implement RAG with Google Vertex AI?"
- "Show me Azure OpenAI healthcare implementation"
- "What are the costs for AWS Bedrock RAG?"

**Use Case Guidance:**
- "How do I summarize patient records?"
- "What's the best pattern for clinical notes?"
- "Show FHIR integration examples"

**Technical Details:**
- "What embedding models should I use?"
- "How do I handle 200K token contexts?"
- "Explain multi-modal RAG for medical imaging"

### Understanding Responses

The ADK agent will:
1. 🔍 Query the ChromaDB vector store
2. 📚 Retrieve relevant pattern documentation
3. 🤖 Generate a response using Gemini
4. 📎 Cite source documents (IDs and metadata)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User's Browser                          │
│                  http://127.0.0.1:8000                      │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              ADK Web UI (FastAPI + Web UI)                  │
│                adk web .adk/agents                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│           ADK Agent (Gemini 2.5 Flash)                      │
│        .adk/agents/chromadb_agent/agent.py                  │
│                                                             │
│  Tools:                                                     │
│  • query_architecture_patterns()                            │
│  • get_store_info()                                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│          RAG Query Interface                                │
│      src/document_store/search/rag_query.py                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│            ChromaDB Vector Store                            │
│              data/chroma_db/                                │
│                                                             │
│  Contents:                                                  │
│  • 23 RAG patterns                                          │
│  • 5 Vendor guides                                          │
│  • 3 Healthcare use cases                                   │
│  • 67 AI design patterns                                    │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `GOOGLE_API_KEY` | *required* | Gemini API access |
| `ADK_MODEL` | `gemini-2.5-flash` | Override Gemini model |
| `ADK_PERSIST_DIRECTORY` | `data/chroma_db` | ChromaDB location |
| `ADK_COLLECTION_NAME` | `architecture_patterns` | Collection to query |
| `ADK_WEB_HOST` | `127.0.0.1` | Web UI host |
| `ADK_WEB_PORT` | `8000` | Web UI port |
| `ADK_ALLOW_ORIGINS` | `*` | CORS origins |
| `ADK_INSTRUCTION` | *see below* | Custom agent prompt |

### Custom Agent Instructions

Create a file `custom_instruction.txt`:

```
You are an expert in healthcare AI architecture patterns.
Focus on HIPAA compliance and patient data privacy.
Always mention security considerations.
```

Then regenerate the agent:

```bash
python3 scripts/setup_adk_agent.py \
  --instruction-file custom_instruction.txt \
  --overwrite
```

### Using Different Models

```bash
# Use Gemini 1.5 Pro for better quality (higher cost)
export ADK_MODEL="gemini-1.5-pro"

# Use Gemini 2.0 Flash Lite for lower cost
export ADK_MODEL="gemini-2.0-flash-lite"

# Then restart the UI
./scripts/start_adk_default_ui.sh
```

## Troubleshooting

### Issue: "GOOGLE_API_KEY not set"

**Solution:**
```bash
# Get key from: https://aistudio.google.com/app/apikey
export GOOGLE_API_KEY='your-key-here'

# Or add to .env file in project root:
echo 'GOOGLE_API_KEY=your-key-here' > .env
```

### Issue: "ChromaDB is empty"

**Solution:**
```bash
# Populate the database with patterns
python3 scripts/initialize_and_test.py
```

### Issue: "adk: command not found"

**Solution:**
```bash
# Reinstall google-adk
pip install --upgrade google-adk>=1.18.0

# Add Python scripts to PATH
export PATH="$PATH:$(python3 -m site --user-base)/bin"

# Or use the quick start script which handles this
./scripts/quick_start_adk.sh
```

### Issue: "Module not found" errors

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# If specific packages are missing, install them individually:
pip install google-adk>=1.18.0
pip install chromadb>=0.5.0
pip install sentence-transformers>=3.3.0
```

### Issue: Web UI shows 404 or connection errors

**Solution:**
```bash
# Check if the server is running
curl http://127.0.0.1:8000/health

# Check the ADK agent directory exists
ls -la .adk/agents/chromadb_agent/

# Regenerate if needed
python3 scripts/setup_adk_agent.py --overwrite

# Try different port
ADK_WEB_PORT=8080 ./scripts/start_adk_default_ui.sh
```

### Issue: Slow responses or timeout

**Solutions:**
- Use a faster model: `export ADK_MODEL="gemini-2.5-flash"`
- Reduce `n_results` in queries (default is 5)
- Check your internet connection
- Verify API key is valid and not rate-limited

## Advanced Usage

### Programmatic Access

You can also use the ADK agent programmatically:

```python
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path.cwd() / "src"))

from document_store.agents.adk_agent import ADKAgentQuery
from document_store.storage.vector_store import VectorStore

# Initialize
vector_store = VectorStore(
    persist_directory="data/chroma_db",
    collection_name="architecture_patterns"
)

adk_query = ADKAgentQuery(vector_store)

# Query
results = adk_query.query(
    query="What is Contextual Retrieval?",
    n_results=5,
    use_agent=True
)

# Access agent response
print(results['agent_response']['answer'])
```

### CLI-Only Mode

For terminal-based interaction:

```bash
# Interactive REPL
adk run .adk/agents/chromadb_agent

# Then type your questions:
> What are the best RAG patterns for healthcare?
```

### Custom Web UI

If you want to customize the UI:

```bash
# Clone the ADK web repository
git clone https://github.com/google/adk-web.git
cd adk-web

# Install and build
npm install
npm run serve -- --backend=http://localhost:8000

# In another terminal, start the API server
cd /path/to/SummarizerArchitecture
adk api_server --host=0.0.0.0 --port=8000 \
  --allow_origins=http://localhost:4200 .adk/agents
```

## Performance Tips

1. **Faster responses**: Use `gemini-2.5-flash` (default)
2. **Better quality**: Use `gemini-1.5-pro` or `gemini-2.0-flash-thinking`
3. **Lower cost**: Reduce `n_results` parameter
4. **Caching**: ADK caches embeddings and results automatically

## Cost Considerations

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Speed |
|-------|---------------------|----------------------|-------|
| Gemini 2.5 Flash | $0.075 | $0.30 | Fast |
| Gemini 1.5 Pro | $1.25 | $5.00 | Medium |
| Gemini 2.0 Flash Lite | $0.04 | $0.12 | Very Fast |

**Typical query cost:** $0.001 - $0.01 per query with Gemini 2.5 Flash

## What's Next?

- **Add More Patterns**: Edit files in `docs/patterns/` and re-ingest
- **Customize Agent**: Modify [.adk/agents/chromadb_agent/agent.py](.adk/agents/chromadb_agent/agent.py)
- **Deploy to Cloud**: See [docs/vendor-guides/google-adk.md](docs/vendor-guides/google-adk.md)
- **Add Custom Tools**: Extend the agent with additional functions

## Related Documentation

- [scripts/ADK_SETUP.md](../scripts/ADK_SETUP.md) - Detailed setup checklist
- [docs/vendor-guides/google-adk.md](docs/vendor-guides/google-adk.md) - Complete ADK guide
- [docs/agent-setup-guide.md](docs/agent-setup-guide.md) - Agent architecture overview
- [Official ADK Docs](https://google.github.io/adk-docs/) - Google's documentation

## Support

If you encounter issues:

1. Check [scripts/ADK_SETUP.md](../scripts/ADK_SETUP.md) troubleshooting section
2. Verify all prerequisites are met
3. Try the quick start script: `./scripts/quick_start_adk.sh`
4. Review error messages carefully
5. Check ADK version: `pip show google-adk`

---

**Ready to start?** Run:

```bash
./scripts/quick_start_adk.sh
```

Then open http://127.0.0.1:8000 in your browser!
