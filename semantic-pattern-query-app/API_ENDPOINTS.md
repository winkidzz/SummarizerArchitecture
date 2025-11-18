# API Endpoints Reference

## Base URL
```
http://localhost:8000
```

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

## Interactive API Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation where you can:
- See all endpoints
- Try requests directly in the browser
- View request/response schemas
- Test the API without writing code

---

**Note**: The `/ingest` endpoint processes files synchronously. For large datasets (100+ files), this may take several minutes. The API will return once ingestion is complete.

