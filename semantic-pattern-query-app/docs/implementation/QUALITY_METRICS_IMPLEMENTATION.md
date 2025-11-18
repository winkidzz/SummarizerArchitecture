# RAG Quality Metrics Implementation

## Overview

This document describes the implementation of comprehensive quality metrics for the RAG (Retrieval-Augmented Generation) system. These metrics enable granular monitoring and evaluation of the entire RAG pipeline, from document retrieval to answer generation.

## Implementation Status

✅ **Phase 1: Complete** - All quality metrics have been implemented and tested.

## Architecture

### Module Structure

```
src/document_store/
├── evaluation/
│   ├── __init__.py                 # Module exports
│   ├── ir_metrics.py               # Classical IR metrics (450+ lines)
│   ├── context_metrics.py          # Context quality metrics (300+ lines)
│   └── answer_quality.py           # Answer quality metrics (480+ lines)
├── monitoring/
│   └── metrics.py                  # Prometheus metric definitions (updated)
└── search/
    └── hybrid_retriever.py         # Integration with retrieval (updated)
```

### Test Scripts

```
semantic-pattern-query-app/
├── test_quality_metrics.py              # Full integration test (requires Prometheus)
└── test_quality_metrics_standalone.py   # Standalone test (no dependencies)
```

## Implemented Metrics

### 1. Classical Information Retrieval (IR) Metrics

File: [`src/document_store/evaluation/ir_metrics.py`](../src/document_store/evaluation/ir_metrics.py)

These metrics evaluate the quality of document retrieval:

#### Precision@k
- **Definition**: Fraction of top-k retrieved documents that are relevant
- **Formula**: `Precision@k = (# relevant in top-k) / k`
- **Range**: 0.0 to 1.0
- **Use Case**: Measures relevance of retrieved results

#### Recall@k
- **Definition**: Fraction of all relevant documents found in top-k
- **Formula**: `Recall@k = (# relevant in top-k) / (total # relevant)`
- **Range**: 0.0 to 1.0
- **Use Case**: Measures coverage of relevant documents

#### Hit Rate@k
- **Definition**: Binary metric - whether ANY relevant doc appears in top-k
- **Formula**: `Hit Rate@k = 1 if any relevant in top-k, else 0`
- **Range**: 0.0 or 1.0
- **Use Case**: Measures if retrieval found at least one relevant document

#### Mean Reciprocal Rank (MRR)
- **Definition**: Reciprocal of rank of first relevant document
- **Formula**: `MRR = 1 / (position of first relevant doc)`
- **Range**: 0.0 to 1.0
- **Use Case**: Measures how quickly users find relevant results

#### Mean Average Precision (MAP)
- **Definition**: Mean of precision values at each relevant document position
- **Formula**: `MAP = avg(Precision@k for each relevant position k)`
- **Range**: 0.0 to 1.0
- **Use Case**: Measures overall ranking quality

#### Normalized Discounted Cumulative Gain (NDCG@k)
- **Definition**: Position-aware ranking quality with graded relevance
- **Formula**: `NDCG@k = DCG@k / IDCG@k` where `DCG = sum(rel_i / log2(i+1))`
- **Range**: 0.0 to 1.0
- **Use Case**: Measures ranking quality with position weighting

**Prometheus Metrics**:
- `rag_retrieval_precision_at_k{k_value}` (Histogram)
- `rag_retrieval_recall_at_k{k_value}` (Histogram)
- `rag_retrieval_hit_rate_at_k{k_value}` (Histogram)
- `rag_retrieval_mrr` (Histogram)
- `rag_retrieval_map` (Histogram)
- `rag_retrieval_ndcg_at_k{k_value}` (Histogram)

### 2. Context Quality Metrics

File: [`src/document_store/evaluation/context_metrics.py`](../src/document_store/evaluation/context_metrics.py)

These metrics evaluate the quality of retrieved context before answer generation:

#### Context Precision
- **Definition**: Fraction of retrieved chunks that are relevant to query
- **Formula**: `(# relevant chunks) / (total # chunks)`
- **Range**: 0.0 to 1.0
- **Use Case**: Measures if retrieval is getting relevant context

#### Context Recall
- **Definition**: Whether retrieved context covers all necessary facts
- **Formula**: `(# covered facts) / (total # required facts)`
- **Range**: 0.0 to 1.0
- **Use Case**: Measures completeness of retrieved context

