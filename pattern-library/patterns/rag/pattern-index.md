# RAG Pattern Index

Complete index of all RAG patterns documented in this reference architecture.

## Core Patterns

| Pattern | Description | Complexity | Use Case |
|---------|------------|------------|----------|
| [Basic RAG](./basic-rag.md) | Standard retrieval-augmented generation | Low | Simple Q&A, prototyping |
| [Advanced RAG](./advanced-rag.md) | Multi-step retrieval and query decomposition | Medium | Complex queries, multi-hop reasoning |
| [Self-RAG](./self-rag.md) | Self-reflective with quality control | High | Quality-critical applications |

## Hybrid & Multi-Strategy

| Pattern | Description | Complexity | Use Case |
|---------|------------|------------|----------|
| [Hybrid RAG](./hybrid-rag.md) | Combines multiple retrieval strategies | Medium | Diverse document types, high recall |
| [Multi-Query RAG](./multi-query-rag.md) | Multiple query variations and fusion | Medium | Query ambiguity |
| [Parent-Child RAG](./parent-child-rag.md) | Hierarchical document chunking | Medium | Large documents, hierarchical structure |

## Agentic Patterns

| Pattern | Description | Complexity | Use Case |
|---------|------------|------------|----------|
| [Agentic RAG](./agentic-rag.md) | Agent-based retrieval and generation | High | Complex workflows, tool use |
| [Adaptive RAG](./adaptive-rag.md) | Adaptive strategy selection | High | Variable query complexity |

## Specialized Patterns

| Pattern | Description | Complexity | Use Case |
|---------|------------|------------|----------|
| [Corrective RAG](./corrective-rag.md) | Self-correcting retrieval | High | Accuracy-critical, feedback loops |
| [Modular RAG](./modular-rag.md) | Composable retrieval components | Medium | Flexible, reusable components |
| [Compressed RAG](./compressed-rag.md) | Compressed context retrieval | Low | Token limit constraints |
| [Small-to-Big RAG](./small-to-big-rag.md) | Progressive context expansion | Medium | Large documents, context optimization |

## Advanced Patterns

| Pattern | Description | Complexity | Use Case |
|---------|------------|------------|----------|
| [Graph RAG](./graph-rag.md) | Graph-based knowledge retrieval | High | Entity relationships, knowledge graphs |
| [Reranking RAG](./reranking-rag.md) | Multi-stage reranking with BAR-RAG | Medium | High precision requirements |
| [Streaming RAG](./streaming-rag.md) | Real-time streaming | Medium | Live data, real-time requirements |
| [Recursive RAG](./recursive-rag.md) | Recursive query decomposition | High | Complex document processing |

## Healthcare & Privacy Patterns (New - Feb 2026)

| Pattern | Description | Complexity | Use Case |
|---------|------------|------------|----------|
| [Medical RAG](./medical-rag.md) | Healthcare-optimized RAG with clinical validation | High | Clinical decision support, medical literature |
| [Local RAG](./local-rag.md) | Privacy-preserving on-device RAG (CUBO) | Medium | HIPAA/GDPR compliance, air-gapped environments |
| [Multi-Modal RAG](./multi-modal-rag.md) | Images, audio, video with OmniRAG-Agent | High | Medical imaging, radiology, pathology |

## Quick Selection Guide

### Start Here
- **New to RAG?** → [Basic RAG](./basic-rag.md)
- **Simple queries?** → [Basic RAG](./basic-rag.md) or [Compressed RAG](./compressed-rag.md)
- **Complex queries?** → [Advanced RAG](./advanced-rag.md) or [Self-RAG](./self-rag.md)

### By Requirement
- **High Accuracy** → [Self-RAG](./self-rag.md), [Corrective RAG](./corrective-rag.md), [Reranking RAG](./reranking-rag.md)
- **High Recall** → [Hybrid RAG](./hybrid-rag.md), [Multi-Query RAG](./multi-query-rag.md)
- **Low Latency** → [Basic RAG](./basic-rag.md), [Compressed RAG](./compressed-rag.md)
- **Real-Time** → [Streaming RAG](./streaming-rag.md)
- **Large Documents** → [Parent-Child RAG](./parent-child-rag.md), [Small-to-Big RAG](./small-to-big-rag.md)
- **Complex Relationships** → [Graph RAG](./graph-rag.md)
- **Agent Workflows** → [Agentic RAG](./agentic-rag.md), [Adaptive RAG](./adaptive-rag.md)
- **Healthcare/Medical** → [Medical RAG](./medical-rag.md), [Multi-Modal RAG](./multi-modal-rag.md)
- **Privacy/HIPAA/GDPR** → [Local RAG](./local-rag.md)
- **Medical Imaging** → [Multi-Modal RAG](./multi-modal-rag.md)

## RAG Pipeline Engineering Patterns

These retrieval patterns are powered by pipeline infrastructure. For patterns on building, operating, and optimizing the pipeline itself, see:

**[RAG Pipeline Pattern Index](../rag-pipeline/pattern-index.md)** — 10 patterns covering ingestion, chunking, embedding, indexing, freshness, orchestration, and evaluation.

| Pipeline Pattern | Complements These RAG Patterns |
|-----------------|-------------------------------|
| [Chunking Strategies](../rag-pipeline/chunking-strategies.md) | Parent-Child RAG, Small-to-Big RAG |
| [Embedding Model Selection](../rag-pipeline/embedding-model-selection.md) | Hybrid RAG, Multi-Modal RAG |
| [Vector Database Selection](../rag-pipeline/vector-database-selection.md) | Basic RAG, Graph RAG |
| [Index Freshness Patterns](../rag-pipeline/index-freshness-patterns.md) | Streaming RAG, Corrective RAG |
| [RAG Evaluation Patterns](../rag-pipeline/rag-evaluation-patterns.md) | Self-RAG, Reranking RAG |

## Reference

Based on comprehensive RAG strategies analysis and latest 2026 research.

### Key Research Papers (2026)

| Paper | arXiv | Key Contribution |
|-------|-------|------------------|
| Medical RAG Best Practices | [2602.03368](https://arxiv.org/abs/2602.03368) | Industrial best practices for healthcare RAG |
| A-RAG: Agentic RAG | [2602.03442](https://arxiv.org/abs/2602.03442) | Hierarchical retrieval interfaces for agents |
| BAR-RAG: Boundary-Aware Reranking | [2602.03689](https://arxiv.org/abs/2602.03689) | Evidence selection suitable for generators |
| OmniRAG-Agent | [2602.03707](https://arxiv.org/abs/2602.03707) | Agentic multi-modal RAG for long audio-video |
| CUBO: Local RAG | [2602.03731](https://arxiv.org/abs/2602.03731) | Privacy-preserving RAG on consumer hardware |

**Video Reference**: [RAG Strategies Overview](https://youtu.be/tLMViADvSNE?si=C8Zq1H0Uww_FpxZ7)

## Contributing

When adding new patterns:
1. Use the [pattern template](../templates/pattern-template.md)
2. Add to this index
3. Update the [main README](./README.md)
4. Include multi-vendor implementations

