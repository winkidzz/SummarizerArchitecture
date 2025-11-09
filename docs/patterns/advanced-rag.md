# Advanced RAG Pattern

## Overview

Advanced RAG extends Basic RAG with multi-step retrieval, query decomposition, and iterative refinement. It handles complex queries that require reasoning across multiple documents or multiple retrieval passes.

## Architecture

### High-Level Architecture

```
User Query → Query Decomposition → Multiple Retrieval Steps → 
Context Refinement → Re-ranking → LLM Generation → Response
```

### Components

- **Query Decomposer**: Breaks complex queries into sub-queries
- **Multi-Step Retriever**: Performs iterative retrieval
- **Context Refiner**: Refines and filters retrieved context
- **Reranker**: Re-ranks documents by relevance
- **LLM**: Generates response with refined context

### Data Flow

1. Complex query is decomposed into sub-queries
2. Each sub-query triggers retrieval
3. Retrieved documents are merged and deduplicated
4. Context is refined and filtered
5. Documents are re-ranked by relevance
6. Final context is assembled
7. LLM generates response

## When to Use

### Ideal Use Cases
- Multi-hop reasoning queries
- Queries requiring information from multiple documents
- Complex analytical questions
- Comparative queries across multiple sources
- Queries needing iterative refinement

### Characteristics of Suitable Problems
- Queries cannot be answered with single retrieval
- Need to synthesize information from multiple sources
- Require reasoning across document boundaries
- Benefit from query decomposition

## When NOT to Use

### Anti-Patterns
- Simple, direct questions (use Basic RAG)
- Real-time streaming requirements
- Very large document corpora without optimization
- Queries with single, clear answer location

### Characteristics of Unsuitable Problems
- Simple queries that Basic RAG handles well
- Low-latency requirements
- Limited computational resources

## Implementation Examples

### LangChain Implementation

```python
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

# Multi-step retrieval with query decomposition
prompt_template = """Use the following pieces of context to answer the question.
If you don't know the answer, break down the question into sub-questions and retrieve more context.

Context: {context}
Question: {question}
Answer:"""

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

chain = load_qa_chain(
    llm=OpenAI(),
    chain_type="map_reduce",  # Multi-step processing
    prompt=PROMPT
)
```

### Google ADK Implementation

```python
from document_store.orchestrator import DocumentStoreOrchestrator

orchestrator = DocumentStoreOrchestrator(use_adk_agent=True)

# Advanced RAG with agent-based query decomposition
results = orchestrator.query_patterns(
    query="Compare basic RAG vs advanced RAG patterns",
    n_results=10,  # More results for complex queries
    use_agent=True,  # ADK agent handles decomposition
)
```

## Performance Characteristics

### Latency
- Typical latency: 500-2000ms (multiple retrieval steps)
- Factors:
  - Number of retrieval steps
  - Query decomposition complexity
  - Re-ranking overhead

### Throughput
- Typical throughput: 5-20 requests/second
- Lower than Basic RAG due to multiple steps

### Resource Requirements
- Memory: 4-8GB
- CPU: 4-8 cores
- Storage: Same as Basic RAG

## Trade-offs

### Advantages
- Handles complex, multi-step queries
- Better accuracy for analytical questions
- Can synthesize information across documents
- More robust to query variations

### Disadvantages
- Higher latency due to multiple steps
- More complex to implement
- Higher computational cost
- More difficult to debug

## Architecture Diagram

```mermaid
graph TD
    A[Complex Query] --> B[Query Decomposition]
    B --> C[Sub-Query 1]
    B --> D[Sub-Query 2]
    B --> E[Sub-Query 3]
    
    C --> F[Retrieval Step 1]
    D --> G[Retrieval Step 2]
    E --> H[Retrieval Step 3]
    
    F --> I[Context Merging]
    G --> I
    H --> I
    
    I --> J[Context Refinement]
    J --> K[Re-ranking]
    K --> L[LLM
    L --> M[Response]
```

## Related Patterns
- [Basic RAG](./basic-rag.md) - Simpler alternative
- [Self-RAG](./self-rag.md) - Adds quality control
- [Recursive RAG](./recursive-rag.md) - Recursive decomposition

## References
- [RAG Strategies Video](https://youtu.be/tLMViADvSNE?si=C8Zq1H0Uww_FpxZ7)

## Version History
- **v1.0** (2025-11-08): Initial version

