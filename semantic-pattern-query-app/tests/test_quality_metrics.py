#!/usr/bin/env python3
"""
Test script for RAG quality metrics.

This script demonstrates:
1. Classical IR metrics (Precision@k, Recall@k, MRR, MAP, NDCG@k)
2. Context quality metrics (precision, recall, relevancy, utilization)
3. Answer quality metrics (faithfulness, relevancy, completeness, hallucination detection)
4. Integration with Prometheus metrics collection
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from document_store.evaluation import (
    # IR Metrics
    evaluate_retrieval_quality,
    # Context Quality
    evaluate_context_quality,
    # Answer Quality
    evaluate_answer_quality,
    HallucinationSeverity
)
from document_store.monitoring.metrics import MetricsCollector


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")


def test_ir_metrics():
    """Test classical Information Retrieval metrics."""
    print_section("Classical IR Metrics Test")

    # Simulate a retrieval scenario
    retrieved_doc_ids = [
        "doc1", "doc2", "doc3", "doc4", "doc5",
        "doc6", "doc7", "doc8", "doc9", "doc10"
    ]

    # Ground truth: docs 1, 3, 5, 8, 10 are relevant
    relevant_doc_ids = {"doc1", "doc3", "doc5", "doc8", "doc10"}

    # Graded relevance scores (for NDCG)
    relevance_scores = {
        "doc1": 3.0,  # Highly relevant
        "doc2": 0.0,  # Not relevant
        "doc3": 2.0,  # Moderately relevant
        "doc4": 0.0,
        "doc5": 2.0,
        "doc6": 0.0,
        "doc7": 0.0,
        "doc8": 1.0,  # Somewhat relevant
        "doc9": 0.0,
        "doc10": 1.0
    }

    print("Scenario:")
    print(f"  Retrieved: {len(retrieved_doc_ids)} documents")
    print(f"  Relevant: {len(relevant_doc_ids)} documents")
    print(f"  Relevant docs: {sorted(relevant_doc_ids)}")

    # Evaluate
    metrics = evaluate_retrieval_quality(
        retrieved_doc_ids=retrieved_doc_ids,
        relevant_doc_ids=relevant_doc_ids,
        relevance_scores=relevance_scores,
        k_values=[1, 3, 5, 10]
    )

    print("\nResults:")
    print(f"  Precision@1:  {metrics['precision@k'][1]:.3f}")
    print(f"  Precision@3:  {metrics['precision@k'][3]:.3f}")
    print(f"  Precision@5:  {metrics['precision@k'][5]:.3f}")
    print(f"  Precision@10: {metrics['precision@k'][10]:.3f}")
    print()
    print(f"  Recall@1:     {metrics['recall@k'][1]:.3f}")
    print(f"  Recall@3:     {metrics['recall@k'][3]:.3f}")
    print(f"  Recall@5:     {metrics['recall@k'][5]:.3f}")
    print(f"  Recall@10:    {metrics['recall@k'][10]:.3f}")
    print()
    print(f"  Hit Rate@1:   {metrics['hit_rate@k'][1]:.3f}")
    print(f"  Hit Rate@3:   {metrics['hit_rate@k'][3]:.3f}")
    print(f"  Hit Rate@5:   {metrics['hit_rate@k'][5]:.3f}")
    print(f"  Hit Rate@10:  {metrics['hit_rate@k'][10]:.3f}")
    print()
    print(f"  MRR:          {metrics['mrr']:.3f}")
    print(f"  MAP:          {metrics['map']:.3f}")
    print()
    print(f"  NDCG@1:       {metrics['ndcg@k'][1]:.3f}")
    print(f"  NDCG@3:       {metrics['ndcg@k'][3]:.3f}")
    print(f"  NDCG@5:       {metrics['ndcg@k'][5]:.3f}")
    print(f"  NDCG@10:      {metrics['ndcg@k'][10]:.3f}")

    # Record to Prometheus
    MetricsCollector.record_ir_metrics(
        precision_at_k=metrics['precision@k'],
        recall_at_k=metrics['recall@k'],
        hit_rate_at_k=metrics['hit_rate@k'],
        mrr=metrics['mrr'],
        map_score=metrics['map'],
        ndcg_at_k=metrics['ndcg@k']
    )

    print("\n✅ IR metrics recorded to Prometheus")

    return metrics


def test_context_quality():
    """Test context quality metrics."""
    print_section("Context Quality Metrics Test")

    query = "What are the patient's current medications and dosages?"

    retrieved_chunks = [
        "Patient is currently taking Metformin 500mg twice daily.",
        "Blood pressure reading: 120/80 mmHg.",
        "Patient also takes Lisinopril 10mg once daily.",
        "Last visit was on January 15, 2024.",
        "Atorvastatin 20mg prescribed for cholesterol management."
    ]

    generated_answer = (
        "The patient is currently on three medications: "
        "Metformin 500mg twice daily for diabetes, "
        "Lisinopril 10mg once daily for blood pressure, "
        "and Atorvastatin 20mg for cholesterol."
    )

    # Ground truth: chunks 0, 2, 4 are relevant (medications)
    relevant_chunk_indices = {0, 2, 4}

    # Chunk relevance scores (from retrieval)
    chunk_relevance_scores = [0.92, 0.45, 0.88, 0.25, 0.85]

    print("Scenario:")
    print(f"  Query: {query}")
    print(f"  Retrieved: {len(retrieved_chunks)} chunks")
    print(f"  Relevant chunks: {sorted(relevant_chunk_indices)}")
    print(f"  Generated answer length: {len(generated_answer)} chars")

    # Evaluate
    metrics = evaluate_context_quality(
        query=query,
        retrieved_chunks=retrieved_chunks,
        generated_answer=generated_answer,
        chunk_relevance_scores=chunk_relevance_scores,
        relevant_chunk_indices=relevant_chunk_indices
    )

    print("\nResults:")
    print(f"  Context Precision:   {metrics['context_precision']:.3f}")
    print(f"  Context Recall:      {metrics['context_recall']:.3f}")
    print(f"  Context Relevancy:   {metrics['context_relevancy']:.3f}")
    print(f"  Context Utilization: {metrics['context_utilization']:.3f}")

    # Record to Prometheus
    MetricsCollector.record_context_quality(
        precision=metrics['context_precision'],
        recall=metrics['context_recall'],
        relevancy=metrics['context_relevancy'],
        utilization=metrics['context_utilization']
    )

    print("\n✅ Context quality metrics recorded to Prometheus")

    return metrics


def test_answer_quality():
    """Test answer quality metrics."""
    print_section("Answer Quality Metrics Test")

    query = "What is the patient's diagnosis and treatment plan?"

    context_chunks = [
        "Patient diagnosed with Type 2 Diabetes Mellitus in January 2024.",
        "Treatment plan includes Metformin 500mg twice daily.",
        "Patient advised to follow diabetic diet and exercise regimen.",
        "Follow-up appointment scheduled in 3 months."
    ]

    # Good answer (faithful to context)
    good_answer = (
        "The patient was diagnosed with Type 2 Diabetes Mellitus in January 2024. "
        "The treatment plan includes Metformin 500mg twice daily, along with "
        "a diabetic diet and exercise regimen. A follow-up appointment is scheduled in 3 months."
    )

    # Answer with hallucination
    bad_answer = (
        "The patient was diagnosed with Type 2 Diabetes Mellitus in January 2024. "
        "The treatment includes Metformin 500mg and insulin injections three times daily. "
        "Patient has been referred to a cardiologist for heart surgery next week."
    )

    print("Scenario 1: Good Answer (Faithful)")
    print(f"  Query: {query}")
    print(f"  Context chunks: {len(context_chunks)}")
    print(f"  Answer: {good_answer[:100]}...")

    # Evaluate good answer
    good_metrics = evaluate_answer_quality(
        query=query,
        answer=good_answer,
        context_chunks=context_chunks
    )

    print("\nResults (Good Answer):")
    print(f"  Faithfulness:         {good_metrics['faithfulness']:.3f}")
    print(f"  Relevancy:            {good_metrics['relevancy']:.3f}")
    print(f"  Completeness:         {good_metrics['completeness']:.3f}")
    print(f"  Citation Grounding:   {good_metrics['citation_grounding']:.3f}")
    print(f"  Has Hallucination:    {good_metrics['has_hallucination']}")
    print(f"  Hallucination Severity: {good_metrics['hallucination_severity']}")
    print(f"  Supported Claims:     {good_metrics['supported_claims_count']}/{good_metrics['total_claims_count']}")

    # Record to Prometheus
    MetricsCollector.record_answer_quality(
        faithfulness=good_metrics['faithfulness'],
        relevancy=good_metrics['relevancy'],
        completeness=good_metrics['completeness'],
        citation_grounding=good_metrics['citation_grounding'],
        has_hallucination=good_metrics['has_hallucination'],
        hallucination_severity=good_metrics['hallucination_severity']
    )

    print("\n" + "-"*80)
    print("\nScenario 2: Bad Answer (Hallucinations)")
    print(f"  Answer: {bad_answer[:100]}...")

    # Evaluate bad answer
    bad_metrics = evaluate_answer_quality(
        query=query,
        answer=bad_answer,
        context_chunks=context_chunks
    )

    print("\nResults (Bad Answer):")
    print(f"  Faithfulness:         {bad_metrics['faithfulness']:.3f}")
    print(f"  Relevancy:            {bad_metrics['relevancy']:.3f}")
    print(f"  Completeness:         {bad_metrics['completeness']:.3f}")
    print(f"  Citation Grounding:   {bad_metrics['citation_grounding']:.3f}")
    print(f"  Has Hallucination:    {bad_metrics['has_hallucination']}")
    print(f"  Hallucination Severity: {bad_metrics['hallucination_severity']}")
    print(f"  Supported Claims:     {bad_metrics['supported_claims_count']}/{bad_metrics['total_claims_count']}")
    if bad_metrics['unsupported_claims']:
        print(f"\n  Unsupported Claims:")
        for claim in bad_metrics['unsupported_claims']:
            print(f"    - {claim}")

    # Record to Prometheus
    MetricsCollector.record_answer_quality(
        faithfulness=bad_metrics['faithfulness'],
        relevancy=bad_metrics['relevancy'],
        completeness=bad_metrics['completeness'],
        citation_grounding=bad_metrics['citation_grounding'],
        has_hallucination=bad_metrics['has_hallucination'],
        hallucination_severity=bad_metrics['hallucination_severity']
    )

    print("\n✅ Answer quality metrics recorded to Prometheus")

    return good_metrics, bad_metrics


def main():
    """Run all metric tests."""
    print("\n" + "="*80)
    print("RAG Quality Metrics Test Suite".center(80))
    print("="*80)

    try:
        # Test IR metrics
        ir_metrics = test_ir_metrics()

        # Test context quality
        context_metrics = test_context_quality()

        # Test answer quality
        good_answer_metrics, bad_answer_metrics = test_answer_quality()

        # Summary
        print_section("Summary")
        print("✅ All metrics calculated successfully!")
        print("\nKey Insights:")
        print(f"  - Retrieval Precision@5: {ir_metrics['precision@k'][5]:.1%}")
        print(f"  - Context Relevancy: {context_metrics['context_relevancy']:.1%}")
        print(f"  - Answer Faithfulness (Good): {good_answer_metrics['faithfulness']:.1%}")
        print(f"  - Answer Faithfulness (Bad): {bad_answer_metrics['faithfulness']:.1%}")
        print(f"  - Hallucination Detected: {bad_answer_metrics['has_hallucination']}")

        print("\n📊 All metrics have been recorded to Prometheus")
        print("   View them at: http://localhost:8000/metrics")
        print("   Grafana dashboards: http://localhost:3333")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
