# AI Summarization Reference Architecture

A comprehensive, evolving reference architecture for building AI-powered summarization systems across various use cases.

## Overview

This project provides architecture blueprints, RAG patterns, and implementation guidance for building production-quality AI summarization systems, with a **focus on healthcare use cases**. It serves as a living reference that evolves as new patterns and technologies emerge.

### Important Clarification

- **Project Infrastructure**: Uses local/Ollama/free LLM tools for the AI assistant that helps build and maintain documentation
- **Documented Patterns**: Support **ALL vendors** (Gemini, Anthropic, GCP, Azure, AWS, enterprise platforms) - **NO restrictions**
- **Healthcare Focus**: Patterns designed for healthcare summarization (medical documents, clinical notes, patient records)
- **Cost-Effective Options**: Shown as alternatives for development/testing, not constraints for production patterns
- **Enterprise Support**: Full support for enterprise cloud platforms and premium models for production healthcare

## Key Features

- **Pattern Library**: Comprehensive collection of RAG patterns and summarization architectures
- **Use Case Guidance**: Clear guidance on when to use which pattern for specific use cases
- **Full Vendor Support**: Implementation examples for ALL vendors - Gemini (Vertex AI), Anthropic (Claude), Azure OpenAI, AWS Bedrock, GCP, LangChain, Spring AI, Google ADK, Claude Skills, and more
- **Healthcare Focus**: Patterns designed for healthcare summarization use cases (medical documents, clinical notes, patient records)
- **Cost-Effective Options**: Document cost-effective alternatives (local models, free tiers) as options, not requirements
- **Document Store**: Embedded file-based document store with Docling processing and ChromaDB vector storage
- **Google ADK Agent Library**: Primary agent-based querying interface for intelligent pattern queries
- **Ollama Integration**: Local LLM support for specialized RAG tasks, embeddings, and custom workflows
- **RAG Query Interface**: Query the knowledge base about architecture patterns
- **Web Search Integration**: Dynamically retrieve relevant content to update patterns
- **Evolving Architecture**: Continuously updated with latest patterns and techniques
- **Production Quality**: Tested code examples and comprehensive documentation

## Quick Start

### 1. Install Dependencies

**Windows (PowerShell):**
```powershell
.\scripts\install_dependencies.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/install_dependencies.sh
./scripts/install_dependencies.sh
```

**Manual:**
```bash
pip install -r requirements.txt
```

### 2. Initialize and Test

Run the comprehensive initialization and testing script:

```bash
python scripts/initialize_and_test.py
```

This script:
- Initializes all components
- Tests document processing
- Tests vector store operations
- Tests RAG query interface
- Tests web search
- Tests orchestrator integration
- Tests agent integrations (if available)
- Generates test summary

**Note**: This script extends existing example scripts rather than creating isolated tests, following the project's "Extend, Don't Duplicate" principle.

### 3. Use the Document Store

```python
from document_store.orchestrator import DocumentStoreOrchestrator

# Initialize with agents
orchestrator = DocumentStoreOrchestrator(
    use_adk_agent=True,        # Enable Google ADK agent (primary)
    ollama_model="llama3",     # Enable Ollama for specialized tasks
)

# Ingest documents
orchestrator.ingest_documents(["./docs/patterns/"])

# Query patterns using ADK agent (primary method)
results = orchestrator.query_patterns(
    "What is basic RAG?",
    use_agent=True,
)

# Or use Ollama for specialized RAG
results = orchestrator.query_patterns(
    "Explain advanced RAG",
    use_ollama_rag=True,
)
```

### 4. Launch the Google ADK Web UI (Recommended!)

**Query patterns through an interactive web interface!**

The project includes a fully configured Google ADK agent that provides:
- 🌐 Web-based chat interface at http://127.0.0.1:8000
- 🤖 AI agent powered by Gemini 2.5 Flash
- 🔍 Semantic search across all patterns, guides, and use cases
- 📊 Intelligent responses with source citations

**One-command launch:**
```bash
./scripts/quick_start_adk.sh
```

This script checks all prerequisites, guides you through setup, and launches the web UI.

**Manual launch (if you prefer):**
```bash
# Set your Google AI API key (get from: https://aistudio.google.com/app/apikey)
export GOOGLE_API_KEY='your-key-here'

# Generate the ADK agent configuration
python3 scripts/setup_adk_agent.py

# Launch the web UI
./scripts/start_adk_default_ui.sh

# Or use CLI mode:
adk run .adk/agents/chromadb_agent
```

**📖 Complete Guide:** See [docs/ADK_QUICKSTART.md](docs/ADK_QUICKSTART.md) for detailed instructions, troubleshooting, and advanced usage.

**📋 Technical Reference:** See [scripts/ADK_SETUP.md](scripts/ADK_SETUP.md) for the full checklist and customization options.

## Project Structure

