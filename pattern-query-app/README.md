# Pattern Query Application

**An intelligent document store and query system for the Healthcare AI Pattern Library.**

This application indexes, stores, and queries the [Healthcare AI Pattern Library](../pattern-library/) using vector search and AI agents. It's a **tool to work with the patterns**, not the patterns themselves.

> **Looking for the patterns?** See [`../pattern-library/`](../pattern-library/) for the reference architecture documentation.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ (Python 3.10+ recommended)
- Ollama (for local LLM) or Google Cloud account (for ADK)
- 500MB disk space for ChromaDB

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Ingest pattern library into ChromaDB
python scripts/ingest_all_docs.py

# Start the query interface
python scripts/start_ollama_agent.py  # Or use ADK: ./scripts/start_adk_ollama.sh
```

### Access the Web UI
Open http://127.0.0.1:8080 in your browser to query patterns!

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
│   ├── chromadb_agent/
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

## 🔧 Development

### Running Tests
```bash
python scripts/initialize_and_test.py
```

### Pattern Validation
```bash
python scripts/pattern_validator.py
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
