# API Guide

Complete reference for all REST API endpoints with examples.

## Base URL
```
http://localhost:8000
```

## Interactive Documentation

Visit http://localhost:8000/docs for **Swagger UI** - interactive API documentation where you can try all endpoints in your browser.

## Endpoints

### 1. Root
**GET** `/`

Returns API information.

**Response:**
```json
{
  "name": "Semantic Pattern Query API",
  "version": "1.0.0",
  "status": "running"
}
```

### 2. Health Check
**GET** `/health`

Checks system health and service connectivity.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "qdrant": "connected",
    "elasticsearch": "connected",
    "redis": "connected",
    "ollama": "connected"
  },
  "stats": {
    "qdrant": {...},
    "embedding_models": {...},
    "vector_dimension": 384
  }
}
```

### 3. Query
**POST** `/query`

Query the pattern library using RAG.

**Request Body:**
```json
{
  "query": "What is RAPTOR RAG?",
  "top_k": 10,
  "use_cache": true,
  "user_context": null
}
```

**Response:**
```json
{
  "answer": "RAPTOR RAG is a retrieval technique...",
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

### 4. Ingest ⭐ NEW
**POST** `/ingest`

Trigger ingestion of pattern library files.

**Request Body:**
```json
{
  "directory_path": "../pattern-library",
  "pattern": "**/*.md",
  "force_reingest": false
}
```

**Parameters:**
- `directory_path` (optional): Path to directory containing files. Defaults to `PATTERN_LIBRARY_PATH` env var or `../pattern-library`
- `pattern` (optional): File pattern to match. Default: `**/*.md` (all markdown files recursively)
- `force_reingest` (optional): Force re-ingestion even if document exists. Default: `false`

**Response:**
```json
{
  "status": "success",
  "files_processed": 113,
  "total_chunks": 2450,
  "message": "Successfully ingested 113/113 files, 2450 total chunks",
  "stats": {
    "qdrant": {
      "points_count": 2450,
      "vectors_count": 2450
    },
    "embedding_models": {
      "local": "all-MiniLM-L12-v2",
      "qwen": "qwen3:14b"
    },
    "vector_dimension": 384
  }
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "directory_path": "../pattern-library",
    "pattern": "**/*.md",
    "force_reingest": false
  }'
```

### 5. Stats
**GET** `/stats`

Get system statistics.

**Response:**
```json
{
  "qdrant": {
    "collection_name": "pattern_documents",
    "points_count": 2450,
    "vectors_count": 2450,
    "config": {
      "vector_size": 384,
      "distance": "Cosine",
      "on_disk": true
    }
  },
  "embedding_models": {
    "local": "all-MiniLM-L12-v2",
    "qwen": "qwen3:14b"
  },
  "vector_dimension": 384
}
```

## Usage Examples

### Ingest Pattern Library
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Query After Ingestion
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAPTOR RAG?",
    "top_k": 5
  }'
```

### Check Stats
```bash
curl http://localhost:8000/stats
```

## Python SDK Usage

### Query Pattern Library

```python
import requests

# Query the pattern library
response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "What is RAPTOR RAG?",
        "top_k": 5
    }
)

result = response.json()
print("Answer:", result["answer"])
print(f"Found {len(result['sources'])} sources")
print(f"Cache hit: {result['cache_hit']}")

# Print sources
for i, source in enumerate(result["sources"], 1):
    print(f"\n{i}. {source['source_path']}")
```

### Ingest Documents

```python
import requests

# Ingest pattern library
response = requests.post(
    "http://localhost:8000/ingest",
    json={
        "directory_path": "../pattern-library",
        "pattern": "**/*.md",
        "force_reingest": False
    }
)

result = response.json()
print(f"Ingested {result['files_processed']} files")
print(f"Total chunks: {result['total_chunks']}")
```

### Check System Health

```python
import requests

response = requests.get("http://localhost:8000/health")
health = response.json()

print(f"Status: {health['status']}")
for service, status in health['services'].items():
    print(f"  {service}: {status}")
```

## Advanced Examples

### Using Gemini Embedder

To use Gemini embeddings instead of Ollama, update your `.env`:

```bash
QUERY_EMBEDDER_TYPE=gemini
GEMINI_API_KEY=your-api-key-here
```

Then restart the server. All queries will use Gemini embeddings.

### Batch Queries

```python
import requests
import concurrent.futures

def query_pattern(question):
    response = requests.post(
        "http://localhost:8000/query",
        json={"query": question, "top_k": 3}
    )
    return question, response.json()

questions = [
    "What is RAPTOR RAG?",
    "Explain hybrid retrieval",
    "How does semantic chunking work?",
]

# Query in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(query_pattern, questions))

for question, result in results:
    print(f"\nQ: {question}")
    print(f"A: {result['answer'][:100]}...")
```

### Monitor System Stats

```python
import requests
import time

while True:
    stats = requests.get("http://localhost:8000/stats").json()
    print(f"Documents: {stats['qdrant']['points_count']}")
    print(f"Embedder: {stats['embedding_models']['local']}")
    time.sleep(10)
```

## Error Handling

### Handle Connection Errors

```python
import requests
from requests.exceptions import ConnectionError, Timeout

try:
    response = requests.post(
        "http://localhost:8000/query",
        json={"query": "What is RAG?"},
        timeout=30
    )
    response.raise_for_status()
    result = response.json()
except ConnectionError:
    print("Error: Cannot connect to API server")
    print("Make sure the server is running: ./venv/bin/python3 src/api_server.py")
except Timeout:
    print("Error: Query timeout (>30s)")
except requests.HTTPError as e:
    print(f"HTTP Error: {e.response.status_code}")
    print(e.response.json())
```

### Validate Response

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"query": "What is RAG?"}
)

if response.status_code == 200:
    result = response.json()

    # Validate response structure
    assert "answer" in result, "Missing 'answer' field"
    assert "sources" in result, "Missing 'sources' field"
    assert len(result["sources"]) > 0, "No sources returned"

    print("Query successful!")
    print(result["answer"])
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

## Performance Tips

1. **Use Caching**: Set `use_cache: true` (default) for repeated queries
2. **Adjust top_k**: Lower values (3-5) are faster, higher (10-20) more comprehensive
3. **Parallel Queries**: Use ThreadPoolExecutor for batch queries
4. **Monitor Health**: Check `/health` endpoint before critical operations

## Notes

- The `/ingest` endpoint is **synchronous** - it blocks until ingestion completes
- For large datasets (100+ files), ingestion may take 2-5 minutes
- Semantic cache improves response time by 40%+ for similar queries
- Use `/stats` to monitor document count and system configuration

---

**Next**: See [CONFIGURATION.md](CONFIGURATION.md) for environment variable reference

