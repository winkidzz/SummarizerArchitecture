# AI Summarization Reference Architecture

**A monorepo containing healthcare AI architecture patterns AND a tool to query them.**

This project contains TWO distinct components:

1. **[📚 Pattern Library](pattern-library/)** - Healthcare AI architecture documentation (116 patterns)
2. **[🔍 Query Application](pattern-query-app/)** - Tool to index and search the patterns

---

## 🎯 What Is This Project?

This is a **monorepo** that combines:

### 📚 [Healthcare AI Pattern Library](pattern-library/)
**A comprehensive reference architecture** documenting 87 AI patterns, 6 vendor guides, and 3 healthcare use cases.

- **Purpose**: Documentation and blueprints for building healthcare AI systems
- **Content**: RAG patterns, AI design patterns, HIPAA guidance, vendor implementations
- **Format**: 116 markdown files with architecture diagrams and code examples
- **Audience**: Healthcare developers, AI architects, ML engineers

**[→ Browse the Pattern Library](pattern-library/)**

### 🔍 [Pattern Query Application](pattern-query-app/)
**An intelligent document store** that indexes and queries the pattern library using vector search and AI agents.

- **Purpose**: Tool to search and interact with the patterns
- **Technology**: ChromaDB, Google ADK, Ollama, FastAPI
- **Features**: Web UI, Python API, CLI, healthcare data connectors
- **Audience**: Developers wanting to query patterns programmatically

**[→ Use the Query Application](pattern-query-app/)**

---

## 🚀 Quick Start

### For Pattern Users (Recommended)
**Just want to read the patterns? Start here:**

```bash
# Browse patterns in your favorite markdown viewer
cd pattern-library/
ls patterns/rag/           # RAG patterns
ls patterns/ai-design/     # AI design patterns
ls use-cases/              # Healthcare use cases
ls vendor-guides/          # Implementation guides
```

**[📖 Pattern Library README](pattern-library/README.md)**

### For Application Users
**Want to query patterns with an AI agent?**

```bash
# Install dependencies
cd pattern-query-app/
pip install -r requirements.txt

# Ingest patterns into ChromaDB
python scripts/ingest_all_docs.py

# Start web UI (Ollama - 100% local)
python scripts/start_ollama_agent.py
# → Open http://127.0.0.1:8080

# Or use Google ADK
./scripts/start_adk_ollama.sh
```

**[🔍 Query App README](pattern-query-app/README.md)**

---

## 📁 Repository Structure

```
AI-Summarization-Reference-Architecture/
│
├── README.md                      # ← You are here
│
├── 📚 pattern-library/            # THE PATTERNS (Documentation)
│   ├── README.md                  # Pattern library overview
│   ├── patterns/
│   │   ├── rag/                   # 24 RAG patterns
│   │   │   ├── basic-rag.md
│   │   │   ├── contextual-retrieval.md
│   │   │   ├── raptor-rag.md
│   │   │   └── ...
│   │   └── ai-design/             # 63 AI design patterns
│   │       ├── deployment/        # 8 patterns
│   │       ├── explainability/    # 6 patterns
│   │       ├── mlops/             # 7 patterns
│   │       ├── security/          # 6 patterns
│   │       └── ...
│   ├── use-cases/                 # 3 healthcare scenarios
│   ├── vendor-guides/             # 6 implementation guides
│   ├── framework/                 # Architecture guidance
│   └── templates/                 # Pattern templates
│
├── 🔍 pattern-query-app/          # THE APPLICATION (Tool)
│   ├── README.md                  # App overview & setup
│   ├── src/                       # Application source code
│   │   └── document_store/
│   ├── scripts/                   # Ingestion, setup, query
│   ├── examples/                  # Usage examples
│   ├── .adk/                      # ADK agent packages
│   ├── docs/                      # App documentation
│   ├── requirements.txt
│   └── setup.py
│
├── 📋 project/                    # PROJECT INFRASTRUCTURE
│   ├── specs/                     # Project specifications
│   └── memory/                    # Project constitution
│
├── 📊 data/                       # RUNTIME DATA (gitignored)
│   └── chroma_db/                 # Vector database
│
├── CLAUDE.md                      # Claude AI configuration
└── IMPLEMENTATION_SUMMARY.md      # Implementation notes
```

---

## 🎯 Use Cases

### "I want to learn about healthcare AI patterns"
→ **Browse [pattern-library/](pattern-library/)**
- Read markdown files directly
- No installation required
- Patterns are vendor-agnostic with multi-vendor examples

### "I want to query patterns with AI"
→ **Use [pattern-query-app/](pattern-query-app/)**
- Install and run the app
- Query via web UI, Python API, or CLI
- Get AI-powered answers with source citations

### "I want to implement a pattern in my system"
1. **Find your pattern** in [pattern-library/](pattern-library/)
2. **Read implementation guide** in [pattern-library/vendor-guides/](pattern-library/vendor-guides/)
3. **Copy code examples** (production-ready)
4. **Adapt to your use case**

### "I want to contribute a new pattern"
1. **Use template** from [pattern-library/templates/](pattern-library/templates/)
2. **Follow pattern structure**
3. **Include healthcare examples**
4. **Submit PR**

---

## 📚 Pattern Library Highlights

