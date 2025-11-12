# Claude AI Assistant Instructions - Pattern Query App

## Project Overview

You are working on the **Pattern Query Application** - a document storage and querying tool for the Healthcare AI Pattern Library. This app allows users to search and query architecture patterns using vector search and AI agents.

**IMPORTANT**: This is a **supporting tool** that queries patterns. The actual patterns are in `../pattern-library/`.

## Critical Context for AI Assistants

### Python Environment
- **Python Version**: 3.12.12 (see [../.python-version](../.python-version))
- **Virtual Environment**: `../venv312/` (shared with parent project)
- **ADK Location**: `../venv312/bin/adk`
- **Always use**: `../venv312/bin/adk` (NOT system-installed adk)
- **Always use**: `../venv312/bin/python` or `python3` (NOT python)

### Starting the Application

#### CORRECT Way to Start (Most Common Use Case)

```bash
cd pattern-query-app

# Option 1: Using the startup script (RECOMMENDED)
# This script automatically configures everything
export OLLAMA_MODEL="qwen3:14b"
export OLLAMA_BASE_URL="http://localhost:11434/v1"
../venv312/bin/adk web --host=127.0.0.1 --port=8000 --allow_origins="*" .adk/agents

# Option 2: Using the shell script (if adk is in PATH)
./scripts/start_adk_ollama.sh
```

**Key Points:**
1. **Always point to `.adk/agents`** (the parent directory), NOT `.adk/agents/ollama_agent`
2. **Use the venv312 adk**: `../venv312/bin/adk`
3. **Set OLLAMA_MODEL** to `qwen3:14b` (default in this project)
4. **Access at**: http://127.0.0.1:8000

#### INCORRECT Ways (Common Mistakes to Avoid)

❌ **DON'T**: Point to a specific agent subdirectory
```bash
# WRONG - this will fail to load agents
adk web .adk/agents/ollama_agent
```

❌ **DON'T**: Use system Python or absolute paths
```bash
# WRONG - uses system Python instead of venv312
/usr/local/bin/adk web
~/.local/bin/adk web
```

❌ **DON'T**: Run from the wrong directory
```bash
# WRONG - adk needs to be run from pattern-query-app/
cd ..
adk web pattern-query-app/.adk/agents
```

### Two Agents Available

The app has **two agents** in `.adk/agents/`:

1. **ollama_agent** (Local, No API Key Required)
   - Uses local Ollama models (qwen3:14b, gemma3:4b)
   - Configuration: `OLLAMA_MODEL`, `OLLAMA_BASE_URL`
   - Best for: Development, testing, offline use
   - Queries: ChromaDB vector store with RAG

2. **gemini_agent** (Google Gemini Cloud)
   - Uses Google Gemini API (gemini-2.5-flash)
   - Configuration: `GOOGLE_API_KEY` (required)
   - Best for: Production, high-quality responses
   - Queries: ChromaDB vector store with RAG

**Both agents** use the same ChromaDB database and tools. The only difference is which LLM they use.

### Web UI Behavior

When you start `adk web .adk/agents`:
- The UI shows **all available agents** in a dropdown
- User must **select an agent** before chatting
- If "No agents found" appears:
  - Check you're pointing to `.adk/agents` (not a subdirectory)
  - Verify agent.py and __init__.py exist in each agent folder
  - Ensure root_agent is exported in __init__.py

## Project Structure

```
pattern-query-app/
├── CLAUDE.md                    # THIS FILE - Instructions for AI assistants
├── README.md                    # Main project documentation
├── requirements.txt             # Python dependencies
├── .python-version              # Python version (managed by parent project)
├── .adk/
│   └── agents/                  # ADK agent packages (POINT HERE with adk web)
│       ├── ollama_agent/        # Local Ollama agent
│       │   ├── __init__.py      # Exports root_agent
│       │   └── agent.py         # Agent definition
│       └── chromadb_agent/      # Google Gemini agent
│           ├── __init__.py
│           └── agent.py
├── src/
│   └── document_store/          # Core application logic
│       ├── orchestrator.py      # Main API
│       ├── storage/
│       │   └── vector_store.py  # ChromaDB wrapper
│       ├── search/
│       │   └── rag_query.py     # RAG query interface
│       └── agents/
│           ├── adk_agent.py     # ADK integration
│           └── ollama_agent.py  # Ollama integration
├── scripts/                     # Utility scripts
│   ├── start_adk_ollama.sh      # Start Ollama agent
│   ├── start_adk_default_ui.sh  # Start default UI
│   ├── ingest_all_docs.py       # Ingest patterns to ChromaDB
│   └── initialize_and_test.py   # Setup and test
├── data/
│   └── chroma_db/               # ChromaDB vector database
│       └── architecture_patterns/  # Collection with 116+ documents
├── docs/                        # Documentation
│   ├── ADK_QUICKSTART.md        # Quick start guide
│   ├── agent-setup-guide.md     # Agent configuration
│   └── troubleshooting-guide.md # Common issues
└── examples/                    # Example usage scripts
```

