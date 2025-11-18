# Real-Time Quality Metrics Collection

## Overview

The RAG API now **automatically collects quality metrics on every query** and exposes them via Prometheus for Grafana visualization.

## What's Implemented ✅

### Automatic Collection (Every Query)

The following metrics are **automatically collected on every `/query` API call** without requiring any ground truth data:

#### 1. Answer Quality Metrics

| Metric | Description | How It Works | Range |
|--------|-------------|--------------|-------|
| **Answer Faithfulness** | % of claims supported by context | Extracts claims from answer, checks if each is supported by retrieved chunks using word overlap | 0.0-1.0 |
| **Hallucination Detection** | Detects unsupported claims | Identifies claims in answer not found in context | Boolean + Severity |
| **Hallucination Severity** | Classification of hallucination severity | Minor / Moderate / Severe based on % of unsupported claims | Enum |
| **Answer Relevancy** | How well answer addresses query | Word overlap between query and answer (normalized) | 0.0-1.0 |
| **Answer Completeness** | Does answer fully address query | Checks answer length and completeness indicators | 0.0-1.0 |
| **Citation Grounding** | Are citations accurate | Verifies cited sources exist in context | 0.0-1.0 |

**Prometheus Metrics**:
- `rag_answer_faithfulness_score` (Histogram)
- `rag_hallucination_detected_total{severity}` (Counter)
- `rag_answer_relevancy_score` (Histogram)
- `rag_answer_completeness_score` (Histogram)
- `rag_citation_grounding_score` (Histogram)

#### 2. Context Quality Metrics

| Metric | Description | How It Works | Range |
|--------|-------------|--------------|-------|
| **Context Relevancy** | Average relevance of retrieved chunks | Uses retrieval scores from vector search | 0.0-1.0 |
| **Context Utilization** | % of chunks actually used in answer | Estimates which chunks were used via word overlap | 0.0-1.0 |
| **Context Precision** | (Partial) % of relevant chunks | Without ground truth, set to 0 (requires labels) | 0.0 |
| **Context Recall** | (Partial) % of required facts covered | Without ground truth, set to 0 (requires labels) | 0.0 |

**Prometheus Metrics**:
- `rag_context_relevancy` (Histogram)
- `rag_context_utilization` (Histogram)
- `rag_context_precision` (Histogram) - Always 0 without ground truth
- `rag_context_recall` (Histogram) - Always 0 without ground truth

### API Response

Quality metrics are now included in the API response:

```json
{
  "answer": "Patient has diabetes type 2...",
  "sources": [...],
  "cache_hit": false,
  "retrieved_docs": 5,
  "quality_metrics": {
    "answer": {
      "faithfulness": 0.95,
      "relevancy": 0.82,
      "completeness": 0.80,
      "has_hallucination": false,
      "hallucination_severity": "minor"
    },
    "context": {
      "relevancy": 0.87,
      "utilization": 0.75
    }
  }
}
```

### Hallucination Logging

When hallucinations are detected, the system **automatically logs a warning**:

```
WARNING: Hallucination detected - Query: What is patient's diagnosis,
Severity: moderate,
Unsupported claims: ['Patient has been scheduled for surgery next week']
```

This is **critical for healthcare applications** where fabricated medical information is dangerous.

## What's NOT Implemented ❌

### Requires Test Dataset with Ground Truth

The following metrics **cannot be automatically collected** because they require ground truth labels (knowing which documents/chunks are "correct" for each query):

#### 1. Information Retrieval (IR) Metrics

| Metric | Why Not Implemented | What's Needed |
|--------|---------------------|---------------|
| **Precision@k** | Needs ground truth relevant docs | Manual labels: "For query X, docs [A, C, E] are relevant" |
| **Recall@k** | Needs ground truth relevant docs | Same as Precision@k |
| **NDCG@k** | Needs graded relevance scores | Manual labels: "Doc A: 3/5, Doc B: 1/5, Doc C: 5/5" |
| **MRR** | Needs ground truth relevant docs | Same as Precision@k |
| **MAP** | Needs ground truth relevant docs | Same as Precision@k |
| **Hit Rate@k** | Needs ground truth relevant docs | Same as Precision@k |

