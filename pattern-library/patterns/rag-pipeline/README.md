# RAG Pipeline Engineering Patterns

This directory contains patterns for **building, operating, and optimizing RAG pipelines** — the end-to-end infrastructure that turns unstructured data into searchable, semantically meaningful vectors that power retrieval-augmented generation systems.

> **How this differs from [`patterns/rag/`](../rag/)**: The RAG patterns folder documents *retrieval architecture strategies* (basic, hybrid, agentic, etc.). This folder documents the *pipeline engineering* — the data ingestion, chunking, vectorization, indexing, freshness management, and evaluation infrastructure that those retrieval strategies depend on.

---

## What Is a RAG Pipeline?

A RAG pipeline bridges the gap between unstructured data sources and the retrieval + generation layer. It handles:

1. **Ingesting** data from diverse sources (S3, GCS, databases, SaaS platforms, file systems)
2. **Extracting** content from unstructured formats (PDFs, HTML, DOCX, images, audio)
3. **Chunking** documents into retrieval-friendly segments
4. **Embedding** chunks into vector representations that capture semantic meaning
5. **Indexing** vectors into a vector database for efficient retrieval
6. **Maintaining** index freshness so the system doesn't serve stale or hallucinated answers
7. **Evaluating** pipeline quality to ensure retrieval accuracy

```
┌─────────────┐    ┌──────────────┐    ┌───────────┐    ┌───────────┐    ┌──────────────┐
│  Source Data │───▶│  Extraction  │───▶│ Chunking  │───▶│ Embedding │───▶│ Vector Store │
│  (S3, GCS,  │    │  & Cleaning  │    │ & Split   │    │ & Vectori-│    │  & Indexing  │
│  DB, SaaS)  │    │              │    │ Strategy  │    │  zation   │    │              │
└─────────────┘    └──────────────┘    └───────────┘    └───────────┘    └──────────────┘
                                                                                │
                    ┌──────────────┐    ┌───────────┐    ┌───────────┐          │
                    │  Evaluation  │◀───│ Retrieval │◀───│   Query   │◀─────────┘
                    │  & Quality   │    │  Engine   │    │  (User)   │
                    └──────────────┘    └───────────┘    └───────────┘
```

---

## The Challenge of Unstructured Data

Unstructured data — customer feedback, research papers, clinical documents, knowledge bases — is everywhere. But unlocking its value is hard because:

- **Hard to search**: Traditional keyword search misses context, relationships, and semantics
- **Hard to keep current**: Updating or removing outdated content from unstructured sources is time-consuming
- **Hard to scale**: Processing large volumes for real-time queries is a major engineering challenge
- **Hard to evaluate**: Measuring whether your pipeline is producing quality results requires specialized tooling

RAG pipelines solve this by transforming unstructured data into vector embeddings that represent semantic meaning, then indexing them for efficient retrieval.

---

## Pattern Categories

### Data Ingestion & Extraction
Patterns for connecting to data sources and extracting content from unstructured formats.

1. [Source Connector Patterns](./source-connector-patterns.md) — Connecting to S3, GCS, databases, SaaS, file systems
2. [Document Extraction Patterns](./document-extraction-patterns.md) — Extracting text from PDFs, HTML, DOCX, images, audio

### Chunking & Splitting Strategies
Patterns for breaking documents into retrieval-optimized segments.

3. [Chunking Strategies](./chunking-strategies.md) — Fixed-size, semantic, sentence, paragraph, recursive, structure-aware

### Embedding & Vectorization
Patterns for converting text chunks into vector representations.

4. [Embedding Model Selection](./embedding-model-selection.md) — Choosing and configuring embedding models for your data
5. [Vectorization Strategies](./vectorization-strategies.md) — Batch vs. real-time, multi-modal, fine-tuned embeddings

### Vector Store & Indexing
Patterns for storing and indexing embeddings for efficient retrieval.

6. [Vector Database Selection](./vector-database-selection.md) — Pinecone, Weaviate, ChromaDB, Qdrant, Milvus, pgvector, Astra, Elastic
7. [Index Architecture Patterns](./index-architecture-patterns.md) — HNSW, IVF, flat indexes, hybrid (vector + keyword) indexing

### Index Maintenance & Freshness
Patterns for keeping vector indexes current and preventing hallucinations from stale data.

8. [Index Freshness Patterns](./index-freshness-patterns.md) — Incremental ingestion, scheduled rebuilds, change detection, staleness management

### Pipeline Orchestration & Automation
Patterns for end-to-end pipeline design, scheduling, and operations.

