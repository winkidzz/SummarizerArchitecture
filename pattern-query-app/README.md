# Pattern Query Application

**An intelligent document store and query system for the Healthcare AI Pattern Library.**

This application indexes, stores, and queries the [Healthcare AI Pattern Library](../pattern-library/) using vector search and AI agents. It's a **tool to work with the patterns**, not the patterns themselves.

> **Looking for the patterns?** See [`../pattern-library/`](../pattern-library/) for the reference architecture documentation.

---

## 📚 Documentation Quick Links

**New here? Start with these guides:**

- **[START_HERE.md](START_HERE.md)** - 5-minute quick start guide with decision tree
- **[CLAUDE.md](CLAUDE.md)** - Comprehensive instructions for AI assistants (helps any LLM understand the project)
- **[ADK_QUICKSTART.md](docs/ADK_QUICKSTART.md)** - Detailed ADK setup guide with troubleshooting
- **[README.md](README.md)** (this file) - Full project documentation

**Choose your path:**
- 🚀 Just want to start the app? → [START_HERE.md](START_HERE.md)
- 🤖 Are you an AI assistant? → [CLAUDE.md](CLAUDE.md)
- 📖 Want detailed docs? → Keep reading below

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12.12 (managed via `../venv312/`)
- Ollama running locally (with qwen3:14b model)
- 500MB disk space for ChromaDB

### One-Command Start

```bash
cd pattern-query-app && \
export OLLAMA_MODEL="qwen3:14b" && \
export OLLAMA_BASE_URL="http://localhost:11434/v1" && \
../venv312/bin/adk web --host=127.0.0.1 --port=8000 --allow_origins="*" .adk/agents
```

### First-Time Setup

```bash
# 1. Ingest pattern library into ChromaDB (one time only)
cd pattern-query-app
../venv312/bin/python scripts/ingest_all_docs.py

# 2. Start the web UI
export OLLAMA_MODEL="qwen3:14b"
export OLLAMA_BASE_URL="http://localhost:11434/v1"
../venv312/bin/adk web --host=127.0.0.1 --port=8000 --allow_origins="*" .adk/agents
```

### Access the Web UI
1. Open http://127.0.0.1:8000 in your browser
2. Select **ollama_agent** from the dropdown
3. Start querying patterns!

> **Detailed setup guide**: See [START_HERE.md](START_HERE.md) for step-by-step instructions with troubleshooting.

---

## 🎯 What Does This App Do?

This application provides **three ways to query the pattern library**:

### 1. 📱 Web UI (Recommended)
Interactive web interface powered by Google ADK or Ollama:
- **ADK UI**: Google's official Agent Development Kit interface
- **Ollama UI**: 100% local interface (no API keys)
- Natural language queries
- Real-time pattern retrieval
- Source citations

**Start**: `./scripts/start_adk_ollama.sh` or `python scripts/start_ollama_agent.py`

### 2. 🐍 Python API
Programmatic access for integration:
```python
from document_store.orchestrator import DocumentStoreOrchestrator

orchestrator = DocumentStoreOrchestrator(
    persist_directory="./data/chroma_db",
    collection_name="architecture_patterns",
)

result = orchestrator.query_patterns(
    query="What RAG patterns work best for clinical notes?",
    n_results=5
)
print(result["response"])
```

### 3. ⌨️ CLI
Command-line interface for quick queries:
```bash
python scripts/query_with_ollama.py "Explain Contextual Retrieval"
```

---

## 🏗️ Architecture

### Components

```
pattern-query-app/
├── src/document_store/          # Core application
│   ├── orchestrator.py           # Main orchestration layer
│   ├── storage/
│   │   └── vector_store.py       # ChromaDB vector store
│   ├── search/
│   │   ├── rag_query.py          # RAG query interface
│   │   └── web_search.py         # Web search integration
│   ├── processors/
│   │   └── docling_processor.py  # Document processing
│   ├── agents/
│   │   ├── adk_agent.py          # Google ADK agent
│   │   └── ollama_agent.py       # Ollama local LLM
│   └── healthcare/               # Healthcare data connectors
│       ├── fhir_client.py
│       ├── ehr_client.py
│       ├── bigquery_connector.py
│       ├── spanner_connector.py
│       └── pubsub_events.py
├── .adk/agents/                  # ADK agent packages
│   ├── gemini_agent/
│   └── ollama_agent/
├── scripts/                      # Utility scripts
├── examples/                     # Usage examples
└── docs/                         # App documentation
```