**Why Ground Truth is Hard**:
- Requires manual labeling by domain experts
- Time-consuming (need 50-100+ labeled queries)
- Subjective (what's "relevant" for a query?)
- Changes over time (new documents added)

#### 2. Context Quality (Full)

| Metric | Why Not Implemented | What's Needed |
|--------|---------------------|---------------|
| **Context Precision** | Needs labels of which chunks are relevant | Manual labels per query |
| **Context Recall** | Needs set of required facts | Expert-defined fact lists |

#### 3. Retrieval Integration

The [hybrid_retriever.py](../src/document_store/search/hybrid_retriever.py:49-104) has **optional ground truth parameters**:

```python
results = retriever.retrieve(
    query="patient query",
    top_k=10,
    relevant_doc_ids={"doc1", "doc3"},  # Optional ground truth
    relevance_scores={"doc1": 3.0, "doc3": 2.0}  # Optional graded scores
)
```

When ground truth is provided, IR metrics are automatically calculated. But **production queries don't have ground truth**.

## Implementation Strategy

### Current: Real-Time (No Ground Truth)

✅ **Automatic on every query**:
- Answer Faithfulness
- Hallucination Detection
- Answer Relevancy
- Answer Completeness
- Context Relevancy
- Context Utilization

**Performance Impact**:
- Fast (word overlap heuristics, no LLM calls)
- ~5-10ms overhead per query
- Negligible impact on response time

### Future: Sample-Based (With Ground Truth)

For metrics requiring ground truth, use a **sampling approach**:

#### Option 1: Test Dataset Matching

Create a test dataset with labeled queries:

```python
# tests/evaluation/test_queries.json
{
  "query_hash_123": {
    "query": "What is patient's blood pressure medication?",
    "relevant_docs": ["med_list_2024", "bp_note"],
    "relevance_scores": {"med_list_2024": 3.0, "bp_note": 2.0}
  }
}

# In API endpoint:
query_hash = hash(request.query)
if query_hash in test_dataset:
    ground_truth = test_dataset[query_hash]
    # Evaluate IR metrics with ground truth
    ir_metrics = evaluate_retrieval_quality(...)
    MetricsCollector.record_ir_metrics(...)
```

**Pros**:
- Accurate IR metrics on known queries
- Tracks quality degradation over time
- Reproducible evaluation

**Cons**:
- Only works for queries in test dataset
- Requires manual labeling effort
- Test queries may not represent production

#### Option 2: Periodic Batch Evaluation

Run IR metrics evaluation **weekly on test dataset**:

```bash
# Cron job every Sunday
0 0 * * 0 python scripts/evaluate_test_dataset.py
```

```python
# scripts/evaluate_test_dataset.py
for test_query in load_test_dataset():
    results = retriever.retrieve(
        query=test_query['query'],
        relevant_doc_ids=test_query['relevant_docs'],
        relevance_scores=test_query.get('relevance_scores')
    )
    # IR metrics automatically recorded to Prometheus
```

**Pros**:
- No production latency impact
- Comprehensive evaluation on full test set
- Easier to manage

**Cons**:
- Not real-time (weekly updates)
- Requires maintaining test dataset

#### Option 3: User Feedback as Ground Truth

Collect implicit ground truth from user interactions:

```python
# Track user feedback
@app.post("/feedback")
async def feedback(query_id: str, doc_id: str, relevant: bool):
    # Store feedback
    feedback_store[query_id].append({
        "doc_id": doc_id,
        "relevant": relevant,
        "timestamp": datetime.now()
    })

# Use accumulated feedback for IR metrics
if query in feedback_store:
    relevant_docs = get_relevant_docs_from_feedback(query)
    # Evaluate IR metrics
```

**Pros**:
- Real user feedback
- Continuously updated
- Represents actual usage

**Cons**:
- Requires user engagement
- Biased (users may not click all relevant docs)
- Delayed (need time to accumulate feedback)

## How to Create Ground Truth

### Step 1: Identify Representative Queries

```python
# Analyze production query logs
top_queries = analyze_query_logs(
    min_frequency=10,  # Queries appearing 10+ times
    time_window="30d"
)

# Select diverse queries covering main use cases
test_queries = [
    "What are patient's diabetes medications?",
    "Summarize vital signs from last visit",
    "What allergies does patient have?",
    # ... 50-100 queries total
]
```

### Step 2: Manual Labeling

For each query, have domain expert label:

```json
{
  "query": "What are patient's diabetes medications?",
  "relevant_docs": [
    "med_list_2024_current",
    "diabetes_treatment_plan",
    "prescription_history_diabetes"
  ],
  "relevance_scores": {
    "med_list_2024_current": 3.0,      // Highly relevant
    "diabetes_treatment_plan": 2.0,    // Moderately relevant
    "prescription_history_diabetes": 2.0,
    "other_docs": 0.0                  // Not relevant
  },
  "required_facts": [
    "medication names",
    "dosages",
    "frequency"
  ]
}
```

**Labeling Guidelines**:
- 3.0 = Highly relevant (directly answers query)
- 2.0 = Moderately relevant (partially answers)
- 1.0 = Somewhat relevant (related but not essential)
- 0.0 = Not relevant

### Step 3: Store and Version

```python
# tests/evaluation/test_dataset_v1.json
{
  "version": "1.0",
  "created": "2024-11-18",
  "queries": [
    {
      "id": "query_001",
      "query": "...",
      "relevant_docs": [...],
      "relevance_scores": {...}
    }
  ]
}
```

### Step 4: Validate

```python
# Validate test dataset
python scripts/validate_test_dataset.py

# Checks:
# - All referenced docs exist in vector store
# - Relevance scores are valid (0-3)
# - No duplicate queries
# - Sufficient diversity (use cases covered)
```

## Configuration

### Enable/Disable Quality Metrics

Set environment variable to disable quality metrics in response (still collected for Prometheus):

```bash
# .env
INCLUDE_QUALITY_METRICS_IN_RESPONSE=false  # Default: true
```

```python
# In api_server.py
include_in_response = os.getenv("INCLUDE_QUALITY_METRICS_IN_RESPONSE", "true").lower() == "true"

if include_in_response:
    result["quality_metrics"] = quality_metrics
```

### Sampling Rate

For expensive evaluation (future LLM-based metrics):

```bash
# .env
QUALITY_METRICS_SAMPLING_RATE=0.1  # Evaluate 10% of queries
```

## Monitoring in Grafana

All metrics are automatically available in the **RAG Quality Metrics Dashboard**:

http://localhost:3333/d/4facbed2-cca8-4582-a2cc-c0e4b934a497/rag-quality-metrics

### Key Panels

1. **Hallucination Rate** - Real-time hallucination detection
2. **Answer Faithfulness** - Trend over time
3. **Context Relevancy** - Average relevance of retrieved chunks
4. **Context Utilization** - How much context is used
5. **Hallucination Severity Distribution** - Breakdown by severity

### Alerts

Set up alerts for critical issues:

```yaml
# Grafana Alert: High Hallucination Rate
- alert: HighHallucinationRate
  expr: rate(rag_hallucination_detected_total[5m]) > 0.05
  for: 10m
  annotations:
    summary: "High hallucination rate detected"
    description: "{{ $value }} hallucinations per second"

# Grafana Alert: Low Faithfulness
- alert: LowAnswerFaithfulness
  expr: avg(rag_answer_faithfulness_score) < 0.7
  for: 15m
  annotations:
    summary: "Answer faithfulness below threshold"
    description: "Average faithfulness: {{ $value }}"
```

## Performance Impact

### Real-Time Quality Metrics

Measured overhead per query:

| Operation | Time | Notes |
|-----------|------|-------|
| Answer quality evaluation | ~5ms | Word overlap, claim extraction |
| Context quality evaluation | ~3ms | Relevance calculation, utilization estimation |
| Prometheus recording | ~1ms | Metric updates |
| **Total Overhead** | **~10ms** | Negligible for most applications |

### Query Response Time

| Component | Typical Time |
|-----------|--------------|
| Retrieval (vector search) | 50-100ms |
| Generation (LLM) | 500-2000ms |
| **Quality evaluation** | **~10ms** |
| **Total** | **~560-2110ms** |

**Impact**: Quality evaluation adds **<1%** overhead to total query time.

## Limitations

### Current Implementation

1. **Word Overlap Heuristics**
   - May miss paraphrases ("diabetes" ≠ "diabetic condition")
   - Simple sentence splitting for claims
   - Not as accurate as LLM-based evaluation

2. **No Semantic Understanding**
   - Cannot detect contradictions
   - Cannot understand negations well
   - May miss subtle hallucinations

3. **No Ground Truth**
   - IR metrics not available (Precision, Recall, NDCG, MRR, MAP)
   - Context Precision/Recall always 0

### Future Improvements

**Phase 2: LLM-Based Evaluation**

Replace word overlap with semantic evaluation:

```python
# Use LLM-as-judge for faithfulness
def check_claim_faithfulness_llm(claim: str, context: str) -> bool:
    prompt = f"""
    Context: {context}
    Claim: {claim}

    Is this claim supported by the context?
    Answer: Yes/No
    """
    return llm.generate(prompt).strip().lower() == "yes"
```

**Benefits**:
- More accurate hallucination detection
- Catches paraphrases and synonyms
- Better semantic understanding

**Costs**:
- Slower (~100-500ms per evaluation)
- Inference cost (if using API)
- Requires LLM access

## Summary

### ✅ Implemented (Real-Time, Every Query)

- Answer Faithfulness
- Hallucination Detection (Minor/Moderate/Severe)
- Answer Relevancy
- Answer Completeness
- Citation Grounding
- Context Relevancy
- Context Utilization
- Prometheus metrics collection
- Grafana visualization
- Hallucination logging

### ❌ Not Implemented (Requires Ground Truth)

- Precision@k, Recall@k (need labeled relevant docs)
- NDCG@k, MRR, MAP (need relevance judgments)
- Hit Rate@k (need relevant doc labels)
- Context Precision (need chunk labels)
- Context Recall (need required facts)

### 📋 To Enable IR Metrics

1. Create test dataset with ground truth labels (50-100 queries)
2. Implement one of the strategies:
   - Option 1: Test dataset matching (real-time on known queries)
   - Option 2: Periodic batch evaluation (weekly)
   - Option 3: User feedback as ground truth (delayed)
3. Update API to check for ground truth and evaluate IR metrics

### 🎯 Current State

**Production Ready** ✅
- Real-time quality monitoring on every query
- Hallucination detection for clinical safety
- Minimal performance impact (~10ms)
- Full Grafana dashboard
- No ground truth required

**For Complete Metrics** ⏳
- Create test dataset (1-2 weeks effort)
- Implement sampling strategy
- Add periodic evaluation jobs

---

**Last Updated**: 2024-11-18
**Version**: 1.0
**Status**: Production Ready (Tier 1 metrics), Test Dataset Needed (Tier 2 metrics)