## Common Tasks and Commands

### 1. Starting the Application

**Task**: Start the web UI for querying patterns

**Commands**:
```bash
cd pattern-query-app

# Best: Use venv312 ADK directly
export OLLAMA_MODEL="qwen3:14b"
export OLLAMA_BASE_URL="http://localhost:11434/v1"
../venv312/bin/adk web --host=127.0.0.1 --port=8000 --allow_origins="*" .adk/agents
```

**Expected Output**:
```
+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://127.0.0.1:8000.                         |
+-----------------------------------------------------------------------------+
```

**Access**: Open http://127.0.0.1:8000 in browser

### 2. Ingesting Patterns into ChromaDB

**Task**: Load pattern library into the vector database

**Commands**:
```bash
cd pattern-query-app
../venv312/bin/python scripts/ingest_all_docs.py
```

**Expected Output**: ~116 documents ingested

### 3. Testing the Setup

**Task**: Verify ChromaDB and agents are working

**Commands**:
```bash
cd pattern-query-app
../venv312/bin/python scripts/initialize_and_test.py
```

### 4. Querying via CLI

**Task**: Query patterns from command line

**Commands**:
```bash
cd pattern-query-app
../venv312/bin/python scripts/query_with_ollama.py "What is RAPTOR RAG?"
```

### 5. Checking ChromaDB Status

**Task**: Verify patterns are loaded

**Commands**:
```bash
../venv312/bin/python -c "
from src.document_store.storage.vector_store import VectorStore
vs = VectorStore()
print(vs.get_collection_info())
"
```

## Agent Tools and Capabilities

Each agent has access to these tools:

### 1. query_architecture_patterns()
Search the ChromaDB vector store for patterns.

**Parameters**:
- `query` (str): Natural language question
- `n_results` (int): Number of results (default: 5)
- `pattern_type` (str, optional): Filter by pattern (e.g., "basic-rag")
- `vendor` (str, optional): Filter by vendor (e.g., "gemini", "azure")

**Returns**: Dict with matched documents, metadata, and distances

### 2. get_store_info()
Get metadata about the ChromaDB collection.

**Returns**: Document counts, collection name, persistence path

## Configuration

### Environment Variables

```bash
# Ollama Configuration (for ollama_agent)
export OLLAMA_MODEL="qwen3:14b"              # or gemma3:4b
export OLLAMA_BASE_URL="http://localhost:11434/v1"

# Google Gemini Configuration (for chromadb_agent)
export GOOGLE_API_KEY="your-api-key"         # Get from https://aistudio.google.com/app/apikey

# ADK Configuration
export ADK_PERSIST_DIRECTORY="data/chroma_db"
export ADK_COLLECTION_NAME="architecture_patterns"
export ADK_WEB_PORT="8000"
export ADK_WEB_HOST="127.0.0.1"
```

### Files

- `.env.example` - Template for environment variables
- `requirements.txt` - Python package dependencies
- `../.python-version` - Python version (3.12.12)

## Troubleshooting Common Issues

### Issue: "No agents found"

**Cause**: ADK is pointing to wrong directory or agents not properly structured

**Solution**:
```bash
# Check agent structure
ls -la .adk/agents/ollama_agent/
# Should show: __init__.py, agent.py, __pycache__/

# Verify __init__.py exports root_agent
cat .adk/agents/ollama_agent/__init__.py
# Should contain: from .agent import root_agent

# Point to parent directory
../venv312/bin/adk web .adk/agents  # NOT .adk/agents/ollama_agent
```

### Issue: "adk: command not found"

**Cause**: Not using the venv312 environment

**Solution**:
```bash
# Use full path to venv312 adk
../venv312/bin/adk web .adk/agents

# Or activate venv312 first
source ../venv312/bin/activate
adk web .adk/agents
```