#### Context Relevancy
- **Definition**: Average relevance score of all retrieved chunks
- **Formula**: `avg(relevance_score for each chunk)`
- **Range**: 0.0 to 1.0
- **Use Case**: Measures overall quality of retrieved context

#### Context Utilization
- **Definition**: Fraction of retrieved context actually used in answer
- **Formula**: `(# chunks used) / (total # chunks)`
- **Range**: 0.0 to 1.0
- **Use Case**: Detects over-retrieval (too many irrelevant chunks)

**Prometheus Metrics**:
- `rag_context_precision` (Histogram)
- `rag_context_recall` (Histogram)
- `rag_context_relevancy` (Histogram)
- `rag_context_utilization` (Histogram)

### 3. Answer Quality Metrics

File: [`src/document_store/evaluation/answer_quality.py`](../src/document_store/evaluation/answer_quality.py)

These metrics evaluate the quality of generated answers:

#### Answer Faithfulness
- **Definition**: Fraction of claims in answer supported by retrieved context
- **Formula**: `(# supported claims) / (total # claims)`
- **Range**: 0.0 to 1.0
- **Use Case**: Detects hallucinations (unsupported claims)

#### Hallucination Detection
- **Definition**: Identifies unsupported claims in generated answer
- **Severity Levels**: Minor, Moderate, Severe
- **Output**: Boolean flag + severity + list of unsupported claims
- **Use Case**: Quality control for answer generation

#### Answer Relevancy
- **Definition**: How well answer addresses the query
- **Implementation**: Word overlap or embedding similarity
- **Range**: 0.0 to 1.0
- **Use Case**: Ensures answer is on-topic

#### Answer Completeness
- **Definition**: Whether answer fully addresses all query aspects
- **Implementation**: Checks for expected elements, answer length, completeness indicators
- **Range**: 0.0 to 1.0
- **Use Case**: Ensures comprehensive answers

#### Citation Grounding
- **Definition**: Whether cited sources actually support the claims
- **Formula**: `(# accurate citations) / (total # citations)`
- **Range**: 0.0 to 1.0
- **Use Case**: Validates citation accuracy

**Prometheus Metrics**:
- `rag_answer_faithfulness_score` (Histogram)
- `rag_hallucination_detected{severity}` (Counter)
- `rag_answer_relevancy_score` (Histogram)
- `rag_answer_completeness_score` (Histogram)
- `rag_citation_grounding_score` (Histogram)

## Integration with Retrieval Pipeline

### Hybrid Retriever Integration

File: [`src/document_store/search/hybrid_retriever.py`](../src/document_store/search/hybrid_retriever.py:51-110)

The `HealthcareHybridRetriever.retrieve()` method now accepts optional ground truth parameters:

```python
def retrieve(
    self,
    query: str,
    top_k: int = 10,
    filters: Optional[Dict[str, Any]] = None,
    embedder_type: Optional[str] = None,
    relevant_doc_ids: Optional[Set[str]] = None,      # Ground truth
    relevance_scores: Optional[Dict[str, float]] = None  # Graded relevance
) -> List[Dict[str, Any]]:
```

When ground truth is provided, IR metrics are automatically calculated and recorded to Prometheus.

### Metrics Collection

The `MetricsCollector` class in [`metrics.py`](../src/document_store/monitoring/metrics.py) provides helper methods:

```python
# Record IR metrics
MetricsCollector.record_ir_metrics(
    precision_at_k={1: 0.8, 3: 0.67, 5: 0.6, 10: 0.5},
    recall_at_k={1: 0.2, 3: 0.4, 5: 0.6, 10: 1.0},
    hit_rate_at_k={1: 1.0, 3: 1.0, 5: 1.0, 10: 1.0},
    mrr=0.85,
    map_score=0.72,
    ndcg_at_k={1: 0.9, 3: 0.85, 5: 0.8, 10: 0.75}
)

# Record context quality metrics
MetricsCollector.record_context_quality(
    precision=0.75,
    recall=0.80,
    relevancy=0.85,
    utilization=0.70
)

# Record answer quality metrics
MetricsCollector.record_answer_quality(
    faithfulness=0.92,
    relevancy=0.88,
    completeness=0.85,
    citation_grounding=0.95,
    has_hallucination=False,
    hallucination_severity="minor"
)
```

## Usage Examples

