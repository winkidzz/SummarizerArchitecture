# RAG Patterns Library

This directory contains comprehensive documentation for various Retrieval-Augmented Generation (RAG) strategies and patterns.

## Pattern Categories

### Core RAG Patterns
1. [Basic RAG](./basic-rag.md) - Standard retrieval-augmented generation
2. [Advanced RAG](./advanced-rag.md) - Multi-step retrieval and query decomposition
3. [Self-RAG](./self-rag.md) - Self-reflective retrieval-augmented generation

### Hybrid and Multi-Strategy Patterns
4. [Hybrid RAG](./hybrid-rag.md) - Combining multiple retrieval strategies
5. [Multi-Query RAG](./multi-query-rag.md) - Multiple query generation and fusion
6. [Parent-Child RAG](./parent-child-rag.md) - Hierarchical document chunking

### Agentic Patterns
7. [Agentic RAG](./agentic-rag.md) - Agent-based retrieval and generation
8. [Adaptive RAG](./adaptive-rag.md) - Adaptive retrieval based on query complexity

### Specialized Patterns
9. [Corrective RAG](./corrective-rag.md) - Self-correcting retrieval
10. [Modular RAG](./modular-rag.md) - Modular retrieval components
11. [Compressed RAG](./compressed-rag.md) - Compressed context retrieval
12. [Small-to-Big RAG](./small-to-big-rag.md) - Progressive context expansion

### Advanced Patterns
13. [Graph RAG](./graph-rag.md) - Graph-based knowledge retrieval
14. [Reranking RAG](./reranking-rag.md) - Multi-stage reranking
15. [Streaming RAG](./streaming-rag.md) - Real-time streaming RAG
16. [Recursive RAG](./recursive-rag.md) - Recursive query decomposition

## Pattern Selection Guide

Use this guide to select the right RAG pattern for your use case:

### Simple Queries
- **Basic RAG**: Single-step retrieval for straightforward questions
- **Compressed RAG**: When context size is a concern

### Complex Queries
- **Advanced RAG**: Multi-step reasoning required
- **Self-RAG**: Need self-reflection and quality control
- **Adaptive RAG**: Query complexity varies significantly

### Multi-Source Information
- **Hybrid RAG**: Combining vector, keyword, and semantic search
- **Multi-Query RAG**: Need multiple perspectives on the same query
- **Graph RAG**: Complex relationships between entities

### Quality and Accuracy
- **Corrective RAG**: Need self-correction capabilities
- **Reranking RAG**: Multiple retrieval stages for better results
- **Self-RAG**: Built-in quality assessment

### Real-Time Requirements
- **Streaming RAG**: Real-time or near-real-time responses
- **Modular RAG**: Need flexible, composable components

### Large Documents
- **Parent-Child RAG**: Hierarchical document structure
- **Small-to-Big RAG**: Progressive context expansion
- **Recursive RAG**: Complex document decomposition

### Agent-Based Systems
- **Agentic RAG**: Agent orchestration required
- **Adaptive RAG**: Dynamic strategy selection

## RAG Pipeline Engineering

These retrieval patterns depend on a well-built pipeline. For the engineering patterns that power ingestion, chunking, embedding, indexing, and freshness management, see:

**[RAG Pipeline Engineering Patterns](../rag-pipeline/)** — 10 patterns covering:
- Source Connectors, Document Extraction
- Chunking Strategies, Embedding Model Selection, Vectorization
- Vector Database Selection, Index Architecture, Index Freshness
- Pipeline Orchestration, RAG Evaluation

## Pattern Index

See [Pattern Index](./pattern-index.md) for a complete table of all patterns with quick selection guide.

## Reference

Based on comprehensive RAG strategies analysis. See individual pattern documents for detailed implementation guidance.

**Video Reference**: [RAG Strategies Overview](https://youtu.be/tLMViADvSNE?si=C8Zq1H0Uww_FpxZ7)

**Note**: Pattern documentation is initialized with templates. Please review the video and fill in specific implementation details, vendor examples, and architecture diagrams for each pattern.

## Contributing

When adding new patterns:
1. Use the [pattern template](../templates/pattern-template.md)
2. Include multi-vendor implementations
3. Provide clear use case guidance
4. Add architecture diagrams
5. Document performance characteristics

