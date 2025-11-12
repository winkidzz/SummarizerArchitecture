# Agent Setup Guide: Google ADK and Ollama

This guide explains how to set up and use Google ADK Agent Library and Ollama for querying and building RAG systems in the AI Summarization Reference Architecture project.

## Overview

The project uses a two-tier agent approach:

1. **Google ADK Agent Library** (Primary): For intelligent, agent-based querying of architecture patterns
2. **Ollama** (Specialized): For local LLM tasks, RAG building, embeddings, and privacy-sensitive operations

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Agent Query Architecture                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │  Google ADK      │──────▶│   Vector Store   │        │
│  │  Agent Library   │      │   (ChromaDB)     │        │
│  │  (Primary)       │      └──────────────────┘        │
│  └──────────────────┘                                   │
│         │                                                │
│         ▼                                                │
│  ┌──────────────────┐                                   │
│  │  Query Results   │                                   │
│  └──────────────────┘                                   │
│                                                         │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │     Ollama       │──────▶│   Vector Store   │        │
│  │  (Specialized)   │      │   (ChromaDB)     │        │
│  └──────────────────┘      └──────────────────┘        │
│         │                                                │
│         ▼                                                │
│  ┌──────────────────┐                                   │
│  │  RAG Response    │                                   │
│  │  Embeddings      │                                   │
│  │  Custom Models   │                                   │
│  └──────────────────┘                                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Google ADK Agent Library Setup

### Installation

```bash
# Install Google ADK (when available)
# pip install google-adk
# Or install from Google Cloud SDK
```

**Note**: Google ADK package structure may vary. Adjust imports based on actual package.

#### Repo Quickstart

1. **Install dependencies**: `pip install -r requirements.txt` (this now pulls `google-adk>=1.18.0`).
2. **Set credentials**: `export GOOGLE_API_KEY="..."` (or add it to `.env`).
3. **Generate/update the agent**: `python scripts/setup_adk_agent.py`.
   - Customise with `--persist-directory`, `--collection-name`, `--model`, or pass `--instruction-file` for bespoke prompts.
   - The script writes `.adk/agents/gemini_agent/agent.py`, which ADK auto-discovers.
4. **Launch the UI** (optional): `scripts/start_adk_default_ui.sh` wraps `adk web --host --port .adk/agents`.
5. **CLI usage**: `adk run .adk/agents/gemini_agent` for a REPL experience.

Refer to `scripts/ADK_SETUP.md` for a concise checklist covering environment variables, troubleshooting, and tips for the Angular-based ADK Web project.

### Features

- **Agent-based Querying**: Intelligent, context-aware querying
- **Prebuilt Plugins**: Access to prebuilt tools and plugins
- **Observability**: Dashboards for token usage, latency, errors
- **Security**: Model Armor for prompt injection screening
- **Testing**: Built-in testing playground

### Usage

```python
from document_store.orchestrator import DocumentStoreOrchestrator

# Initialize with ADK agent
orchestrator = DocumentStoreOrchestrator(
    use_adk_agent=True,  # Enable ADK agent
)

# Query using ADK agent (primary method)
results = orchestrator.query_patterns(
    query="What is basic RAG pattern?",
    use_agent=True,  # Use ADK agent
)
```

### Direct ADK Agent Usage

```python
from document_store.agents.adk_agent import ADKAgentQuery
from document_store.storage.vector_store import VectorStore

vector_store = VectorStore()
adk_agent = ADKAgentQuery(vector_store)

# Query with agent
results = adk_agent.query(
    query="How to implement RAG with Gemini?",
    pattern_type="basic-rag",
    vendor="gemini",
)
```

## Ollama Setup

### Installation