### Example 1: Evaluate Retrieval Quality

```python
from document_store.evaluation import evaluate_retrieval_quality

# Retrieved documents (in ranked order)
retrieved_doc_ids = ["doc1", "doc2", "doc3", "doc4", "doc5"]

# Ground truth relevant documents
relevant_doc_ids = {"doc1", "doc3", "doc5"}

# Optional: Graded relevance scores
relevance_scores = {"doc1": 3.0, "doc3": 2.0, "doc5": 1.0}

# Evaluate
metrics = evaluate_retrieval_quality(
    retrieved_doc_ids=retrieved_doc_ids,
    relevant_doc_ids=relevant_doc_ids,
    relevance_scores=relevance_scores,
    k_values=[1, 3, 5, 10]
)

print(f"Precision@5: {metrics['precision@k'][5]}")
print(f"NDCG@5: {metrics['ndcg@k'][5]}")
print(f"MRR: {metrics['mrr']}")
```

### Example 2: Evaluate Context Quality

```python
from document_store.evaluation import evaluate_context_quality

metrics = evaluate_context_quality(
    query="What is the patient's condition?",
    retrieved_chunks=["chunk1", "chunk2", "chunk3"],
    generated_answer="The patient has diabetes.",
    chunk_relevance_scores=[0.9, 0.7, 0.5],
    relevant_chunk_indices={0, 2}  # Ground truth
)

print(f"Context Precision: {metrics['context_precision']}")
print(f"Context Utilization: {metrics['context_utilization']}")
```

### Example 3: Evaluate Answer Quality

```python
from document_store.evaluation import evaluate_answer_quality

metrics = evaluate_answer_quality(
    query="What is the diagnosis?",
    answer="Patient has type 2 diabetes.",
    context_chunks=["Diabetes type 2 diagnosis confirmed."]
)

print(f"Faithfulness: {metrics['faithfulness']}")
print(f"Has Hallucination: {metrics['has_hallucination']}")
print(f"Unsupported Claims: {metrics['unsupported_claims']}")
```

## Testing

### Standalone Test (No Dependencies)

```bash
cd semantic-pattern-query-app
python3 test_quality_metrics_standalone.py
```

This test demonstrates all metrics work correctly without requiring the full application stack.

**Sample Output**:
```
Classical IR Metrics:
  • Precision@5:  60.0%  (relevance of top 5 results)
  • Recall@5:     60.0%  (coverage of relevant docs)
  • MRR:          1.000  (rank of first relevant doc)
  • NDCG@5:       0.785  (position-aware quality)

Context Quality Metrics:
  • Precision:    60.0%  (relevant chunks retrieved)
  • Relevancy:    67.0%  (avg chunk relevance)
  • Utilization:  80.0%  (chunks used in answer)

Answer Quality Metrics:
  • Faithfulness: 100.0%  (claims supported)
  • Hallucination: False  (no unsupported claims)
```

### Full Integration Test (Requires Prometheus)

```bash
cd semantic-pattern-query-app
pip install prometheus_client
python3 test_quality_metrics.py
```

This test also records metrics to Prometheus for visualization in Grafana.

## Monitoring & Visualization

### Prometheus Metrics Endpoint

All metrics are exposed at: `http://localhost:8000/metrics`

### Grafana Dashboard (To Be Created)

**Recommended Dashboard Structure**:

1. **IR Metrics Panel**
   - Precision@k time series (k=1,3,5,10)
   - Recall@k time series
   - MRR and MAP trends
   - NDCG@k heatmap

2. **Context Quality Panel**
   - Context precision gauge
   - Context relevancy trend
   - Context utilization over time
   - Precision vs Utilization scatter plot

3. **Answer Quality Panel**
   - Faithfulness score trend
   - Hallucination rate (counter)
   - Hallucination severity distribution
   - Answer relevancy vs completeness

4. **Quality Alerts**
   - Alert: Faithfulness < 0.7 (potential hallucinations)
   - Alert: Context precision < 0.5 (poor retrieval)
   - Alert: NDCG@5 < 0.6 (poor ranking)

## Ground Truth Requirements

### When is Ground Truth Needed?

