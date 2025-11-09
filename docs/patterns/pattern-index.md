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
| [Reranking RAG](./reranking-rag.md) | Multi-stage reranking | Medium | High precision requirements |
| [Streaming RAG](./streaming-rag.md) | Real-time streaming | Medium | Live data, real-time requirements |
| [Recursive RAG](./recursive-rag.md) | Recursive query decomposition | High | Complex document processing |

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

## Reference

Based on comprehensive RAG strategies analysis.

**Video Reference**: [RAG Strategies Overview](https://youtu.be/tLMViADvSNE?si=C8Zq1H0Uww_FpxZ7)

## Contributing

When adding new patterns:
1. Use the [pattern template](../templates/pattern-template.md)
2. Add to this index
3. Update the [main README](./README.md)
4. Include multi-vendor implementations

