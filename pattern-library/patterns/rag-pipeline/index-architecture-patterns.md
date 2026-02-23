# Index Architecture Patterns

## Overview
Index architecture patterns define how vector embeddings are structured and organized within a vector database for efficient similarity search. The index type directly impacts query latency, accuracy (recall), memory usage, and build time. Choosing the right index architecture is critical for balancing speed and accuracy at your scale.

## Pipeline Stage
- [ ] Data Ingestion
- [ ] Document Processing & Extraction
- [ ] Chunking & Splitting
- [ ] Embedding & Vectorization
- [x] Vector Store & Indexing
- [ ] Index Maintenance & Freshness
- [ ] Pipeline Orchestration
- [ ] Evaluation & Quality Assurance

## Index Types

### Comparison Matrix

| Index Type | Query Speed | Recall | Build Time | Memory | Best Scale | Best For |
|------------|-------------|--------|------------|--------|------------|----------|
| **Flat (Brute Force)** | Slowest | 100% (exact) | Fastest | Low | < 100K | Development, ground truth |
| **IVF (Inverted File)** | Fast | 90-99% | Medium | Medium | 100K-10M | Cost-effective production |
| **HNSW** | Fastest | 95-99% | Slow | High | 100K-100M | Low-latency production |
| **ScaNN** | Very Fast | 95-99% | Medium | Medium | 1M-1B | Google ecosystem |
| **DiskANN** | Fast | 95-99% | Slow | Low (disk) | 1B+ | Billion-scale, cost-sensitive |
| **Hybrid (Vector + BM25)** | Medium | Varies | Medium | High | Any | Combined semantic + keyword |

### HNSW (Hierarchical Navigable Small World)
- **How it works**: Builds a multi-layer graph where each node connects to its nearest neighbors. Search navigates from coarse upper layers to fine lower layers.
- **Key parameters**: `M` (connections per node, default 16), `ef_construction` (build quality, default 200), `ef_search` (query quality, default 100)
- **Best for**: Most production RAG systems — best speed/recall trade-off

### IVF (Inverted File Index)
- **How it works**: Clusters vectors into partitions using k-means. At query time, only searches the nearest clusters.
- **Key parameters**: `nlist` (number of clusters), `nprobe` (clusters to search at query time)
- **Best for**: Memory-constrained environments, large datasets where HNSW memory is too expensive

### Flat (Brute Force)
- **How it works**: Compares the query vector against every vector in the dataset.
- **Best for**: Small datasets (< 100K), ground truth benchmarking, development

### Hybrid Indexes (Vector + Keyword)
- **How it works**: Combines dense vector search (semantic) with sparse keyword search (BM25/TF-IDF) using score fusion
- **Fusion methods**: Reciprocal Rank Fusion (RRF), weighted linear combination
- **Best for**: Queries requiring both semantic understanding and exact keyword matching

## Configuration & Strategy

### HNSW Tuning Guide
| Parameter | Low Recall / Fast | Balanced | High Recall / Slow |
|-----------|-------------------|----------|-------------------|
| M | 8 | 16 | 32 |
| ef_construction | 100 | 200 | 400 |
| ef_search | 50 | 100 | 200 |

### IVF Tuning Guide
| Scale | nlist | nprobe | Notes |
|-------|-------|--------|-------|
| 100K vectors | 100 | 10 | 10% probe ratio |
| 1M vectors | 1,000 | 50 | 5% probe ratio |
| 10M vectors | 10,000 | 100 | 1% probe ratio |

## Healthcare Considerations
- Hybrid indexes (vector + keyword) are recommended for clinical data — medical terminology, drug names, and ICD codes benefit from exact keyword matching alongside semantic search
- HNSW is the default recommendation for most clinical RAG systems due to its speed/recall balance

## Related Patterns
- [Vector Database Selection](./vector-database-selection.md) — Choose the DB first, then configure the index
- [Embedding Model Selection](./embedding-model-selection.md) — Embedding dimensions affect index sizing
- [Hybrid RAG](../rag/hybrid-rag.md) — RAG pattern that leverages hybrid indexing

## References
- [HNSW Paper](https://arxiv.org/abs/1603.09320)
- [FAISS Index Documentation](https://faiss.ai/)
- [DiskANN Paper](https://arxiv.org/abs/1907.07520)

## Version History
- **v1.0** (2026-02-05): Initial version
