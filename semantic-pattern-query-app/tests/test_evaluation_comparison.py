#!/usr/bin/env python3
"""
Side-by-side comparison: Good vs Bad RAG outputs.

Demonstrates how evaluation metrics catch quality issues.
"""

import sys
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from document_store.evaluation import (
    evaluate_retrieval_quality,
    evaluate_answer_quality,
)


def compare_retrieval_strategies():
    """Compare two different retrieval strategies."""
    print("\n" + "="*100)
    print("  RETRIEVAL COMPARISON: Vector Search vs Hybrid Search")
    print("="*100)

    query = "Patient's diabetes medications"
    relevant_docs = {"med_list_current", "diabetes_note", "prescription_2024"}

    # Strategy 1: Vector search only (semantic but might miss exact terms)
    vector_results = [
        "glucose_monitor", "med_list_current", "diet_plan",
        "diabetes_note", "lab_results", "insulin_pump"
    ]

    # Strategy 2: Hybrid search (semantic + keyword)
    hybrid_results = [
        "med_list_current", "prescription_2024", "diabetes_note",
        "glucose_monitor", "lab_results", "diet_plan"
    ]

    print(f"\nQuery: '{query}'")
    print(f"Ground truth relevant: {sorted(relevant_docs)}\n")

    # Evaluate vector search
    vector_metrics = evaluate_retrieval_quality(
        retrieved_doc_ids=vector_results,
        relevant_doc_ids=relevant_docs,
        k_values=[1, 3, 5]
    )

    # Evaluate hybrid search
    hybrid_metrics = evaluate_retrieval_quality(
        retrieved_doc_ids=hybrid_results,
        relevant_doc_ids=relevant_docs,
        k_values=[1, 3, 5]
    )

    # Display comparison
    print("-"*100)
    print(f"{'Metric':<25} {'Vector Only':<25} {'Hybrid (Vector+BM25)':<25} {'Winner'}")
    print("-"*100)

    metrics_to_compare = [
        ("Precision@1", vector_metrics['precision@k'][1], hybrid_metrics['precision@k'][1]),
        ("Precision@3", vector_metrics['precision@k'][3], hybrid_metrics['precision@k'][3]),
        ("Recall@3", vector_metrics['recall@k'][3], hybrid_metrics['recall@k'][3]),
        ("MRR", vector_metrics['mrr'], hybrid_metrics['mrr']),
        ("MAP", vector_metrics['map'], hybrid_metrics['map']),
    ]

    for name, vector_score, hybrid_score in metrics_to_compare:
        vector_str = f"{vector_score:.1%}"
        hybrid_str = f"{hybrid_score:.1%}"
        winner = "🏆 Hybrid" if hybrid_score > vector_score else ("🏆 Vector" if vector_score > hybrid_score else "Tie")
        print(f"{name:<25} {vector_str:<25} {hybrid_str:<25} {winner}")

    print("-"*100)
    print("\n✅ Hybrid search wins with better precision and ranking!")
    print("   IR metrics help you choose the best retrieval strategy.\n")


def compare_llm_outputs():
    """Compare outputs from different LLM models/prompts."""
    print("\n" + "="*100)
    print("  ANSWER QUALITY COMPARISON: GPT-4 vs Claude vs Gemini (Simulated)")
    print("="*100)

    query = "What are the patient's risk factors for cardiovascular disease?"

    context = [
        "Patient is a 62-year-old male with hypertension.",
        "Current smoker, 1 pack per day for 30 years.",
        "BMI 32, classified as obese.",
        "HbA1c 8.2% indicating poorly controlled diabetes.",
        "LDL cholesterol 165 mg/dL (elevated).",
        "Family history: Father had MI at age 58."
    ]

    # Simulated outputs from different models
    outputs = {
        "GPT-4 (detailed)": (
            "The patient has multiple cardiovascular risk factors: "
            "1) Hypertension (on treatment), "
            "2) Current smoker (30 pack-year history), "
            "3) Obesity (BMI 32), "
            "4) Poorly controlled Type 2 Diabetes (HbA1c 8.2%), "
            "5) Elevated LDL cholesterol (165 mg/dL), "
            "6) Positive family history (father MI at 58). "
            "All major modifiable risk factors are present."
        ),
        "Claude (concise)": (
            "Key cardiovascular risk factors identified: hypertension, active smoking, "
            "obesity, uncontrolled diabetes, elevated cholesterol, and family history of early MI."
        ),
        "Gemini (hallucinated)": (
            "The patient has cardiovascular risk factors including hypertension and smoking. "
            "Recent stress test showed abnormal results requiring cardiac catheterization. "
            "Patient has been scheduled for coronary artery bypass surgery next month."
        ),
        "Local Model (incomplete)": (
            "Patient has high blood pressure and smokes."
        )
    }

    print(f"\nQuery: '{query}'")
    print(f"Context: {len(context)} chunks from patient record\n")

    results = []

    for model_name, answer in outputs.items():
        metrics = evaluate_answer_quality(
            query=query,
            answer=answer,
            context_chunks=context
        )
        results.append((model_name, answer, metrics))

    # Display comparison table
    print("-"*100)
    print(f"{'Model':<25} {'Faithful':<12} {'Complete':<12} {'Halluc.':<12} {'Claims':<15}")
    print("-"*100)

    for model_name, answer, metrics in results:
        faithful = f"{metrics['faithfulness']:.0%}"
        complete = f"{metrics['completeness']:.0%}"
        halluc = "🚨 Yes" if metrics['has_hallucination'] else "✅ No"
        claims = f"{metrics['supported_claims_count']}/{metrics['total_claims_count']}"

        flag = "🏆" if metrics['faithfulness'] >= 0.9 and not metrics['has_hallucination'] else "  "
        print(f"{flag} {model_name:<23} {faithful:<12} {complete:<12} {halluc:<12} {claims:<15}")

    print("-"*100)

    # Show details for problematic output
    print("\n🚨 Detected Hallucination in Gemini Output:")
    for model_name, answer, metrics in results:
        if "Gemini" in model_name and metrics['unsupported_claims']:
            print(f"\n  Model: {model_name}")
            print(f"  Answer: {answer[:100]}...")
            print(f"\n  Unsupported claims:")
            for i, claim in enumerate(metrics['unsupported_claims'], 1):
                print(f"    {i}. {claim}")

    print("\n✅ Evaluation metrics identify the safest, most complete answer!")
    print("   Use these metrics to select the best LLM for your healthcare use case.\n")