| Metric | Requires Ground Truth | Source |
|--------|----------------------|--------|
| Precision@k | Yes | Manual labeling or test dataset |
| Recall@k | Yes | Manual labeling or test dataset |
| NDCG@k | Optional (can use binary) | Graded relevance judgments |
| MRR | Yes | Manual labeling or test dataset |
| MAP | Yes | Manual labeling or test dataset |
| Context Precision | Yes | Manual chunk relevance labels |
| Context Recall | Yes | Required facts for query |
| Context Relevancy | No | Uses retrieval scores |
| Context Utilization | No | Estimated from text overlap |
| Answer Faithfulness | No | Computed from context |
| Hallucination Detection | No | Computed from context |
| Answer Relevancy | No | Word overlap or embeddings |
| Answer Completeness | Optional | Expected elements list |
| Citation Grounding | No | Verified against context |

### Collecting Ground Truth

**Option 1: Test Dataset**
- Create curated test queries with known relevant documents
- Use for periodic quality evaluation
- Store in `tests/evaluation/test_queries.json`

**Option 2: Manual Labeling**
- Sample random production queries
- Have domain experts label relevant documents
- Use for continuous quality monitoring

**Option 3: User Feedback**
- Implicit signals (click-through, dwell time)
- Explicit feedback (thumbs up/down, relevance ratings)
- Build ground truth from user interactions

## Performance Considerations

### Computational Cost

- **IR Metrics**: O(k) per query - very fast
- **Context Metrics**: O(n) where n = # chunks - fast
- **Answer Metrics**: O(m) where m = # claims - moderate
- **Hallucination Detection**: O(m × n) - can be slow for many claims

### Optimization Strategies

1. **Sampling**: Evaluate metrics on sample of queries (e.g., 10%)
2. **Async Processing**: Run evaluation async, don't block responses
3. **Caching**: Cache ground truth labels for common queries
4. **Batch Evaluation**: Run expensive metrics in batch jobs

### Production Deployment

**Recommended Approach**:
1. Use lightweight metrics (relevancy, utilization) on all queries
2. Use IR metrics on sampled queries with ground truth
3. Run expensive metrics (hallucination detection) async or in batch
4. Alert on quality degradation

## Future Enhancements

### Phase 2: Advanced Metrics (Future)

1. **LLM-as-Judge Evaluation**
   - Use LLM to evaluate answer quality
   - More accurate hallucination detection
   - Better claim extraction

2. **Embedding-Based Metrics**
   - Semantic similarity for answer relevancy
   - Better chunk usage detection
   - Embedding-based hallucination detection

3. **RAGAS Framework Integration**
   - Official RAGAS implementation
   - Additional metrics (context ranking, noise robustness)
   - Comprehensive evaluation pipeline

4. **TruLens Integration**
   - Groundedness evaluation
   - Context relevance scoring
   - Answer relevance with chain-of-thought

5. **A/B Testing Support**
   - Compare retrieval strategies
   - Measure impact of model changes
   - Statistical significance testing

## References

### Evaluation Frameworks

- **RAGAS**: [https://github.com/explodinggradients/ragas](https://github.com/explodinggradients/ragas)
- **DeepEval**: [https://github.com/confident-ai/deepeval](https://github.com/confident-ai/deepeval)
- **TruLens**: [https://github.com/truera/trulens](https://github.com/truera/trulens)
- **LlamaIndex**: [https://docs.llamaindex.ai/en/stable/module_guides/evaluating/](https://docs.llamaindex.ai/en/stable/module_guides/evaluating/)

### Research Papers

- **IR Metrics**: "The TREC Routing and Ad-Hoc Environments" (Voorhees, 1998)
- **NDCG**: "Cumulated Gain-Based Evaluation of IR Techniques" (Järvelin & Kekäläinen, 2002)
- **RAG Evaluation**: "Benchmarking Large Language Models in Retrieval-Augmented Generation" (Chen et al., 2023)

### Internal Documentation

- [Report on RAG Metrics](./report.md) - Comprehensive metrics reference from evaluation frameworks
- [Grafana Setup](../GRAFANA_SETUP_COMPLETE.md) - Existing monitoring dashboards
- [Ports Documentation](./PORTS.md) - Service endpoints

## Support

For questions or issues with quality metrics:

1. Check the test scripts for usage examples
2. Review the implementation files for detailed docstrings
3. Consult the [report.md](./report.md) for metrics theory
4. Open an issue with the development team

---

**Document Version**: 1.0
**Last Updated**: 2024-11-18
**Author**: AI Summarization Reference Architecture Team