### Issue: Using Python 3.9 instead of 3.12

**Cause**: Hardcoded path to old Python version

**Solution**:
```bash
# Always use venv312
../venv312/bin/python scripts/ingest_all_docs.py

# Or check which python
which python3  # Should point to 3.12.12
```

### Issue: Agent not responding to queries

**Cause**: Multiple possible causes

**Solutions**:
1. Check Ollama is running: `curl http://localhost:11434/api/tags`
2. Check model is downloaded: `ollama list | grep qwen3`
3. Check ChromaDB has data: `python -c "from src.document_store.storage.vector_store import VectorStore; print(VectorStore().get_collection_info())"`
4. Check agent selected in UI dropdown
5. Check browser console for errors

### Issue: Wrong port or "Address already in use"

**Solution**:
```bash
# Check what's on port 8000
lsof -i :8000

# Kill existing process
kill -9 <PID>

# Or use different port
ADK_WEB_PORT=8080 ../venv312/bin/adk web .adk/agents
```

## Example Queries to Test

Once the UI is running, try these queries:

**Pattern Discovery**:
- "What RAG patterns are available?"
- "Explain Contextual Retrieval"
- "Compare RAPTOR RAG vs Basic RAG"

**Healthcare-Specific**:
- "How do I summarize patient records?"
- "Best pattern for clinical notes?"
- "Show FHIR integration examples"

**Vendor Comparisons**:
- "Compare Azure and AWS for healthcare RAG"
- "What are Gemini pricing options?"
- "Show me Google Vertex AI examples"

## Dependencies and Requirements

### Prerequisites
- Python 3.12.12 (managed via parent project)
- Ollama (for local models)
- 500MB disk space (for ChromaDB)
- 2-4GB RAM (for running local LLMs)

### Key Python Packages
- `google-adk>=1.18.0` - Google Agent Development Kit
- `chromadb>=0.5.0` - Vector database
- `sentence-transformers>=3.3.0` - Embeddings
- `ollama>=0.4.0` - Ollama integration
- `fastapi>=0.115.0` - Web framework
- `uvicorn>=0.32.0` - ASGI server

## Related Projects

- **Pattern Library** (`../pattern-library/`): The documentation this app queries
- **Parent Project** (`../`): Overall architecture project
- **Venv312** (`../venv312/`): Shared Python environment

## Communication Guidelines for AI Assistants

When helping with this project:

1. **Always check Python version**: Use `../venv312/bin/python` or verify `.python-version`
2. **Always use venv312 adk**: Never use system-installed or Python 3.9 paths
3. **Point to `.adk/agents`**: Not subdirectories when starting web UI
4. **Check working directory**: Should be `pattern-query-app/` for most commands
5. **Verify prerequisites**: Ollama running, ChromaDB populated, models downloaded
6. **Test incrementally**: Start app → Check UI loads → Select agent → Try query
7. **Read error messages carefully**: They usually indicate the exact issue

## Success Criteria

The application is working correctly when:

✅ ADK web server starts without errors
✅ Web UI shows at http://127.0.0.1:8000
✅ Both agents appear in dropdown (ollama_agent, chromadb_agent)
✅ Selected agent responds to queries
✅ Responses include citations from ChromaDB
✅ No "No agents found" warnings
✅ Python 3.12 is being used (check version in logs)

## Quick Reference Commands

```bash
# Start the app (RECOMMENDED)
cd pattern-query-app && \
export OLLAMA_MODEL="qwen3:14b" && \
export OLLAMA_BASE_URL="http://localhost:11434/v1" && \
../venv312/bin/adk web --host=127.0.0.1 --port=8000 --allow_origins="*" .adk/agents

# Ingest patterns
cd pattern-query-app && ../venv312/bin/python scripts/ingest_all_docs.py

# Check ChromaDB
cd pattern-query-app && ../venv312/bin/python -c "from src.document_store.storage.vector_store import VectorStore; print(VectorStore().get_collection_info())"

# Check Ollama models
ollama list

# Check Ollama is running
curl http://localhost:11434/api/tags

# Kill processes on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

---

**Remember**: This project uses Python 3.12.12 from `../venv312/`, always point ADK to `.adk/agents` directory, and the correct startup command is well-documented above. Follow these instructions exactly and the app will start correctly on the first try.
