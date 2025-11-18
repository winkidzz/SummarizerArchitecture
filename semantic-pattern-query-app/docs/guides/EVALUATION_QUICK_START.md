# RAG Evaluation Metrics - Quick Start Guide

## Overview

This guide shows you how to quickly start using the evaluation metrics in your RAG system.

## What We Have (Current Implementation - No LLM Required)

### ✅ Classical IR Metrics
- **What**: Precision@k, Recall@k, MRR, MAP, NDCG@k
- **When to use**: Evaluate document retrieval quality
- **Requirements**: Ground truth labels (which docs are relevant)
- **Speed**: Very fast (pure math, no ML)

### ✅ Context Quality Metrics
- **What**: Context precision, relevancy, utilization
- **When to use**: Evaluate retrieved chunks before answer generation
- **Requirements**: Relevance scores (from retrieval), optional ground truth
- **Speed**: Fast (word overlap heuristics)

### ✅ Answer Quality Metrics
- **What**: Faithfulness, hallucination detection, completeness
- **When to use**: Evaluate generated answers for safety
- **Requirements**: Query, answer, context chunks
- **Speed**: Fast (word overlap heuristics)

### ⚠️ Limitations (Current Implementation)
- Uses **word overlap** instead of semantic similarity
- May miss paraphrases (e.g., "diabetes" vs "diabetic condition")
- Simple sentence splitting for claim extraction
- Not as accurate as LLM-based evaluation

## Quick Examples

### 1. Evaluate Retrieval Quality

```python
from document_store.evaluation import evaluate_retrieval_quality

# Your retrieval results
retrieved_docs = ["doc1", "doc2", "doc3", "doc4", "doc5"]

# Ground truth (you need to provide this)
relevant_docs = {"doc1", "doc3", "doc5"}

# Evaluate
metrics = evaluate_retrieval_quality(
    retrieved_doc_ids=retrieved_docs,
    relevant_doc_ids=relevant_docs,
    k_values=[1, 3, 5, 10]
)

# Check results
print(f"Precision@5: {metrics['precision@k'][5]:.1%}")
print(f"Recall@5: {metrics['recall@k'][5]:.1%}")
print(f"MRR: {metrics['mrr']:.3f}")
print(f"MAP: {metrics['map']:.3f}")
```

### 2. Evaluate Context Quality

```python
from document_store.evaluation import evaluate_context_quality

metrics = evaluate_context_quality(
    query="What is the patient's diagnosis?",
    retrieved_chunks=[
        "Patient diagnosed with diabetes type 2.",
        "Blood pressure is normal.",
        "No known allergies."
    ],
    generated_answer="Patient has diabetes type 2.",
    chunk_relevance_scores=[0.92, 0.45, 0.38]  # From retrieval
)

print(f"Context Precision: {metrics['context_precision']:.1%}")
print(f"Context Utilization: {metrics['context_utilization']:.1%}")
```

### 3. Detect Hallucinations

```python
from document_store.evaluation import evaluate_answer_quality

metrics = evaluate_answer_quality(
    query="What medications is the patient taking?",
    answer="Patient is taking Metformin 500mg and insulin injections.",
    context_chunks=[
        "Current medications: Metformin 500mg twice daily.",
        "Blood glucose levels monitored regularly."
    ]
)

if metrics['has_hallucination']:
    print(f"⚠️ Hallucination detected! Severity: {metrics['hallucination_severity']}")
    print(f"Unsupported claims:")
    for claim in metrics['unsupported_claims']:
        print(f"  - {claim}")
else:
    print(f"✅ All claims supported (Faithfulness: {metrics['faithfulness']:.1%})")
```

## Running Tests

### Test 1: Basic Functionality
```bash
cd semantic-pattern-query-app
python3 test_quality_metrics_standalone.py
```

Shows all metrics work correctly.

### Test 2: Healthcare Use Cases
```bash
python3 test_healthcare_evaluation.py
```

Demonstrates:
- Clinical note summarization
- Medication reconciliation
- Adverse event detection

### Test 3: Side-by-Side Comparisons
```bash
python3 test_evaluation_comparison.py
```

Compares:
- Vector vs Hybrid search
- Different LLM models
- Chunking strategies

## Integration with Your RAG Pipeline

### Option 1: Manual Evaluation (Testing/Development)

```python
from document_store.evaluation import (
    evaluate_retrieval_quality,
    evaluate_answer_quality
)

# After retrieval
retrieval_metrics = evaluate_retrieval_quality(
    retrieved_doc_ids=results,
    relevant_doc_ids=ground_truth  # From test dataset
)

# After generation
answer_metrics = evaluate_answer_quality(
    query=user_query,
    answer=generated_answer,
    context_chunks=retrieved_chunks
)

# Log or display metrics
print(f"Retrieval Precision@5: {retrieval_metrics['precision@k'][5]}")
print(f"Answer Faithfulness: {answer_metrics['faithfulness']}")
```

### Option 2: Automated Monitoring (Production)

The hybrid retriever already has IR metrics integration:

```python
from document_store.search.hybrid_retriever import HealthcareHybridRetriever

# When you have ground truth (e.g., test queries)
results = retriever.retrieve(
    query="patient query",
    top_k=10,
    relevant_doc_ids={"doc1", "doc3"},  # Ground truth
    relevance_scores={"doc1": 3.0, "doc3": 2.0}  # Optional
)

# Metrics automatically calculated and sent to Prometheus!
```

### Option 3: Periodic Batch Evaluation

```python
# Run on sample of production queries
for query_data in test_dataset:
    results = retriever.retrieve(
        query=query_data['query'],
        relevant_doc_ids=query_data['relevant_docs']
    )
    # Metrics recorded to Prometheus

# View metrics in Grafana at http://localhost:3333
```

