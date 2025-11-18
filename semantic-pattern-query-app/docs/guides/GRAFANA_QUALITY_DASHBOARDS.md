# Grafana Quality Metrics Dashboards

## Overview

The RAG system now has comprehensive quality metrics dashboards in Grafana for monitoring retrieval, context, and answer quality.

## Dashboard: RAG Quality Metrics

**URL**: http://localhost:3333/d/4facbed2-cca8-4582-a2cc-c0e4b934a497/rag-quality-metrics

### Dashboard Sections

#### 1. Quality Overview (Top Row)

**Overall Quality Score** - Composite metric averaging:
- Retrieval Precision@5
- Answer Faithfulness
- Context Relevancy

**Thresholds**:
- 🟢 Green: ≥ 70% (Good quality)
- 🟡 Yellow: 50-70% (Needs attention)
- 🔴 Red: < 50% (Critical)

**Hallucination Rate** - Rate of detected hallucinations per second
- 🟢 Green: 0 hallucinations/sec
- 🟡 Yellow: 0.01-0.05 hallucinations/sec
- 🔴 Red: > 0.05 hallucinations/sec

**Retrieval Precision@5** - What % of top 5 results are relevant
- 🟢 Green: ≥ 60%
- 🟡 Yellow: 40-60%
- 🔴 Red: < 40%

**Answer Faithfulness** - What % of claims are supported by context
- 🟢 Green: ≥ 90%
- 🟡 Yellow: 70-90%
- 🔴 Red: < 70%

**Hallucination Severity Distribution** - Pie chart showing breakdown by severity:
- Minor: Small factual inaccuracies
- Moderate: Significant unsupported claims
- Severe: Completely fabricated information

**Context Relevancy** - Average relevance score of retrieved chunks
- 🟢 Green: ≥ 70%
- 🟡 Yellow: 50-70%
- 🔴 Red: < 50%

**Context Utilization** - % of retrieved chunks actually used in answer
- 🟢 Green: ≥ 70%
- 🟡 Yellow: 50-70%
- 🔴 Red: < 50%

#### 2. Retrieval Quality Metrics

**Precision@k Over Time** - Line chart showing:
- Precision@1, @3, @5, @10
- Trend over time
- Helps identify retrieval degradation

**Recall@k Over Time** - Line chart showing:
- Recall@1, @3, @5, @10
- Coverage of relevant documents
- Balances with precision

**NDCG@k (Ranking Quality)** - Normalized Discounted Cumulative Gain
- Measures ranking quality with position weighting
- NDCG@1, @3, @5, @10
- Higher is better (max = 1.0)

**MRR (Mean Reciprocal Rank)** - Reciprocal of first relevant document rank
- MRR = 1.0: First result is relevant (perfect)
- MRR = 0.5: First relevant at position 2
- MRR = 0.33: First relevant at position 3

**MAP (Mean Average Precision)** - Overall ranking quality
- Considers precision at all relevant document positions
- Range: 0.0 to 1.0

#### 3. Context Quality Metrics

**Context Precision Over Time** - % of retrieved chunks that are relevant
- Measures retrieval noise
- Low precision = too many irrelevant chunks

**Context Recall Over Time** - % of required facts covered by retrieved chunks
- Measures retrieval completeness
- Low recall = missing important information

**Context Relevancy Trend** - Average relevance score with percentiles
- P95, P50, Average
- Identifies outliers and trends

**Context Utilization Trend** - % of chunks used in answer
- P95, P50, Average
- Low utilization suggests over-retrieval

#### 4. Answer Quality Metrics

**Answer Faithfulness Over Time** - % of claims supported by context
- P95, P50, P5 (5th percentile shows worst cases)
- Critical for healthcare - low faithfulness = hallucinations

**Answer Relevancy Over Time** - How well answer addresses query
- P95, P50, Average
- Low relevancy = off-topic answers