1. **Install Ollama**:
   - Visit [ollama.com](https://ollama.com)
   - Download and install for your platform
   - Or use: `curl -fsSL https://ollama.com/install.sh | sh`

2. **Install Python Package**:
```bash
pip install ollama
```

3. **Start Ollama Service**:
```bash
ollama serve
```

4. **Pull Models**:
```bash
ollama pull llama3
ollama pull mistral
ollama pull gemma
```

### Features

- **Local Execution**: Run models entirely on local hardware
- **Privacy**: No data sent to cloud services
- **Customization**: Create custom models with Modelfile
- **Specialized Tasks**: RAG building, embeddings, custom workflows
- **Model Variety**: Support for Llama, Mistral, Gemma, Qwen, etc.

### Usage

#### Basic RAG with Ollama

```python
from document_store.agents.ollama_agent import OllamaAgent
from document_store.storage.vector_store import VectorStore

vector_store = VectorStore()
ollama_agent = OllamaAgent(
    model="llama3",
    vector_store=vector_store,
)

# Query with RAG
results = ollama_agent.query_with_rag(
    query="What is advanced RAG?",
    n_results=5,
)
```

#### Generate Embeddings

```python
# Generate embeddings using Ollama
texts = ["Document 1", "Document 2"]
embeddings = ollama_agent.generate_embeddings(texts)
```

#### Build Custom Model

```python
# Create custom model with Modelfile
modelfile = """
FROM llama3
SYSTEM You are an expert in AI architecture patterns.
PARAMETER temperature 0.7
"""

ollama_agent.create_custom_model(
    model_name="architecture-expert",
    base_model="llama3",
    modelfile_content=modelfile,
)
```

## Integration with Orchestrator

The orchestrator supports both agents:

```python
from document_store.orchestrator import DocumentStoreOrchestrator

orchestrator = DocumentStoreOrchestrator(
    use_adk_agent=True,        # Enable ADK agent (primary)
    ollama_model="llama3",     # Enable Ollama for specialized tasks
)

# Primary querying with ADK agent
results = orchestrator.query_patterns(
    query="What is basic RAG?",
    use_agent=True,
)

# Specialized RAG with Ollama
results = orchestrator.query_patterns(
    query="Explain advanced RAG",
    use_ollama_rag=True,  # Use Ollama for RAG response
)
```

## When to Use What

### Use Google ADK Agent When:
- ✅ Primary querying interface
- ✅ Need intelligent agent reasoning
- ✅ Want observability and debugging
- ✅ Need security features (Model Armor)
- ✅ Using prebuilt plugins and tools
- ✅ Production querying workflows

### Use Ollama When:
- ✅ Building RAG systems
- ✅ Generating embeddings locally
- ✅ Privacy-sensitive operations
- ✅ Custom model experimentation
- ✅ Specialized agent workflows
- ✅ Offline/local execution required
- ✅ Model customization needed

## Model Selection Strategy

1. **Querying**: Google ADK Agent Library (primary)
2. **RAG Building**: Ollama with appropriate model (llama3, mistral, etc.)
3. **Embeddings**: Ollama models or sentence-transformers
4. **Specialized Tasks**: Ollama with custom Modelfiles
5. **Production Patterns**: Multi-vendor support (ADK, Ollama, cloud models)

## Troubleshooting

### Google ADK Issues

**Problem**: ADK not found
**Solution**: 
- Install from Google Cloud SDK
- Check package name and version
- Verify Google Cloud credentials

**Problem**: Agent initialization fails
**Solution**:
- Check ADK configuration
- Verify vector store is initialized
- Check logs for specific errors

### Ollama Issues

**Problem**: Ollama connection failed
**Solution**:
- Ensure Ollama service is running: `ollama serve`
- Check base_url (default: http://localhost:11434)
- Verify Ollama is installed

**Problem**: Model not found
**Solution**:
- Pull the model: `ollama pull <model-name>`
- List available models: `ollama list`
- Check model name spelling

**Problem**: Embedding generation fails
**Solution**:
- Ensure model supports embeddings
- Check model is loaded
- Verify text input format

## Best Practices

1. **Primary Querying**: Always use Google ADK agent as primary interface
2. **Specialized Tasks**: Use Ollama for RAG building and embeddings
3. **Model Selection**: Choose appropriate Ollama model for task
4. **Privacy**: Use Ollama for sensitive data
5. **Customization**: Create custom Ollama models for specific use cases
6. **Testing**: Test both agents independently before integration
7. **Monitoring**: Monitor ADK agent observability dashboards
8. **Fallback**: Implement fallback to direct RAG if agents fail

## Examples

See example scripts:
- `examples/adk_agent_query.py`: ADK agent querying
- `examples/ollama_rag_example.py`: Ollama RAG usage

## Next Steps

1. Install Google ADK (when available)
2. Set up Ollama and pull models
3. Test agent integrations
4. Customize models for your use case
5. Integrate into your RAG systems