```
.
├── memory/
│   └── constitution.md          # Project principles and guidelines
├── specs/
│   └── [feature-specs]/         # Feature specifications
├── docs/
│   ├── patterns/                # Pattern documentation
│   ├── use-cases/               # Use case documentation
│   ├── vendor-guides/           # Vendor-specific guides
│   ├── document-store-setup.md  # Document store setup guide
│   └── agent-setup-guide.md    # Agent setup guide
├── src/
│   └── document_store/          # Document store implementation
│       ├── processors/          # Docling processor
│       ├── storage/             # ChromaDB vector store
│       ├── search/             # RAG query and web search
│       └── agents/              # ADK and Ollama agents
├── templates/                   # Documentation templates
├── examples/                    # Working code examples
│   ├── ingest_documents.py      # Document ingestion example
│   ├── query_patterns.py        # Query patterns example
│   ├── web_search_example.py   # Web search example
│   ├── adk_agent_query.py       # ADK agent example
│   └── ollama_rag_example.py   # Ollama RAG example
├── scripts/                     # Utility scripts
│   ├── initialize_and_test.py   # Comprehensive test script
│   ├── install_dependencies.ps1 # Windows install script
│   └── install_dependencies.sh  # Linux/Mac install script
└── data/                        # Document store data (gitignored)
```

## Development Principles

### Code Reusability and Extension
- **Extend Existing Scripts**: Do not create separate test files for every question or feature
- **Build on Existing Components**: Use and extend existing scripts, examples, and utilities as much as possible
- **Avoid Silo Test Runs**: Integrate tests into existing workflows rather than creating isolated test suites
- **Incremental Enhancement**: Add functionality to existing scripts rather than creating new ones
- **Unified Testing**: Use existing example scripts as test harnesses, extending them with new test cases
- **Script Evolution**: Evolve existing scripts to handle multiple scenarios rather than creating scenario-specific files

## Documentation

### Core Documentation
- [Constitution](./memory/constitution.md): Project principles and guidelines
- [Specification](./specs/001-ai-summarization-reference-architecture/spec.md): Project specification
- [Implementation Plan](./specs/001-ai-summarization-reference-architecture/plan.md): Implementation roadmap

### Architecture Framework
- [Architecture Framework](./docs/architecture-framework.md): Well-Architected Framework principles
- [Deployment Guide](./docs/deployment-guide.md): Deployment archetypes and strategies
- [Testing Guide](./docs/testing-guide.md): Testing approach and best practices
- [Healthcare Development Lifecycle](./docs/healthcare-development-lifecycle.md): Complete checklist from ideation to production with RACI matrices
- [Technical Tools & Frameworks](./docs/technical-tools-framework.md): Comprehensive catalog of tools organized by Well-Architected Framework pillars
- [Project Planning & Delivery](./docs/project-planning-delivery.md): Project planning, delivery strategies, and resource management by phase

### Patterns and Guides
- [RAG Patterns](./docs/patterns/): Complete RAG pattern library
- [Pattern Index](./docs/patterns/pattern-index.md): Quick pattern selection guide
- [AI Design Patterns](./docs/ai-design-patterns/README.md): Comprehensive catalog of AI design patterns (beyond RAG)
- [AI Design Pattern Index](./docs/ai-design-patterns/pattern-index.md): Quick selection guide for AI design patterns
- [AI Development Techniques](./docs/ai-development-techniques.md): Comprehensive catalog of AI/ML techniques, methodologies, and frameworks
- [Healthcare Focus](./docs/healthcare-focus.md): Healthcare summarization use cases
- [Healthcare Data Access Patterns](./docs/healthcare-data-patterns.md): FHIR, EHR APIs, BigQuery, Spanner, Pub/Sub integration
- [Vendor Selection Guide](./docs/vendor-selection-guide.md): Guide for selecting vendors and platforms
- [Use Cases](./docs/use-cases/): Use case-specific guidance
- [Vendor Guides](./docs/vendor-guides/): Vendor-specific implementation guides
- [Document Store Setup](./docs/document-store-setup.md): Document store setup and usage
- [Agent Setup Guide](./docs/agent-setup-guide.md): Google ADK and Ollama setup

## Examples

Example scripts are available in the `examples/` directory. These scripts serve as both examples and test harnesses:

- `ingest_documents.py`: Ingest documents into the knowledge base
- `query_patterns.py`: Query architecture patterns
- `web_search_example.py`: Use web search to find patterns
- `adk_agent_query.py`: ADK agent querying
- `ollama_rag_example.py`: Ollama RAG usage

**Note**: The `scripts/initialize_and_test.py` script extends these examples to provide comprehensive testing.

## Technology Stack

- **AI Vendors**: Gemini, Anthropic, Azure OpenAI, AWS Bedrock
- **Frameworks**: LangChain, Spring AI, Google ADK
- **Document Processing**: Docling
- **Vector Database**: ChromaDB (embedded)
- **Querying**: Google ADK Agent Library (primary)
- **Local LLM**: Ollama (specialized tasks)
- **Embeddings**: Ollama models or Sentence Transformers
- **Web Search**: DuckDuckGo Search
- **Techniques**: RAG patterns, agentic AI, latest generation techniques
- **Documentation**: Markdown, Mermaid diagrams

## Contributing

This is a reference architecture project. Contributions should:
- Follow the constitution principles
- Include multi-vendor implementations
- Provide clear use case guidance
- Include working code examples
- Maintain documentation quality
- **Extend existing scripts** rather than creating new ones
- **Build on existing components** whenever possible

## License

[Add license information]

## Acknowledgments

This project uses [spec-kit](https://github.com/github/spec-kit) for specification-driven development.