def compare_chunk_sizes():
    """Compare different chunking strategies."""
    print("\n" + "="*100)
    print("  CONTEXT QUALITY COMPARISON: Small Chunks (256) vs Large Chunks (1024)")
    print("="*100)

    from document_store.evaluation import evaluate_context_quality

    query = "What medications is the patient taking for diabetes?"

    # Small chunks (256 tokens) - more precise but may split related info
    small_chunks = [
        "Metformin 500mg",
        "twice daily with meals",
        "Glipizide 5mg",
        "once daily before breakfast",
        "Blood pressure: Lisinopril 10mg daily",
        "Cholesterol: Atorvastatin 20mg nightly"
    ]
    small_relevant = {0, 1, 2, 3}  # Diabetes meds
    small_scores = [0.92, 0.88, 0.89, 0.85, 0.45, 0.42]

    # Large chunks (1024 tokens) - more context but less precise
    large_chunks = [
        "Current medications include Metformin 500mg twice daily with meals for diabetes management, "
        "and Glipizide 5mg once daily before breakfast for additional glycemic control.",
        "Cardiovascular medications: Lisinopril 10mg daily for blood pressure control, "
        "and Atorvastatin 20mg nightly for cholesterol management.",
        "Patient adherent to medication regimen, no reported side effects."
    ]
    large_relevant = {0}  # Only first chunk has diabetes meds
    large_scores = [0.95, 0.38, 0.52]

    answer = "The patient is taking Metformin 500mg twice daily and Glipizide 5mg once daily for diabetes."

    # Evaluate small chunks
    small_metrics = evaluate_context_quality(
        query=query,
        retrieved_chunks=small_chunks,
        generated_answer=answer,
        chunk_relevance_scores=small_scores,
        relevant_chunk_indices=small_relevant
    )

    # Evaluate large chunks
    large_metrics = evaluate_context_quality(
        query=query,
        retrieved_chunks=large_chunks,
        generated_answer=answer,
        chunk_relevance_scores=large_scores,
        relevant_chunk_indices=large_relevant
    )

    print(f"\nQuery: '{query}'\n")

    # Display comparison
    print("-"*100)
    print(f"{'Metric':<30} {'Small Chunks (256)':<25} {'Large Chunks (1024)':<25} {'Winner'}")
    print("-"*100)

    comparisons = [
        ("Chunks Retrieved", len(small_chunks), len(large_chunks)),
        ("Context Precision", small_metrics['context_precision'], large_metrics['context_precision']),
        ("Context Relevancy", small_metrics['context_relevancy'], large_metrics['context_relevancy']),
        ("Context Utilization", small_metrics['context_utilization'], large_metrics['context_utilization']),
    ]

    for name, small_val, large_val in comparisons:
        if isinstance(small_val, float):
            small_str = f"{small_val:.1%}"
            large_str = f"{large_val:.1%}"
            winner = "🏆 Small" if small_val > large_val else ("🏆 Large" if large_val > small_val else "Tie")
        else:
            small_str = str(small_val)
            large_str = str(large_val)
            winner = "🏆 Large" if large_val < small_val else "🏆 Small"

        print(f"{name:<30} {small_str:<25} {large_str:<25} {winner}")

    print("-"*100)
    print("\n✅ Small chunks have better precision (less noise)")
    print("✅ Large chunks have better relevancy (more context per chunk)")
    print("\n   Use context quality metrics to optimize your chunking strategy!\n")


def main():
    """Run all comparison tests."""
    print("\n" + "="*100)
    print("  RAG EVALUATION: Side-by-Side Comparisons")
    print("="*100)
    print("\n  Demonstrating how evaluation metrics help you make better decisions\n")

    try:
        # Test 1: Retrieval strategies
        compare_retrieval_strategies()

        # Test 2: LLM model selection
        compare_llm_outputs()

        # Test 3: Chunking strategies
        compare_chunk_sizes()

        # Summary
        print("="*100)
        print("  SUMMARY: Why These Metrics Matter")
        print("="*100)
        print("\n  1. Choose Better Retrieval Strategies")
        print("     → IR metrics show hybrid search outperforms vector-only")
        print("\n  2. Select Safer LLM Models")
        print("     → Hallucination detection identifies dangerous fabricated claims")
        print("\n  3. Optimize Chunking Parameters")
        print("     → Context quality metrics guide chunk size decisions")
        print("\n  4. Monitor Production Quality")
        print("     → Track metrics over time to detect degradation")
        print("\n  5. Build Trust with Stakeholders")
        print("     → Quantifiable quality metrics for healthcare compliance")
        print("\n" + "="*100)
        print("\n🎯 Ready to integrate these metrics into your RAG pipeline!")
        print("   Track them in Grafana for continuous quality monitoring.\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
