# 🚀 START HERE - Pattern Query App

**New to this project? Start here!**

This guide will get you up and running in under 5 minutes.

---

## What Does This App Do?

This app lets you **query the Healthcare AI Pattern Library** using natural language. Instead of manually searching through documentation, ask questions like:

- "What RAG patterns work best for clinical notes?"
- "Compare Azure vs AWS for healthcare summarization"
- "Show me FHIR integration examples"

The app uses **vector search** and **AI agents** to find relevant patterns and answer your questions.

---

## Quick Start Decision Tree

Follow this flowchart to get started:

```
┌─────────────────────────────────────┐
│  Do you want to start the app?      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  1. Are you in the right directory? │
└──────────────┬──────────────────────┘
               │
               ▼
       cd pattern-query-app
               │
               ▼
┌─────────────────────────────────────┐
│  2. Is ChromaDB populated?          │
│  (Run once, first time only)        │
└──────────────┬──────────────────────┘
               │
               ▼
       ../venv312/bin/python scripts/ingest_all_docs.py
       ✅ ~116 documents loaded
               │
               ▼
┌─────────────────────────────────────┐
│  3. Is Ollama running?              │
│  (Check: curl localhost:11434)      │
└──────────────┬──────────────────────┘
               │
               ▼
       ollama list
       ✅ qwen3:14b (or gemma3:4b)
               │
               ▼
┌─────────────────────────────────────┐
│  4. Start the app!                  │
└──────────────┬──────────────────────┘
               │
               ▼
       export OLLAMA_MODEL="qwen3:14b"
       export OLLAMA_BASE_URL="http://localhost:11434/v1"
       ../venv312/bin/adk web --host=127.0.0.1 --port=8000 --allow_origins="*" .adk/agents
               │
               ▼
       ✅ Open http://127.0.0.1:8000
       ✅ Select "ollama_agent" from dropdown
       ✅ Ask your question!
```

---

## One-Command Quick Start

If you've already done the setup, just run:

```bash
cd pattern-query-app && \
export OLLAMA_MODEL="qwen3:14b" && \
export OLLAMA_BASE_URL="http://localhost:11434/v1" && \
../venv312/bin/adk web --host=127.0.0.1 --port=8000 --allow_origins="*" .adk/agents
```

Then open **http://127.0.0.1:8000** in your browser.

---

## First-Time Setup (One Time Only)

### Step 1: Verify Prerequisites

```bash
# Check Python version (should be 3.12.12)
python3 --version

# Check venv312 exists
ls ../venv312/bin/adk

# Check Ollama is running
curl http://localhost:11434/api/tags

# Check Ollama has qwen3:14b model
ollama list | grep qwen3
```

### Step 2: Install Dependencies (if needed)

```bash
cd pattern-query-app
pip install -r requirements.txt
```

### Step 3: Populate ChromaDB

```bash
cd pattern-query-app
../venv312/bin/python scripts/ingest_all_docs.py
```

**Expected output**: ~116 documents ingested

### Step 4: Start the App

```bash
export OLLAMA_MODEL="qwen3:14b"
export OLLAMA_BASE_URL="http://localhost:11434/v1"
../venv312/bin/adk web --host=127.0.0.1 --port=8000 --allow_origins="*" .adk/agents
```

### Step 5: Access the Web UI

1. Open **http://127.0.0.1:8000** in your browser
2. Select **ollama_agent** from the dropdown
3. Type your question in the chat box
4. Get answers with citations!

---

## Example Questions to Try

Once you're in the web UI:

**Beginner Questions**:
```
What RAG patterns are available?
Explain contextual retrieval
How does basic RAG work?
```

**Healthcare-Specific**:
```
How do I summarize patient records?
What's the best pattern for clinical notes?
Show me FHIR integration examples
```

**Vendor Comparisons**:
```
Compare Azure vs AWS for healthcare RAG
What are the costs for Google Vertex AI?
Show me Anthropic Claude examples
```

**Technical Deep Dives**:
```
How do I handle 200K token contexts?
What embedding models should I use?
Explain multi-modal RAG for medical imaging
```

---

## Troubleshooting

### Issue: "No agents found"

**Problem**: ADK can't find the agents

