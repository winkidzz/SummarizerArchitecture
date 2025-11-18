# How to Query the Semantic Pattern Query App

## Quick Start

After ingesting the pattern library, you can query it in three ways:

## Method 1: CLI Script (Easiest)

```bash
cd semantic-pattern-query-app
source venv/bin/activate
python scripts/query_example.py "What is RAPTOR RAG?"
```

**Output:**
```
================================================================================
ANSWER
================================================================================
RAPTOR RAG is a retrieval technique that uses recursive clustering...

================================================================================
SOURCES
================================================================================

[1] patterns/rag/raptor-rag.md
    Type: rag_pattern

================================================================================
METADATA
================================================================================
Cache hit: False
Retrieved docs: 5
Context docs used: 3
```

## Method 2: FastAPI REST API

### Start the API Server

```bash
cd semantic-pattern-query-app
source venv/bin/activate
python src/api_server.py
```

Or using uvicorn directly:
```bash
uvicorn src.api_server.py:app --host 0.0.0.0 --port 8000
```

### Query via HTTP

**Using curl:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAPTOR RAG?",
    "top_k": 5,
    "use_cache": true
  }'
```

**Using Python requests:**
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "What is RAPTOR RAG?",
        "top_k": 5,
        "use_cache": True
    }
)

result = response.json()
print(result["answer"])
print(f"Sources: {len(result['sources'])}")
```

**Using the interactive API docs:**
1. Start the server: `python src/api_server.py`
2. Open browser: http://localhost:8000/docs
3. Click on `/query` endpoint
4. Click "Try it out"
5. Enter your query and click "Execute"

### API Endpoints

**POST `/query`**
- Query the pattern library
- Request body:
  ```json
  {
    "query": "Your question here",
    "top_k": 10,
    "use_cache": true,
    "user_context": null
  }
  ```
- Response:
  ```json
  {
    "answer": "Generated answer...",
    "sources": [
      {
        "document_id": "raptor-rag",
        "source_path": "patterns/rag/raptor-rag.md",
        "document_type": "rag_pattern"
      }
    ],
    "cache_hit": false,
    "retrieved_docs": 5,
    "context_docs_used": 3
  }
  ```

**GET `/health`**
- Check system health and service status
- Returns service connectivity and stats

**GET `/stats`**
- Get system statistics
- Returns Qdrant collection info, embedding models, etc.

## Method 3: Python Programmatic

```python
from src.document_store.orchestrator import SemanticPatternOrchestrator

# Initialize orchestrator
orchestrator = SemanticPatternOrchestrator()

# Query
result = orchestrator.query(
    query="What is RAPTOR RAG?",
    top_k=5,
    use_cache=True
)

# Access results
print(result["answer"])
print(f"Sources: {len(result['sources'])}")
for source in result["sources"]:
    print(f"  - {source.get('source_path')}")
```

## Example Queries

Try these example queries:

```bash
# RAG patterns
python scripts/query_example.py "What is RAPTOR RAG?"
python scripts/query_example.py "Explain hybrid retrieval"
python scripts/query_example.py "How does semantic chunking work?"

# AI design patterns
python scripts/query_example.py "What is A/B testing for ML models?"
python scripts/query_example.py "Explain model versioning"

# Healthcare use cases
python scripts/query_example.py "How to summarize patient records?"
python scripts/query_example.py "What are best practices for clinical note generation?"

# Vendor guides
python scripts/query_example.py "How to use LangChain for RAG?"
python scripts/query_example.py "Azure OpenAI implementation guide"
```

## Query Parameters

### `query` (required)
- Your question or search query
- Example: "What is RAPTOR RAG?"

### `top_k` (optional, default: 10)
- Number of documents to retrieve
- Higher = more context, but slower
- Recommended: 5-10 for most queries

### `use_cache` (optional, default: true)
- Enable semantic caching
- Similar queries return cached results faster
- Set to `false` to always get fresh results

### `user_context` (optional)
- Additional context for multi-tenant scenarios
- Example: `{"organization_id": "org123", "user_id": "user456"}`

## Response Format

```python
{
    "answer": "Generated answer text...",
    "sources": [
        {
            "document_id": "raptor-rag",
            "source_path": "patterns/rag/raptor-rag.md",
            "document_type": "rag_pattern",
            "relevance": "cited"
        }
    ],
    "cache_hit": false,  # True if result came from cache
    "retrieved_docs": 5,  # Number of docs retrieved
    "context_docs_used": 3  # Number of docs used in context
}
```

## Troubleshooting

### "No relevant information found"
- Make sure you've ingested the pattern library first
- Check that services are running (Qdrant, Elasticsearch, Ollama)
- Try a different query

### "Service unhealthy"
- Check that all Docker services are running: `docker-compose ps`
- Verify Ollama is running: `ollama list`
- Check service logs: `docker-compose logs`

### Slow queries
- First query is slower (no cache)
- Subsequent similar queries should be faster
- Check Ollama is running and model is loaded

## Next Steps

1. **Ingest patterns**: `python scripts/ingest_patterns.py`
2. **Start API server**: `python src/api_server.py`
3. **Query via CLI**: `python scripts/query_example.py "Your question"`
4. **Or use API**: Visit http://localhost:8000/docs

---

**Happy Querying!** 🚀