### Technology Stack
- **Vector Store**: ChromaDB (embedded, file-based)
- **Document Processing**: Docling (PDF, DOCX, MD)
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)
- **LLM Interfaces**:
  - Google ADK (cloud-based, latest Google AI)
  - Ollama (local, Gemma3:4b or Qwen3:14b)
- **Web Framework**: FastAPI + Uvicorn
- **Healthcare Integrations**: FHIR, BigQuery, Cloud Spanner

---

## 📊 Features

### Core Features
✅ **Vector Search**: Semantic search over 116 pattern documents
✅ **RAG Query**: Retrieval-Augmented Generation for accurate answers
✅ **Multi-Agent**: Google ADK and Ollama agents
✅ **Web UI**: Interactive pattern exploration
✅ **Source Citations**: Every answer cites source documents
✅ **Metadata Filtering**: Filter by pattern type, vendor, use case

### Advanced Features
✅ **Healthcare Data Integration**: FHIR, EHR, BigQuery connectors
✅ **Web Search**: Supplement pattern library with live web results
✅ **Local LLMs**: 100% local with Ollama (no API keys)
✅ **Pattern Validation**: Validate pattern documentation quality
✅ **Bulk Ingestion**: Ingest all patterns in one command

---

## 🛠️ Usage

### Ingesting Patterns

```bash
# Ingest all patterns from ../pattern-library/
python scripts/ingest_all_docs.py

# Verify ingestion
python -c "from src.document_store.storage.vector_store import VectorStore; vs = VectorStore(); print(vs.get_collection_info())"
```

### Querying Patterns

**Web UI** (Recommended):
```bash
./scripts/start_adk_ollama.sh
# Open http://127.0.0.1:8080
```

**Python API**:
```python
from document_store.orchestrator import DocumentStoreOrchestrator

orch = DocumentStoreOrchestrator()
result = orch.query_patterns("What is RAPTOR RAG?")
print(result["response"])
```

**CLI**:
```bash
python scripts/query_with_ollama.py "Compare RAPTOR vs Basic RAG"
```

### Healthcare Data Integration

```python
from document_store.healthcare.fhir_client import FHIRClient

# Query FHIR resources
fhir = FHIRClient(base_url="https://your-fhir-server.com")
patients = fhir.search_patients(family="Smith")

# Combine with pattern library
result = orchestrator.query_patterns(
    f"Best RAG pattern for summarizing patient {patients[0]['id']}?"
)
```

---

## 🎛️ Configuration

### Environment Variables

```bash
# Ollama Configuration
export OLLAMA_MODEL="gemma3:4b"           # or qwen3:14b
export OLLAMA_BASE_URL="http://localhost:11434/v1"

# ADK Configuration
export ADK_AGENT_NAME="ollama_pattern_agent"
export ADK_PERSIST_DIRECTORY="data/chroma_db"
export ADK_COLLECTION_NAME="architecture_patterns"

# Healthcare Integration (Optional)
export FHIR_BASE_URL="https://your-fhir-server.com"
export BIGQUERY_PROJECT="your-project-id"
export SPANNER_INSTANCE="your-instance-id"
```

### Supported LLM Models

**Ollama (Local)**:
- `gemma3:4b` - Fast, Google's 4B model (recommended)
- `qwen3:14b` - More detailed, 14B model
- `llama3` - Meta's Llama 3
- Any Ollama model

**Google ADK (Cloud)**:
- `gemini-1.5-pro` - Best quality
- `gemini-1.5-flash` - Fast, cost-effective
- `gemini-1.0-pro` - Stable

---

## 📖 Documentation

- [Setup Guide](docs/ADK_QUICKSTART.md) - Complete ADK setup
- [Agent Setup](docs/agent-setup-guide.md) - Configure agents
- [Document Store Setup](docs/document-store-setup.md) - ChromaDB configuration
- [Troubleshooting](docs/troubleshooting-guide.md) - Common issues
- [Technical Tools](docs/technical-tools-framework.md) - Tool catalog

---

## 🧪 Examples

See [`examples/`](examples/) for working code:
- `adk_agent_query.py` - Query using Google ADK
- `ollama_rag_example.py` - Local RAG with Ollama
- `query_patterns.py` - Pattern querying examples
- `ingest_documents.py` - Custom ingestion
- `healthcare_data_integration.py` - FHIR/EHR integration
- `web_search_example.py` - Web search integration

---

