# Quick Start - Query the App

## 1. Start the API Server

```bash
cd semantic-pattern-query-app
source venv/bin/activate
python src/api_server.py
```

Server will start at: **http://localhost:8000**

## 2. Query Methods

### Option A: Interactive API Docs (Easiest)
1. Open browser: http://localhost:8000/docs
2. Click `/query` endpoint
3. Click "Try it out"
4. Enter query: `"What is RAPTOR RAG?"`
5. Click "Execute"

### Option B: Command Line
```bash
python scripts/query_example.py "What is RAPTOR RAG?"
```

### Option C: HTTP Request
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAPTOR RAG?", "top_k": 5}'
```

### Option D: Python Code
```python
from src.document_store.orchestrator import SemanticPatternOrchestrator

orchestrator = SemanticPatternOrchestrator()
result = orchestrator.query("What is RAPTOR RAG?", top_k=5)
print(result["answer"])
```

## 3. Example Queries

- "What is RAPTOR RAG?"
- "Explain hybrid retrieval"
- "How does semantic chunking work?"
- "What are best practices for RAG in healthcare?"

