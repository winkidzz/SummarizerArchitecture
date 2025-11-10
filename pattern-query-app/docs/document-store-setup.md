# Document Store Setup Guide

This guide explains how to set up and use the document store for the AI Summarization Reference Architecture project.

## Overview

The document store provides:
- **Document Processing**: Convert various document formats (PDF, DOCX, PPTX, etc.) into structured data using Docling
- **Embedded Storage**: Store processed documents in a local file-based vector database (ChromaDB)
- **RAG Query Interface**: Query the knowledge base for architecture patterns
- **Web Search Integration**: Dynamically retrieve relevant content from the web

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

Key dependencies:
- `docling`: Document processing framework
- `chromadb`: Embedded vector database
- `sentence-transformers`: Embedding models
- `duckduckgo-search`: Web search tool

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Document Store Architecture                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐      ┌──────────────┐               │
│  │   Docling    │──────▶│   Vector     │               │
│  │  Processor   │      │    Store     │               │
│  └──────────────┘      │  (ChromaDB)  │               │
│                         └──────┬───────┘               │
│                                │                        │
│                         ┌──────▼───────┐               │
│                         │ RAG Query    │               │
│                         │  Interface   │               │
│                         └──────┬───────┘               │
│                                │                        │
│  ┌──────────────┐      ┌──────▼───────┐               │
│  │  Web Search  │──────▶│ Orchestrator │               │
│  │     Tool     │      │              │               │
│  └──────────────┘      └──────────────┘               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Usage

### 1. Initialize the Document Store

```python
from document_store.orchestrator import DocumentStoreOrchestrator

orchestrator = DocumentStoreOrchestrator(
    persist_directory="./data/chroma_db",
    collection_name="architecture_patterns",
)
```

### 2. Ingest Documents

```python
# Ingest single document
orchestrator.ingest_documents([
    "./docs/patterns/basic-rag.md"
])

# Ingest multiple documents
orchestrator.ingest_documents([
    "./docs/patterns/",
    "./specs/001-ai-summarization-reference-architecture/",
])
```

### 3. Query Patterns

```python
# Simple query
results = orchestrator.query_patterns(
    query="What is basic RAG pattern?",
    n_results=5
)

# Query with filters
results = orchestrator.query_patterns(
    query="RAG implementation",
    pattern_type="basic-rag",
    vendor="gemini",
    n_results=3
)
```

### 4. Web Search Integration

```python
from document_store.search.web_search import WebSearchTool

web_search = WebSearchTool(backend="duckduckgo")
results = web_search.search_architecture_patterns(
    pattern_name="advanced RAG",
    max_results=10
)
```

## Directory Structure

```
.
├── src/
│   └── document_store/
│       ├── __init__.py
│       ├── orchestrator.py
│       ├── processors/
│       │   ├── __init__.py
│       │   └── docling_processor.py
│       ├── storage/
│       │   ├── __init__.py
│       │   └── vector_store.py
│       └── search/
│           ├── __init__.py
│           ├── rag_query.py
│           └── web_search.py
├── examples/
│   ├── ingest_documents.py
│   ├── query_patterns.py
│   └── web_search_example.py
├── data/
│   └── chroma_db/          # ChromaDB storage (auto-created)
└── requirements.txt
```

## Configuration

### Embedding Models

Default: `all-MiniLM-L6-v2` (sentence-transformers)

To use a different model:

```python
orchestrator = DocumentStoreOrchestrator(
    embedding_model="all-mpnet-base-v2"  # Larger, more accurate model
)
```

### Storage Location

The vector store is stored in `./data/chroma_db/` by default. You can change this:

```python
orchestrator = DocumentStoreOrchestrator(
    persist_directory="./custom/path/to/storage"
)
```

## Example Workflows

### Workflow 1: Initial Setup

1. Process existing documentation:
```python
orchestrator.ingest_documents([
    "./docs/patterns/",
    "./docs/use-cases/",
    "./specs/",
])
```

2. Verify ingestion:
```python
info = orchestrator.get_store_info()
print(f"Documents in store: {info['document_count']}")
```

### Workflow 2: Querying Patterns

```python
# Find patterns for a specific use case
results = orchestrator.query_patterns(
    query="document summarization use case",
    n_results=5
)

# Get vendor-specific patterns
results = orchestrator.query_patterns(
    query="Gemini implementation",
    vendor="gemini"
)
```

### Workflow 3: Updating Knowledge Base

```python
# Search for new patterns
search_results = orchestrator.search_and_ingest(
    query="latest RAG patterns 2024",
    max_results=10
)

# Process and ingest new documents
orchestrator.ingest_documents([
    "./new_patterns/pattern-x.md"
])
```

## Troubleshooting

### Issue: Docling Import Error

**Solution**: Install docling:
```bash
pip install docling
```

### Issue: ChromaDB Import Error

**Solution**: Install chromadb:
```bash
pip install chromadb
```

### Issue: Embedding Model Download

**Solution**: The first run will download the embedding model. Ensure you have internet connectivity.

### Issue: Document Processing Fails

**Solution**: 
- Check that the document format is supported (PDF, DOCX, PPTX, HTML, MD, TXT)
- Verify file paths are correct
- Check file permissions

## Best Practices

1. **Regular Updates**: Periodically update the knowledge base with new patterns
2. **Metadata**: Add meaningful metadata to documents for better filtering
3. **Versioning**: Keep track of document versions in metadata
4. **Backup**: Regularly backup the `data/chroma_db/` directory
5. **Testing**: Test queries before using in production RAG systems

## Integration with RAG Systems

The document store can be integrated with RAG systems:

```python
# In your RAG system
from document_store.orchestrator import DocumentStoreOrchestrator

orchestrator = DocumentStoreOrchestrator()

# Query for relevant patterns
results = orchestrator.query_patterns(
    query=user_query,
    n_results=5
)

# Use results as context for LLM
context = "\n\n".join([r['content'] for r in results['results']])
```

## Next Steps

- Review example scripts in `examples/`
- Customize embedding models for your use case
- Add custom metadata to documents
- Integrate with your RAG systems