## 🧪 Evaluation & Testing

### CSV Formatting Evaluation

Test LLM model capabilities for generating properly formatted CSV output across different Ollama models.

**Quick Start:**
```bash
# Validate an existing response
python3 scripts/run_simple_eval.py \
  --eval-file csv_format_eval_set.json \
  --validate-response /path/to/agent_response.txt

# Generate test plan for multiple models
python3 scripts/run_simple_eval.py \
  --eval-type csv \
  --eval-file csv_format_eval_set.json \
  --models qwen3:14b,gemma2:27b,llama3.1:70b
```

**Manual Testing Workflow:**

1. **Configure Model** (in `.env`):
   ```bash
   OLLAMA_MODEL=gemma2:27b  # Change to model you want to test
   ```

2. **Start Ollama Agent**:
   ```bash
   ./scripts/start_adk_ollama.sh
   # Opens http://127.0.0.1:8000
   ```

3. **Run Test Query** (in web UI):
   ```
   list the 'Complete Techniques Catalog' as csv that i can copy paste into google sheet
   ```

4. **Save Response**:
   - Copy the full agent response
   - Save to `test/llm_response_<model>.txt`
   - Example: `test/llm_response_gemma2_27b.txt`

5. **Validate Response**:
   ```bash
   python3 scripts/run_simple_eval.py \
     --eval-file csv_format_eval_set.json \
     --validate-response test/llm_response_gemma2_27b.txt
   ```

6. **Repeat for Other Models**:
   - Update `OLLAMA_MODEL` in `.env`
   - Restart agent
   - Run query and save response
   - Validate

**Expected Results:**
- ✅ **Valid CSV**: 163 rows, 7 columns, proper quoting
- ❌ **Invalid**: Markdown outline, wrong structure, field splitting

**Current Results:**
- ✅ Gemini (gemini-2.0-flash-exp): PASS (163 rows, 7 columns)
- ❌ Qwen3:14b: FAIL (returns markdown outline)
- ❌ mannix/deepseek-coder-v2-lite-instruct:q8_0: FAIL (10 rows, 3 columns - partial response)
- ❌ granite4:latest: FAIL (0 rows, 1 column - no valid CSV output)
- ❌ gemma3:4b-it-qat: FAIL (36 rows, many empty columns - partial response)
- ❌ gpt-oss:latest: FAIL (13 rows, 9 columns - severe truncation)
- ⚠️ Gemma2:27b, Llama3.1:70b: Not yet tested

📖 **Detailed Guide**: See [docs/CSV_EVALUATION.md](docs/CSV_EVALUATION.md) for complete documentation.

---

## 🔧 Development

### Running Tests
```bash
python scripts/initialize_and_test.py
```

### Pattern Validation
```bash
python scripts/pattern_validator.py
```

### RAG Evaluation
```bash
# Standard RAG query evaluation
python3 scripts/run_simple_eval.py --eval-file simple_eval_set.json
```

### Custom Ingestion
```python
from document_store.orchestrator import DocumentStoreOrchestrator

orch = DocumentStoreOrchestrator()
orch.ingest_documents([
    "/path/to/custom-pattern.md",
    "/path/to/another-pattern.pdf"
])
```

---

## 🚀 Deployment

### Local Development
```bash
python scripts/start_ollama_agent.py
```

### Production (ADK)
```bash
export GOOGLE_CLOUD_PROJECT="your-project"
export ADK_WEB_PORT="8080"
./scripts/start_adk_ollama.sh
```

### Docker (Coming Soon)
```bash
docker build -t pattern-query-app .
docker run -p 8080:8080 pattern-query-app
```

---

## 📊 Performance

- **Query Latency**: 500ms-2s (with Ollama local)
- **Ingestion Speed**: ~100 docs/minute
- **Storage**: ~5MB for 116 patterns + embeddings
- **Memory**: 2-4GB RAM (with Gemma3:4b)

---

## 🤝 Contributing

Contributions welcome! Areas of focus:
- New healthcare data connectors
- Performance optimizations
- Additional LLM integrations
- UI/UX improvements

---

## 📝 License

Part of the AI Summarization Reference Architecture project. See root README for license.

---

## 🔗 Related

- **[Pattern Library](../pattern-library/)**: The documentation this app queries
- **[Project Docs](../project/)**: Project specifications and planning

---

**This is a supporting tool** for the Healthcare AI Pattern Library. For the patterns themselves, see [`../pattern-library/`](../pattern-library/).