**Solution**:
```bash
# Make sure you're pointing to .adk/agents (not a subdirectory)
../venv312/bin/adk web .adk/agents

# NOT this:
../venv312/bin/adk web .adk/agents/ollama_agent  # ❌ WRONG
```

### Issue: "adk: command not found"

**Problem**: Not using the venv312 environment

**Solution**:
```bash
# Use the full path
../venv312/bin/adk web .adk/agents

# Check it exists
ls ../venv312/bin/adk
```

### Issue: Agent not responding

**Problem**: Multiple possible causes

**Solutions**:
1. **Check Ollama is running**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Check model is downloaded**:
   ```bash
   ollama list | grep qwen3
   # If not found: ollama pull qwen3:14b
   ```

3. **Check ChromaDB has data**:
   ```bash
   ../venv312/bin/python -c "from src.document_store.storage.vector_store import VectorStore; print(VectorStore().get_collection_info())"
   ```

4. **Check you selected an agent** in the UI dropdown

### Issue: Port 8000 already in use

**Solution**:
```bash
# Find and kill the process
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Or use a different port
ADK_WEB_PORT=8080 ../venv312/bin/adk web .adk/agents
```

---

## What's Next?

Once you're up and running:

1. **Explore the patterns**: Ask questions about different RAG patterns
2. **Try both agents**: Compare `ollama_agent` vs `gemini_agent` (needs GOOGLE_API_KEY)
3. **Read the docs**:
   - [ADK_QUICKSTART.md](docs/ADK_QUICKSTART.md) - Detailed setup guide
   - [README.md](README.md) - Full project documentation
   - [CLAUDE.md](CLAUDE.md) - Instructions for AI assistants
4. **Check examples**: See `examples/` for code samples

---

## Architecture Overview

```
User Browser (http://127.0.0.1:8000)
        ↓
   ADK Web UI
        ↓
   ollama_agent (qwen3:14b via Ollama)
        ↓
   Tools: query_architecture_patterns()
        ↓
   ChromaDB Vector Store (116+ documents)
        ↓
   Pattern Library (../pattern-library/)
```

---

## Two Agents Available

### 1. ollama_agent (Recommended for Getting Started)
- ✅ **No API key required**
- ✅ **Runs 100% locally**
- ✅ **Free to use**
- Uses: Ollama models (qwen3:14b, gemma3:4b)
- Best for: Development, testing, learning

### 2. gemini_agent (Production Quality)
- ⚠️ **Requires GOOGLE_API_KEY**
- ☁️ **Uses Google Gemini API**
- 💰 **Paid (but very cheap ~$0.001/query)**
- Uses: gemini-2.5-flash
- Best for: Production, high-quality responses

**Both agents** query the same ChromaDB database with the same tools. The only difference is which LLM they use.

---

## Quick Reference

| Task | Command |
|------|---------|
| Start app | `cd pattern-query-app && ../venv312/bin/adk web .adk/agents` |
| Ingest patterns | `cd pattern-query-app && ../venv312/bin/python scripts/ingest_all_docs.py` |
| Check ChromaDB | `../venv312/bin/python -c "from src.document_store.storage.vector_store import VectorStore; print(VectorStore().get_collection_info())"` |
| Check Ollama | `curl http://localhost:11434/api/tags` |
| List models | `ollama list` |
| Pull model | `ollama pull qwen3:14b` |
| Kill port 8000 | `lsof -i :8000 \| grep LISTEN \| awk '{print $2}' \| xargs kill -9` |

---

## Need Help?

1. **Read the docs**:
   - [CLAUDE.md](CLAUDE.md) - Comprehensive AI assistant instructions
   - [ADK_QUICKSTART.md](docs/ADK_QUICKSTART.md) - Detailed setup guide
   - [troubleshooting-guide.md](docs/troubleshooting-guide.md) - Common issues

2. **Check the examples**:
   - [examples/](examples/) - Working code samples

3. **Review the architecture**:
   - [README.md](README.md) - Full project documentation

---

**Ready to start?** Just run:

```bash
cd pattern-query-app && \
export OLLAMA_MODEL="qwen3:14b" && \
export OLLAMA_BASE_URL="http://localhost:11434/v1" && \
../venv312/bin/adk web --host=127.0.0.1 --port=8000 --allow_origins="*" .adk/agents
```

Then open **http://127.0.0.1:8000** and start asking questions!