### RAG Patterns (24 patterns)
- **Basic RAG**: Foundational retrieval-augmented generation
- **Contextual Retrieval**: 49-67% error reduction (Anthropic Sept 2024)
- **RAPTOR RAG**: Recursive abstractive processing (25-40% improvement)
- **Multi-Modal RAG**: Text + images + audio for medical data
- **Long Context**: 200K-2M token strategies for full patient histories

**[→ Browse all RAG patterns](pattern-library/patterns/rag/)**

### AI Design Patterns (63 patterns)
- **Deployment** (8): A/B testing, canary, blue-green, edge
- **MLOps** (7): CI/CD, model registry, experiment tracking
- **Security** (6): Differential privacy, encryption, watermarking
- **Performance** (7): Caching, quantization, pruning, batching

**[→ Browse all AI design patterns](pattern-library/patterns/ai-design/)**

### Healthcare Use Cases (3 scenarios)
- Patient Record Summarization
- Clinical Note Generation (SOAP notes)
- Real-Time Clinical Data Monitoring

**[→ Browse use cases](pattern-library/use-cases/)**

### Vendor Guides (6 platforms)
- Anthropic Claude (HIPAA BAA, Prompt Caching)
- Google Vertex AI (2M context, Healthcare API)
- Azure OpenAI (HIPAA, PHI handling)
- AWS Bedrock (Knowledge Bases, HealthLake)
- LangChain (Multi-vendor, FHIR)
- Google ADK (Agent Development Kit)

**[→ Browse vendor guides](pattern-library/vendor-guides/)**

---

## 🔍 Query Application Highlights

### Features
✅ **Vector Search**: Semantic search over all patterns
✅ **RAG Query**: AI-powered answers with citations
✅ **Web UI**: Interactive pattern exploration
✅ **Multi-LLM**: Google ADK (cloud) + Ollama (local)
✅ **Healthcare Integration**: FHIR, EHR, BigQuery connectors

### Technology
- **Vector Store**: ChromaDB (embedded)
- **Embeddings**: SentenceTransformers
- **LLMs**: Google Gemini (ADK) or Ollama (Gemma3, Qwen3)
- **Web Framework**: FastAPI + Uvicorn
- **Agents**: Google ADK agents

**[→ Explore query app features](pattern-query-app/)**

---

## 🏥 Healthcare Focus

All patterns are designed for healthcare requirements:

✅ **HIPAA Compliance**: PHI handling, encryption, BAAs
✅ **Clinical Accuracy**: Reduce hallucinations, cite sources
✅ **Multi-Modal**: Medical imaging, pathology, ECG
✅ **Integrations**: FHIR, EHR, HL7, BigQuery Healthcare
✅ **Real-Time**: Monitoring, alerts, streaming
✅ **Explainability**: Clinical decision support requirements

---

## 🚀 Supported Vendors

**ALL vendors fully supported** - no restrictions:

✅ Google (Gemini, Vertex AI, Healthcare API)
✅ Anthropic (Claude, HIPAA BAA)
✅ Microsoft (Azure OpenAI, Healthcare APIs)
✅ AWS (Bedrock, HealthLake, Comprehend Medical)
✅ OpenAI (GPT-4, Assistants API)
✅ Local/Ollama (Gemma, Llama, Qwen)
✅ LangChain (multi-vendor orchestration)

Patterns show implementation examples for multiple vendors.

---

## 📊 Project Statistics

### Pattern Library
- **87 patterns** (24 RAG + 63 AI Design)
- **3 use cases** (healthcare scenarios)
- **6 vendor guides** (major platforms)
- **10 framework docs** (guidance)
- **4 templates** (for contributors)
- **116 total markdown files**

### Query Application
- **18 source files** (Python)
- **18 scripts** (setup, ingestion, query)
- **6 examples** (working code)
- **4 ADK agents** (Google ADK + Ollama)

---

## 🤝 Contributing

### Contributing Patterns
1. Use [pattern template](pattern-library/templates/pattern-template.md)
2. Include healthcare examples
3. Provide multi-vendor implementations
4. Add architecture diagrams
5. Submit PR to `pattern-library/`

### Contributing to App
1. Fork the repository
2. Make changes in `pattern-query-app/`
3. Test thoroughly
4. Submit PR with description

---

## 📝 License

This project is part of the AI Summarization Reference Architecture initiative.

---

## 🔗 Navigation

| Component | Description | README |
|-----------|-------------|--------|
| **Pattern Library** | Healthcare AI patterns (documentation) | [📚 README](pattern-library/README.md) |
| **Query Application** | Tool to search patterns (application) | [🔍 README](pattern-query-app/README.md) |
| **Project Docs** | Specifications and planning | [📋 project/](project/) |

---

## 💡 Key Concepts

### This is a Monorepo
- **Pattern Library** = Documentation (can be used standalone)
- **Query Application** = Tool to query documentation (optional)
- Both live in the same repository for convenience

### Clear Separation
- Pattern docs in `pattern-library/`
- Application code in `pattern-query-app/`
- No mixing of concerns

### Independent Usage
- Can use patterns without the app (just read markdown)
- Can use app without contributing patterns (just query)
- Can use both together (full experience)

---

**📚 Start with the patterns**: [pattern-library/](pattern-library/)
**🔍 Or query them with AI**: [pattern-query-app/](pattern-query-app/)