**Hallucination Detection Rate** - Rate of hallucinations by severity
- Minor, Moderate, Severe (separate lines)
- Critical safety metric for healthcare

**Answer Completeness** - % of query aspects addressed
- P95, Average
- Low completeness = partial answers

**Citation Grounding** - % of citations that are accurate
- Average over time
- Critical for source attribution

#### 5. Quality Alerts & Trends

**Quality Score Trend (7 Days)** - Composite quality over 7 days
- 7-day moving average vs current
- Identifies quality degradation

**Critical Issues (Last Hour)** - Count of critical issues:
- Severe hallucinations
- Low faithfulness (< 50%)
- Poor retrieval (Precision@5 < 30%)

**Thresholds**:
- 🟢 Green: 0 issues
- 🟡 Yellow: 1-5 issues
- 🔴 Red: > 5 issues

**Precision vs Recall Correlation** - Shows tradeoff between:
- Precision@5 (relevance)
- Recall@5 (coverage)
- Helps optimize retrieval strategy

**Context Quality vs Answer Quality** - Correlation between:
- Context Relevancy
- Answer Faithfulness
- Shows if poor context leads to hallucinations

## Using the Dashboard

### Monitoring Production Quality

1. **Overall Health Check** (Top row)
   - Quick glance at Overall Quality Score
   - Check for hallucinations (should be green)
   - Verify retrieval precision and answer faithfulness

2. **Investigate Issues**
   - If hallucination rate is high → Check Answer Quality section
   - If quality score drops → Check all three sections (Retrieval, Context, Answer)
   - Look for correlations between metrics

3. **Track Improvements**
   - After deploying changes (new embeddings, prompts, chunking):
   - Monitor quality trends over 7 days
   - Compare before/after metrics

### Alert Setup Recommendations

Create Grafana alerts for:

```yaml
Critical Alerts (PagerDuty/Slack):
- Severe hallucinations > 0 in last hour
- Overall quality score < 50% for 15 minutes
- Answer faithfulness < 60% for 5 minutes

Warning Alerts (Email):
- Hallucination rate > 0.01/sec for 30 minutes
- Retrieval precision@5 < 40% for 1 hour
- Context utilization < 30% (over-retrieval)
```

### Common Patterns to Watch

**Pattern 1: High Hallucination Rate**
- **Symptom**: Hallucination rate spike, low faithfulness
- **Cause**: LLM generating unsupported claims
- **Action**: Check prompt engineering, consider stricter generation constraints

**Pattern 2: Low Retrieval Precision**
- **Symptom**: Precision@k drops, context precision low
- **Cause**: Retrieval returning too many irrelevant documents
- **Action**: Tune retrieval parameters, review embedding quality

**Pattern 3: Low Context Utilization**
- **Symptom**: Context utilization < 50%, high context volume
- **Cause**: Over-retrieval (fetching too many chunks)
- **Action**: Reduce top_k, improve relevance threshold

**Pattern 4: Precision-Recall Tradeoff**
- **Symptom**: High precision but low recall (or vice versa)
- **Cause**: Retrieval parameters not balanced
- **Action**: Tune k values, adjust similarity thresholds

**Pattern 5: Quality Degradation**
- **Symptom**: 7-day trend shows declining quality score
- **Cause**: Data drift, model degradation, changing query patterns
- **Action**: Review recent deployments, check data quality

## Metric Definitions (Quick Reference)

