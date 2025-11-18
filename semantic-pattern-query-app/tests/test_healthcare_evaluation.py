#!/usr/bin/env python3
"""
Healthcare-specific RAG evaluation test.

Demonstrates evaluation metrics with realistic healthcare scenarios.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from document_store.evaluation import (
    evaluate_retrieval_quality,
    evaluate_context_quality,
    evaluate_answer_quality,
)


def print_header(title: str):
    """Print formatted header."""
    print(f"\n{'='*100}")
    print(f"  {title}")
    print(f"{'='*100}\n")


def test_clinical_note_summarization():
    """Test evaluation for clinical note summarization use case."""
    print_header("Use Case 1: Clinical Note Summarization")

    query = "Summarize the patient's chief complaint and vital signs from today's visit"

    # Simulated retrieved chunks (from patient record)
    retrieved_chunks = [
        "Chief complaint: Patient reports persistent headache for 3 days, throbbing pain rated 7/10.",
        "Vital signs: BP 145/92, HR 88, Temp 98.6F, RR 16, SpO2 98% on room air.",
        "Past medical history: Hypertension, Type 2 Diabetes, managed with medications.",
        "Current medications: Lisinopril 10mg daily, Metformin 500mg twice daily.",
        "Social history: Non-smoker, occasional alcohol use.",
        "Review of systems: Denies chest pain, shortness of breath, nausea.",
        "Physical exam: Alert and oriented, mild temporal tenderness bilaterally.",
        "Assessment: Tension headache, hypertension poorly controlled."
    ]

    # Ground truth: Chunks 0, 1, 7 are relevant to the query
    relevant_chunk_indices = {0, 1, 7}

    # Chunk relevance scores (from retrieval system)
    chunk_relevance_scores = [0.95, 0.92, 0.45, 0.38, 0.22, 0.41, 0.78, 0.85]

    # Generated answer (good)
    good_answer = (
        "Chief complaint: Persistent headache for 3 days with throbbing pain (7/10 severity). "
        "Vital signs: Blood pressure 145/92 (elevated), heart rate 88 bpm, temperature 98.6°F, "
        "respiratory rate 16, oxygen saturation 98% on room air. "
        "Assessment indicates tension headache with poorly controlled hypertension."
    )

    # Generated answer (with hallucination)
    hallucinated_answer = (
        "Chief complaint: Persistent headache for 3 days with throbbing pain (7/10 severity). "
        "Vital signs: Blood pressure 145/92, heart rate 88 bpm. "
        "Patient has been prescribed new pain medication and referred to neurology for MRI scan. "
        "Blood work shows elevated cholesterol levels requiring statin therapy."
    )

    print("Query:")
    print(f"  '{query}'")
    print(f"\nRetrieved: {len(retrieved_chunks)} chunks")
    print(f"Relevant chunks: {sorted(relevant_chunk_indices)} (chief complaint, vitals, assessment)")

    # Evaluate context quality
    print("\n" + "-"*100)
    print("Context Quality Evaluation")
    print("-"*100)

    context_metrics = evaluate_context_quality(
        query=query,
        retrieved_chunks=retrieved_chunks,
        generated_answer=good_answer,
        chunk_relevance_scores=chunk_relevance_scores,
        relevant_chunk_indices=relevant_chunk_indices
    )

    print(f"  Context Precision:   {context_metrics['context_precision']:.1%}  "
          f"({len(relevant_chunk_indices)}/{len(retrieved_chunks)} chunks relevant)")
    print(f"  Context Relevancy:   {context_metrics['context_relevancy']:.1%}  "
          f"(avg relevance score)")
    print(f"  Context Utilization: {context_metrics['context_utilization']:.1%}  "
          f"(chunks used in answer)")

    # Evaluate good answer
    print("\n" + "-"*100)
    print("Answer Quality Evaluation - Good Answer (Faithful)")
    print("-"*100)
    print(f"Answer: {good_answer[:120]}...")

    good_metrics = evaluate_answer_quality(
        query=query,
        answer=good_answer,
        context_chunks=retrieved_chunks
    )

    print(f"\n  Faithfulness:    {good_metrics['faithfulness']:.1%}  "
          f"({good_metrics['supported_claims_count']}/{good_metrics['total_claims_count']} claims supported)")
    print(f"  Relevancy:       {good_metrics['relevancy']:.1%}  (addresses query)")
    print(f"  Completeness:    {good_metrics['completeness']:.1%}  (covers all aspects)")
    print(f"  Hallucination:   {good_metrics['has_hallucination']}  (no fabricated info)")

    # Evaluate hallucinated answer
    print("\n" + "-"*100)
    print("Answer Quality Evaluation - Bad Answer (Hallucinations)")
    print("-"*100)
    print(f"Answer: {hallucinated_answer[:120]}...")

    bad_metrics = evaluate_answer_quality(
        query=query,
        answer=hallucinated_answer,
        context_chunks=retrieved_chunks
    )

    print(f"\n  Faithfulness:    {bad_metrics['faithfulness']:.1%}  "
          f"({bad_metrics['supported_claims_count']}/{bad_metrics['total_claims_count']} claims supported)")
    print(f"  Hallucination:   {bad_metrics['has_hallucination']}  (🚨 detected)")
    print(f"  Severity:        {bad_metrics['hallucination_severity']}")

    if bad_metrics['unsupported_claims']:
        print(f"\n  Unsupported Claims:")
        for i, claim in enumerate(bad_metrics['unsupported_claims'], 1):
            print(f"    {i}. {claim}")

    print("\n✅ Clinical note summarization evaluation complete\n")


def test_medication_reconciliation():
    """Test evaluation for medication reconciliation use case."""
    print_header("Use Case 2: Medication Reconciliation")

    query = "What are the patient's current cardiac medications and their dosages?"

    # Simulated document retrieval
    retrieved_doc_ids = [
        "med_rec_2024", "vitals_jan", "med_rec_2023", "lab_results",
        "cardiac_note", "discharge_summary", "prescription_history", "allergy_list"
    ]

    # Ground truth: med_rec_2024, cardiac_note, prescription_history are relevant
    relevant_doc_ids = {"med_rec_2024", "cardiac_note", "prescription_history"}

    # Graded relevance (higher = more relevant)
    relevance_scores = {
        "med_rec_2024": 3.0,           # Most relevant
        "vitals_jan": 0.0,
        "med_rec_2023": 1.0,           # Somewhat relevant (old)
        "lab_results": 0.0,
        "cardiac_note": 2.0,           # Very relevant
        "discharge_summary": 1.0,      # Somewhat relevant
        "prescription_history": 2.0,   # Very relevant
        "allergy_list": 0.0
    }

    print("Query:")
    print(f"  '{query}'")
    print(f"\nRetrieved: {len(retrieved_doc_ids)} documents")
    print(f"Relevant: {sorted(relevant_doc_ids)}")

    # Evaluate retrieval quality
    print("\n" + "-"*100)
    print("Retrieval Quality Evaluation")
    print("-"*100)

    ir_metrics = evaluate_retrieval_quality(
        retrieved_doc_ids=retrieved_doc_ids,
        relevant_doc_ids=relevant_doc_ids,
        relevance_scores=relevance_scores,
        k_values=[1, 3, 5, 8]
    )

    print(f"  Precision@1:  {ir_metrics['precision@k'][1]:.1%}  "
          f"(is top result relevant?)")
    print(f"  Precision@3:  {ir_metrics['precision@k'][3]:.1%}  "
          f"(how many in top 3 are relevant?)")
    print(f"  Precision@5:  {ir_metrics['precision@k'][5]:.1%}  "
          f"(how many in top 5 are relevant?)")
    print(f"\n  Recall@3:     {ir_metrics['recall@k'][3]:.1%}  "
          f"(found {int(ir_metrics['recall@k'][3] * len(relevant_doc_ids))}/{len(relevant_doc_ids)} relevant docs)")
    print(f"  Recall@5:     {ir_metrics['recall@k'][5]:.1%}  "
          f"(found {int(ir_metrics['recall@k'][5] * len(relevant_doc_ids))}/{len(relevant_doc_ids)} relevant docs)")
    print(f"\n  MRR:          {ir_metrics['mrr']:.3f}  "
          f"(reciprocal rank of first relevant)")
    print(f"  MAP:          {ir_metrics['map']:.3f}  "
          f"(average precision across all relevant)")
    print(f"  NDCG@3:       {ir_metrics['ndcg@k'][3]:.3f}  "
          f"(ranking quality with position weighting)")

    print("\n✅ Medication reconciliation evaluation complete\n")


def test_adverse_event_detection():
    """Test evaluation for adverse event detection in clinical notes."""
    print_header("Use Case 3: Adverse Event Detection")

    query = "Are there any adverse drug reactions or side effects mentioned?"

    context_chunks = [
        "Patient reports increased dizziness since starting new blood pressure medication.",
        "Blood glucose levels remain stable on current diabetes regimen.",
        "Patient denies any rash, itching, or allergic reactions.",
        "Experiencing persistent dry cough that started 2 weeks after ACE inhibitor initiation.",
        "No nausea, vomiting, or gastrointestinal complaints."
    ]

    # Ground truth: chunks 0 and 3 describe adverse events
    relevant_chunks = {0, 3}
    chunk_scores = [0.88, 0.32, 0.25, 0.91, 0.28]

    # Good answer (detects both adverse events)
    good_answer = (
        "Yes, two potential adverse drug reactions are documented: "
        "1) Increased dizziness since starting new blood pressure medication, and "
        "2) Persistent dry cough that started 2 weeks after ACE inhibitor initiation. "
        "The dry cough is a known side effect of ACE inhibitors."
    )

    # Bad answer (misses events, adds false info)
    bad_answer = (
        "Yes, the patient is experiencing severe allergic reactions including rash and itching. "
        "Patient has been prescribed antihistamines and advised to discontinue all medications immediately."
    )

    print("Query:")
    print(f"  '{query}'")
    print(f"\nContext: {len(context_chunks)} chunks")
    print(f"Actual adverse events in context: chunks {sorted(relevant_chunks)}")

    # Evaluate good answer
    print("\n" + "-"*100)
    print("Answer Evaluation - Accurate Detection")
    print("-"*100)
    print(f"Answer: {good_answer}")

    good_metrics = evaluate_answer_quality(
        query=query,
        answer=good_answer,
        context_chunks=context_chunks
    )

    print(f"\n  Faithfulness:    {good_metrics['faithfulness']:.1%}  "
          f"✅ All claims supported by context")
    print(f"  Relevancy:       {good_metrics['relevancy']:.1%}  "
          f"✅ Directly addresses query")
    print(f"  Hallucination:   {good_metrics['has_hallucination']}  "
          f"✅ No fabricated information")

    # Evaluate bad answer
    print("\n" + "-"*100)
    print("Answer Evaluation - Dangerous Hallucination (Clinical Safety Issue)")
    print("-"*100)
    print(f"Answer: {bad_answer}")

    bad_metrics = evaluate_answer_quality(
        query=query,
        answer=bad_answer,
        context_chunks=context_chunks
    )

    print(f"\n  Faithfulness:    {bad_metrics['faithfulness']:.1%}  "
          f"🚨 Claims NOT in context")
    print(f"  Hallucination:   {bad_metrics['has_hallucination']}  "
          f"🚨 SEVERE clinical safety issue")
    print(f"  Severity:        {bad_metrics['hallucination_severity']}  "
          f"🚨 {bad_metrics['hallucination_severity'].upper()}")

    print(f"\n  🚨 CRITICAL: Unsupported Clinical Claims Detected:")
    for i, claim in enumerate(bad_metrics['unsupported_claims'], 1):
        print(f"    {i}. {claim}")

    print("\n  ⚠️  This demonstrates why hallucination detection is critical for healthcare AI!")

    print("\n✅ Adverse event detection evaluation complete\n")


def main():
    """Run all healthcare evaluation tests."""
    print("\n" + "="*100)
    print("  Healthcare RAG Evaluation - Real-World Use Cases")
    print("="*100)
    print("\n  Demonstrating evaluation metrics with realistic healthcare scenarios")
    print("  Shows both successful and problematic outputs\n")

    try:
        # Test 1: Clinical note summarization
        test_clinical_note_summarization()

        # Test 2: Medication reconciliation
        test_medication_reconciliation()

        # Test 3: Adverse event detection
        test_adverse_event_detection()

        # Summary
        print_header("Summary")
        print("✅ All healthcare evaluation scenarios completed successfully!\n")
        print("Key Takeaways:\n")
        print("  1. IR Metrics (Precision, Recall, NDCG, MRR, MAP)")
        print("     → Measure retrieval quality - are we finding the right documents?\n")
        print("  2. Context Quality Metrics (Precision, Relevancy, Utilization)")
        print("     → Measure context quality - are we retrieving relevant chunks?\n")
        print("  3. Answer Quality Metrics (Faithfulness, Hallucination Detection)")
        print("     → Measure answer safety - is the LLM making things up?\n")
        print("  4. Hallucination Detection is CRITICAL for healthcare AI")
        print("     → False medical information can be dangerous\n")
        print("  5. These metrics enable:")
        print("     → Quality monitoring in production")
        print("     → A/B testing different retrieval strategies")
        print("     → Alerting on quality degradation")
        print("     → Compliance and audit trails\n")
        print("="*100)
        print("\n🎯 Ready for integration into production RAG pipeline!")
        print("   Next: Create Grafana dashboard to visualize these metrics over time\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