## When to Use Each Metric

### IR Metrics (Precision, Recall, NDCG, etc.)

**Use when:**
- Testing different retrieval algorithms
- Comparing vector search vs BM25 vs hybrid
- A/B testing embedding models
- Evaluating re-ranking strategies

**Requires:**
- Ground truth relevant documents for each query
- Can collect from: manual labeling, user feedback, test datasets

**Example use case:**
> "Should we switch from sentence-transformers to Gemini embeddings?"
> → Measure Precision@5 and NDCG@5 before and after

### Context Quality Metrics

**Use when:**
- Optimizing chunk size (128 vs 512 vs 1024 tokens)
- Testing different chunking strategies (fixed vs semantic)
- Evaluating context window utilization
- Detecting over-retrieval (too many chunks)

**Requires:**
- Retrieval relevance scores (automatically available)
- Optional: ground truth relevant chunks

**Example use case:**
> "Are we retrieving too many irrelevant chunks?"
> → Check Context Precision and Context Utilization

### Answer Quality Metrics (Faithfulness, Hallucination)

**Use when:**
- **CRITICAL for healthcare**: Detecting fabricated medical information
- Comparing different LLM models (GPT-4 vs Claude vs Gemini)
- Testing prompt engineering changes
- Monitoring answer safety in production

**Requires:**
- Only the query, answer, and retrieved context
- No ground truth needed!

**Example use case:**
> "Is our LLM making up medical facts?"
> → Monitor Faithfulness score and Hallucination Detection

## Ground Truth: How to Get It

You need ground truth for some metrics. Here are options:

### Option 1: Create Test Dataset (Recommended)

```python
# Example: tests/evaluation/test_queries.json
{
  "queries": [
    {
      "query": "What are the patient's diabetes medications?",
      "relevant_docs": ["med_list_2024", "diabetes_note", "prescription"],
      "relevant_chunks": [0, 2, 5],
      "expected_answer_elements": ["metformin", "dosage", "frequency"]
    }
  ]
}
```

Create 50-100 test queries covering your main use cases.

### Option 2: Manual Labeling

```python
# Label a sample of production queries
# 1. Retrieve documents for query
# 2. Have domain expert mark which are relevant
# 3. Store labels for periodic evaluation

labeled_queries = {
    "query_id_123": {
        "query": "...",
        "relevant_docs": ["doc1", "doc3"],
        "timestamp": "2024-01-15"
    }
}
```

### Option 3: User Feedback

```python
# Collect implicit feedback
# - Click-through rate on results
# - Dwell time on documents
# - Thumbs up/down on answers

# Use to derive relevance labels
if click_through_rate > 0.5:
    label_as_relevant()
```

## Production Deployment Strategy

### Phase 1: Development/Testing (All Metrics)
- Run all metrics on test dataset
- Use for model selection and optimization
- No performance impact (offline evaluation)

### Phase 2: Staging (Sampled Metrics)
- Sample 10% of queries
- Run full evaluation on sample
- Monitor for quality degradation

### Phase 3: Production (Lightweight Metrics)
- **Always run**: Answer faithfulness, hallucination detection (fast, no ground truth)
- **Sample 5%**: IR metrics (requires ground truth from test dataset)
- **Weekly batch**: Full evaluation on test dataset

### Example Production Config

```python
# config.yaml
evaluation:
  production:
    answer_quality:
      enabled: true           # Always on
      sampling_rate: 1.0      # 100%
    retrieval_quality:
      enabled: true
      sampling_rate: 0.05     # 5% of queries
    batch_evaluation:
      enabled: true
      schedule: "weekly"      # Every Sunday
      test_dataset: "tests/evaluation/test_queries.json"
```

## Alerting Thresholds

Set up alerts in Grafana/Prometheus:

```yaml
alerts:
  - name: "High Hallucination Rate"
    condition: hallucination_rate > 0.10  # More than 10%
    severity: critical

  - name: "Low Retrieval Precision"
    condition: precision_at_5 < 0.50      # Less than 50%
    severity: warning

  - name: "Low Answer Faithfulness"
    condition: faithfulness < 0.70        # Less than 70%
    severity: critical
```

## What's Next?

### Current Status ✅
- All metrics implemented and tested
- No LLM required (fast, deterministic)
- Ready for production integration

### Future Enhancements (Phase 2) 🚀

**LLM-Based Evaluation** (more accurate but slower/costly):
- Use LLM-as-judge for faithfulness
- Semantic similarity (embeddings) instead of word overlap
- Better claim extraction using NLI models
- RAGAS framework integration

**If you need these**, let me know and I can implement:
- Embedding-based semantic similarity
- LLM-as-judge evaluation (with Ollama/Gemini/Claude)
- RAGAS framework integration
- TruLens integration

## Troubleshooting

### "Faithfulness scores seem too low"
- Current implementation uses strict word overlap
- Paraphrases may not match (e.g., "hypertension" vs "high blood pressure")
- **Solution**: Consider LLM-based evaluation for semantic matching

### "Need more accurate hallucination detection"
- Word overlap can miss semantic hallucinations
- **Solution**: Use embedding similarity or LLM-as-judge

### "Metrics calculation is slow"
- Current implementation is already very fast (no LLM calls)
- If still slow, reduce sampling rate or use batch evaluation

## Resources

- **Implementation Guide**: [QUALITY_METRICS_IMPLEMENTATION.md](./QUALITY_METRICS_IMPLEMENTATION.md)
- **Test Scripts**: Run examples to see metrics in action
- **Code**: See `src/document_store/evaluation/` for implementations

## Questions?

The evaluation system is ready to use! All metrics work without requiring LLMs, making them fast and cost-effective for production monitoring.

For more advanced LLM-based evaluation, we can implement Phase 2 enhancements.