| Metric | Formula | Range | Ideal Value |
|--------|---------|-------|-------------|
| Precision@k | (# relevant in top-k) / k | 0-1 | > 0.6 |
| Recall@k | (# relevant in top-k) / (total relevant) | 0-1 | > 0.7 |
| MRR | 1 / (rank of first relevant) | 0-1 | > 0.8 |
| MAP | Avg precision at all relevant positions | 0-1 | > 0.7 |
| NDCG@k | DCG@k / Ideal DCG@k | 0-1 | > 0.7 |
| Context Precision | (# relevant chunks) / (total chunks) | 0-1 | > 0.6 |
| Context Relevancy | Avg relevance score of chunks | 0-1 | > 0.7 |
| Context Utilization | (# chunks used) / (total chunks) | 0-1 | > 0.5 |
| Answer Faithfulness | (# supported claims) / (total claims) | 0-1 | > 0.9 |
| Answer Relevancy | Similarity between query and answer | 0-1 | > 0.7 |
| Answer Completeness | Addresses all query aspects | 0-1 | > 0.8 |

## Dashboard URLs

All dashboards are accessible at `http://localhost:3333`:

1. **RAG Quality Metrics** (NEW)
   - http://localhost:3333/d/4facbed2-cca8-4582-a2cc-c0e4b934a497/rag-quality-metrics
   - Comprehensive quality monitoring

2. **RAG Performance - Detailed Analytics**
   - http://localhost:3333 (check dashboard list)
   - Performance metrics (latency, throughput)

3. **RAG System - Real-Time Telemetry**
   - http://localhost:3333 (check dashboard list)
   - Real-time system monitoring

4. **Embedder Comparison - Ollama vs Gemini**
   - http://localhost:3333 (check dashboard list)
   - Compare embedding model performance

5. **Infrastructure Health**
   - http://localhost:3333 (check dashboard list)
   - System resources and health

## Troubleshooting

### "No data in quality metrics panels"

**Cause**: Metrics haven't been recorded yet

**Solution**:
1. Run evaluation tests to generate metrics:
   ```bash
   cd semantic-pattern-query-app
   python3 test_quality_metrics.py  # Requires prometheus_client
   ```

2. Or use hybrid retriever with ground truth:
   ```python
   results = retriever.retrieve(
       query="test query",
       relevant_doc_ids={"doc1", "doc3"}  # Ground truth
   )
   ```

3. Check Prometheus scraping:
   - Visit http://localhost:8000/metrics
   - Verify metrics are exposed
   - Check Prometheus targets: http://localhost:9090/targets

### "Dashboard shows errors"

**Cause**: Prometheus or Grafana not running

**Solution**:
```bash
cd semantic-pattern-query-app
docker-compose up -d grafana prometheus
./scripts/import_dashboards.sh
```

### "Metrics show 0 or NaN"

**Cause**: Division by zero or no ground truth

**Solution**:
- Some metrics require ground truth (Precision, Recall, NDCG, MRR, MAP)
- Others work without ground truth (Faithfulness, Relevancy, Utilization)
- Use test dataset with ground truth labels for full metrics

## Next Steps

1. **Create Test Dataset**
   - Create `tests/evaluation/test_queries.json` with ground truth
   - Run periodic batch evaluation
   - See [EVALUATION_QUICK_START.md](./EVALUATION_QUICK_START.md)

2. **Set Up Alerts**
   - Configure Grafana alerts for critical thresholds
   - Integrate with Slack/PagerDuty
   - Document on-call procedures

3. **Baseline Metrics**
   - Run evaluation on representative queries
   - Document current baseline metrics
   - Track improvements over time

4. **A/B Testing**
   - Use metrics to compare strategies
   - Track quality impact of changes
   - Data-driven decision making

## Resources

- **Implementation Guide**: [QUALITY_METRICS_IMPLEMENTATION.md](./QUALITY_METRICS_IMPLEMENTATION.md)
- **Quick Start**: [EVALUATION_QUICK_START.md](./EVALUATION_QUICK_START.md)
- **Test Scripts**: `test_quality_metrics_standalone.py`, `test_healthcare_evaluation.py`
- **Grafana Docs**: https://grafana.com/docs/grafana/latest/

---

**Dashboard Version**: 1.0
**Last Updated**: 2024-11-18
**Created By**: AI Summarization Reference Architecture Team
