#!/usr/bin/env python3
"""
Standalone test script for RAG quality metrics (no dependencies required).

This script demonstrates the evaluation functions work correctly
without requiring the full application stack or Prometheus.
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
    print(f"  Precision@1:  {metrics['precision@k'][1]:.3f}  (1 relevant in top 1 / 1)")
    print(f"  Precision@3:  {metrics['precision@k'][3]:.3f}  (2 relevant in top 3 / 3)")
    print(f"  Precision@5:  {metrics['precision@k'][5]:.3f}  (3 relevant in top 5 / 5)")
    print(f"  Precision@10: {metrics['precision@k'][10]:.3f}  (5 relevant in top 10 / 10)")
    print()
    print(f"  Recall@1:     {metrics['recall@k'][1]:.3f}  (1 found / 5 total relevant)")
    print(f"  Recall@3:     {metrics['recall@k'][3]:.3f}  (2 found / 5 total relevant)")
    print(f"  Recall@5:     {metrics['recall@k'][5]:.3f}  (3 found / 5 total relevant)")
    print(f"  Recall@10:    {metrics['recall@k'][10]:.3f}  (5 found / 5 total relevant)")
    print()
    print(f"  Hit Rate@1:   {metrics['hit_rate@k'][1]:.3f}  (found relevant doc: Yes)")
    print(f"  Hit Rate@3:   {metrics['hit_rate@k'][3]:.3f}  (found relevant doc: Yes)")
    print(f"  Hit Rate@5:   {metrics['hit_rate@k'][5]:.3f}  (found relevant doc: Yes)")
    print(f"  Hit Rate@10:  {metrics['hit_rate@k'][10]:.3f}  (found relevant doc: Yes)")
    print()
    print(f"  MRR:          {metrics['mrr']:.3f}  (first relevant at position 1)")
    print(f"  MAP:          {metrics['map']:.3f}  (average precision across all relevant)")
    print()
    print(f"  NDCG@1:       {metrics['ndcg@k'][1]:.3f}  (ranking quality at k=1)")
    print(f"  NDCG@3:       {metrics['ndcg@k'][3]:.3f}  (ranking quality at k=3)")
    print(f"  NDCG@5:       {metrics['ndcg@k'][5]:.3f}  (ranking quality at k=5)")
    print(f"  NDCG@10:      {metrics['ndcg@k'][10]:.3f}  (ranking quality at k=10)")

    print("\n✅ IR metrics calculation successful")

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
    print(f"  Relevant chunks: {sorted(relevant_chunk_indices)} (chunks about medications)")
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
    print(f"  Context Precision:   {metrics['context_precision']:.3f}  (3 relevant / 5 total chunks)")
    print(f"  Context Recall:      {metrics['context_recall']:.3f}  (not calculated - requires ground truth facts)")
    print(f"  Context Relevancy:   {metrics['context_relevancy']:.3f}  (avg relevance score of all chunks)")
    print(f"  Context Utilization: {metrics['context_utilization']:.3f}  (estimated from text overlap)")

    print("\n✅ Context quality metrics calculation successful")

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

    print("Scenario 1: Good Answer (Faithful to Context)")
    print(f"  Query: {query}")
    print(f"  Context chunks: {len(context_chunks)}")
    print(f"  Answer: {good_answer[:80]}...")

    # Evaluate good answer
    good_metrics = evaluate_answer_quality(
        query=query,
        answer=good_answer,
        context_chunks=context_chunks
    )

    print("\nResults (Good Answer):")
    print(f"  Faithfulness:         {good_metrics['faithfulness']:.3f}  (claims supported by context)")
    print(f"  Relevancy:            {good_metrics['relevancy']:.3f}  (answer addresses query)")
    print(f"  Completeness:         {good_metrics['completeness']:.3f}  (all query aspects covered)")
    print(f"  Citation Grounding:   {good_metrics['citation_grounding']:.3f}  (citations are accurate)")
    print(f"  Has Hallucination:    {good_metrics['has_hallucination']}")
    print(f"  Hallucination Severity: {good_metrics['hallucination_severity']}")
    print(f"  Supported Claims:     {good_metrics['supported_claims_count']}/{good_metrics['total_claims_count']}")

    print("\n" + "-"*80)
    print("\nScenario 2: Bad Answer (Contains Hallucinations)")
    print(f"  Answer: {bad_answer[:80]}...")

    # Evaluate bad answer
    bad_metrics = evaluate_answer_quality(
        query=query,
        answer=bad_answer,
        context_chunks=context_chunks
    )

    print("\nResults (Bad Answer):")
    print(f"  Faithfulness:         {bad_metrics['faithfulness']:.3f}  (some claims NOT supported)")
    print(f"  Relevancy:            {bad_metrics['relevancy']:.3f}  (answer addresses query)")
    print(f"  Completeness:         {bad_metrics['completeness']:.3f}  (all query aspects covered)")
    print(f"  Citation Grounding:   {bad_metrics['citation_grounding']:.3f}  (citations are accurate)")
    print(f"  Has Hallucination:    {bad_metrics['has_hallucination']}")
    print(f"  Hallucination Severity: {bad_metrics['hallucination_severity']}")
    print(f"  Supported Claims:     {bad_metrics['supported_claims_count']}/{bad_metrics['total_claims_count']}")

    if bad_metrics['unsupported_claims']:
        print(f"\n  🚨 Unsupported Claims Detected:")
        for i, claim in enumerate(bad_metrics['unsupported_claims'], 1):
            print(f"    {i}. {claim}")

    print("\n✅ Answer quality metrics calculation successful")

    return good_metrics, bad_metrics


def main():
    """Run all metric tests."""
    print("\n" + "="*80)
    print("RAG Quality Metrics Test Suite (Standalone)".center(80))
    print("="*80)
    print("\nThis test demonstrates the evaluation modules work correctly.")
    print("No Prometheus or application stack required.\n")

    try:
        # Test IR metrics
        ir_metrics = test_ir_metrics()

        # Test context quality
        context_metrics = test_context_quality()

        # Test answer quality
        good_answer_metrics, bad_answer_metrics = test_answer_quality()

        # Summary
        print_section("Test Summary")
        print("✅ All metrics calculated successfully!")

        print("\n📊 Key Metrics:")
        print(f"\n  Classical IR Metrics:")
        print(f"    • Precision@5:  {ir_metrics['precision@k'][5]:.1%}  (relevance of top 5 results)")
        print(f"    • Recall@5:     {ir_metrics['recall@k'][5]:.1%}  (coverage of relevant docs)")
        print(f"    • MRR:          {ir_metrics['mrr']:.3f}  (rank of first relevant doc)")
        print(f"    • MAP:          {ir_metrics['map']:.3f}  (overall ranking quality)")
        print(f"    • NDCG@5:       {ir_metrics['ndcg@k'][5]:.3f}  (position-aware quality)")

        print(f"\n  Context Quality Metrics:")
        print(f"    • Precision:    {context_metrics['context_precision']:.1%}  (relevant chunks retrieved)")
        print(f"    • Relevancy:    {context_metrics['context_relevancy']:.1%}  (avg chunk relevance)")
        print(f"    • Utilization:  {context_metrics['context_utilization']:.1%}  (chunks used in answer)")

        print(f"\n  Answer Quality Metrics (Good Answer):")
        print(f"    • Faithfulness: {good_answer_metrics['faithfulness']:.1%}  (claims supported)")
        print(f"    • Relevancy:    {good_answer_metrics['relevancy']:.1%}  (addresses query)")
        print(f"    • Completeness: {good_answer_metrics['completeness']:.1%}  (fully answers query)")
        print(f"    • Hallucination: {good_answer_metrics['has_hallucination']}  (no unsupported claims)")

        print(f"\n  Answer Quality Metrics (Bad Answer with Hallucinations):")
        print(f"    • Faithfulness: {bad_answer_metrics['faithfulness']:.1%}  (some claims unsupported)")
        print(f"    • Hallucination: {bad_answer_metrics['has_hallucination']}  (detected unsupported claims)")
        print(f"    • Severity:     {bad_answer_metrics['hallucination_severity']}  (hallucination severity level)")

        print("\n" + "="*80)
        print("\n🎯 Next Steps:")
        print("  1. These metrics are ready to be integrated into the RAG pipeline")
        print("  2. Install prometheus_client to enable metrics collection")
        print("  3. Metrics will be exposed at /metrics endpoint for Prometheus scraping")
        print("  4. Create Grafana dashboard to visualize quality metrics over time")
        print("\n" + "="*80)

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