9. [Pipeline Orchestration Patterns](./pipeline-orchestration-patterns.md) — End-to-end workflows, error handling, retry, scheduling, CI/CD

### Evaluation & Quality Assurance
Patterns for measuring and improving pipeline quality.

10. [RAG Evaluation Patterns](./rag-evaluation-patterns.md) — RAGAS, retrieval metrics (MRR, NDCG, Recall@k), generation quality, A/B testing

---

## Pattern Selection Guide

### By Pipeline Stage

| Stage | Pattern | When to Use |
|-------|---------|-------------|
| Ingestion | [Source Connector Patterns](./source-connector-patterns.md) | Connecting to any external data source |
| Extraction | [Document Extraction Patterns](./document-extraction-patterns.md) | Processing PDFs, HTML, images, audio |
| Chunking | [Chunking Strategies](./chunking-strategies.md) | Deciding how to split documents |
| Embedding | [Embedding Model Selection](./embedding-model-selection.md) | Choosing the right embedding model |
| Embedding | [Vectorization Strategies](./vectorization-strategies.md) | Deciding how and when to vectorize |
| Indexing | [Vector Database Selection](./vector-database-selection.md) | Picking a vector store |
| Indexing | [Index Architecture Patterns](./index-architecture-patterns.md) | Designing the index structure |
| Maintenance | [Index Freshness Patterns](./index-freshness-patterns.md) | Keeping indexes current |
| Orchestration | [Pipeline Orchestration Patterns](./pipeline-orchestration-patterns.md) | Automating the full pipeline |
| Evaluation | [RAG Evaluation Patterns](./rag-evaluation-patterns.md) | Measuring quality |

### By Problem

| Your Problem | Start Here |
|--------------|------------|
| "I need to ingest data from multiple sources" | [Source Connector Patterns](./source-connector-patterns.md) |
| "My PDFs/documents aren't extracting cleanly" | [Document Extraction Patterns](./document-extraction-patterns.md) |
| "My retrieval results are poor" | [Chunking Strategies](./chunking-strategies.md), [Embedding Model Selection](./embedding-model-selection.md) |
| "Which vector database should I use?" | [Vector Database Selection](./vector-database-selection.md) |
| "My index is returning outdated answers" | [Index Freshness Patterns](./index-freshness-patterns.md) |
| "I need to automate my pipeline end-to-end" | [Pipeline Orchestration Patterns](./pipeline-orchestration-patterns.md) |
| "How do I know if my pipeline is working well?" | [RAG Evaluation Patterns](./rag-evaluation-patterns.md) |
| "I need to handle clinical/medical documents" | [Document Extraction Patterns](./document-extraction-patterns.md) + [Chunking Strategies](./chunking-strategies.md) |

---

## Relationship to RAG Architecture Patterns

These pipeline patterns are the **foundation** that RAG retrieval architectures build on:

```
┌─────────────────────────────────────────────────────────────┐
│                  RAG Architecture Patterns                   │
│        (Basic RAG, Hybrid RAG, Agentic RAG, etc.)          │
│                    patterns/rag/                             │
├─────────────────────────────────────────────────────────────┤
│                RAG Pipeline Engineering Patterns             │
│     (Ingestion, Chunking, Embedding, Indexing, etc.)       │
│                  patterns/rag-pipeline/                      │
└─────────────────────────────────────────────────────────────┘
```

- **Choose your pipeline patterns** to build the data infrastructure
- **Choose your RAG architecture pattern** to define the retrieval + generation strategy
- The two work together: a well-engineered pipeline makes every retrieval pattern perform better

---

## Healthcare Focus

All pipeline patterns include healthcare-specific guidance:
- **HIPAA Compliance**: PHI handling during ingestion, processing, and storage
- **Clinical Document Processing**: FHIR, HL7, CDA, SOAP notes, clinical summaries
- **De-identification**: Removing or masking PHI during extraction
- **Audit Trails**: Data lineage tracking for compliance
- **Medical Terminology**: Handling ICD codes, SNOMED CT, LOINC during chunking and embedding

---

## Pattern Index

See [Pattern Index](./pattern-index.md) for a complete table of all pipeline patterns with complexity, key technologies, and selection guidance.

## Contributing

When adding new RAG pipeline patterns:
1. Use the [RAG pipeline template](../../templates/rag-pipeline-template.md)
2. Indicate the pipeline stage(s) the pattern covers
3. Include data flow diagrams showing input → transformation → output
4. Document configuration parameters and their impact
5. Provide cost-per-document estimates
6. Include healthcare-specific considerations
7. Add evaluation guidance and metrics
