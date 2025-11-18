# Query Examples

## Quick Start

The API server is now running! Here's how to query it:

## Method 1: Interactive API Docs (Easiest) 🌟

1. **Open your browser**: http://localhost:8000/docs
2. **Click on** `/query` endpoint
3. **Click** "Try it out"
4. **Enter your query**:
   ```json
   {
     "query": "What is RAPTOR RAG?",
     "top_k": 5,
     "use_cache": true
   }
   ```
5. **Click** "Execute"
6. **See the answer** with sources and citations!

## Method 2: Command Line (curl)

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAPTOR RAG?",
    "top_k": 5
  }'
```

## Method 3: Python Script

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "What is RAPTOR RAG?",
        "top_k": 5
    }
)

result = response.json()
print("Answer:", result["answer"])
print("Sources:", len(result["sources"]))
```

## Method 4: CLI Script

```bash
cd semantic-pattern-query-app
source venv/bin/activate
python scripts/query_example.py "What is RAPTOR RAG?"
```

## Example Queries to Try

### RAG Patterns
- "What is RAPTOR RAG?"
- "Explain hybrid retrieval"
- "How does semantic chunking work?"
- "What is contextual retrieval?"

### AI Design Patterns
- "What is A/B testing for ML models?"
- "Explain model versioning"
- "How does canary deployment work?"

### Healthcare Use Cases
- "How to summarize patient records?"
- "What are best practices for clinical note generation?"

### Vendor Guides
- "How to use LangChain for RAG?"
- "Azure OpenAI implementation guide"

## API Endpoints

- **POST** `/query` - Query the pattern library
- **GET** `/health` - Check system health
- **GET** `/stats` - Get system statistics
- **GET** `/docs` - Interactive API documentation

## Response Format

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

---

**Server is running at**: http://localhost:8000
**API Docs**: http://localhost:8000/docs

