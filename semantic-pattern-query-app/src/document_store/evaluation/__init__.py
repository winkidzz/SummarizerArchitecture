"""
Evaluation module for RAG system quality metrics.

This module provides implementations for:
- Classical Information Retrieval metrics (Precision@k, Recall@k, MRR, MAP, NDCG@k)
- Context quality metrics (precision, recall, relevancy, utilization)
- Answer quality metrics (faithfulness, relevancy, completeness, hallucination detection)
"""

from .ir_metrics import (
    calculate_precision_at_k,
    calculate_recall_at_k,
    calculate_mrr,
    calculate_map,
    calculate_ndcg_at_k,
    calculate_hit_rate_at_k,
    evaluate_retrieval_quality
)

from .context_metrics import (
    calculate_context_precision,
    calculate_context_recall,
    calculate_context_relevancy,
    calculate_context_utilization,
    estimate_chunk_usage_from_answer,
    evaluate_context_quality
)

from .answer_quality import (
    HallucinationSeverity,
    extract_claims_from_answer,
    check_claim_support,
    calculate_answer_faithfulness,
    detect_hallucinations,
    calculate_answer_relevancy_simple,
    calculate_answer_completeness,
    extract_citations_from_answer,
    calculate_citation_grounding,
    evaluate_answer_quality
)

__all__ = [
    # IR Metrics
    'calculate_precision_at_k',
    'calculate_recall_at_k',
    'calculate_mrr',
    'calculate_map',
    'calculate_ndcg_at_k',
    'calculate_hit_rate_at_k',
    'evaluate_retrieval_quality',
    # Context Quality Metrics
    'calculate_context_precision',
    'calculate_context_recall',
    'calculate_context_relevancy',
    'calculate_context_utilization',
    'estimate_chunk_usage_from_answer',
    'evaluate_context_quality',
    # Answer Quality Metrics
    'HallucinationSeverity',
    'extract_claims_from_answer',
    'check_claim_support',
    'calculate_answer_faithfulness',
    'detect_hallucinations',
    'calculate_answer_relevancy_simple',
    'calculate_answer_completeness',
    'extract_citations_from_answer',
    'calculate_citation_grounding',
    'evaluate_answer_quality'
]
