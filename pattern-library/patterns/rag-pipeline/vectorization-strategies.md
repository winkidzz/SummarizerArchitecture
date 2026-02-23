# Vectorization Strategies

## Overview
Vectorization strategies define **how and when** text chunks are converted into vector embeddings at scale. While [Embedding Model Selection](./embedding-model-selection.md) covers *which model* to use, this pattern covers the *operational strategy* — batch vs. real-time processing, parallelism, caching, multi-modal handling, and fine-tuning approaches.

## Pipeline Stage
- [ ] Data Ingestion
- [ ] Document Processing & Extraction
- [ ] Chunking & Splitting
- [x] Embedding & Vectorization
- [ ] Vector Store & Indexing
- [ ] Index Maintenance & Freshness
- [ ] Pipeline Orchestration
- [ ] Evaluation & Quality Assurance

## Architecture

### Pipeline Architecture
```mermaid
graph LR
    CQ[Chunk Queue] --> BS{Batch or<br/>Real-Time?}
    BS -->|Batch| BP[Batch Processor]
    BS -->|Real-Time| RT[Real-Time Processor]
    BP --> EC[Embedding Cache]
    RT --> EC
    EC --> VS[Vector Store Writer]

    style BS fill:#fff3e0,stroke:#333
```

### Strategy Variations

#### Variation A: Batch Vectorization
- **Description**: Collect chunks in a queue, embed in large batches on a schedule
- **Best For**: Initial corpus indexing, nightly data refreshes, cost optimization
- **Trade-off**: High throughput and lower cost, but latency between document ingestion and searchability

#### Variation B: Real-Time Vectorization
- **Description**: Embed each chunk immediately upon arrival
- **Best For**: Near real-time freshness requirements, streaming data sources
- **Trade-off**: Lowest latency but higher per-chunk cost and lower throughput

#### Variation C: Hybrid (Micro-Batch)
- **Description**: Buffer chunks for short intervals (1-60 seconds), then batch embed
- **Best For**: Balancing freshness with cost efficiency
- **Trade-off**: Near-real-time with batch-level efficiency

#### Variation D: Multi-Modal Vectorization
- **Description**: Use different embedding models for different content types (text, images, tables)
- **Best For**: Documents with mixed content (medical imaging + clinical notes)
- **Trade-off**: Best cross-modal retrieval but higher complexity

#### Variation E: Fine-Tuned Vectorization
- **Description**: Fine-tune the embedding model on domain-specific data before vectorization
- **Best For**: Specialized domains where off-the-shelf models underperform
- **Trade-off**: Highest domain accuracy but requires training pipeline and labeled data

## Implementation Examples

### Batch Vectorization
```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def batch_embed(chunks: list[str], batch_size: int = 100) -> list[list[float]]:
    all_embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        response = await client.embeddings.create(
            input=batch,
            model="text-embedding-3-small",
        )
        all_embeddings.extend([item.embedding for item in response.data])
    return all_embeddings
```

### Embedding Cache
```python
import hashlib
import redis
import json

cache = redis.Redis()

def cached_embed(chunk: str, embed_fn) -> list[float]:
    key = f"emb:{hashlib.sha256(chunk.encode()).hexdigest()}"
    cached = cache.get(key)
    if cached:
        return json.loads(cached)
    embedding = embed_fn(chunk)
    cache.set(key, json.dumps(embedding), ex=86400)  # 24h TTL
    return embedding
```

## Performance Characteristics

### Pipeline Throughput
- Batch (cloud API): 500-2,000 chunks/sec with parallelism
- Real-time (cloud API): 10-100 chunks/sec per connection
- Batch (self-hosted GPU): 1,000-10,000 chunks/sec
- Micro-batch: 100-500 chunks/sec (balanced)

### Cost Optimization
- Embedding caching can reduce costs by 30-70% for corpora with overlapping content
- Batch processing reduces API overhead vs. individual calls
- Dimension reduction (e.g., 3072 → 1024) reduces storage cost with minimal quality loss

## Healthcare Considerations

### HIPAA Compliance
- Cached embeddings may constitute derived PHI — apply same security controls
- Batch processing logs should not contain PHI content, only document IDs

### Clinical Data Specifics
- Consider separate embedding strategies for different clinical document types
- Medical images require vision-language models (CLIP, BiomedCLIP)

## Related Patterns
- [Embedding Model Selection](./embedding-model-selection.md) — Which model to use for vectorization
- [Vector Database Selection](./vector-database-selection.md) — Next stage: storing the vectors
- [Index Freshness Patterns](./index-freshness-patterns.md) — How vectorization timing affects freshness
- [Pipeline Orchestration Patterns](./pipeline-orchestration-patterns.md) — Scheduling batch vectorization

## References
- [OpenAI Batch API](https://platform.openai.com/docs/guides/batch)
- [ONNX Runtime for Efficient Inference](https://onnxruntime.ai/)

## Version History
- **v1.0** (2026-02-05): Initial version
